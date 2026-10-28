"""Local-only bridge to the CGAL continuous surface-path executable (stdlib only).

Run: PYTHONPATH=python python3 -m dimension_pipeline.surface_geodesic
"""

import argparse
import json
import math
import os
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_BINARY = Path(__file__).parents[2]/'tmp/surface-geodesic-build/surface_geodesic'


def validate_payload(payload):
    if not isinstance(payload, dict) or payload.get('units') != 'mm':
        raise ValueError('Expected mesh coordinates in mm')
    mesh = payload.get('mesh', {})
    vertices, faces = mesh.get('vertices'), mesh.get('triangles')
    number = lambda x: type(x) in (int, float) and math.isfinite(x)
    if not isinstance(vertices, list) or not 3 <= len(vertices) <= 20000 or not all(
        isinstance(p, list) and len(p) == 3 and all(number(v) for v in p) for p in vertices
    ):
        raise ValueError('Expected 3–20,000 finite 3D vertices')
    if not isinstance(faces, list) or not 1 <= len(faces) <= 40000 or not all(
        isinstance(f, list) and len(f) == 3 and all(type(i) is int and 0 <= i < len(vertices) for i in f)
        and len(set(f)) == 3 for f in faces
    ):
        raise ValueError('Expected valid indexed triangles')
    queries = payload.get('queries')
    if not isinstance(queries, list) or not 1 <= len(queries) <= 2:
        raise ValueError('Expected 1–2 path queries')
    ids = set()
    for query in queries:
        if not isinstance(query, dict) or not isinstance(query.get('id'), str) or not 1 <= len(query['id']) <= 100 or query['id'] in ids:
            raise ValueError('Expected unique query IDs')
        ids.add(query['id'])
        for field in ('start', 'end'):
            a = query.get(field, {})
            if not isinstance(a, dict) or a.get('kind') != 'barycentric' or type(a.get('triangle_index')) is not int or not 0 <= a['triangle_index'] < len(faces):
                raise ValueError('Expected barycentric endpoints on valid triangles')
            weights = a.get('weights')
            if not isinstance(weights, list) or len(weights) != 3 or not all(number(w) and 0 <= w <= 1 for w in weights) or abs(sum(weights)-1) > 1e-9:
                raise ValueError('Invalid endpoint weights')
    return vertices, faces, queries


def solve_payload(payload, binary=DEFAULT_BINARY):
    vertices, faces, queries = validate_payload(payload)
    if not Path(binary).is_file():
        raise FileNotFoundError('Build the native surface_geodesic executable first; see SURFACE_GEODESICS.md')
    lines = [f'{len(vertices)} {len(faces)} {len(queries)}']
    lines.extend(' '.join(map(str, p)) for p in vertices)
    lines.extend(' '.join(map(str, f)) for f in faces)
    for query in queries:
        for field in ('start', 'end'):
            a = query[field]
            lines.append(' '.join(map(str, [a['triangle_index'], *a['weights']])))
    started = time.perf_counter()
    process = subprocess.run([str(binary)], input='\n'.join(lines)+'\n', capture_output=True, text=True, timeout=25, check=False)
    if process.returncode:
        raise ValueError('Continuous solver rejected the mesh/query: '+process.stderr.strip()[:500])
    result = json.loads(process.stdout)
    if len(result.get('results', [])) != len(queries):
        raise ValueError('Unexpected native result count')
    for query, path in zip(queries, result['results']):
        path['id'] = query['id']
        if path['status'] == 'ok':
            # Preserve the exact supplied attachment representation in exports.
            path['path'][0], path['path'][-1] = query['start'], query['end']
    result['elapsed_ms'] = round((time.perf_counter()-started)*1000, 3)
    return result


class Handler(BaseHTTPRequestHandler):
    workers = threading.BoundedSemaphore(2)
    binary = DEFAULT_BINARY

    def permitted_origin(self):
        origin = self.headers.get('Origin')
        return not origin or urlparse(origin).hostname in ('127.0.0.1', 'localhost', '::1')

    def reply(self, code, result):
        body = json.dumps(result, allow_nan=False).encode()
        self.send_response(code)
        origin = self.headers.get('Origin')
        if origin and self.permitted_origin():
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # The viewer may abort a superseded landmark request.

    def do_OPTIONS(self):
        if not self.permitted_origin():
            self.reply(403, {'error': 'Only local research origins are allowed'}); return
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin', 'http://127.0.0.1'))
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if not self.permitted_origin():
            self.reply(403, {'error': 'Only local research origins are allowed'}); return
        if self.path != '/health':
            self.reply(404, {'error': 'Unknown endpoint'}); return
        self.reply(200 if Path(self.binary).is_file() else 503, {'available': Path(self.binary).is_file(), 'method': 'cgal_continuous_v1'})

    def do_POST(self):
        if not self.permitted_origin():
            self.reply(403, {'error': 'Only local research origins are allowed'}); return
        if self.path != '/solve':
            self.reply(404, {'error': 'Unknown endpoint'}); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 10*1024*1024:
                self.reply(413, {'error': 'Expected a request no larger than 10 MB'}); return
            if not self.workers.acquire(blocking=False):
                self.reply(429, {'error': 'Solver busy; retry after the current solve completes'}); return
            try:
                payload = json.loads(self.rfile.read(length))
                result = solve_payload(payload, self.binary)
                self.reply(200, result)
            finally:
                self.workers.release()
        except FileNotFoundError as error:
            self.reply(503, {'error': str(error)})
        except subprocess.TimeoutExpired:
            self.reply(504, {'error': 'Continuous solve exceeded the 25-second limit'})
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            self.reply(422, {'error': str(error)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5180)
    parser.add_argument('--binary', type=Path, default=Path(os.environ.get('MASQFIT_GEODESIC_BINARY', DEFAULT_BINARY)))
    args = parser.parse_args()
    Handler.binary = args.binary.resolve()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Local continuous surface solver: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()
