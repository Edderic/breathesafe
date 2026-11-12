"""Provisional tape calibration and independent perimeter comparison on one surface."""
import argparse
import html
import json
import math
import os
import statistics
import subprocess
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image
from scipy.spatial import cKDTree

from .gaussian_validation import eligible_faces
from .gaussian_volume import source_samples
from .mask_route_review import sample_polyline, source_coverage
from .photogrammetry_trial import digest


NODE = r'''
const fs=require('fs'),M=require(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8')),g=M.graph(d.mesh);
const rows=[];
for(let i=0;i<d.points.length-1;i++) rows.push(M.route(d.mesh,g,d.points,[d.points[i].name,d.points[i+1].name],'surface'));
process.stdout.write(JSON.stringify(rows));
'''


def compare_lengths(calibration_length, perimeter_length, calibration_readings, check_readings):
    values=[calibration_length,perimeter_length,*calibration_readings,*check_readings]
    if not calibration_readings or not check_readings or any(not math.isfinite(x) or x<=0 for x in values):
        raise ValueError('Lengths and tape readings must be finite and positive')
    calibration_mm=statistics.median(calibration_readings)
    check_mm=statistics.median(check_readings)
    factor=calibration_mm/calibration_length
    prediction=perimeter_length*factor
    return {'calibration_median_mm':calibration_mm,'check_median_mm':check_mm,
        'provisional_mm_per_reconstruction_unit':factor,'estimated_perimeter_mm':prediction,
        'signed_difference_mm':prediction-check_mm,'relative_difference':prediction/check_mm-1,
        'calibration_reading_sensitivity_mm':[perimeter_length*x/calibration_length for x in (min(calibration_readings),max(calibration_readings))],
        'accepted_measurement_mm':None,
        'interpretation':'single-capture provisional comparison; reading sensitivity is not a confidence interval; tape and surface routes may differ'}


def run(args):
    session,neck,coverage,bifold,out=map(Path,(args.session,args.neck,args.coverage,args.bifold,args.out))
    state=json.loads((session/'session.json').read_text())
    volume=json.loads((neck/'report.json').read_text())
    automatic=json.loads((coverage/'report.json').read_text())
    selected=next(v for v in volume['variants'] if v['id']==automatic['selected_surface'])
    mesh_path=neck/(selected['id']+'.ply');raw_path=session/state['result']['full_mesh']
    if not (digest(mesh_path)==selected['mesh_sha256']==automatic['selected_sha256']):
        raise ValueError('Selected surfaces differ')
    if not (digest(raw_path)==volume['source_sha256']==automatic['source_sha256']):raise ValueError('Raw source changed')
    if automatic['session_id']!=state['id']:raise ValueError('Wrong coverage session')
    candidate=trimesh.load(mesh_path,process=False);raw=trimesh.load(raw_path,process=False);span=volume['eye_proxy_span']
    samples,_,_=source_samples(raw,span);tree=cKDTree(samples)
    eligible=eligible_faces(candidate,span,tree);ids=np.flatnonzero(eligible)
    lookup=np.full(len(candidate.faces),-1,dtype=int);lookup[ids]=np.arange(len(ids))
    graph=trimesh.Trimesh(vertices=candidate.vertices,faces=candidate.faces[eligible],process=False)
    named={d['name']:p for d,p in zip(automatic['descriptors'],automatic['runs']['all_views']['smoothed_points']) if d['kind']=='guide'}
    anchors=[]
    for name in ('left_tragion','subnasale','right_tragion'):
        record=named[name]
        if record['status']!='supported':raise ValueError('Unsupported calibration anchor: '+name)
        a=dict(record['attachment']);triangle=a['triangle_index']
        if lookup[triangle]<0:raise ValueError('Calibration anchor outside eligible surface: '+name)
        a['triangle_index']=int(lookup[triangle]);a['weights']=np.clip(a['weights'],0,1).tolist()
        total=sum(a['weights']);a['weights']=[w/total for w in a['weights']]
        anchors.append({'name':name,'attachment':a})
    module=Path(__file__).with_name('flame_measurements_ui.js').resolve()
    payload={'mesh':{'vertices':graph.vertices.tolist(),'triangles':graph.faces.tolist()},'points':anchors}
    print('Routing bitragion–subnasale calibration arc',flush=True)
    result=subprocess.run(['node','-e',NODE,str(module)],input=json.dumps(payload),capture_output=True,text=True,check=True,timeout=240)
    paths=json.loads(result.stdout);native=sum(p['length'] for p in paths)
    points=[];weights=[]
    for path in paths:
        p,w=sample_polyline(path['points'],span*.01);points.extend(p);weights.extend(w)
    cameras=[];masks=[]
    for view in automatic['input_views']:
        capture=next(c for c in state['captures'] if c['slot']==view['slot'])
        if digest(session/capture['image'])!=view['image_sha256'] or digest(session/capture['mask'])!=view['mask_sha256']:
            raise ValueError('Source photo or mask changed')
        cameras.append(state['result']['cameras']['registered:'+view['slot']+'.png'])
        mask=np.asarray(Image.open(session/capture['mask']).convert('L'))>=128
        masks.append(cv2.dilate(mask.astype(np.uint8),np.ones((7,7),np.uint8))>0)
    print('Auditing calibration arc source support:',len(points),'samples',flush=True)
    evidence=source_coverage(np.array(points),cameras,masks,candidate,raw,tree,span)
    supported=sum(w for w,e in zip(weights,evidence) if e['supported'])
    perimeter=json.loads((bifold/'report.json').read_text())
    if perimeter['style']!='bifold' or perimeter['session_id']!=state['id']:
        raise ValueError('Wrong comparison session or style')
    if perimeter['selected_mesh_sha256']!=digest(mesh_path) or perimeter['coverage_report_sha256']!=digest(coverage/'report.json'):
        raise ValueError('Perimeter coverage source changed')
    length=perimeter['summary']['complete_geometry_proposal_length']
    if length is None:raise ValueError('Cannot compare an incomplete geometric perimeter')
    comparison=compare_lengths(native,length,args.calibration,args.bifold_readings)
    report={'version':'tape_validation_v1','session_id':state['id'],
        'readings':{'calibration':{'path':'left tragion via subnasale to right tragion','mm':args.calibration},
            'bifold':{'path':'full saved bifold perimeter; tape path equivalence unverified','mm':args.bifold_readings},
            'under_chin':{'mm':245,'path':'under-mandible side-to-side via under-chin; endpoints approximate',
                'superseded_mm':[228,230,240],'prediction_mm':None,'reason':'endpoint correspondence unavailable; not the closed trifold loop'}},
        'calibration':{'native_length':native,'paths':paths,'anchors':{n:named[n] for n in ('left_tragion','subnasale','right_tragion')},
            'sample_points':np.array(points).tolist(),'sample_evidence':evidence,'source_supported_fraction':supported/native,
            'edge_fallback_segments':sum(p['edge_fallback_segments'] for p in paths),'endpoint_review':'automatic candidates; anatomical review pending',
            'policy':'local triangle-strip surface route through three anchors, not a physical tape simulation'},
        'bifold':{'native_length':length,'source_supported_fraction':perimeter['summary']['source_supported_fraction_of_routed_length'],
            'route_review':perimeter['summary']['review_status']},'comparison':comparison,
        'provenance':{'selected_mesh_sha256':digest(mesh_path),'coverage_report_sha256':digest(coverage/'report.json'),
            'bifold_report_sha256':digest(bifold/'report.json'),'routing_code_sha256':digest(module),'algorithm_sha256':digest(__file__)}}
    out.mkdir(parents=True,exist_ok=False)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    # Retain the established interactive geometry viewer for direct calibration-path inspection.
    template=Path(__file__).with_name('mask_route_review.html').read_text()
    paths_for_view=[{'status':'routed','points':p['points'],'length':p['length'],'source_supported_fraction':None,
        'edge_fallback_segments':p['edge_fallback_segments']} for p in paths]
    viewer_report={'summary':{'routed_edges':2,'total_edges':2,'controls':3,'automatic_correspondence_supported_controls':3,
        'complete_geometry_proposal_length':native,'source_supported_fraction_of_routed_length':supported/native,
        'source_supported_sampled_length':float(supported),'complete_source_supported_proposal_length':native if all(e['supported'] for e in evidence) else None},
        'paths':paths_for_view,'controls':[]}
    for n in ('left_tragion','subnasale','right_tragion'):
        viewer_report['controls'].append({'index':n,'projection_distance_over_eye_span':named[n]['surface_distance_over_eye_span'],'automatic_correspondence_status':'supported'})
    # Reuse the immutable selected surface display from the bifold viewer.
    viewer=(bifold/'review.html').read_text().split('<script id="data" type="application/json">',1)[1].split('</script>',1)[0]
    data=json.loads(viewer);R=np.array(state['result']['cameras'][state['result']['frontal_camera_key']]['R'])
    transform=lambda p:(np.asarray(p)@R.T*np.array([1,-1,-1])).tolist()
    data.update(report=viewer_report,paths=[{'color':'#ef9f35','points':transform(p['points'])} for p in paths],
        controls=transform([named[n]['surface_point'] for n in ('left_tragion','subnasale','right_tragion')]),
        source_guide=[],neck_viewer=os.path.relpath(neck/'comparison.html',out))
    data.pop('photo_overlays',None)
    template=template.replace('Trifold / duckbill','Calibration arc').replace('contact route on the neck-inclusive surface','through bitragion and subnasale')
    template=template.replace('The original FLAME route is registered through matched camera centers and projected onto source-proximate triangles.',
        'This route connects three automatically triangulated surface anchors: left tragion, subnasale and right tragion. Confirm the anatomical endpoints and tape path.')
    (out/'calibration-route.html').write_text(template.replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    def fmt(x):return f'{x:.1f}'
    rows=[('Calibration tape median',fmt(comparison['calibration_median_mm'])+' mm'),
        ('Calibration surface arc',f'{native:.5f} native units'),('Calibration sampled source support',f'{100*supported/native:.1f}%'),
        ('Provisional scale',f'{comparison["provisional_mm_per_reconstruction_unit"]:.4f} mm / native unit'),
        ('Bifold estimated full perimeter',fmt(comparison['estimated_perimeter_mm'])+' mm'),
        ('Bifold tape median',fmt(comparison['check_median_mm'])+' mm'),
        ('Estimate minus tape',f'{comparison["signed_difference_mm"]:+.1f} mm ({comparison["relative_difference"]:+.1%})'),
        ('Bifold sampled source support',f'{100*report["bifold"]["source_supported_fraction"]:.1f}%'),
        ('Estimate using calibration reading extremes',' – '.join(fmt(x) for x in comparison['calibration_reading_sensitivity_mm'])+' mm'),
        ('Under-chin reference','245 mm; no prediction until endpoints match')]
    table=''.join('<tr><th>'+html.escape(a)+'</th><td>'+html.escape(b)+'</td></tr>' for a,b in rows)
    page='''<!doctype html><meta charset="utf-8"><title>Tape validation</title><style>body{font:17px system-ui;max-width:1000px;margin:35px auto;color:#243b46}td,th{padding:12px;border-bottom:1px solid #ccc;text-align:left}table{width:100%;border-collapse:collapse}.note{background:#fff2d1;padding:15px}</style><h1>Provisional tape calibration and bifold comparison</h1><p class="note">Scale is estimated from the bitragion–subnasale tape median only. Bifold readings are an independent comparison and never adjust scale. Automatic endpoints and projected mask paths still need anatomical/path review. This is one capture, not validated measurement accuracy.</p>'''+table.join(['<table>','</table>'])+f'''<p><a href="calibration-route.html">Inspect the calibration arc on the head</a> · <a href="{html.escape(os.path.relpath(bifold/'review.html',out))}">Inspect the bifold perimeter</a> · <a href="report.json">Download measurements and provenance</a></p><p>Calibration readings: {html.escape(str(args.calibration))} mm. Bifold readings: {html.escape(str(args.bifold_readings))} mm. The sensitivity range uses the calibration reading extremes only; it is not a confidence interval. The 245 mm under-chin reading supersedes 228, 230 and 240 mm. Its approximate endpoints do not define a matching reconstructed subarc.</p><p>Surface routes use local triangle-strip shortcuts, with any edge fallbacks recorded. A tape can bridge concavities or compress skin; numerical disagreement also includes endpoint and path differences. Source-photo consistency does not establish anatomical truth. No prior draft or accepted calibration is overwritten.</p>'''
    (out/'review.html').write_text(page)
    print(json.dumps(comparison,indent=2),flush=True);print(out/'review.html',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('session','neck','coverage','bifold','out'):parser.add_argument('--'+key,required=True)
    parser.add_argument('--calibration',nargs='+',type=float,required=True)
    parser.add_argument('--bifold-readings',nargs='+',type=float,required=True)
    run(parser.parse_args())
