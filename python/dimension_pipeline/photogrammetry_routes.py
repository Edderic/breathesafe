"""Evaluate automatic saved FLAME guide recipes on observed reconstruction geometry.

Interpolated network image coordinates are candidate seeds, not anatomical truth.
Only contiguous supported edges receive lengths; missing edges never get bridged.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

from .flame_open import load_model
from .flame_mapping import topology_id
from .photogrammetry_trial import attach, digest, triangulate


def edge_lengths(mesh, attachments, pairs):
    edges = mesh.edges_unique
    weights = np.linalg.norm(mesh.vertices[edges[:, 0]]-mesh.vertices[edges[:, 1]], axis=1)
    graph = coo_matrix((np.r_[weights, weights], (np.r_[edges[:, 0], edges[:, 1]],
                        np.r_[edges[:, 1], edges[:, 0]])), shape=(len(mesh.vertices),)*2).tocsr()
    points = {}
    for i, a in attachments.items():
        triangle = mesh.faces[a['triangle_index']]
        point = np.array(a['weights']) @ mesh.vertices[triangle]
        vertex = int(triangle[np.argmin(np.linalg.norm(mesh.vertices[triangle]-point, axis=1))])
        points[i] = (point, vertex, np.linalg.norm(mesh.vertices[vertex]-point))
    result = []
    for a, b in pairs:
        if a not in points or b not in points:
            result.append(None)
            continue
        qa, va, da = points[a]; qb, vb, db = points[b]
        if attachments[a]['triangle_index'] == attachments[b]['triangle_index']:
            length = np.linalg.norm(qb-qa)
        else:
            length = dijkstra(graph, directed=False, indices=va)[vb]+da+db
        result.append(float(length) if np.isfinite(length) else None)
    return result


def run(args):
    folder, trial, predictions = Path(args.session), Path(args.trial), Path(args.predictions)
    state = json.loads((folder/'session.json').read_text())
    base = json.loads((trial/'report.json').read_text())
    draft = json.loads(Path(args.measurements).read_text())
    _, _, faces, model = load_model(args.model)
    if draft['model_sha256'] != model['model_sha256'] or draft['topology_id'] != topology_id(faces):
        raise ValueError('Guide topology/model differs')
    # Session may be the expanded-mask copy: photo hashes, not session name, establish shared source pixels.
    recipe, routes = [], []
    named = {}
    for point in draft['points']:
        if point.get('attachment'):
            named[point['name']] = len(recipe)
            recipe.append(point['attachment'])
    for key in ('scale', 'check'):
        order = draft['routes'][key]
        if all(name in named for name in order):
            indices = [named[name] for name in order]
            routes.append({'name': key, 'pairs': list(zip(indices, indices[1:]))})
    for perimeter in draft['perimeters']:
        if not perimeter['closed']:
            continue
        pairs = []
        for stroke in perimeter['strokes']:
            ids = list(range(len(recipe), len(recipe)+len(stroke)))
            recipe.extend(stroke)
            pairs.extend(zip(ids, ids[1:]))
            if len(perimeter['strokes']) == 1:
                pairs.append((ids[-1], ids[0]))
        routes.append({'name': perimeter['style'], 'pairs': pairs})
    cameras, observations = [], []
    for slot in base['slots']:
        if digest(predictions/(slot+'.npz')) != base['predictions'][slot]['prediction']:
            raise ValueError('Prediction changed')
        cameras.append(state['result']['cameras']['registered:'+slot+'.png'])
        xy = np.load(predictions/(slot+'.npz'), allow_pickle=False)['vertex_coord']
        observations.append([np.array(a['weights']) @ xy[faces[a['triangle_index']]] for a in recipe])
    observations = np.array(observations)
    records = triangulate(cameras, observations)
    raw_path = folder/state['result']['full_mesh']
    if digest(raw_path) != base['raw_sha256']:
        raise ValueError('Trial mesh changed')
    raw = trimesh.load(raw_path, process=False)
    print('Guide candidates', len(records), 'consensus', sum(r['status']=='consistent' for r in records), flush=True)
    attach(raw, records, cameras, observations, base['eye_proxy_span'])
    attachments = {i: r['attachment'] for i, r in enumerate(records) if r['status']=='supported'}
    output = {'version': 'automatic_reconstruction_routes_v1', 'session_id': state['id'],
              'units': 'reconstruction_unit', 'measurements_sha256': digest(args.measurements),
              'raw_sha256': base['raw_sha256'], 'guide_status': 'unreviewed automatic predictions; reviews and scale do not transfer',
              'seed_method': 'barycentric interpolation of dense image predictions; approximate candidate correspondence',
              'length_method': 'mesh-edge shortest paths between nearest face vertices plus endpoint offsets; approximate, not continuous geodesic or tape simulation',
              'status_counts': dict(Counter(r['status'] for r in records)), 'points': records, 'variants': []}
    pairs = [pair for route in routes for pair in route['pairs']]
    for variant_name, mesh in [('raw', raw)]+[(v['name'], trimesh.load(trial/(v['name']+'.ply'), process=False)) for v in base['variants']]:
        print('Measuring', variant_name, flush=True)
        lengths = edge_lengths(mesh, attachments, pairs)
        rows, offset = [], 0
        for route in routes:
            values = lengths[offset:offset+len(route['pairs'])]; offset += len(route['pairs'])
            valid = [v for v in values if v is not None]
            rows.append({'name': route['name'], 'total_edges': len(values), 'supported_edges': len(valid),
                         'supported_partial_length': sum(valid),
                         'complete_length': sum(valid) if len(valid)==len(values) and values else None})
        chords = {}
        for name, endpoints in [('nose', ['subnasale', 'pronasale']), ('bridge', ['sellion', 'pronasale'])]:
            indices = [named.get(n) for n in endpoints]
            if all(i in attachments for i in indices):
                points = [np.array(attachments[i]['weights']) @ mesh.triangles[attachments[i]['triangle_index']] for i in indices]
                chords[name] = float(np.linalg.norm(points[1]-points[0]))
            else:
                chords[name] = None
        output['variants'].append({'name': variant_name, 'routes': rows, 'chords': chords})
    output['algorithm_sha256'] = digest(__file__)
    (trial/'automatic-routes.json').write_text(json.dumps(output, indent=2, allow_nan=False))
    print(json.dumps(output['variants'], indent=2), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('session', 'trial', 'predictions', 'measurements', 'model'):
        p.add_argument('--'+name, required=True)
    run(p.parse_args())


if __name__ == '__main__':
    main()
