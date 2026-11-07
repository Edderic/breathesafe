"""Compare fixed arc support before/after mask expansion using camera-pose alignment."""
import argparse
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from scipy.spatial.transform import Rotation

from .flame_fit import similarity
from .flame_arc_coverage import diagnose, exclude_triangles, digest


def align_cameras(original, trial, span):
    old=original['result']['cameras'];new=trial['result']['cameras']
    keys=sorted(k for k in old if k.startswith('registered:turn_') and k in new)
    if len(keys)<54:raise ValueError('Need at least 54 matching turn-camera registrations.')
    def centers(cameras):return np.array([-np.asarray(cameras[k]['R']).T@np.asarray(cameras[k]['t']) for k in keys])
    source=centers(new);target=centers(old)
    scale,rotation,translation=similarity(source,target)
    distances=np.linalg.norm(scale*source@rotation.T+translation-target,axis=1)
    angles=[Rotation.from_matrix(np.asarray(new[k]['R'])@rotation.T@np.asarray(old[k]['R']).T).magnitude()*180/np.pi for k in keys]
    rms=float(np.sqrt(np.mean(distances**2)))
    if rms>.06*span:raise ValueError('Camera alignment RMS exceeds the arc distance threshold; compare registration first.')
    return scale,rotation,translation,{'method':'proper_similarity_on_all_common_registered_turn_camera_centers; no surface or arc fitting',
        'camera_count':len(keys),'camera_keys':keys,'scale':scale,'R':rotation.tolist(),'t':translation.tolist(),
        'camera_center_rms':rms,'camera_center_rms_fraction_eye_span':rms/span,
        'camera_center_max':float(distances.max()),'median_orientation_difference_degrees':float(np.median(angles)),
        'units':'original_reconstruction_unit','physical_calibration':False}


def run(original_folder,trial_folder,coverage_folder,seed_path,out,fit_folder):
    original_folder=Path(original_folder).resolve();trial_folder=Path(trial_folder).resolve()
    coverage_folder=Path(coverage_folder).resolve();seed_path=Path(seed_path).resolve();out=Path(out).resolve()
    if out.exists() or any(out==p or p in out.parents for p in (original_folder,trial_folder,coverage_folder,seed_path.parent)):
        raise ValueError('Use a fresh output directory outside source artifacts.')
    old_path=original_folder/'session.json';new_path=trial_folder/'session.json'
    original=json.loads(old_path.read_text());trial=json.loads(new_path.read_text())
    snapshots={p:digest(p) for p in (old_path,new_path,coverage_folder/'report.json',seed_path)}
    report=json.loads((coverage_folder/'report.json').read_text())
    if report['session_id']!=original['id'] or digest(seed_path)!=report['seed_mesh_sha256']:
        raise ValueError('Original coverage/seed identity mismatch.')
    if trial.get('mask_experiment',{}).get('source_session_id')!=original['id'] or trial['status']!='surface_ready':
        raise ValueError('Use a completed mask trial derived from this source session.')
    a={c['slot']:c for c in original['captures']};b={c['slot']:c for c in trial['captures']}
    if set(a)!=set(b) or len(a)!=61 or any(c.get('mask_approved') is not True for c in b.values()):
        raise ValueError('Need the same 61 reviewed captures.')
    def capture_path(folder,name):
        path=(folder/name).resolve()
        if folder not in path.parents:raise ValueError('Capture path escapes session.')
        return path
    for slot in a:
        before=Image.open(capture_path(original_folder,a[slot]['image'])).convert('RGB')
        after=Image.open(capture_path(trial_folder,b[slot]['image'])).convert('RGB')
        if before.size!=after.size or before.tobytes()!=after.tobytes():raise ValueError('Capture pixels changed; cannot isolate mask effect.')
    guide_path=Path(fit_folder)/'report.json'
    if digest(guide_path)!=report['experiment_report_sha256']:raise ValueError('Original guide report changed.')
    guides={g['id']:g for g in json.loads(guide_path.read_text())['arc_experiment']['guides']}
    span=report['eye_proxy_span'];scale,rotation,translation,alignment=align_cameras(original,trial,span)
    def analysis(state):
        raw=state['result']['surface']['mesh'];return trimesh.Trimesh(raw['vertices'],raw['triangles'],process=False)
    old_mesh=exclude_triangles(analysis(original),report['exclusions'])
    new_mesh=analysis(trial);new_mesh.vertices=scale*np.asarray(new_mesh.vertices)@rotation.T+translation
    new_mesh=exclude_triangles(new_mesh,report['exclusions'])
    seed=trimesh.load(seed_path,process=False)
    for arc in report['arcs']:
        old=arc['targets']['broader']
        seed_faces=np.array([a['triangle_index'] for a in guides[arc['id']]['attachments']])
        updated=diagnose(np.asarray(arc['points']),seed.face_normals[seed_faces],new_mesh,span,report['exclusions'])
        arc['targets']={'cropped':old,'broader':updated}
        first={tuple(e) for e in old['supported_edges']};second={tuple(e) for e in updated['supported_edges']}
        arc['recovered_by_broader']=[e[0] for e in sorted(second-first)]
        arc['lost_on_broader']=[e[0] for e in sorted(first-second)]
    report.update(version='webcam-neck-mask-coverage-v1',trial_session_id=trial['id'],alignment=alignment,
        session_snapshots={str(p):sha for p,sha in snapshots.items()},algorithm_sha256=digest(__file__),
        targets={'cropped':{'label':'Original masks · broader analysis','triangles':len(old_mesh.faces)},
                 'broader':{'label':'Expanded masks · aligned broader analysis','triangles':len(new_mesh.faces)}},
        limitations=report['limitations']+['New reconstruction aligned by shared camera centers; alignment uncertainty affects support.',
            'Same photographs verified pixel-for-pixel; all trial masks individually approved.',
            'Both targets use broader bounded analysis and the original-world nose exclusion.',
            'Coverage is against the unchanged original FLAME guide, not an anatomical accuracy measurement.'])
    camera=original['result']['cameras'][original['result']['frontal_camera_key']]
    view=np.diag([1.,-1.,-1.])@np.asarray(camera['R']);center=old_mesh.bounds.mean(axis=0)
    def display(points):return np.round((np.asarray(points)-center)@view.T,7).tolist()
    def payload(mesh):return {'vertices':display(mesh.vertices),'triangles':mesh.faces.tolist()}
    data={'report':report,'seed':payload(seed),'cropped':payload(old_mesh),'broader':payload(new_mesh),
          'arc_points':[display(arc['points']) for arc in report['arcs']]}
    for p,sha in snapshots.items():
        if digest(p)!=sha:raise ValueError('Source changed during comparison.')
    out.mkdir(parents=True)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    html=Path(__file__).with_name('flame_arc_coverage.html').read_text()
    replacements={
        'Why arc sections were rejected':'Under-jaw coverage after expanding masks',
        'Cropped fitting target':'Original masks · broader analysis',
        'Broader analysis mesh':'Expanded masks · aligned broader analysis',
        'Fixed original annotated FLAME fit. Compare its arc coverage against the cropped fitting target and the broader bounded analysis mesh. Both keep the same nose exclusion. This inspection does not change the fits, measurements or review statuses.':
        'Same 61 photos, with expanded masks individually reviewed. The new reconstruction is aligned to the original using 60 shared turn cameras. Both targets use the broader analysis mesh and the original nose exclusion. FLAME guides remain fixed; alignment uncertainty affects the comparison.',
        '<th>Cropped</th><th>Broader</th>':'<th>Original masks</th><th>Expanded masks</th>',
        'broader target':'expanded-mask target','broader mesh':'expanded-mask mesh',
        'More support on the broader mesh identifies crop sensitivity.':'More support on the expanded-mask mesh describes reconstruction agreement after camera alignment.',
        'value="broader">':'value="broader" selected>',
    }
    for before,after in replacements.items():html=html.replace(before,after)
    # Avoid implying the fitting crop is still the intervention in this view.
    html=html.replace('identifies crop sensitivity','describes reconstruction agreement after camera alignment')
    html=html.replace('It does not prove a rejected section was on the neck','It does not prove a recovered section is anatomically correct')
    (out/'coverage.html').write_text(html.replace('/*COVERAGE_DATA*/',json.dumps(data,separators=(',',':'),allow_nan=False).replace('<','\\u003c')))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('original','trial','coverage','seed','out','fit'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();run(args.original,args.trial,args.coverage,args.seed,args.out,args.fit)
