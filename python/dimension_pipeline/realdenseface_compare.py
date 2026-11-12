"""Review dense-prior and landmark FLAME fits with shared framing and draft lengths."""
import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import trimesh

from .flame_mapping import topology_id
from .flame_photo_fit import digest
from .flame_photo_fit import NOSE, embed, fit_pose_only, load_embedding, project, visible


def heldout_diagnostics(mesh, report, baseline, embedding):
    indices, triangles, weights = embedding
    points = embed(mesh.vertices, mesh.faces, triangles, weights)
    nose = np.isin(indices, list(NOSE))
    rows = []
    for view in baseline['views']:
        if view['split'] != 'held_out_shape':
            continue
        observed = np.asarray(view['observed_pixels'])
        pose = fit_pose_only(points, observed, report['focal_pixels'], view['image_size'], ~nose)
        gate = visible(mesh.vertices, mesh.faces, triangles, weights, pose)
        error = np.linalg.norm(project(points, pose, report['focal_pixels'], view['image_size'])-observed, axis=1)
        rows.append({'slot': view['slot'], 'rms_pixels': float(np.sqrt(np.mean(error[gate]**2))),
                     'nose_rms_pixels': float(np.sqrt(np.mean(error[gate & nose]**2))),
                     'visible_count': int(gate.sum())})
    return {'method': 'fixed identity and focal; non-nose MediaPipe pose estimation on four validation photos; front-facing gate only',
            'interpretation': 'detector agreement, not physical accuracy', 'views': rows,
            'pooled_per_view_rms_pixels': float(np.sqrt(np.mean([r['rms_pixels']**2 for r in rows]))),
            'pooled_per_view_nose_rms_pixels': float(np.sqrt(np.mean([r['nose_rms_pixels']**2 for r in rows])))}


def measures(draft, meshes):
    # Same surface routing implementation as the established FLAME editor.
    script = r'''
const fs=require('fs'),M=require(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8')),output=[];
for(const mesh of d.meshes){
 const edges=M.graph(mesh),points=d.draft.points.map(p=>({...p,status:'pending'})),rows=[],paths=[],markers=[];
 for(const p of points)if(p.attachment){const q=M.location(mesh,p.attachment).point;markers.push({name:p.name,point:q});}
 for(const [key,label]of [['scale','Bitragion–subnasale arc'],['check','Bitragion–menton arc']]){
  try{const a=M.route(mesh,edges,points,d.draft.routes[key],'surface');rows.push({key,label,length:a.length,method:a.method,fallbacks:a.edge_fallback_segments});paths.push({key,points:a.points});}
  catch(e){rows.push({key,label,error:e.message});}
 }
 for(const [key,names,label]of [['nose',['subnasale','pronasale'],'Subnasale–pronasale chord'],['bridge',['sellion','pronasale'],'Sellion–pronasale chord']]){
  const ps=names.map(n=>markers.find(p=>p.name===n));if(ps.every(Boolean)){rows.push({key,label,length:M.distance(ps[0].point,ps[1].point),method:'euclidean_chord'});paths.push({key,points:ps.map(p=>p.point)});}
 }
 const span=M.distance(markers.find(p=>p.name==='left_tragion').point,markers.find(p=>p.name==='right_tragion').point);
 for(const p of d.draft.perimeters.filter(p=>p.closed)){
  const key=p.style;try{const a=M.measurePerimeter(p,mesh,edges,span*.08);rows.push({key,label:p.style+' perimeter (draft)',length:a.length,method:a.method,fallbacks:a.edge_fallback_segments});for(const path of a.paths)paths.push({key,points:path.points});}
  catch(e){rows.push({key,label:p.style+' perimeter (draft)',error:e.message});}
 }
 output.push({rows,paths,markers});
}
process.stdout.write(JSON.stringify(output));
'''
    result = subprocess.run(['node', '-e', script, str(Path(__file__).with_name('flame_measurements_ui.js').resolve())],
        input=json.dumps({'draft': draft, 'meshes': meshes}), text=True, capture_output=True, timeout=90, check=True)
    return json.loads(result.stdout)


def build(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    baseline_folder = Path(args.baseline)
    baseline_report = json.loads((baseline_folder/'report.json').read_text())
    draft = json.loads(Path(args.measurements).read_text())
    baseline_mesh = trimesh.load(baseline_folder/'flame-photo.ply', process=False)
    if draft['model_sha256'] != baseline_report['model']['model_sha256'] or draft['topology_id'] != topology_id(baseline_mesh.faces):
        raise ValueError('Measurement guide model/topology differs')
    if draft['session_id'] != baseline_report['session_id']:
        raise ValueError('Guide belongs to a different session')
    variants = []
    for folder_name in args.dense:
        folder = Path(folder_name)
        report = json.loads((folder/'report.json').read_text())
        mesh = trimesh.load(folder/'flame-dense.ply', process=False)
        if (report['model']['model_sha256'] != baseline_report['model']['model_sha256']
                or report['session_id'] != baseline_report['session_id'] or not np.array_equal(mesh.faces, baseline_mesh.faces)
                or report['baseline_report_sha256'] != digest(baseline_folder/'report.json')):
            raise ValueError('Incompatible dense fit comparison')
        target = 'dense-depth'+str(report['depth_weight']).replace('.', '-')+'.ply'
        mesh.export(out/target)
        variants.append({'id': target[:-4], 'label': 'Dense priors · depth weight '+str(report['depth_weight']),
                         'vertices': mesh.vertices.tolist(), 'triangles': mesh.faces.tolist(), 'report': report,
                         'mesh_file': target, 'poses': report['poses'], 'focal_pixels': report['focal_pixels']})
    baseline_mesh.export(out/'direct-photo.ply')
    baseline = {'label': 'Direct Photo FLAME · 105 landmarks', 'vertices': baseline_mesh.vertices.tolist(),
                'triangles': baseline_mesh.faces.tolist(), 'report': baseline_report, 'mesh_file': 'direct-photo.ply',
                'poses': {v['slot']: v['pose'] for v in baseline_report['views']}, 'focal_pixels': baseline_report['focal_pixels']}
    measurements = measures(draft, [baseline]+variants)
    for item, measured in zip([baseline]+variants, measurements):
        item['measurements'] = measured
    if args.embedding:
        embedding = load_embedding(args.embedding, baseline_mesh.faces)
        for item in [baseline]+variants:
            mesh = trimesh.Trimesh(item['vertices'], item['triangles'], process=False)
            item['validation'] = heldout_diagnostics(mesh, item['report'], baseline_report, embedding)
    metadata = {'version': 'dense_vs_direct_photo_review_v1', 'session_id': draft['session_id'],
                'units': 'FLAME_model_native_uncalibrated', 'guide_source_sha256': digest(args.measurements),
                'guide_status': 'pending_review_on_each_new_surface; original reviews and scale do not transfer',
                'models': [{'label': m['label'], 'mesh_file': m['mesh_file'], 'measurements': m['measurements'],
                            'geometry': m['report']['geometry'], 'validation': m.get('validation')} for m in [baseline]+variants]}
    (out/'measurements.json').write_text(json.dumps(metadata, indent=2, allow_nan=False))
    payload = {'baseline': baseline, 'variants': variants, 'metadata': metadata}
    encoded = json.dumps(payload, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    page = Path(__file__).with_name('realdenseface_compare.html').read_text()
    (out/'comparison.html').write_text(page.replace('/*COMPARE_DATA*/', encoded))
    (out/'fit-reports.json').write_text(json.dumps({'baseline': baseline_report, 'dense': [v['report'] for v in variants]}, indent=2))
    print(out/'comparison.html')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--dense', nargs='+', required=True)
    parser.add_argument('--measurements', required=True)
    parser.add_argument('--embedding', help='Optional official embedding for matched sparse validation diagnostics')
    parser.add_argument('--out', required=True)
    build(parser.parse_args())


if __name__ == '__main__':
    main()
