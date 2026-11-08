"""Experimental local neutral FLAME fit to RealDenseFace priors, not the CUDA solver.

Shared identity/focal, per-photo rigid cameras, frozen CPU ray visibility per
outer round. Preserves neck-relative camera-z depth and uncertainty weighting.
"""
import argparse
import io
import json
import time
import zipfile
from pathlib import Path

import cv2
import numpy as np
import scipy.sparse
import trimesh
from scipy.optimize import least_squares

from .flame_open import ArrayUnpickler, load_model
from .flame_photo_fit import TRAIN, digest, photo_loss, project
from .realdenseface_local import ASSETS_SHA256, check_asset


class JointUnpickler(ArrayUnpickler):
    def find_class(self, module, name):
        if module in ('scipy.sparse.csc', 'scipy.sparse._csc') and name == 'csc_matrix':
            return scipy.sparse.csc_matrix
        if module in ('scipy.sparse.csr', 'scipy.sparse._csr') and name == 'csr_matrix':
            return scipy.sparse.csr_matrix
        return super().find_class(module, name)


def neck_regressor(path, provenance, count):
    path = Path(path)
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as archive:
            content = archive.read(provenance['model_member'])
    else:
        content = path.read_bytes()
    data = JointUnpickler(io.BytesIO(content), encoding='latin1').load()
    regressor = data['J_regressor']
    row = np.asarray(regressor[1].todense()).ravel()
    if row.shape != (count,) or not np.isfinite(row).all() or not np.isclose(row.sum(), 1, atol=1e-4):
        raise ValueError('Invalid FLAME neck-joint regressor')
    return row


def relative_depth(vertices, neck, pose):
    # Both upstream perspective camera and OpenCV use positive forward camera z.
    return (vertices-neck) @ cv2.Rodrigues(pose[:3])[0][2]


def visibility(vertices, faces, pose, ids, tolerance=1e-5):
    """Ray to each candidate vertex; reject an intervening surface triangle."""
    rotation = cv2.Rodrigues(pose[:3])[0]
    center = -rotation.T @ pose[3:]
    rays = vertices[ids]-center
    distance = np.linalg.norm(rays, axis=1)
    unit = rays/distance[:, None]
    mesh = trimesh.Trimesh(vertices, faces, process=False)
    hit, ray_ids, _ = mesh.ray.intersects_location(np.tile(center, (len(ids), 1)), unit, multiple_hits=False)
    keep = np.zeros(len(ids), dtype=bool)
    hit_distance = np.linalg.norm(hit-center, axis=1)
    keep[ray_ids] = np.abs(hit_distance-distance[ray_ids]) <= tolerance
    normals = np.asarray(mesh.vertex_normals)[ids]
    return keep & (np.sum(normals*-rays, axis=1) > 0) & ((vertices[ids] @ rotation.T+pose[3:])[:, 2] > 0)


def residual_and_jacobian(beta, log_focal, poses, template, basis, neck, neck_basis, views, masks,
                          depth_weight, prior, jacobian=False):
    components = len(beta)
    vertices = template+np.einsum('vck,k->vc', basis, beta)
    joint = neck+neck_basis @ beta
    focal = views[0]['size'][0]*np.exp(log_focal)
    rows = []
    blocks = []
    for index, (view, pose, mask) in enumerate(zip(views, poses, masks)):
        ids = view['ids'][mask]
        v = vertices[ids]
        b = basis[ids]
        rotation = cv2.Rodrigues(pose[:3])[0]
        cam = v @ rotation.T+pose[3:]
        # Upstream normalizes coordinates by image size and uses .018*exp(-.5 logvar).
        # Multiplying all data terms by native width gives pixel-like residual units.
        width, height = view['size']
        weights = .018*np.exp(-.5*view['coord_logvar'][mask])
        axis_weights = weights[:, None]*np.array([1., width/height])
        predicted, cv_jac = cv2.projectPoints(v, pose[:3], pose[3:], np.array([[focal, 0, width/2], [0, focal, height/2], [0, 0, 1.]]), None)
        predicted = predicted[:, 0]
        xy = (predicted-view['xy'][mask])*axis_weights
        depth_weights = width*depth_weight*.018*np.exp(-.5*view['depth_logvar'][mask])
        delta = v-joint
        z = delta @ rotation[2]
        depth = (z-view['depth'][mask])*depth_weights
        # Keep depth rows even in the zero-depth ablation for an identical layout.
        rows.append(np.c_[xy, depth].ravel())
        if not jacobian:
            continue
        n = len(ids)
        local = np.zeros((n, 3, components+1+6*len(views)))
        dp = np.zeros((n, 2, 3))
        dp[:, 0, 0] = focal/cam[:, 2]
        dp[:, 1, 1] = focal/cam[:, 2]
        dp[:, :, 2] = -focal*cam[:, :2]/cam[:, 2, None]**2
        local[:, :2, :components] = np.einsum('nij,jc,nck->nik', dp, rotation, b)*axis_weights[:, :, None]
        local[:, 2, :components] = np.einsum('c,nck->nk', rotation[2], b-neck_basis[None])*depth_weights[:, None]
        local[:, :2, components] = (predicted-np.array([width/2, height/2]))*axis_weights
        offset = components+1+6*index
        local[:, :2, offset:offset+6] = cv_jac[:, :6].reshape(n, 2, 6)*axis_weights[:, :, None]
        # Rotation derivative only for relative depth; translations cancel at the neck.
        for k in range(3):
            perturb = pose[:3].copy()
            perturb[k] += 1e-7
            derivative = (cv2.Rodrigues(perturb)[0][2]-rotation[2])/1e-7
            local[:, 2, offset+k] = (delta @ derivative)*depth_weights
        blocks.append(scipy.sparse.csr_matrix(local.reshape(-1, local.shape[-1])))
    residual = np.r_[np.concatenate(rows), np.sqrt(prior)*beta]
    if not jacobian:
        return residual
    last = scipy.sparse.hstack([scipy.sparse.eye(components)*np.sqrt(prior), scipy.sparse.csr_matrix((components, 1+6*len(views)))])
    return scipy.sparse.vstack(blocks+[last], format='csr')


def fit(template, basis, faces, regressor, views, initial, components=100, depth_weight=2., prior=10000., rounds=3, evaluations=60):
    basis = basis[:, :, :components]
    joint = regressor @ template
    joint_basis = np.einsum('v,vck->ck', regressor, basis)
    width = views[0]['size'][0]
    # Baseline seeds shape/camera only. No reconstruction geometry enters this fit.
    beta = np.zeros(components)
    values = initial['shape_coefficients']
    beta[:min(len(values), components)] = values[:components]
    pose_lookup = {v['slot']: v['pose'] for v in initial['views']}
    poses = np.array([pose_lookup[v['slot']] for v in views])
    x = np.r_[beta, np.log(initial['focal_pixels']/width), poses.ravel()]
    lower = np.r_[np.full(components, -3.), np.log(.5), np.tile([-np.inf]*5+[.001], len(views))]
    upper = np.r_[np.full(components, 3.), np.log(3.), np.full(6*len(views), np.inf)]
    history = []
    for outer in range(rounds):
        current = template+np.einsum('vck,k->vc', basis, x[:components])
        cameras = x[components+1:].reshape(-1, 6)
        masks = [visibility(current, faces, pose, v['ids']) for pose, v in zip(cameras, views)]
        for mask, view in zip(masks, views):
            mask &= (view['xy'][:, 0] >= 0) & (view['xy'][:, 0] < view['size'][0])
            mask &= (view['xy'][:, 1] >= 0) & (view['xy'][:, 1] < view['size'][1])
        if any(mask.sum() < 100 for mask in masks):
            raise ValueError('Too few visible dense correspondences')
        def evaluate(parameters, jac=False):
            return residual_and_jacobian(parameters[:components], parameters[components], parameters[components+1:].reshape(-1, 6),
                template, basis, joint, joint_basis, views, masks, depth_weight, prior, jacobian=jac)
        result = least_squares(evaluate, x, jac=lambda p: evaluate(p, True), bounds=(lower, upper),
            loss=lambda z: photo_loss(z, components), f_scale=3., x_scale='jac', max_nfev=evaluations,
            ftol=1e-5, xtol=1e-6, gtol=1e-5)
        x = result.x
        history.append({'round': outer+1, 'cost': float(result.cost), 'evaluations': result.nfev,
                        'stop': result.message, 'success': bool(result.success), 'visible_counts': [int(m.sum()) for m in masks]})
        print('Dense fit', depth_weight, history[-1], flush=True)
    return template+np.einsum('vck,k->vc', basis, x[:components]), x, history


def run(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    initial = json.loads(Path(args.baseline_report).read_text())
    template, basis, faces, provenance = load_model(args.model)
    if provenance['model_sha256'] != initial['model']['model_sha256']:
        raise ValueError('Baseline uses a different FLAME model')
    regressor = neck_regressor(args.model, provenance, len(template))
    check_asset(args.assets, ASSETS_SHA256)
    with np.load(args.assets, allow_pickle=False) as assets:
        if not np.array_equal(assets['faces'], faces):
            raise ValueError('Prediction and model topology differ')
        ids = np.unique(assets['key_region_faces'])
    prediction_folder = Path(args.predictions)
    prediction_report = json.loads((prediction_folder/'report.json').read_text())
    if prediction_report['weights_sha256'] != '9644fb9c7b7b8b5b6ca0d06fdebae418c154f1f4224a1ef5298777cc399ea15c':
        raise ValueError('Unexpected RealDenseFace predictor')
    rows = {v['slot']: v for v in prediction_report['views']}
    base_rows = {v['slot']: v for v in initial['views']}
    views = []
    for slot in TRAIN:
        if rows[slot]['image_sha256'] != base_rows[slot]['sha256'] or base_rows[slot]['split'] != 'train':
            raise ValueError('Dense predictions do not match training split')
        path = prediction_folder/(slot+'.npz')
        with np.load(path, allow_pickle=False) as data:
            values = [np.asarray(data[k], dtype=float) for k in ('vertex_coord', 'vertex_coord_log_var', 'vertex_depth', 'vertex_depth_log_var')]
        if [v.shape for v in values] != [(5023, 2), (5023, 1), (5023, 1), (5023, 1)] or not all(np.isfinite(v).all() for v in values):
            raise ValueError('Invalid dense predictions')
        views.append({'slot': slot, 'size': base_rows[slot]['image_size'], 'ids': ids,
                      'xy': values[0][ids], 'coord_logvar': np.clip(values[1][ids, 0], -8, 3),
                      'depth': values[2][ids, 0], 'depth_logvar': np.clip(values[3][ids, 0], -8, 3),
                      'sha256': digest(path)})
    start = time.monotonic()
    shape, parameters, history = fit(template, basis, faces, regressor, views, initial, args.components,
                                     args.depth_weight, args.prior, args.rounds, args.evaluations)
    tri, ref = shape[faces], template[faces]
    normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    reference = np.cross(ref[:, 1]-ref[:, 0], ref[:, 2]-ref[:, 0])
    report = {'version': 'realdenseface_local_fit_v1', 'model': provenance, 'session_id': initial['session_id'],
              'method': 'experimental SciPy fit; not an implementation of the official CUDA solver',
              'components': args.components, 'depth_weight': args.depth_weight, 'prior': args.prior,
              'units': 'FLAME_model_native_uncalibrated', 'shape_coefficients': parameters[:args.components].tolist(),
              'focal_pixels': float(views[0]['size'][0]*np.exp(parameters[args.components])),
              'poses': {v['slot']: p.tolist() for v, p in zip(views, parameters[args.components+1:].reshape(-1, 6))},
              'seconds': time.monotonic()-start, 'history': history,
              'baseline_report_sha256': digest(args.baseline_report), 'prediction_report_sha256': digest(prediction_folder/'report.json'),
              'prediction_hashes': {v['slot']: v['sha256'] for v in views},
              'initialization': 'direct-photo shape and cameras', 'held_out_photos_used_for_shape': False,
              'relative_depth_reference': 'FLAME neck joint (index 1), camera-z, translation cancels',
              'geometry': {'normal_reversals_vs_neutral': int(np.count_nonzero(np.sum(normals*reference, axis=1) < 0)),
                           'degenerate_triangles': int(np.count_nonzero(np.linalg.norm(normals, axis=1) < 1e-15)),
                           'coefficients_at_bound': int(np.count_nonzero(np.abs(parameters[:args.components]) > 2.99)),
                           'self_intersections': 'not_checked'},
              'limitations': ['Neutral expression and all articulation fixed to zero.',
                             'CPU ray visibility recomputed between optimization rounds, frozen within each round.',
                             'RealDenseFace depth learned from a different FLAME release; Open compatibility is exploratory.',
                             'No physical scale, measurement validation or anatomical accuracy established.']}
    trimesh.Trimesh(shape, faces, process=False).export(out/'flame-dense.ply')
    np.savez(out/'parameters.npz', parameters=parameters)
    (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    print(out/'report.json', report['geometry'], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('model', 'predictions', 'assets', 'baseline-report', 'out'):
        parser.add_argument('--'+key, required=True)
    parser.add_argument('--components', type=int, default=100, choices=(50, 100, 300))
    parser.add_argument('--depth-weight', type=float, default=2.)
    parser.add_argument('--prior', type=float, default=10000.)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--evaluations', type=int, default=60)
    args = parser.parse_args()
    if not np.isfinite([args.depth_weight, args.prior]).all() or args.depth_weight < 0 or args.prior <= 0 or min(args.rounds, args.evaluations) < 1:
        parser.error('Invalid fitting parameters')
    run(args)


if __name__ == '__main__':
    main()
