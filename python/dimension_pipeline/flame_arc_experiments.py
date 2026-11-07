"""Bounded style-arc fitting trials on a private saved analysis mesh."""
import argparse
import copy
import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import trimesh

from .flame_fit import fit, prepare, nearest, outside
from .flame_open import load_model
from .flame_mapping import topology_id
from .mesh_comparison import mesh_identity
from .flame_arc_loss import annotations_from_node, prepare_constraints, evaluate_arcs


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(session,model,seed_folder,annotations,out,probe=None,iterations=40):
    if not 1 <= iterations <= 100: raise ValueError('Use 1–100 iterations.')
    folder=Path(session).resolve();seed_folder=Path(seed_folder).resolve();out=Path(out).resolve()
    if out.exists() or out==folder or folder in out.parents or out==seed_folder or seed_folder in out.parents:
        raise ValueError('Use a fresh private output directory outside the source session and seed fit.')
    session_bytes=(folder/'session.json').read_bytes();state=json.loads(session_bytes)
    draft=json.loads(Path(annotations).read_text());seed_report=json.loads((seed_folder/'report.json').read_text())
    template,basis,faces,provenance=load_model(model)
    seed_row=next((v for v in seed_report['variants'] if v.get('id',str(v['components']))==draft['fit_id']),None)
    if seed_row is None: raise ValueError('Unknown annotated seed fit.')
    seed_path=seed_folder/seed_row['full_mesh']
    if digest(seed_path)!=draft['mesh_sha256'] or provenance['model_sha256']!=draft['model_sha256'] or topology_id(faces)!=draft['topology_id']:
        raise ValueError('Annotations do not match the seed mesh/model/topology.')
    if state['id']!=draft['session_id'] or mesh_identity(state['result']['surface']['mesh'])!=seed_report['source_mesh_id']:
        raise ValueError('Annotations and seed fit must refer to this unchanged analysis surface.')
    payload=json.loads(Path(probe).read_text()) if probe else None
    if payload:payload['_session_folder']=str(folder)
    source,target,ids,face_ids,initial,span,exclusions,camera=prepare(state,template,faces,payload)
    seed=trimesh.load(seed_path,process=False)
    identity={key:draft[key] for key in ('session_id','fit_id','model_sha256','topology_id','mesh_sha256')}
    definitions=annotations_from_node(draft,seed,{**identity,'_span':span})
    constraints,importance,coverage,guides=prepare_constraints(definitions,seed,target,template,basis,ids,span,exclusions)
    if not constraints: raise ValueError('No perimeter has enough contiguous reconstruction support for an arc-length comparison.')
    report=copy.deepcopy(seed_report)
    report.update(variants=[],regional_mapping=None,regional_mapping_sha256=None,
                  method='independent_neutral_shape_fits_with_frozen_style_arc_regions_and_optional_partial_length_IRLS',
                  arc_experiment={'version':'flame-style-arc-loss-v1','annotations_sha256':digest(annotations),
                                  'seed_mesh_sha256':digest(seed_path),'definition_count':len(definitions),
                                  'closed_full_perimeters_only':True,'coverage':coverage,'guides':guides,
                                  'supported_target_count':len(constraints),'saved_lengths_are_ground_truth':False,
                                  'named_calibration_routes':'not length targets: no independent tape readings supplied',
                                  'pending_definitions':'exploratory guides only; original review statuses preserved',
                                  'method':'frozen_surface_projection_and_contiguous_support_gating_v1',
                                  'loss':'mean robust area-weighted surface residual / eye_span^2 + 0.0001*sum(beta^2) + lambda_arc*mean((L_supported-L_analysis_supported)^2/L_analysis_supported^2)',
                                  'fixed_region_weights':'1+3*(1-(distance_to_fixed_supported_arc_samples/(0.12*eye_span))^2)^2 inside radius; otherwise 1',
                                  'solver':'alternating robust trimmed surface correspondences, weighted similarity, arc-aware scale, bounded linearized shape solve; no guarantee of monotonic nonlinear loss',
                                  'policy':{'sample_spacing_fraction_eye_span':.025,'projection_limit_fraction_eye_span':.06,
                                            'minimum_absolute_normal_dot':.5,'edge_projection_length_ratio':[.5,1.5],
                                            'minimum_contiguous_edges':3,'minimum_contiguous_length_fraction_eye_span':.075,
                                            'minimum_supported_edge_fraction_for_loss':.2},
                                  'limitations':['No independent tape/reference-scan targets in this file.',
                                                 'Partial support gives partial-arc losses, not full-perimeter accuracy.',
                                                 'Mirrored halves are not independent evidence; only one full loop per definition is used.',
                                                 'Projection uses a fixed seed fit and can inherit its alignment errors.',
                                                 'Surface noise can bias reconstruction-derived lengths; the loss weights are exploratory.']},
                  source_session_sha256=hashlib.sha256(session_bytes).hexdigest(),
                  fit_algorithm_sha256=digest(Path(__file__).with_name('flame_fit.py')),
                  arc_algorithm_sha256=digest(Path(__file__).with_name('flame_arc_loss.py')),
                  routing_algorithm_sha256=digest(Path(__file__).with_name('flame_measurements_ui.js')),
                  algorithm_sha256=digest(__file__),maximum_iterations=iterations)
    out.mkdir(parents=True)
    (out/'route-definitions.json').write_text(json.dumps(draft,indent=2)+'\n')
    (out/'face-topology.json').write_bytes((seed_folder/'face-topology.json').read_bytes())
    source.export(out/'analysis.ply');target.export(out/'fitting-target.ply')
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    save()
    trials=[('100','Baseline',None,0.),('100-arc','Arc regions ×4',importance,0.),
            ('100-length-low','Arc regions + length 0.01',importance,.01),('100-length-high','Arc regions + length 0.05',importance,.05)]
    for key,label,weights,arc_weight in trials:
        started=time.monotonic();print(label,flush=True)
        vertices,row=fit(template,basis,faces,ids,target,initial,span,exclusions,100,iterations,
                         importance=weights,arc_constraints=constraints,arc_weight=arc_weight,
                         progress=lambda h: print(f"  iteration {h['iteration']}: RMS {h['rms_before_update']:.6f}",flush=True))
        mesh=trimesh.Trimesh(vertices,faces,process=False)
        row.update(id=key,label=label,weighting='style_arcs',arc_loss_weight=arc_weight,
                   arc_evaluation=evaluate_arcs(mesh,guides,coverage,span),
                   full_mesh=f'flame-{key}.ply',face_mesh=f'flame-{key}-face.ply')
        reference=np.cross(template[faces[:,1]]-template[faces[:,0]],template[faces[:,2]]-template[faces[:,0]])@np.asarray(row['transform']['R']).T
        normals=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
        row['geometry_checks']={'degenerate_triangles':int(np.count_nonzero(mesh.area_faces<=1e-14*span**2)),
                                'normal_reversals_vs_transformed_neutral':int(np.count_nonzero(np.einsum('ij,ij->i',reference,normals)<0)),
                                'self_intersections':'not_checked'}
        if row['geometry_checks']['degenerate_triangles']:raise ValueError('Fit creates degenerate triangles.')
        face=mesh.submesh([face_ids],append=True,repair=False)
        points,_=trimesh.sample.sample_surface(target,2000,seed=41);points=points[outside(points,exclusions)]
        _,dist,_=nearest(face,points)
        row['target_to_flame_face']={'method':'area_weighted_triangle_samples_to_nearest_triangles','samples':len(points),'seed':41,
                                     'rms':float(np.sqrt(np.mean(dist**2))),'p95':float(np.quantile(dist,.95))}
        # Fixed supported source arc samples also provide a regional surface
        # residual independent of the scalar length objective.
        region=importance>1.5;valid=outside(vertices[ids],exclusions)&region
        if not valid.any():raise ValueError('No covered arc-region vertices remain for evaluation.')
        _,dist,_=nearest(target,vertices[ids][valid])
        row['arc_region_surface_residual']={'vertices':int(valid.sum()),'rms':float(np.sqrt(np.mean(dist**2))),
                                            'p95':float(np.quantile(dist,.95)),'units':'reconstruction_unit'}
        mesh.export(out/row['full_mesh']);face.export(out/row['face_mesh'])
        row.update(full_mesh_sha256=digest(out/row['full_mesh']),face_mesh_sha256=digest(out/row['face_mesh']),seconds=time.monotonic()-started)
        report['variants'].append(row);save()
    if (folder/'session.json').read_bytes()!=session_bytes:raise ValueError('Source session changed during fitting.')
    from .flame_fit_view import write_view
    write_view(out,report,source,target,camera)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('session','model','seed','annotations','out'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--exclude-probe',type=Path);parser.add_argument('--iterations',type=int,default=40)
    args=parser.parse_args()
    try:run(args.session,args.model,args.seed,args.annotations,args.out,args.exclude_probe,args.iterations)
    except (ValueError,OSError,KeyError,subprocess.TimeoutExpired) as exc:parser.exit(1,f'Arc experiment failed: {exc}\n')
