"""Independent straight-line checks using a fixed, previously computed tape scale."""
import argparse
import html
import json
import math
import statistics
from pathlib import Path

import numpy as np

from .photogrammetry_trial import digest


def linear_check(readings, factor, endpoints=None):
    if not readings or any(not math.isfinite(x) or x<=0 for x in [factor,*readings]):
        raise ValueError('Scale and readings must be finite and positive')
    result={'readings_mm':readings,'median_mm':statistics.median(readings),'range_mm':[min(readings),max(readings)],
        'estimated_mm':None,'signed_difference_mm':None,'relative_difference':None,'accepted_measurement_mm':None}
    if endpoints is None:
        result['status']='matching_anatomical_endpoints_unavailable'
        return result
    points=np.asarray(endpoints,dtype=float)
    if points.shape!=(2,3) or not np.isfinite(points).all():raise ValueError('Need two finite 3D endpoints')
    native=float(np.linalg.norm(points[1]-points[0]))
    if native<=0:raise ValueError('Endpoints must differ')
    estimate=native*factor
    result.update(status='provisional_automatic_endpoints_pending_review',native_chord_length=native,
        estimated_mm=estimate,signed_difference_mm=estimate-result['median_mm'],relative_difference=estimate/result['median_mm']-1,
        endpoint_coordinates=points.tolist())
    return result


def run(args):
    parent,coverage,out=Path(args.calibration),Path(args.coverage),Path(args.out)
    calibration=json.loads((parent/'report.json').read_text());automatic=json.loads((coverage/'report.json').read_text())
    if calibration['provenance']['coverage_report_sha256']!=digest(coverage/'report.json'):
        raise ValueError('Automatic endpoint report changed')
    if calibration['session_id']!=automatic['session_id'] or calibration['provenance']['selected_mesh_sha256']!=automatic['selected_sha256']:
        raise ValueError('Endpoint surface/session differs from calibration')
    named={d['name']:p for d,p in zip(automatic['descriptors'],automatic['runs']['all_views']['smoothed_points']) if d['kind']=='guide'}
    face=[named[n] for n in ('sellion','menton')]
    endpoints=[p['surface_point'] for p in face] if all(p['status']=='supported' for p in face) else None
    factor=calibration['comparison']['provisional_mm_per_reconstruction_unit']
    checks={'nose_width':linear_check(args.nose_width,factor),
        'face_length':linear_check(args.face_length,factor,endpoints),
        'face_width':linear_check(args.face_width,factor)}
    checks['face_length']['endpoint_names']=['sellion','menton']
    checks['face_length']['endpoint_source_records']=face
    checks['nose_width']['missing_endpoints']=['left alare','right alare']
    checks['face_width']['missing_endpoints']=['left zygion','right zygion']
    report={'version':'tape_linear_checks_v1','session_id':automatic['session_id'],'checks':checks,
        'fixed_mm_per_reconstruction_unit':factor,'scale_calibration_median_mm':calibration['comparison']['calibration_median_mm'],
        'scale_updated_from_independent_checks':False,'interpupillary_distance':{'status':'skipped_by_participant'},
        'provenance':{'calibration_report_sha256':digest(parent/'report.json'),'coverage_report_sha256':digest(coverage/'report.json'),
            'selected_mesh_sha256':automatic['selected_sha256'],'algorithm_sha256':digest(__file__)},
        'interpretation':'straight 3D endpoint chords, not surface arcs; caliper readings are reference measurements with endpoint/contact uncertainty'}
    out.mkdir(parents=True,exist_ok=False)
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    import os
    rows=[]
    for name,p in checks.items():
        estimate='Pending matching endpoints' if p['estimated_mm'] is None else f'{p["estimated_mm"]:.1f} mm'
        delta='—' if p['signed_difference_mm'] is None else f'{p["signed_difference_mm"]:+.1f} mm ({p["relative_difference"]:+.1%})'
        rows.append('<tr>'+''.join('<td>'+html.escape(x)+'</td>' for x in [name.replace('_',' ').title(),', '.join(str(x) for x in p['readings_mm']),
            f'{p["median_mm"]:.1f} mm',f'{p["range_mm"][0]:.1f}–{p["range_mm"][1]:.1f} mm',estimate,delta])+'</tr>')
    page='''<!doctype html><meta charset="utf-8"><title>Independent caliper checks</title><style>body{font:17px system-ui;max-width:1200px;margin:35px auto;color:#243b46}td,th{padding:12px;border-bottom:1px solid #ccc;text-align:left}table{width:100%;border-collapse:collapse}.note{background:#fff2d1;padding:15px}</style><h1>Independent straight-line checks</h1>'''+f'''<p class="note">The 284 mm bitragion–subnasale calibration stays fixed at {factor:.4f} mm per native unit. None of these check readings adjusts scale. Interpupillary distance was skipped.</p><table><thead><tr><th>Measurement</th><th>Readings (mm)</th><th>Median</th><th>Range</th><th>Reconstruction</th><th>Estimate minus reference</th></tr></thead><tbody>'''+''.join(rows)+f'''</tbody></table><p>Face length is the Euclidean chord between the automatically supported sellion and menton surface candidates. Their anatomical identity remains pending review. Nose width needs left/right alare endpoints; cheekbone width needs left/right zygion endpoints. Neither pair is present in the existing named-point audit, so no substitute width is reported.</p><p><a href="{html.escape(os.path.relpath(parent/'review.html',out))}">Original calibration and bifold comparison</a> · <a href="report.json">Download checks and provenance</a></p><p>One length check cannot establish overall scale accuracy. Landmark placement, local reconstruction shape, caliper contact and path definition can contribute to differences. Surface support does not validate anatomical identity.</p>'''
    (out/'review.html').write_text(page)
    print(json.dumps(checks,indent=2),flush=True);print(out/'review.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('calibration','coverage','out'):p.add_argument('--'+key,required=True)
    for key in ('nose-width','face-length','face-width'):p.add_argument('--'+key,nargs='+',type=float,required=True)
    run(p.parse_args())
