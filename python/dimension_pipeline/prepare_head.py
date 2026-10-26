"""Re-derive the bundled head geometry from the pinned upstream CC0 OBJ.

This is an offline provenance check, not an automatic downloader. The source
hash must match before parsing. The resulting geometry must match the bundle.
"""

import argparse
import hashlib
from pathlib import Path

from .generate_heads import ASSETS, load


def verify_source(path):
    reference = load('makehuman_head.json')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != reference['source']['upstream_sha256']:
        raise ValueError('Source OBJ hash does not match the pinned MakeHuman asset')
    vertices, faces, group = [], [], ''
    for line in content.decode().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == 'v':
            vertices.append(list(map(float, fields[1:4])))
        elif fields[0] == 'g':
            group = ' '.join(fields[1:])
        elif fields[0] == 'f' and group == 'body':
            indices = [int(token.split('/')[0])-1 for token in fields[1:]]
            if all(vertices[i][1] >= 5.8 for i in indices):
                faces.extend([[indices[0], indices[k], indices[k+1]] for k in range(1, len(indices)-1)])
    used = sorted({i for face in faces for i in face})
    remap = {old: new for new, old in enumerate(used)}
    low, high = min(vertices[i][1] for i in used), max(vertices[i][1] for i in used)
    factor = 240/(high-low)
    mesh = {'vertices': [[round(vertices[i][0]*factor, 6), round((vertices[i][1]-(high+low)/2)*factor, 6),
                          round(vertices[i][2]*factor, 6)] for i in used],
            'triangles': [[remap[i] for i in face] for face in faces]}
    if mesh != reference['mesh'] or used != reference['upstream_vertex_indices']:
        raise ValueError('Re-derived geometry does not match the bundled head')
    return hashlib.sha256((ASSETS/'makehuman_head.json').read_bytes()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_obj', type=Path)
    args = parser.parse_args()
    print('Verified bundled head SHA-256:', verify_source(args.source_obj))
