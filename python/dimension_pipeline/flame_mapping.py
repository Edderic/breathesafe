"""Reviewed experimental ARKit analogs on original FLAME topology; no ARKit writes."""
import hashlib
import json
import heapq
from pathlib import Path

import numpy as np

VERSION = 'flame-arkit-analogs-v1'
LEGACY = json.loads(Path(__file__).with_name('legacy_arkit_paths.json').read_text())


def catalog():
    points = {}
    for path in LEGACY['scoring_paths']:
        for segment in LEGACY['segments'][path]:
            for value in segment.split('-'):
                index = int(value)
                points.setdefault(index, set()).add(path)
    return [{'arkit_index': i, 'paths': sorted(paths)} for i, paths in sorted(points.items())]


def topology_id(faces):
    return 'sha256:'+hashlib.sha256(np.asarray(faces, dtype='<i8').tobytes()).hexdigest()


def attachment_point(vertices, faces, attachment):
    if not isinstance(attachment, dict): raise ValueError('Missing FLAME attachment.')
    if attachment.get('kind') == 'vertex':
        i = attachment.get('vertex_index')
        if type(i) is not int or not 0 <= i < len(vertices): raise ValueError('Invalid original FLAME vertex index.')
        return np.asarray(vertices[i]), [i]
    if attachment.get('kind') == 'barycentric':
        i, w = attachment.get('triangle_index'), attachment.get('weights')
        if type(i) is not int or not 0 <= i < len(faces) or not isinstance(w,list) or len(w)!=3:
            raise ValueError('Invalid original FLAME triangle attachment.')
        if any(type(v) not in (int,float) or not np.isfinite(v) or v < 0 or v > 1 for v in w) or abs(sum(w)-1)>1e-7:
            raise ValueError('Invalid barycentric weights.')
        return np.asarray(w) @ vertices[faces[i]], faces[i].tolist()
    raise ValueError('Choose a vertex or barycentric FLAME attachment.')


def validate(mapping, model_sha, faces, vertices, session_id, source_mesh_id):
    if not isinstance(mapping,dict) or mapping.get('version') != VERSION:
        raise ValueError('Unsupported FLAME analog mapping version.')
    if mapping.get('model_sha256') != model_sha or mapping.get('topology_id') != topology_id(faces):
        raise ValueError('Mapping model or original FLAME topology differs.')
    if mapping.get('session_id') != session_id or mapping.get('source_mesh_id') != source_mesh_id:
        raise ValueError('Mapping belongs to a different session or analysis mesh.')
    rows = mapping.get('points')
    allowed = {c['arkit_index'] for c in catalog()}
    if not isinstance(rows,list) or len(rows)>len(allowed): raise ValueError('Invalid mapping point list.')
    seen=set()
    for row in rows:
        if not isinstance(row,dict): raise ValueError('Invalid mapping row.')
        index=row.get('arkit_index')
        if type(index) is not int or index not in allowed or index in seen: raise ValueError('Unknown or duplicate selected ARKit index.')
        seen.add(index)
        if row.get('status') not in ('pending','reviewed','uncertain','unavailable'): raise ValueError('Invalid analog review status.')
        if not isinstance(row.get('notes',''),str) or len(row.get('notes',''))>4000: raise ValueError('Invalid analog notes.')
        radius=row.get('radius_fraction_eye_span');weight=row.get('multiplier')
        if type(radius) not in (int,float) or not np.isfinite(radius) or not .03<=radius<=.5:
            raise ValueError('Analog radius must be 0.03–0.5 model eye spans.')
        if type(weight) not in (int,float) or not np.isfinite(weight) or not 1<=weight<=10:
            raise ValueError('Analog weight must be 1–10.')
        if row.get('attachment') is not None: attachment_point(vertices,faces,row['attachment'])
        elif row['status']=='reviewed': raise ValueError('Reviewed analog needs a FLAME attachment.')
    return rows


def regions(mapping, template, faces, fitting_vertices, model_eye_span):
    """Fixed neutral-topology geodesic neighborhoods; max overlap, smooth falloff."""
    allowed=set(int(i) for i in fitting_vertices)
    graph={i:{} for i in allowed}
    for face in faces:
        if not all(int(i) in allowed for i in face): continue
        for a,b in zip(face,np.roll(face,-1)):
            graph[int(a)][int(b)]=graph[int(b)][int(a)]=float(np.linalg.norm(template[a]-template[b]))
    importance=np.ones(len(fitting_vertices));reports=[]
    for row in mapping['points']:
        if row['status']!='reviewed' or row['multiplier']==1: continue
        point,seeds=attachment_point(template,faces,row['attachment'])
        radius=row['radius_fraction_eye_span']*model_eye_span
        distances={i:float(np.linalg.norm(template[i]-point)) for i in seeds if i in allowed}
        heap=[(d,i) for i,d in distances.items()];heapq.heapify(heap)
        while heap:
            distance,a=heapq.heappop(heap)
            if distance!=distances[a] or distance>radius: continue
            for b,length in graph[a].items():
                candidate=distance+length
                if candidate<=radius and candidate<distances.get(b,np.inf):
                    distances[b]=candidate;heapq.heappush(heap,(candidate,b))
        d=np.array([distances.get(int(i),np.inf) for i in fitting_vertices])
        inside=d<radius
        weights=np.ones(len(d));weights[inside]+= (row['multiplier']-1)*(1-(d[inside]/radius)**2)**2
        importance=np.maximum(importance,weights)
        reports.append({'arkit_index':row['arkit_index'], 'radius_fraction_eye_span':row['radius_fraction_eye_span'],
                        'multiplier':row['multiplier'], 'vertex_ids':np.asarray(fitting_vertices)[inside].tolist(),
                        'status':'ok' if inside.any() else 'outside_fitting_crop'})
    if not np.any(importance>1): raise ValueError('Review at least one weighted analog inside the fitted face crop.')
    return importance,reports
