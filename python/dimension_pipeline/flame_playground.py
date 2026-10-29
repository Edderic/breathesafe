"""Local FLAME shape playground and persistent face library.

PYTHONPATH=python python3 -m dimension_pipeline.flame_playground \
  --model ~/Downloads/FLAME2023Open.zip --source-units m
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

from .flame_open import DOWNLOAD_URL, LICENSE_URL, geometry_report, load_model
from .generate_heads import view_frame
from .geometry import FRAME

REPO = Path(__file__).resolve().parents[2]
ORIGINS = {'http://127.0.0.1:5178', 'http://localhost:5178'}


def coefficients(payload):
    values = payload.get('shape_coefficients') if isinstance(payload, dict) else None
    if not isinstance(values, list) or len(values) != 300 or any(
        type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 2 for v in values
    ):
        raise ValueError('Provide exactly 300 finite shape coefficients between -2 and 2.')
    return [float(v) if v else 0. for v in values]


class Playground:
    def __init__(self, model, library, source_units, source_x='subject_left'):
        self.template, self.basis, self.faces, self.provenance = load_model(model)
        self.factor = {'m': 1000., 'mm': 1.}[source_units]
        self.axes = np.array([-1., 1., 1.]) if source_x == 'subject_right' else np.ones(3)
        if source_x == 'subject_right':
            self.faces = self.faces[:, [0, 2, 1]]
        self.neutral = np.round(self.template*self.factor*self.axes, 6)
        if not 50 <= np.linalg.norm(np.ptp(self.neutral, axis=0)) <= 1000:
            raise ValueError('Implausible neutral head extent: check --source-units.')
        self.source_units, self.source_x = source_units, source_x
        self.topology_id = 'flame-open-'+hashlib.sha256(self.faces.astype('<i8').tobytes()).hexdigest()[:16]
        self.frame = view_frame({'mesh': {'vertices': self.neutral.tolist()}})
        radius = np.linalg.norm(self.neutral-np.array(self.frame['center_mm']), axis=1).max()
        self.frame['pixels_per_mm'] = min(1.45, 200/float(radius))
        self.library = Path(library).resolve()
        # The preview page deliberately only reads explicitly selected /tmp runs.
        self.library.relative_to(REPO/'tmp')
        if not re.fullmatch(r'tmp/[A-Za-z0-9_/-]+', self.library.relative_to(REPO).as_posix()):
            raise ValueError('Use a library under repo/tmp with letters, digits, hyphens and underscores in its path.')
        self.library.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def info(self):
        return {'model_sha256': self.provenance['model_sha256'], 'components': 300,
                'source_units': self.source_units, 'source_x': self.source_x,
                'library_directory': str(self.library), 'coefficient_min': -2, 'coefficient_max': 2}

    def preview(self, payload):
        beta = coefficients(payload)
        vertices = np.round((self.template+np.einsum('vci,i->vc', self.basis, beta))*self.factor*self.axes, 6)
        report = geometry_report(vertices, self.faces, self.neutral)
        if report['degenerate_triangles']:
            raise ValueError('This combination creates degenerate triangles. Reduce the coefficients.')
        settings = {'shape_coefficients': beta, 'source_units': self.source_units, 'source_x': self.source_x,
                    'model_sha256': self.provenance['model_sha256']}
        digest = hashlib.sha256(json.dumps(settings, sort_keys=True, separators=(',', ':')).encode()).hexdigest()[:24]
        identity = 'flame-open-face-'+digest
        record = {'surface_record_version': '1.0.0', 'record_id': identity,
                  'topology_id': self.topology_id, 'units': 'mm', 'coordinate_frame': FRAME,
                  'source': {'identity_id': identity, 'asset_id': 'FLAME-2023-Open', 'domain': 'synthetic',
                             'license': 'FLAME-2023-Open-Model-License', 'license_url': LICENSE_URL, 'url': DOWNLOAD_URL,
                             'attribution': 'Li et al., Learning a model of facial shape and expression from 4D scans, SIGGRAPH Asia 2017; Max Planck Institute for Intelligent Systems.',
                             'provenance': 'Local FLAME Open shape playground; neutral pose/expression. Explicit source-unit conversion, no size normalization. Anatomical frame and population coverage unreviewed.',
                             'parent_record_ids': [], **self.provenance},
                  'generation': {'version': '1.0.0', 'method': 'neutral_linear_shape_basis',
                                 'shape_coefficients': beta, 'expression': 'zero', 'pose': 'zero',
                                 'source_units': self.source_units,
                                 'source_axes': {'x': self.source_x, 'y': 'superior', 'z': 'anterior'}},
                  'mesh': {'vertices': vertices.tolist(), 'triangles': self.faces.tolist()},
                  'preview_camera': self.frame, 'review': {'status': 'pending', 'reviewer': None},
                  'limitations': ['Synthetic shape exploration, not verified population or child coverage.',
                                  'Anatomical labels, physical metric calibration and self-intersections remain unreviewed.']}
        return {'record': record, 'geometry_report': report}

    def list_faces(self):
        rows = []
        for path in self.library.glob('flame-open-face-*/metadata.json'):
            row = json.loads(path.read_text())
            if row.get('model_sha256') == self.provenance['model_sha256'] and row.get('source_units') == self.source_units and row.get('source_x') == self.source_x:
                rows.append(row)
        return sorted(rows, key=lambda row: row['created_at'], reverse=True)

    def save(self, payload):
        name = payload.get('name') if isinstance(payload, dict) else None
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise ValueError('Give the face a name of 1–80 characters.')
        result = self.preview(payload)
        record = result['record']; record['generation']['display_name'] = name.strip()
        record['review']['geometry_report'] = result['geometry_report']
        identity = record['record_id']; folder = self.library/identity
        relative = '/'+folder.relative_to(REPO).as_posix()
        metadata = {'id': identity, 'name': name.strip(), 'created_at': datetime.now(timezone.utc).isoformat(),
                    **self.info(), 'shape_coefficients': record['generation']['shape_coefficients'],
                    'mesh_path': relative+'/face.json', 'manifest_path': relative+'/manifest.json',
                    'preview_url': '/scripts/face_landmarks_preview.html?heads='+relative+'/manifest.json',
                    'geometry_report': result['geometry_report']}
        with self.lock:
            if folder.exists():
                return {'face': json.loads((folder/'metadata.json').read_text()), 'already_saved': True}
            temporary = Path(tempfile.mkdtemp(prefix='.saving-', dir=self.library))
            try:
                content = json.dumps(record, separators=(',', ':'), allow_nan=False)+'\n'
                (temporary/'face.json').write_text(content)
                manifest = {'version': '1.0.0', 'evidence': 'synthetic_geometry_preview', 'anatomical_review': 'pending',
                            'source_identity': identity, 'variants': [{'id': identity, 'mesh': 'face.json',
                            'sha256': hashlib.sha256(content.encode()).hexdigest()}]}
                (temporary/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
                (temporary/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
                os.rename(temporary, folder)
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)
        return {'face': metadata, 'already_saved': False}


class Handler(BaseHTTPRequestHandler):
    playground = None
    workers = threading.BoundedSemaphore(2)

    def permitted(self, write=False):
        # Exact local browser origins, JSON-only writes, and Host checks prevent
        # cross-site form submissions and DNS rebinding into this local writer.
        origin = self.headers.get('Origin')
        host = self.headers.get('Host')
        allowed_hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        return host in allowed_hosts and ((origin in ORIGINS) if write else (not origin or origin in ORIGINS))

    def reply(self, code, payload):
        data = json.dumps(payload, allow_nan=False).encode()
        self.send_response(code)
        if self.headers.get('Origin') in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
            self.send_header('Vary', 'Origin')
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_OPTIONS(self):
        if not self.permitted(write=True):
            self.reply(403, {'error': 'Only the local preview origin is allowed.'}); return
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if not self.permitted():
            self.reply(403, {'error': 'Only local preview access is allowed.'}); return
        if self.path == '/model':
            self.reply(200, self.playground.info())
        elif self.path == '/faces':
            self.reply(200, {'faces': self.playground.list_faces()})
        else:
            self.reply(404, {'error': 'Unknown endpoint.'})

    def do_POST(self):
        if not self.permitted(write=True) or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            self.reply(403, {'error': 'Use JSON from the local preview origin.'}); return
        if self.path not in ('/preview', '/save'):
            self.reply(404, {'error': 'Unknown endpoint.'}); return
        if not self.workers.acquire(blocking=False):
            self.reply(429, {'error': 'Generator busy. Try again shortly.'}); return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 65536:
                self.reply(413, {'error': 'Request must be at most 64 KB.'}); return
            payload = json.loads(self.rfile.read(size))
            result = self.playground.save(payload) if self.path == '/save' else self.playground.preview(payload)
            self.reply(200, result)
        except (ValueError, TypeError) as error:
            self.reply(422, {'error': str(error)})
        except OSError:
            self.reply(500, {'error': 'Could not save the face. Check the library directory permissions and disk space.'})
        finally:
            self.workers.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--source-units', choices=['m', 'mm'], required=True)
    parser.add_argument('--source-x', choices=['subject_left', 'subject_right'], default='subject_left')
    parser.add_argument('--library', type=Path, default=REPO/'tmp/flame-face-library')
    parser.add_argument('--port', type=int, default=5181)
    args = parser.parse_args()
    Handler.playground = Playground(args.model.expanduser(), args.library, args.source_units, args.source_x)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'FLAME playground API: http://127.0.0.1:{args.port}; library: {Handler.playground.library}', flush=True)
    server.serve_forever()
