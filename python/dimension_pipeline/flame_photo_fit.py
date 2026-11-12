"""Neutral, shared-identity FLAME baseline fitted directly to native photo landmarks.

No reconstructed meshes, photogrammetry cameras, masks or saved route lengths enter
this objective. Detector agreement is a diagnostic, not anatomical ground truth.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix

from .flame_open import load_model

TRAIN = ('front', 'turn_05', 'turn_11', 'turn_17', 'turn_22', 'turn_35', 'turn_41', 'turn_48', 'turn_55')
HOLDOUT = ('turn_08', 'turn_20', 'turn_38', 'turn_51')
# Embedding entries use fixed surface locations, not sliding face-oval landmarks.
NOSE = {168, 6, 197, 195, 5, 4, 129, 98, 97, 2, 326, 327, 358}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_embedding(path, faces):
    with np.load(path, allow_pickle=False) as archive:
        indices = archive['landmark_indices']
        triangles = archive['lmk_face_idx']
        weights = archive['lmk_b_coords']
    n = len(indices)
    if (indices.shape != (n,) or triangles.shape != (n,) or weights.shape != (n, 3)
            or indices.dtype.kind not in 'iu' or triangles.dtype.kind not in 'iu'
            or n < 20 or len(np.unique(indices)) != n
            or indices.min() < 0 or indices.max() >= 468
            or triangles.min() < 0 or triangles.max() >= len(faces)
            or not np.isfinite(weights).all() or weights.min() < -1e-6
            or not np.allclose(weights.sum(axis=1), 1, atol=1e-6)):
        raise ValueError('Invalid FLAME/MediaPipe barycentric embedding')
    return indices.astype(int), triangles.astype(int), weights


def embed(vertices, faces, triangles, weights):
    return np.einsum('ni,nic...->nc...', weights, vertices[faces[triangles]])


def project(points, pose, focal, size):
    matrix = np.array([[focal, 0, size[0]/2], [0, focal, size[1]/2], [0, 0, 1.]])
    return cv2.projectPoints(points, pose[:3], pose[3:], matrix, None)[0][:, 0]


def visible(vertices, faces, triangles, weights, pose):
    """Front-facing test only; does not prove freedom from self occlusion."""
    points = embed(vertices, faces, triangles, weights)
    tri = vertices[faces[triangles]]
    normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    rotation = cv2.Rodrigues(pose[:3])[0]
    camera = points @ rotation.T + pose[3:]
    normals = normals @ rotation.T
    facing = np.sum(normals * -camera, axis=1)
    return (camera[:, 2] > 0) & (facing > 0)


def initial_pose(points, observations, focal, size, keep=None):
    keep = np.ones(len(points), dtype=bool) if keep is None else keep
    matrix = np.array([[focal, 0, size[0]/2], [0, focal, size[1]/2], [0, 0, 1.]])
    ok, r, t = cv2.solvePnP(np.ascontiguousarray(points[keep]), np.ascontiguousarray(observations[keep]),
                           matrix, None, flags=cv2.SOLVEPNP_EPNP)
    if not ok or t[2, 0] <= 0:
        raise ValueError('Could not initialize a positive-depth photo camera')
    return np.r_[r[:, 0], t[:, 0]]


def photo_loss(squared, components):
    """Soft-L1 image errors with an actual quadratic Gaussian shape prior."""
    rho = np.empty((3, len(squared)))
    root = np.sqrt(1+squared)
    rho[0] = 2*(root-1)
    rho[1] = 1/root
    rho[2] = -.5/root**3
    rho[0, -components:] = squared[-components:]
    rho[1, -components:] = 1
    rho[2, -components:] = 0
    return rho


def fit_identity(template, basis, faces, embedding, views, components=50, prior=1., rounds=3, evaluations=80):
    indices, triangles, weights = embedding
    basis = basis[:, :, :components]
    points = embed(template, faces, triangles, weights)
    directions = embed(basis, faces, triangles, weights)
    width = views[0]['size'][0]
    if any(v['size'] != views[0]['size'] for v in views):
        raise ValueError('This baseline requires a shared native image size and camera')
    focal = width * 1.2
    poses = np.array([initial_pose(points, v['observations'], focal, v['size']) for v in views])
    # Model-native scale fixes the similarity gauge; it does not calibrate mm.
    x = np.r_[np.zeros(components), np.log(focal/width), poses.ravel()]
    lower = np.r_[np.full(components, -3.), np.log(.5), np.tile([-np.inf]*5+[.001], len(views))]
    upper = np.r_[np.full(components, 3.), np.log(3.), np.full(6*len(views), np.inf)]
    history = []
    for iteration in range(rounds):
        shape = template + np.einsum('vck,k->vc', basis, x[:components])
        poses = x[components+1:].reshape(-1, 6)
        masks = [visible(shape, faces, triangles, weights, pose) for pose in poses]
        if any(np.count_nonzero(mask) < 20 for mask in masks):
            raise ValueError('Insufficient front-facing embedded landmarks')
        count = sum(2*np.count_nonzero(mask) for mask in masks) + components
        sparsity = lil_matrix((count, len(x)), dtype=int)
        cursor = 0
        for i, mask in enumerate(masks):
            end = cursor + 2*np.count_nonzero(mask)
            sparsity[cursor:end, :components+1] = 1
            sparsity[cursor:end, components+1+6*i:components+1+6*(i+1)] = 1
            cursor = end
        sparsity[cursor:, :components] = np.eye(components, dtype=int)

        def residual(parameters):
            current = points + np.einsum('nck,k->nc', directions, parameters[:components])
            f = width*np.exp(parameters[components])
            cameras = parameters[components+1:].reshape(-1, 6)
            values = [(project(current, pose, f, view['size'])-view['observations'])[mask].ravel()
                      for pose, view, mask in zip(cameras, views, masks)]
            # Prior in pixel-residual units. Report it explicitly for sensitivity trials.
            return np.r_[np.concatenate(values), np.sqrt(prior)*parameters[:components]]

        result = least_squares(residual, x, bounds=(lower, upper),
                               loss=lambda z: photo_loss(z, components), f_scale=3.,
                               jac_sparsity=sparsity.tocsr(), max_nfev=evaluations, x_scale='jac',
                               ftol=1e-5, xtol=1e-6, gtol=1e-5)
        x = result.x
        history.append({'round': iteration+1, 'evaluations': result.nfev, 'cost': float(result.cost),
                        'success': bool(result.success), 'stop': result.message,
                        'front_facing_landmarks': [int(m.sum()) for m in masks]})
        print(f'Photo fit round {iteration+1}: cost {result.cost:.3f}, {result.message}', flush=True)
    return template+np.einsum('vck,k->vc', basis, x[:components]), x[:components], width*np.exp(x[components]), x[components+1:].reshape(-1, 6), history


def detect_views(folder, out, slots):
    from .webcam_reconstruction import detect
    from PIL import Image
    captures = {c['slot']: c for c in json.loads((folder/'session.json').read_text())['captures']}
    cache_path = out/'landmarks.json'
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    views = []
    for slot in slots:
        capture = captures[slot]
        if not capture.get('mask_approved') or capture.get('mirrored') is not False:
            raise ValueError(f'{slot}: expected approved, explicitly unmirrored capture')
        path = folder/capture['image']
        if path.parent.resolve() != folder.resolve():
            raise ValueError('Capture must be a direct child of the session folder')
        sha = digest(path)
        if sha != capture['sha256']:
            raise ValueError(f'{slot}: capture hash changed')
        if slot not in cache or cache[slot]['sha256'] != sha:
            landmarks, provenance = detect(path)
            provenance['image'] = 'original native unmirrored capture'
            cache[slot] = {'sha256': sha, 'landmarks': landmarks, 'detector': provenance}
            cache_path.write_text(json.dumps(cache, indent=2))
        with Image.open(path) as image:
            size = image.size
        observed = np.array([[p['x']*size[0], p['y']*size[1]] for p in cache[slot]['landmarks']])
        views.append({'slot': slot, 'path': path, 'size': size, 'sha256': sha, 'all_observations': observed})
        print(f'Prepared {slot}', flush=True)
    return views


def fit_pose_only(points, observed, focal, size, keep):
    pose = initial_pose(points, observed, focal, size, keep)
    result = least_squares(lambda p: (project(points, p, focal, size)-observed)[keep].ravel(),
                           pose, loss='soft_l1', f_scale=3., max_nfev=150)
    return result.x


def run(args):
    import trimesh
    from PIL import Image, ImageDraw
    started = time.monotonic()
    folder, out = Path(args.session).resolve(), Path(args.out).resolve()
    if out.exists() and (out/'report.json').exists():
        raise ValueError('Choose a fresh output folder to preserve previous trials')
    out.mkdir(parents=True, exist_ok=True)
    template, basis, faces, provenance = load_model(args.model)
    embedding = load_embedding(args.embedding, faces)
    indices, triangles, weights = embedding
    views = detect_views(folder, out, TRAIN+HOLDOUT)
    for view in views:
        view['observations'] = view['all_observations'][indices]
    shape, beta, focal, poses, history = fit_identity(template, basis, faces, embedding, views[:len(TRAIN)],
        args.components, args.prior, args.rounds, args.evaluations)
    shape_tri = shape[faces]
    neutral_tri = template[faces]
    normals = np.cross(shape_tri[:, 1]-shape_tri[:, 0], shape_tri[:, 2]-shape_tri[:, 0])
    neutral_normals = np.cross(neutral_tri[:, 1]-neutral_tri[:, 0], neutral_tri[:, 2]-neutral_tri[:, 0])
    points = embed(shape, faces, triangles, weights)
    nose = np.isin(indices, list(NOSE))
    rows = []
    for i, view in enumerate(views):
        heldout = i >= len(TRAIN)
        pose = fit_pose_only(points, view['observations'], focal, view['size'], ~nose) if heldout else poses[i]
        front = visible(shape, faces, triangles, weights, pose)
        predicted = project(points, pose, focal, view['size'])
        errors = np.linalg.norm(predicted-view['observations'], axis=1)
        eye_span = float(np.linalg.norm(view['all_observations'][33]-view['all_observations'][263]))
        def metric(mask):
            return {'count': int(mask.sum()), 'rms_pixels': float(np.sqrt(np.mean(errors[mask]**2))) if mask.any() else None}
        rows.append({'slot': view['slot'], 'split': 'held_out_shape' if heldout else 'train',
                     'sha256': view['sha256'], 'image_size': list(view['size']), 'pose': pose.tolist(),
                     'eye_outer_corner_span_pixels': eye_span, 'all_front_facing': metric(front),
                     'nose_front_facing': metric(front & nose),
                     'pose_estimation': 'non-nose detector landmarks only' if heldout else 'joint training',
                     'observed_pixels': view['observations'].tolist(), 'predicted_pixels': predicted.tolist(),
                     'front_facing': front.tolist()})
        with Image.open(view['path']) as source:
            image = source.convert('RGB')
        draw = ImageDraw.Draw(image)
        for obs, pred, keep in zip(view['observations'], predicted, front):
            if not keep:
                continue
            draw.line([tuple(obs), tuple(pred)], fill='#ffb83d', width=2)
            for p, color in [(obs, '#25e9cf'), (pred, '#ff63c9')]:
                draw.ellipse((p[0]-3, p[1]-3, p[0]+3, p[1]+3), fill=color)
        image.thumbnail((960, 540))
        image.save(out/(view['slot']+'-overlay.jpg'), quality=92)
    trimesh.Trimesh(shape, faces, process=False).export(out/'flame-photo.ply')
    np.savez(out/'parameters.npz', shape=beta, focal_pixels=focal, train_poses=poses)
    report = {'version': 'flame_direct_photo_v1', 'session_id': folder.name,
              'model': provenance, 'embedding_sha256': digest(args.embedding),
              'method': 'shared neutral linear FLAME identity; soft-L1 image reprojection plus quadratic shape prior',
              'coefficients_at_bound': int(np.count_nonzero(np.abs(beta) > 2.99)),
              'components': args.components, 'coefficient_prior': args.prior, 'coefficient_bounds': [-3, 3],
              'focal_pixels': float(focal), 'principal_point': 'fixed image center', 'lens_distortion': 'zero assumed',
              'shape_coefficients': beta.tolist(), 'history': history, 'views': rows,
              'geometry': {'degenerate_triangles': int(np.count_nonzero(np.linalg.norm(normals, axis=1) < 1e-15)),
                           'normal_reversals_vs_neutral': int(np.count_nonzero(np.sum(normals*neutral_normals, axis=1) < 0)),
                           'self_intersections': 'not_checked'},
              'seconds': time.monotonic()-started, 'physical_scale': 'uncalibrated',
              'limitations': ['Neutral expression and articulation fixed to zero.',
                  'Front-facing normals only; no full self-occlusion test.',
                  'Landmarks only: no silhouette, photometric or dense correspondence objective yet.',
                  'Automatic detector agreement does not establish anatomical accuracy.',
                  'Held-out cameras use non-nose detector landmarks; nose is excluded from their pose estimation.',
                  'Unknown focal length and depth/shape ambiguity remain; no physical measurements validated.',
                  'Selected capture chronology is fixed before fitting; no reconstruction data used.']}
    (out/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    page = Path(__file__).with_name('flame_photo_view.html').read_text()
    payload = json.dumps({'report': report, 'vertices': shape.tolist(), 'faces': faces.tolist()},
                         allow_nan=False, separators=(',', ':')).replace('<', '\\u003c')
    (out/'comparison.html').write_text(page.replace('/*PHOTO_DATA*/', payload))
    print(out/'comparison.html', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--embedding', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--components', type=int, choices=(30, 50, 100, 300), default=100)
    parser.add_argument('--prior', type=float, default=100.)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--evaluations', type=int, default=80)
    args = parser.parse_args()
    if not np.isfinite(args.prior) or args.prior <= 0 or args.rounds < 1 or args.evaluations < 1:
        parser.error('prior, rounds and evaluations must be positive')
    run(args)


if __name__ == '__main__':
    main()
