"""Matched face-only and supported jaw/upper-neck FLAME fits on a mask trial."""
import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from .flame_fit import prepare, fit, nearest, outside
from .flame_open import load_model
from .flame_arc_coverage import exclude_triangles, digest
from .flame_arc_loss import prepare_constraints, evaluate_arcs
from .flame_mapping import topology_id
from .webcam_neck_compare import align_cameras
from .mesh_comparison import mesh_identity


def clean_triangles(mesh, span):
    """Reject long/thin caps and one face ring at open mesh boundaries."""
    triangles=mesh.triangles
    lengths=np.linalg.norm(triangles-np.roll(triangles,1,axis=1),axis=2)
    longest=lengths.max(axis=1);area=mesh.area_faces
    aspect=np.divide(longest**2,2*area,out=np.full(len(area),np.inf),where=area>0)
    unique,count=np.unique(mesh.edges_sorted,axis=0,return_counts=True)
    boundary_vertices=np.unique(unique[count==1])
    boundary=np.isin(mesh.faces,boundary_vertices).any(axis=1)
    keep=(longest<=.12*span)&(aspect<=12)&(area>1e-12*span**2)&~boundary
    if keep.sum()<500:raise ValueError('Insufficient target triangles after boundary-quality filtering.')
    return mesh.submesh([np.flatnonzero(keep)],append=True,repair=False),{
        'input_triangles':len(mesh.faces),'kept_triangles':int(keep.sum()),
        'long_edge_triangles':int((longest>.12*span).sum()),'thin_triangles':int((aspect>12).sum()),
        'open_boundary_incident_triangles':int(boundary.sum()),'counts_overlap':True,
        'maximum_edge_fraction_eye_span':.12,'maximum_longest_edge_to_altitude':12,
        'boundary_policy':'discard_all_faces_incident_to_an_original_open_boundary_vertex; no filling or smoothing'}


def face_target(source, state, exclusions):
    result=state['result'];camera=result['cameras'][result['frontal_camera_key']]
    oval=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,
          148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
    predictions=result['raw_predictions']
    polygon=np.array([[predictions[i]['x']*camera['width'],predictions[i]['y']*camera['height']] for i in oval])
    hull=ConvexHull(polygon);centers=source.triangles_center
    view=centers@np.asarray(camera['R']).T+camera['t']
    pixels=view[:,:2]/view[:,2,None]*[camera['fx'],camera['fy']]+[camera['cx'],camera['cy']]
    inside=(pixels@hull.equations[:,:2].T+hull.equations[:,2]<=0).all(axis=1)&(view[:,2]>0)
    indices=np.flatnonzero(inside);origin=-np.asarray(camera['R']).T@np.asarray(camera['t'])
    first=source.ray.intersects_first(np.repeat(origin[None],len(indices),axis=0),centers[indices]-origin)
    selected=indices[first==indices]
    target=source.submesh([selected],append=True,repair=False)
    return exclude_triangles(target,exclusions)


def supported_model_crop(template, faces, face_ids, seed, target, initial, span, exclusions):
    # Same neutral head component as the face crop; do not include eyeballs.
    components=trimesh.graph.connected_components(trimesh.Trimesh(template,faces,process=False).edges_unique,min_len=3)
    head=max(components,key=len)
    eyes=[template[c][np.argmax(template[c,2])] for c in components if len(c)<len(head)]
    eye_center=np.mean(eyes,axis=0);eye_span=np.linalg.norm(eyes[0]-eyes[1])
    keep=np.zeros(len(template),dtype=bool);keep[head]=True
    keep&=(template[:,1]>eye_center[1]-2.05*eye_span)&(template[:,1]<eye_center[1]+.9*eye_span)
    keep&=(np.abs(template[:,0]-eye_center[0])<1.25*eye_span)&(template[:,2]>eye_center[2]-.55*eye_span)
    keep&=template[:,1]<eye_center[1]-.75*eye_span
    keep[np.unique(faces[face_ids])]=True
    display_faces=np.flatnonzero(keep[faces].all(axis=1));candidates=np.unique(faces[display_faces])
    base=np.unique(faces[face_ids]);added=np.setdiff1d(candidates,base)
    close,distance,target_faces=nearest(target,seed.vertices[added])
    normal=np.abs(np.einsum('ij,ij->i',seed.vertex_normals[added],target.face_normals[target_faces]))
    valid=(distance<=.10*span)&(normal>=.5)&outside(seed.vertices[added],exclusions)&outside(close,exclusions)
    supported=added[valid]
    if len(supported)<30:raise ValueError('Fewer than 30 supported added jaw/neck vertices; do not fit missing geometry.')
    return np.unique(np.r_[base,supported]),display_faces,supported,{
        'candidate_added_vertices':len(added),'supported_added_vertices':len(supported),
        'maximum_seed_distance_fraction_eye_span':.10,'minimum_absolute_normal_dot':.5,
        'neutral_crop':'head; eye-relative y [-2.05,0.9], abs(x)<1.25, z>eye_z-0.55, in neutral eye spans',
        'support_gating':'frozen original seed fit; unchanged added vertex set across trials'}


def metric(mesh, ids, target, span, exclusions):
    points=mesh.vertices[ids];points=points[outside(points,exclusions)]
    if not len(points):raise ValueError('No evaluable region points.')
    _,d,_=nearest(target,points)
    return {'vertices':len(points),'rms':float(np.sqrt(np.mean(d*d))),'p95':float(np.quantile(d,.95)),
            'rms_fraction_eye_span':float(np.sqrt(np.mean(d*d))/span),'units':'original_reconstruction_unit'}


def run(original, trial, seed_folder, arc_folder, coverage_folder, model, probe, out):
    original=Path(original).resolve();trial=Path(trial).resolve();seed_folder=Path(seed_folder).resolve();arc_folder=Path(arc_folder).resolve()
    coverage_folder=Path(coverage_folder).resolve();out=Path(out).resolve()
    if out.exists() or any(out==p or p in out.parents for p in (original,trial,seed_folder,arc_folder,coverage_folder)):
        raise ValueError('Use a fresh private output outside source directories.')
    snapshots={p:digest(p) for p in [original/'session.json',trial/'session.json',seed_folder/'report.json',arc_folder/'report.json',coverage_folder/'report.json',Path(probe)]}
    old=json.loads((original/'session.json').read_text());new=json.loads((trial/'session.json').read_text())
    seed_report=json.loads((seed_folder/'report.json').read_text());arc_report=json.loads((arc_folder/'report.json').read_text())
    coverage=json.loads((coverage_folder/'report.json').read_text())
    if (new.get('mask_experiment',{}).get('source_session_id')!=old['id'] or new['status']!='surface_ready' or
        len(new['captures'])!=61 or any(c.get('mask_approved') is not True for c in new['captures'])):
        raise ValueError('Need a completed reviewed mask trial of the original session.')
    if coverage['trial_session_id']!=new['id'] or coverage['session_snapshots'][str(trial/'session.json')]!=digest(trial/'session.json'):
        raise ValueError('Re-run mask comparison after trial session changes.')
    template,basis,faces,model_provenance=load_model(model)
    if model_provenance['model_sha256']!=seed_report['model']['model_sha256']:raise ValueError('FLAME model changed.')
    exclusion=json.loads(Path(probe).read_text());exclusion['_session_folder']=str(original)
    _,_,base_ids,face_ids,initial,span,exclusions,camera=prepare(old,template,faces,exclusion)
    scale,rotation,translation,alignment=align_cameras(old,new,span)
    raw=new['result']['surface']['mesh'];source=trimesh.Trimesh(raw['vertices'],raw['triangles'],process=False)
    source.vertices=scale*source.vertices@rotation.T+translation
    clean,quality=clean_triangles(source,span);clean=exclude_triangles(clean,exclusions)
    baseline_target=face_target(clean,old,exclusions)
    seed_row=next(v for v in seed_report['variants'] if v.get('id',str(v['components']))=='100')
    seed_path=seed_folder/seed_row['full_mesh']
    if digest(seed_path)!=coverage['seed_mesh_sha256'] or topology_id(faces)!=seed_report['flame_topology_id']:
        raise ValueError('Seed geometry or topology changed.')
    seed=trimesh.load(seed_path,process=False)
    expanded_ids,display_faces,neck_ids,crop=supported_model_crop(template,faces,face_ids,seed,clean,initial,span,exclusions)
    # Use a fixed seed envelope to reject residual surfaces away from the intended
    # front-face/jaw/neck crop. No frontal-visibility filter on the expanded target.
    envelope=seed.submesh([display_faces],append=True,repair=False)
    _,distance,_=nearest(envelope,clean.triangles_center)
    selected=np.flatnonzero(distance<=.15*span)
    expanded_target=clean.submesh([selected],append=True,repair=False)
    if len(expanded_target.faces)<500:raise ValueError('Insufficient expanded target.')
    # Recheck source support against the exact final target after envelope filtering.
    expanded_ids,display_faces,neck_ids,crop=supported_model_crop(template,faces,face_ids,seed,expanded_target,initial,span,exclusions)
    definitions=[]
    for g,c in zip(arc_report['arc_experiment']['guides'],arc_report['arc_experiment']['coverage']):
        f=np.array([a['triangle_index'] for a in g['attachments']]);w=np.array([a['weights'] for a in g['attachments']])
        definitions.append({**{k:c[k] for k in ('id','name','style','review_status','mirrored','source_ui_length')},
                            'points':np.einsum('ni,nic->nc',w,seed.vertices[seed.faces[f]])})
    _,importance,arc_coverage,guides=prepare_constraints(definitions,seed,expanded_target,template,basis,expanded_ids,span,exclusions)
    report=copy.deepcopy(seed_report);report.update(session_id=new['id'],source_mesh_id=mesh_identity(raw),
        source_session_sha256=digest(trial/'session.json'),algorithm_sha256=digest(__file__),regional_mapping=None,
        regional_mapping_sha256=None,variants=[],eye_proxy_span=span,exclusions=exclusions,target_triangles=len(expanded_target.faces),
        fitting_source='new mask trial analysis mesh aligned to original world',
        neck_experiment={'version':'flame-supported-jaw-neck-v1','alignment':alignment,'target_quality':quality,'crop':crop,
            'target_seed_envelope_fraction_eye_span':.15,'source_snapshots':{str(p):v for p,v in snapshots.items()},
            'face_baseline_vertices':len(base_ids),'expanded_fit_vertices':len(expanded_ids),
            'common_evaluation':'fixed face vertices and fixed supported added jaw/neck vertices; same targets for both fits',
            'iterations':40,'components':100,'arc_length_loss':False,'arc_region_weights':False,
            'calibration_transferred':False,'annotations_transferred':False},
        arc_experiment={**arc_report['arc_experiment'],'guides':guides,'coverage':arc_coverage,
            'method':'read_only_arc_evaluation_on_fixed_new_expanded_target; no arc loss in these fits'},
        coverage_note='Compare face-only and supported jaw/upper-neck fitting. Only the recorded fitted vertices are constrained; ears, scalp, back of head and unsupported neck remain prior dominated. Old point reviews and tape calibration do not transfer.',
        limitations=['No independent anatomical accuracy validation; source reconstruction is noisy.',
            'Both trials use the same new reconstruction, initialization, 100 components and 40-iteration budget.',
            'Camera alignment uncertainty affects fitting and cross-run comparisons.',
            'Added jaw/neck vertices are constrained only where the fixed seed passes support checks.',
            'No scalar arc-length loss, photo loss, expression fit, hole filling or smoothing.'],
        face_crop={'model':crop,'target':'quality-filtered broader analysis within 0.15 eye spans of fixed seed envelope; same nose exclusion'})
    out.mkdir(parents=True)
    source.export(out/'analysis.ply');expanded_target.export(out/'fitting-target.ply');baseline_target.export(out/'face-target.ply')
    display_ids=np.unique(faces[display_faces])
    (out/'face-topology.json').write_text(json.dumps({'topology_id':topology_id(faces),'original_vertex_ids':display_ids.tolist(),
        'original_triangle_ids':display_faces.tolist(),'original_triangles':faces[display_faces].tolist()}))
    def save():(out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for key,label,ids,target in [('100','Face-only baseline',base_ids,baseline_target),('100-neck','Supported jaw + upper neck',expanded_ids,expanded_target)]:
        start=time.monotonic();print(label,len(ids),'vertices',len(target.faces),'triangles',flush=True)
        vertices,row=fit(template,basis,faces,ids,target,initial,span,exclusions,100,40,
            progress=lambda h:print(h['iteration'],h['rms_before_update'],flush=True))
        mesh=trimesh.Trimesh(vertices,faces,process=False)
        reference=np.cross(template[faces[:,1]]-template[faces[:,0]],template[faces[:,2]]-template[faces[:,0]])@np.asarray(row['transform']['R']).T
        normals=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
        checks={'degenerate_triangles':int((mesh.area_faces<=1e-14*span**2).sum()),
            'normal_reversals_vs_transformed_neutral':int((np.einsum('ij,ij->i',reference,normals)<0).sum()),'self_intersections':'not_checked'}
        if checks['degenerate_triangles']:raise ValueError('Degenerate fitted geometry.')
        row.update(id=key,label=label,weighting='ordinary',fitted_vertex_ids=ids.tolist(),geometry_checks=checks,
            common_face=metric(mesh,base_ids,baseline_target,span,exclusions),
            common_neck=metric(mesh,neck_ids,expanded_target,span,exclusions),
            arc_evaluation=evaluate_arcs(mesh,guides,arc_coverage,span),
            arc_region_surface_residual=metric(mesh,expanded_ids[importance>1.5],expanded_target,span,exclusions),
            full_mesh=f'flame-{key}.ply',face_mesh=f'flame-{key}-face.ply')
        samples,_=trimesh.sample.sample_surface(expanded_target,2000,seed=41)
        _,dist,_=nearest(mesh.submesh([display_faces],append=True,repair=False),samples)
        row['target_to_flame_face']={'rms':float(np.sqrt(np.mean(dist**2))),'p95':float(np.quantile(dist,.95)),'samples':2000,'seed':41}
        mesh.export(out/row['full_mesh']);mesh.submesh([display_faces],append=True,repair=False).export(out/row['face_mesh'])
        row.update(full_mesh_sha256=digest(out/row['full_mesh']),face_mesh_sha256=digest(out/row['face_mesh']),seconds=time.monotonic()-start)
        report['variants'].append(row);save()
    for p,sha in snapshots.items():
        if digest(p)!=sha:raise ValueError('Source changed during fitting.')
    from .flame_fit_view import write_view
    write_view(out,report,source,expanded_target,camera)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('original','trial','seed','arc','coverage','model','probe','out'):parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args();run(a.original,a.trial,a.seed,a.arc,a.coverage,a.model,a.probe,a.out)
