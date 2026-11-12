"""Read-only rejection diagnostics for fixed FLAME arc samples; no refitting."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

from .flame_arc_loss import supported_edges
from .flame_fit import nearest, outside
from .mesh_comparison import mesh_identity


REASONS = {
    'supported': ['Supported', '#46dd92'],
    'exclusion': ['Nose exclusion', '#e787ec'],
    'distance': ['Too far from target', '#ff6565'],
    'normal': ['Surface orientations disagree', '#ffbf47'],
    'degenerate': ['Negligible source step', '#ffffff'],
    'projection_jump': ['Projected step shrinks / stretches', '#61bcff'],
    'short_run': ['Supported run too short', '#b397ff'],
}


def diagnose(source, source_normals, target, span, exclusions):
    projected, distance, faces = nearest(target, source)
    normal_dot = np.abs(np.einsum('ij,ij->i', source_normals, target.face_normals[faces]))
    flags = {
        'exclusion': ~(outside(source, exclusions) & outside(projected, exclusions)),
        'distance': distance > span*.06,
        'normal': normal_dot < .5,
    }
    valid = ~np.logical_or.reduce(list(flags.values()))
    accepted = supported_edges(source, projected, valid, span)
    mask = np.zeros(len(source)-1, dtype=bool)
    mask[accepted[:, 0]] = True
    a = np.linalg.norm(np.diff(source, axis=0), axis=1)
    b = np.linalg.norm(np.diff(projected, axis=0), axis=1)
    edge_flags = {name: value[:-1] | value[1:] for name, value in flags.items()}
    edge_flags['degenerate'] = a <= span*1e-6
    edge_flags['projection_jump'] = (b < a*.5) | (b > a*1.5)
    edge_flags['short_run'] = ~mask & ~np.logical_or.reduce(list(edge_flags.values()))
    # Primary colors are exclusive; all overlapping rejection flags remain in JSON.
    primary = [next((name for name, values in edge_flags.items() if values[i]), 'supported')
               for i in range(len(mask))]
    return {
        'sample_count': len(source), 'valid_sample_count': int(valid.sum()),
        'supported_edges': accepted.tolist(), 'supported_edge_fraction': float(mask.mean()),
        'primary_reasons': primary,
        'primary_counts': {name: primary.count(name) for name in REASONS},
        'edge_flags': {name: np.flatnonzero(value).tolist() for name, value in edge_flags.items()},
        'sample_flags': {name: np.flatnonzero(value).tolist() for name, value in flags.items()},
        'sample_distances': distance.tolist(), 'sample_absolute_normal_dots': normal_dot.tolist(),
        'projected_points': projected.tolist(), 'target_triangle_indices': faces.tolist(),
        'projected_step_lengths': b.tolist(), 'source_step_lengths': a.tolist(),
    }


def exclude_triangles(mesh, exclusions):
    centers = mesh.triangles_center
    radius = np.linalg.norm(mesh.triangles-centers[:, None], axis=2).max(axis=1)
    keep = np.ones(len(mesh.faces), dtype=bool)
    for patch in exclusions:
        keep &= np.linalg.norm(centers-patch['center'], axis=1) > patch['radius']+radius
    if not keep.any(): raise ValueError('No broader analysis triangles outside exclusion.')
    return mesh.submesh([np.flatnonzero(keep)], append=True, repair=False)


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(fit_folder, seed_folder, session_folder, out):
    fit_folder=Path(fit_folder).resolve();seed_folder=Path(seed_folder).resolve()
    session_folder=Path(session_folder).resolve();out=Path(out).resolve()
    if out.exists() or any(out==p or p in out.parents for p in (fit_folder,seed_folder,session_folder)):
        raise ValueError('Use a fresh output directory outside all source directories.')
    report_path=fit_folder/'report.json';fit=json.loads(report_path.read_text())
    state_path=session_folder/'session.json';original=state_path.read_bytes();state=json.loads(original)
    if state['id']!=fit['session_id'] or mesh_identity(state['result']['surface']['mesh'])!=fit['source_mesh_id']:
        raise ValueError('Session analysis surface differs from the arc experiment.')
    seed_report=json.loads((seed_folder/'report.json').read_text())
    matches=[v for v in seed_report['variants'] if v['full_mesh_sha256']==fit['arc_experiment']['seed_mesh_sha256']]
    if len(matches)!=1: raise ValueError('Cannot identify exact annotated seed mesh.')
    seed_path=seed_folder/matches[0]['full_mesh']
    if digest(seed_path)!=fit['arc_experiment']['seed_mesh_sha256']: raise ValueError('Seed mesh hash changed.')
    seed=trimesh.load(seed_path,process=False)
    cropped=trimesh.load(fit_folder/'fitting-target.ply',process=False)
    raw=state['result']['surface']['mesh']
    analysis=trimesh.Trimesh(raw['vertices'],raw['triangles'],process=False)
    broader=exclude_triangles(analysis,fit['exclusions'])
    span=fit['eye_proxy_span'];arcs=[]
    for guide,old in zip(fit['arc_experiment']['guides'],fit['arc_experiment']['coverage']):
        if guide['id']!=old['id']: raise ValueError('Guide order differs from coverage report.')
        faces=np.array([a['triangle_index'] for a in guide['attachments']])
        weights=np.array([a['weights'] for a in guide['attachments']])
        points=np.einsum('ni,nic->nc',weights,seed.vertices[seed.faces[faces]])
        row={k:guide[k] for k in ('id','name','style')}
        row.update(review_status=old['review_status'],points=points.tolist(),targets={})
        for key,target in [('cropped',cropped),('broader',broader)]:
            row['targets'][key]=diagnose(points,seed.face_normals[faces],target,span,fit['exclusions'])
        # PLY stores float32 coordinates; accept a boundary change of one sampled
        # edge, but stop if we are no longer diagnosing the recorded experiment.
        recorded={tuple(e) for e in old['supported_edges']}
        actual={tuple(e) for e in row['targets']['cropped']['supported_edges']}
        if len(recorded.symmetric_difference(actual))>1:
            raise ValueError('Cropped support differs from recorded fit; cannot compare policies.')
        broad={tuple(e) for e in row['targets']['broader']['supported_edges']}
        row['recovered_by_broader']=[e[0] for e in sorted(broad-actual)]
        row['lost_on_broader']=[e[0] for e in sorted(actual-broad)]
        arcs.append(row)
    result={
        'version':'flame-arc-coverage-v1','session_id':fit['session_id'],
        'seed_mesh_sha256':digest(seed_path),'experiment_report_sha256':digest(report_path),
        'source_session_sha256':hashlib.sha256(original).hexdigest(),
        'algorithm_sha256':digest(__file__),'support_algorithm_sha256':digest(Path(__file__).with_name('flame_arc_loss.py')),
        'cropped_target_sha256':digest(fit_folder/'fitting-target.ply'),
        'source_mesh_id':fit['source_mesh_id'],'eye_proxy_span':span,'exclusions':fit['exclusions'],
        'reasons':REASONS,'arcs':arcs,'policy':fit['arc_experiment']['policy'],
        'targets':{'cropped':{'label':'Cropped fitting target','triangles':len(cropped.faces)},
                   'broader':{'label':'Broader analysis mesh · same nose exclusion','triangles':len(broader.faces)}},
        'limitations':['Fixed original annotated seed; no refitting or changed loss weights.',
                       'Broader means bounded analysis mesh, not the full dense reconstruction.',
                       'Both targets keep the same nose exclusion and support thresholds.',
                       'Recovered edges indicate sensitivity to target selection, not anatomical correctness or neck coverage.',
                       'Nearest surfaces may switch when the crop expands; support need not increase monotonically.',
                       'Colors use the first failing check; JSON also records all overlapping flags.',
                       'Overlay lines are not depth-tested. Coverage counts sampled edges, not surface area.']}
    camera=state['result']['cameras'][state['result']['frontal_camera_key']]
    rotation=np.diag([1.,-1.,-1.])@np.asarray(camera['R']);center=cropped.bounds.mean(axis=0)
    def display(points): return np.round((np.asarray(points)-center)@rotation.T,7).tolist()
    def mesh_data(mesh):return {'vertices':display(mesh.vertices),'triangles':mesh.faces.tolist()}
    data={'report':result,'seed':mesh_data(seed),'cropped':mesh_data(cropped),'broader':mesh_data(broader),
          'arc_points':[display(a['points']) for a in arcs]}
    if state_path.read_bytes()!=original:raise ValueError('Session changed during diagnostics.')
    out.mkdir(parents=True)
    (out/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    html=Path(__file__).with_suffix('.html').read_text()
    (out/'coverage.html').write_text(html.replace('/*COVERAGE_DATA*/',json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('fit','seed','session','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    try:run(args.fit,args.seed,args.session,args.out)
    except (ValueError,OSError,KeyError) as exc:parser.exit(1,f'Arc coverage failed: {exc}\n')
