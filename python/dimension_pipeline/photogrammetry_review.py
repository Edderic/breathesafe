"""Build a paired offline trial summary with a long/skinny-triangle support audit."""
import argparse
import html
import json
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

from .photogrammetry_trial import digest, preview
from .flame_open import load_model


def triangle_quality(mesh, attachment, span):
    tri = mesh.triangles[attachment['triangle_index']]
    lengths = np.linalg.norm(tri-np.roll(tri, 1, axis=0), axis=1)
    area2 = np.linalg.norm(np.cross(tri[1]-tri[0], tri[2]-tri[0]))
    return bool(lengths.max() <= span*.12 and area2 > 1e-15 and lengths.max()**2/area2 <= 12)


def build(folders, out, model_path):
    template, _, _, model = load_model(model_path)
    rows, panels = [], []
    for folder in folders:
        base = json.loads((folder/'report.json').read_text())
        session = folder.parents[1]/base['session_id']/'session.json'
        state = json.loads(session.read_text())
        raw_path = session.parent/state['result']['full_mesh']
        if digest(raw_path) != base['raw_sha256']:
            raise ValueError('Raw input changed')
        mesh = trimesh.load(raw_path, process=False)
        def audit(points):
            result = []
            for point in points:
                status = point['status']
                if status == 'supported' and not triangle_quality(mesh, point['attachment'], base['eye_proxy_span']):
                    status = 'rejected_long_or_skinny_triangle'
                result.append(status)
            return result
        if model['model_sha256'] != base['model']['model_sha256']:
            raise ValueError('Sampling model differs')
        statuses = audit(base['points'])
        counts = {region: dict(Counter(s for p, s in zip(base['points'], statuses) if p['region']==region))
                  for region in ('lower_template', 'other_template')}
        for label, lower, upper in [('below_menton_height_template', -np.inf, -.089), ('chin_band_template', -.089, -.055)]:
            counts[label] = dict(Counter(status for point, status in zip(base['points'], statuses)
                                         if point['region']=='lower_template' and lower <= template[point['vertex_id'], 1] < upper))
        route_data = json.loads((folder/'automatic-routes.json').read_text())
        route_statuses = audit(route_data['points'])
        row = {'folder': folder.name, 'session_id': base['session_id'], 'point_status_counts_after_triangle_quality': counts,
               'route_candidate_counts_after_triangle_quality': dict(Counter(route_statuses)),
               'base_report_sha256': digest(folder/'report.json'),
               'route_report_sha256': digest(folder/'automatic-routes.json'),
               'normalizer': base.get('normalizer', {'method':'raw reference eye proxy'}),
               'note': 'quality audit can remove support; no geometry or point is repaired'}
        rows.append(row)
        front = state['result']['cameras'][state['result']['frontal_camera_key']]
        for label, surface in [('raw', mesh)]+[(v['name'], trimesh.load(folder/(v['name']+'.ply'), process=False)) for v in base['variants']]:
            for view, angle in [('front', 0.), ('profile', np.pi/2)]:
                preview(surface, front, folder/f'{label}-{view}.png', yaw=angle, reference=mesh)
        name = folder.name
        links = ' · '.join(f'<a href="{name}/{v["name"]}.ply">{v["name"]} PLY</a>' for v in base['variants'])
        panels.append(f'<article><h2>{html.escape(name)}</h2><a href="{name}/review.html">Open full surface and source-photo report</a><p><a href="{name}/automatic-routes.json">Download automatic route report</a></p><p>'+links+'</p><pre>'+html.escape(json.dumps(counts, indent=2))+'</pre></article>')
    output = {'version':'photogrammetry_paired_review_v1', 'trials':rows,
              'lower_subregions': 'neutral template y < -0.089 (below approximate guide menton height); chin band -0.089 <= y < -0.055; geometric partitions, not anatomical labels',
              'quality_policy': {'maximum_triangle_edge_over_eye_span': .12, 'maximum_edge_squared_over_double_area':12},
              'algorithm_sha256': digest(__file__)}
    (out/'comparison.json').write_text(json.dumps(output, indent=2))
    (out/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Automatic photogrammetry experiments</title>'
        '<style>body{font:17px system-ui;max-width:1400px;margin:30px auto;color:#243b46}main{display:grid;grid-template-columns:1fr 1fr;gap:25px}pre{white-space:pre-wrap;background:#eef3f5;padding:12px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #ccc}</style>'
        '<h1>Automatic photogrammetry experiments</h1><p>Same nine source photos; original masks versus expanded jaw/neck masks. Fixed reconstruction cameras. No FLAME fitted geometry or relative-depth priors used for triangulation.</p>'
        '<p>Counts below include a long/skinny-triangle rejection audit. Individual trial reports show the earlier geometric-consistency checks before this extra audit. These are diagnostic candidates, not validated anatomical landmarks.</p><main>'+''.join(panels)+'</main>'
        '<h2>Interpretation</h2><p>Complete bifold/trifold lengths remain unavailable when controls lack support. Partial mesh-edge lengths must not be extrapolated into full perimeters. Route support counts saved control-to-control edges, unlike the earlier densely sampled FLAME arc reports.</p>'
        '<p>Taubin variants change the existing surface; they do not restore missing anatomy. Normal-direction changes and self-intersection uncertainty prevent automatically choosing a winner based on appearance. All geometry remains in native reconstruction units.</p><p><a href="comparison.json">Download paired audit</a></p>')
    print(json.dumps(output, indent=2), flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trials', nargs='+', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--model', required=True)
    args=p.parse_args()
    build([Path(f) for f in args.trials], Path(args.out), args.model)
