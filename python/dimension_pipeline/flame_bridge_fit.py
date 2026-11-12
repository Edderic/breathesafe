"""Matched FLAME bridge-weight sensitivity trials; defective tip stays excluded."""
import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from .flame_fit import fit, prepare, nearest, outside
from .flame_open import load_model
from .flame_arc_coverage import digest
from .flame_arc_loss import evaluate_arcs
from .flame_mapping import topology_id


def point(mesh, attachment):
    if attachment['kind']=='vertex':return np.asarray(mesh.vertices[attachment['vertex_index']])
    return np.asarray(attachment['weights'])@mesh.vertices[mesh.faces[attachment['triangle_index']]]


def bridge_region(mesh, target, ids, anchors, span, exclusions):
    """Frozen capsule near the named FLAME bridge, gated by target support."""
    start=point(mesh,anchors['sellion']['attachment']);end=point(mesh,anchors['pronasale']['attachment'])
    delta=end-start;length2=float(delta@delta)
    if length2<(.05*span)**2:raise ValueError('Bridge anchor span is too short.')
    positions=mesh.vertices[ids]
    parameter=np.clip((positions-start)@delta/length2,0,1)
    distance=np.linalg.norm(positions-(start+parameter[:,None]*delta),axis=1)
    radius=.12*span
    falloff=np.maximum(0,1-(distance/radius)**2)**2
    close,target_distance,target_faces=nearest(target,positions)
    normal=np.abs(np.einsum('ij,ij->i',mesh.vertex_normals[ids],target.face_normals[target_faces]))
    support=(target_distance<=span*.15)&(normal>=.5)&outside(positions,exclusions)&outside(close,exclusions)
    falloff*=support
    core=ids[falloff>.25]
    if len(core)<8:raise ValueError('Insufficient bridge support outside the tip exclusion.')
    return falloff,core,{'method':'fixed_seed_capsule_sellion_to_pronasale; exclusions_override_weights',
        'radius_fraction_eye_span':.12,'maximum_seed_distance_fraction_eye_span':.15,
        'minimum_absolute_normal_dot':.5,'weighted_vertices':int((falloff>0).sum()),
        'common_evaluation_vertices':core.tolist(),'anchor_statuses':{k:v['status'] for k,v in anchors.items()},
        'anchor_use':'region definitions and measurement proxies only; no positional landmark loss or acceptance transfer'}


def fixed_metric(mesh, ids, target, span, exclusions, forward):
    p=mesh.vertices[ids];close,distance,_=nearest(target,p)
    return {'vertices':len(ids),'rms':float(np.sqrt(np.mean(distance**2))),
        'rms_fraction_eye_span':float(np.sqrt(np.mean(distance**2))/span),
        'p95':float(np.quantile(distance,.95)),
        'mean_signed_forward_offset':float(np.mean((p-close)@forward)),
        'moved_inside_exclusion':int((~outside(p,exclusions)).sum()),
        'method':'same_frozen_vertex_ids_in_every_variant; points_moving_inside_exclusion_are_flagged_not_dropped'}


def nose_measurements(mesh, anchors, forward):
    sub=point(mesh,anchors['subnasale']['attachment']);tip=point(mesh,anchors['pronasale']['attachment'])
    difference=tip-sub
    return {'subnasale_pronasale_anchor_distance':float(np.linalg.norm(difference)),
            'forward_tip_projection_from_subnasale':float(difference@forward),
            'subnasale':sub.tolist(),'pronasale':tip.tolist(),
            'units':'original_reconstruction_unit','reference':'original frontal camera forward axis',
            'status':'unreviewed_FLAME_anchor_proxies; not independent anatomical measurements'}


def run(parent_folder, original_folder, seed_folder, annotations, model, probe, out):
    parent_folder=Path(parent_folder).resolve();original_folder=Path(original_folder).resolve();seed_folder=Path(seed_folder).resolve();out=Path(out).resolve()
    if out.exists() or any(out==p or p in out.parents for p in (parent_folder,original_folder,seed_folder)):
        raise ValueError('Use a fresh private output directory outside source artifacts.')
    parent_path=parent_folder/'report.json';parent=json.loads(parent_path.read_text())
    original=json.loads((original_folder/'session.json').read_text());draft=json.loads(Path(annotations).read_text())
    template,basis,faces,provenance=load_model(model)
    if provenance['model_sha256']!=parent['model']['model_sha256'] or topology_id(faces)!=draft['topology_id']:
        raise ValueError('Model or annotation topology mismatch.')
    seed_report=json.loads((seed_folder/'report.json').read_text());annotated=next(v for v in seed_report['variants'] if v.get('id',str(v['components']))==draft['fit_id'])
    if (digest(seed_folder/annotated['full_mesh'])!=draft['mesh_sha256'] or draft['model_sha256']!=provenance['model_sha256'] or
        draft['session_id']!=original['id']):raise ValueError('Annotation seed identity mismatch.')
    # Validate the complete draft with the same strict local UI validator used for arcs.
    from .flame_arc_loss import annotations_from_node
    annotation_seed=trimesh.load(seed_folder/annotated['full_mesh'],process=False)
    annotations_from_node(draft,annotation_seed,{**{k:draft[k] for k in ('session_id','fit_id','model_sha256','topology_id','mesh_sha256')},'_span':parent['eye_proxy_span']})
    anchors={p['name']:p for p in draft['points'] if p['name'] in ('sellion','subnasale','pronasale')}
    if len(anchors)!=3 or any(not a['attachment'] or a['status']=='unavailable' for a in anchors.values()):
        raise ValueError('Need placed sellion, subnasale and pronasale FLAME anchors.')
    baseline=next(v for v in parent['variants'] if v['id']=='100-neck')
    path=parent_folder/baseline['full_mesh']
    if digest(path)!=baseline['full_mesh_sha256']:raise ValueError('Parent fitted mesh changed.')
    seed=trimesh.load(path,process=False)
    payload=json.loads(Path(probe).read_text());payload['_session_folder']=str(original_folder)
    _,_,base_ids,_,initial,span,exclusions,camera=prepare(original,template,faces,payload)
    if exclusions!=parent['exclusions'] or span!=parent['eye_proxy_span']:raise ValueError('Original exclusion/scale policy differs.')
    ids=np.asarray(baseline['fitted_vertex_ids']);target=trimesh.load(parent_folder/'fitting-target.ply',process=False)
    face_target=trimesh.load(parent_folder/'face-target.ply',process=False)
    falloff,core,region=bridge_region(seed,target,ids,anchors,span,exclusions)
    forward=-np.asarray(camera['R'])[2]
    face_ids=base_ids[outside(seed.vertices[base_ids],exclusions)]
    neck_ids=np.setdiff1d(ids,base_ids)
    arc_points=[]
    for guide,coverage in zip(parent['arc_experiment']['guides'],parent['arc_experiment']['coverage']):
        selected=np.unique(np.asarray(coverage['supported_edges'],dtype=int))
        arc_points.extend(point(seed,guide['attachments'][i]) for i in selected)
    arc_distance=cKDTree(np.asarray(arc_points)).query(seed.vertices[ids])[0]
    arc_importance=1+3*np.maximum(0,1-(arc_distance/(span*.12))**2)**2
    arc_ids=ids[(arc_importance>1.5)&outside(seed.vertices[ids],exclusions)]
    snapshots={p:digest(p) for p in [parent_path,path,parent_folder/'fitting-target.ply',parent_folder/'face-target.ply',
        original_folder/'session.json',Path(annotations),Path(probe)]}
    report=copy.deepcopy(parent);report.update(variants=[],algorithm_sha256=digest(__file__),
        bridge_experiment={'version':'flame-bridge-weight-v1','region':region,'fixed_bridge_vertex_ids':core.tolist(),
            'weights':[1,2,4,8],'iterations':40,'components':100,'initialization':'same eye-based neutral initialization as parent neck experiment',
            'shape_prior':.0001,'coefficient_bound':3,'tip_exclusion_unchanged':True,'photo_constraints':False,
            'source_snapshots':{str(p):sha for p,sha in snapshots.items()},'anatomical_accuracy':'not_evaluated'},
        coverage_note='Bridge-weight sensitivity trial on the same supported face/jaw/neck crop. The defective nasal tip remains excluded. Named nose points are fixed FLAME attachment proxies, not accepted anatomical measurements. Compare common face, jaw/neck and bridge metrics.',
        limitations=parent['limitations']+['Bridge weights can change global pose/scale and surrounding face shape.',
            'No reference nose measurements or photo landmark constraints; the excluded tip remains prior driven.',
            'Signed bridge offset uses closest target triangles along the original frontal forward axis.'])
    out.mkdir(parents=True)
    for name in ('analysis.ply','fitting-target.ply','face-target.ply','face-topology.json'):(out/name).write_bytes((parent_folder/name).read_bytes())
    topology=json.loads((out/'face-topology.json').read_text());display_faces=topology['original_triangle_ids']
    source=trimesh.load(out/'analysis.ply',process=False)
    report['bridge_experiment']['display_bridge_vertex_ids']=core.tolist()
    def save():(out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for multiplier in (1,2,4,8):
        key='100' if multiplier==1 else f'100-bridge{multiplier}';start=time.monotonic()
        print('Bridge weight',multiplier,flush=True)
        vertices,row=fit(template,basis,faces,ids,target,initial,span,exclusions,100,40,
            importance=1+(multiplier-1)*falloff,
            progress=lambda h:print(h['iteration'],h['rms_before_update'],flush=True))
        mesh=trimesh.Trimesh(vertices,faces,process=False)
        reference=np.cross(template[faces[:,1]]-template[faces[:,0]],template[faces[:,2]]-template[faces[:,0]])@np.asarray(row['transform']['R']).T
        normals=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
        checks={'degenerate_triangles':int((mesh.area_faces<=1e-14*span**2).sum()),
            'normal_reversals_vs_transformed_neutral':int((np.einsum('ij,ij->i',reference,normals)<0).sum()),'self_intersections':'not_checked'}
        if checks['degenerate_triangles']:raise ValueError('Fit creates degenerate triangles.')
        row.update(id=key,label='Unweighted bridge baseline' if multiplier==1 else f'Bridge weights ×{multiplier}',
            weighting='bridge',bridge_weight=multiplier,geometry_checks=checks,fitted_vertex_ids=ids.tolist(),
            common_face=fixed_metric(mesh,face_ids,face_target,span,exclusions,forward),
            common_neck=fixed_metric(mesh,neck_ids,target,span,exclusions,forward),
            common_bridge=fixed_metric(mesh,core,target,span,exclusions,forward),nose_measurements=nose_measurements(mesh,anchors,forward),
            arc_evaluation=evaluate_arcs(mesh,parent['arc_experiment']['guides'],parent['arc_experiment']['coverage'],span),
            arc_region_surface_residual=fixed_metric(mesh,arc_ids,target,span,exclusions,forward),
            full_mesh=f'flame-{key}.ply',face_mesh=f'flame-{key}-face.ply')
        samples,_=trimesh.sample.sample_surface(target,2000,seed=41);_,distance,_=nearest(mesh.submesh([display_faces],append=True,repair=False),samples)
        row['target_to_flame_face']={'rms':float(np.sqrt(np.mean(distance**2))),'p95':float(np.quantile(distance,.95)),'samples':2000,'seed':41}
        mesh.export(out/row['full_mesh']);mesh.submesh([display_faces],append=True,repair=False).export(out/row['face_mesh'])
        row.update(full_mesh_sha256=digest(out/row['full_mesh']),face_mesh_sha256=digest(out/row['face_mesh']),seconds=time.monotonic()-start)
        report['variants'].append(row);save()
    for p,sha in snapshots.items():
        if digest(p)!=sha:raise ValueError('Source changed during bridge experiment.')
    from .flame_fit_view import write_view
    write_view(out,report,source,target,camera)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('parent','original','seed','annotations','model','probe','out'):parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args();run(a.parent,a.original,a.seed,a.annotations,a.model,a.probe,a.out)
