"""Private loopback research processor: PYTHONPATH=python python3.12 -m dimension_pipeline.webcam_pilot."""
import argparse
import base64
import fcntl
import hashlib
import io
import json
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .webcam_geometry import calibrate, project
from .webcam_reconstruction import REPO, diagnostics, reconstruct
from .capture_quality import capture_quality, capture_context
from .mesh_comparison import compare_session
from .depth_experiments import run_depth_experiments
from .refinement_experiments import run_refinement_experiments, POLICY as REFINEMENT_POLICY
from .depth_variants import experiment_artifacts, experiment_variants
from .depth_quality import POLICY as DEPTH_POLICY

ROOT = REPO/'.private-webcam-runs'
ORIGINS = {f'http://{host}:{port}' for host in ('localhost', '127.0.0.1') for port in (3000, 5173, 5178)}
VERSION = 'webcam-session-1.0.0'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    temp = path.with_suffix('.writing')
    temp.write_text(json.dumps(value, allow_nan=False)); temp.replace(path)


def png(encoded):
    from PIL import Image
    data = base64.b64decode(encoded, validate=True)
    if len(data) > 16000000:
        raise ValueError('Image exceeds 16 MB.')
    image = Image.open(io.BytesIO(data))
    if image.format != 'PNG' or not 64 <= image.width <= 4096 or not 64 <= image.height <= 4096:
        raise ValueError('Expected a native PNG image between 64 and 4096 pixels per dimension.')
    image.load()
    return image, data


class Store:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve(); self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)
        self.lock = threading.RLock(); self.job = None; self.cancel_event = threading.Event(); self.process = None
        active = self.root/'active-process.json'
        if active.exists():
            previous = json.loads(active.read_text())
            info = subprocess.run(['ps', '-p', str(previous['pid']), '-o', 'lstart=', '-o', 'command='], capture_output=True, text=True).stdout.strip()
            if info and info == previous['fingerprint']:
                os.killpg(previous['pid'], signal.SIGTERM)
                deadline = time.monotonic()+3
                while time.monotonic() < deadline:
                    try:
                        os.kill(previous['pid'], 0)
                    except ProcessLookupError:
                        break
                    time.sleep(.05)
                else:
                    os.killpg(previous['pid'], signal.SIGKILL)
            active.unlink()
        for folder in self.root.iterdir():
            if folder.is_dir() and re.fullmatch(r'[a-f0-9]{32}', folder.name):
                state = self.load(folder.name)
                if state['status'] == 'processing':
                    state.update(status='interrupted', error='Processor stopped. Captures retained; explicitly restart the reconstruction.')
                    self.save(state)
                recovered = False
                for run in state.get('depth_experiments', {}).get('runs', []) + state.get('refinement_experiments', {}).get('runs', []):
                    if run['status'] == 'processing':
                        run.update(status='interrupted', error='Processor stopped. Raw baseline and completed variants retained; explicitly start a new experiment run.')
                        for row in run.get('variants', []):
                            if row['status'] == 'processing': row.update(status='interrupted', error='Processor stopped.')
                        recovered = True
                if recovered: self.save(state)

    def folder(self, identity):
        if not isinstance(identity, str) or not re.fullmatch(r'[a-f0-9]{32}', identity):
            raise ValueError('Invalid session ID.')
        path = self.root/identity
        if path.is_symlink() or not path.is_dir():
            raise ValueError('Unknown session.')
        return path

    def load(self, identity):
        return json.loads((self.folder(identity)/'session.json').read_text())

    def save(self, state):
        write_json(self.folder(state['id'])/'session.json', state)

    def create(self, payload=None):
        context = capture_context((payload or {}).get('capture_context'))
        identity = uuid.uuid4().hex; (self.root/identity).mkdir(mode=0o700)
        state = {'version': VERSION, 'id': identity, 'created_at': datetime.now(timezone.utc).isoformat(),
                 'status': 'capturing', 'captures': [], 'stage': None, 'error': None, 'result': None,
                 'capture_context': context}
        self.save(state); return state

    def capture(self, identity, payload):
        state = self.load(identity)
        if state['status'] != 'capturing':
            raise ValueError('Captures are locked after submission. Create another session for a new capture.')
        slot = payload['slot']
        if not isinstance(slot, str) or not re.fullmatch(r'(front|turn_(0[0-9]|[1-5][0-9]))', slot):
            raise ValueError('Unknown capture slot.')
        image, data = png(payload['image']); mask, mask_data = png(payload['mask'])
        if image.size != mask.size or payload.get('approved') is not True or payload.get('mirrored') is not False:
            raise ValueError('Approve a head-only mask matching the unmirrored native image dimensions.')
        pixels = mask.convert('L')
        if set(pixels.getdata()) != {0, 255}:
            raise ValueError('Mask must be binary and include foreground and background.')
        if state['captures'] and any(c['width'] != image.width or c['height'] != image.height for c in state['captures'] if c['slot'] != slot):
            raise ValueError('All captures must share native image dimensions.')
        if digest(data) != payload.get('sha256'):
            raise ValueError('Capture hash mismatch.')
        stamp = payload.get('timestamp')
        if not isinstance(stamp, str) or len(stamp) > 80:
            raise ValueError('Missing timestamp.')
        metadata = {'slot': slot, 'role': 'frontal' if slot == 'front' else 'reconstruction',
                    'capture_sequence': payload.get('capture_sequence'), 'width': image.width, 'height': image.height,
                    'timestamp': stamp, 'camera_settings': payload.get('camera_settings', {}), 'mirrored': False,
                    'camera_controls': payload.get('camera_controls'), 'capture_quality': capture_quality(image, mask),
                    'sha256': digest(data), 'mask_sha256': digest(mask_data), 'mask_approved': True,
                    'mask_provenance': payload.get('mask_provenance'), 'image': slot+'.png', 'mask': slot+'-mask.png'}
        folder = self.folder(identity)
        (folder/metadata['image']).write_bytes(data); (folder/metadata['mask']).write_bytes(mask_data)
        state['captures'] = [c for c in state['captures'] if c['slot'] != slot]+[metadata]
        self.save(state); return state

    def start(self, identity):
        state = self.load(identity)
        if self.job:
            raise ValueError('One reconstruction at a time; cancel or wait for the current job.')
        if state['status'] not in ('capturing', 'failed', 'cancelled', 'interrupted') or len(state['captures']) != 61 or {c['slot'] for c in state['captures']} != {'front', *('turn_'+str(i).zfill(2) for i in range(60))}:
            raise ValueError('Submit one frontal and 60 reviewed overlapping turn captures.')
        for c in state['captures']:
            for key, hash_key in (('image', 'sha256'), ('mask', 'mask_sha256')):
                if digest((self.folder(identity)/c[key]).read_bytes()) != c[hash_key]:
                    raise ValueError('Stored capture hash mismatch.')
        state.update(status='processing', stage='diagnostics', error=None, result=None)
        self.save(state); self.job = identity; self.cancel_event.clear()
        threading.Thread(target=self.work, args=(identity,), daemon=True).start()
        return state

    def work(self, identity):
        def update(stage):
            with self.lock:
                state = self.load(identity); state['stage'] = stage; self.save(state)
            if self.cancel_event.is_set():
                raise InterruptedError('Cancelled.')
        def run(stage, command, cwd):
            self.native_command(update, stage, command, cwd)
        try:
            result = reconstruct(self.folder(identity), self.load(identity), run, update, self.cancel_event.is_set)
            with self.lock:
                state = self.load(identity)
                if self.cancel_event.is_set():
                    raise InterruptedError('Cancelled.')
                state.update(status='surface_ready', stage='surface_review', result=result); self.save(state)
        except Exception as error:
            with self.lock:
                state = self.load(identity)
                state.update(status='cancelled' if self.cancel_event.is_set() or isinstance(error, InterruptedError) else 'failed', error=str(error))
                self.save(state)
        finally:
            with self.lock:
                self.job = None

    def native_command(self, update, stage, command, cwd):
        update(stage)
        with (cwd/'processing.log').open('a') as log:
            log.write(json.dumps(command)+'\n'); log.flush()
            process = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=log, start_new_session=True)
            with self.lock:
                self.process = process
                fingerprint = subprocess.run(['ps', '-p', str(process.pid), '-o', 'lstart=', '-o', 'command='], capture_output=True, text=True).stdout.strip()
                write_json(self.root/'active-process.json', {'pid': process.pid, 'fingerprint': fingerprint})
            try:
                while process.poll() is None:
                    if self.cancel_event.wait(.2):
                        os.killpg(process.pid, signal.SIGTERM)
                        try: process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL); process.wait()
                        raise InterruptedError('Cancelled.')
                if process.returncode:
                    raise ValueError(f'{stage} failed (exit {process.returncode}). Export session for processing.log.')
            finally:
                with self.lock:
                    self.process = None
                    (self.root/'active-process.json').unlink(missing_ok=True)

    def start_depth_experiments(self, identity, payload, refinement=False):
        key = 'refinement_experiments' if refinement else 'depth_experiments'
        if self.job: raise ValueError('One reconstruction/experiment job at a time.')
        state = self.load(identity)
        if state['status'] not in ('surface_ready', 'calibrated') or not state.get('result') or len(state['captures']) != 61:
            raise ValueError('Depth experiments require a completed raw reconstruction and 61 approved captures.')
        if set(payload)-(set() if refinement else {'resume_run_id'}): raise ValueError('Depth experiments use the versioned fixed profiles; arbitrary parameters are not accepted.')
        experiments = state.setdefault(key, {'version': 'webcam_refinement_experiments_v1' if refinement else 'webcam_depth_experiments_v1', 'runs': []})
        resume = None
        if payload.get('resume_run_id'):
            resume = next((r for r in experiments['runs'] if r['id']==payload['resume_run_id'] and r['status']!='processing'), None)
            if resume is None: raise ValueError('Unknown completed/interrupted experiment run to resume.')
        if len(experiments['runs']) >= 20: raise ValueError('Experiment run limit reached for this session.')
        run = {'id': uuid.uuid4().hex, 'status': 'processing', 'stage': 'queued', 'started_at': datetime.now(timezone.utc).isoformat(),
               'quality_version': (REFINEMENT_POLICY if refinement else DEPTH_POLICY)['version'], 'variants': [], 'resume_from_run': resume['id'] if resume else None}
        experiments['runs'].append(run); self.save(state); self.job = identity; self.cancel_event.clear()
        threading.Thread(target=self.depth_work, args=(identity, run['id'], refinement), daemon=True).start()
        return state

    def depth_work(self, identity, run_id, refinement=False):
        key = 'refinement_experiments' if refinement else 'depth_experiments'
        def record(state): return next(r for r in state[key]['runs'] if r['id'] == run_id)
        def update(stage):
            with self.lock:
                state = self.load(identity); record(state)['stage'] = stage; self.save(state)
            if self.cancel_event.is_set(): raise InterruptedError('Cancelled.')
        def publish(row):
            with self.lock:
                state = self.load(identity); run = record(state)
                run['variants'] = [v for v in run['variants'] if v['id'] != row['id']]+[row]; self.save(state)
        try:
            snapshot = self.load(identity); current = record(snapshot)
            resume = next((r for r in snapshot[key]['runs'] if r['id']==current.get('resume_from_run')), None)
            arguments = (self.folder(identity), snapshot, run_id,
                         lambda stage, command, cwd: self.native_command(update, stage, command, cwd), update, publish, self.cancel_event.is_set)
            if refinement: run_refinement_experiments(*arguments)
            elif resume: run_depth_experiments(*arguments, resume_record=resume)
            else: run_depth_experiments(*arguments)
            with self.lock:
                state = self.load(identity); run = record(state)
                run.update(status='completed_with_failures' if any(v['status']=='failed' for v in run['variants']) else 'completed',
                           stage='review', finished_at=datetime.now(timezone.utc).isoformat()); self.save(state)
        except Exception as error:
            with self.lock:
                state = self.load(identity); run = record(state)
                status = 'cancelled' if self.cancel_event.is_set() or isinstance(error, InterruptedError) else 'failed'
                run.update(status=status, error=str(error), finished_at=datetime.now(timezone.utc).isoformat())
                for row in run['variants']:
                    if row['status'] == 'processing': row.update(status=status, error=str(error))
                self.save(state)
        finally:
            with self.lock: self.job = None

    def depth_review(self, identity, payload):
        if self.job == identity: raise ValueError('Wait for experiment completion before recording review.')
        state = self.load(identity)
        row = next((v for v in experiment_variants(state) if v['id'] == payload.get('variant_id')), None)
        if row is None: raise ValueError('Unknown completed experiment variant.')
        if payload.get('decision') not in ('retain_experimental', 'adjust_further_test', 'reject') or not isinstance(payload.get('notes'), str) or not 1 <= len(payload['notes']) <= 4000:
            raise ValueError('Record a retain/adjust/reject recommendation and review notes.')
        row['recommendation'] = {'decision': payload['decision'], 'reason': payload['notes'], 'reviewed_at': datetime.now(timezone.utc).isoformat(),
                                 'accuracy_status': 'not_independently_validated'}
        self.save(state); return state

    def cancel(self, identity):
        self.folder(identity)
        if self.job != identity:
            raise ValueError('This session has no active job.')
        self.cancel_event.set()
        return {'status': 'cancelling'}

    def calibration(self, identity, payload):
        state = self.load(identity)
        if state['status'] not in ('surface_ready', 'calibrated') or payload.get('coverage_reviewed') is not True:
            raise ValueError('Review ear, nose, chin and both tape routes for surface coverage first.')
        result = state['result']
        surface, cameras, report = calibrate(result['surface'], result['cameras'], payload)
        state['calibrated'] = {'surface': surface, 'cameras': cameras, 'report': report,
                               'projected_points': project(surface['mesh'], cameras[result['frontal_camera_key']], result['raw_predictions'])}
        state['draft'] = {k: payload[k] for k in ('scale_readings_mm', 'check_readings_mm', 'scale_route', 'check_route')}
        if result.get('full_mesh'):
            import trimesh
            full = trimesh.load(self.folder(identity)/result['full_mesh'], force='mesh', process=False)
            full.apply_scale(report['mm_per_reconstruction_unit'])
            full.export(self.folder(identity)/'calibrated-full.ply')
            state['calibrated']['full_mesh'] = 'calibrated-full.ply'
        state['status'] = 'calibrated'; self.save(state); return state

    def decisions(self, identity, payload):
        state = self.load(identity)
        rows = state.get('calibrated', state.get('result') or {}).get('projected_points')
        index, decision = payload.get('index'), payload.get('decision')
        if rows is None or type(index) is not int or not 0 <= index < len(rows) or decision not in ('pending', 'accepted', 'rejected'):
            raise ValueError('Invalid experimental point review.')
        if decision == 'accepted' and rows[index]['status'] != 'ok':
            raise ValueError('A missed ray cannot be accepted.')
        rows[index]['acceptance'] = decision; self.save(state); return state

    def draft(self, identity, payload):
        from .webcam_geometry import attachment
        state = self.load(identity)
        if not state.get('result') or state['status'] == 'processing':
            raise ValueError('A surface is required to save routes.')
        for kind in ('scale_route', 'check_route'):
            if not isinstance(payload.get(kind), list) or len(payload[kind]) > 200:
                raise ValueError('Too many route controls.')
            for a in payload[kind]:
                attachment(state['result']['surface']['mesh'], a)
                if a.get('label') not in ('left_tragion', 'right_tragion', 'subnasale', 'menton', 'control'):
                    raise ValueError('Unknown route control label.')
        state['draft'] = payload; self.save(state); return state

    def export(self, identity):
        if self.job == identity:
            raise ValueError('Wait for cancellation or completion before exporting.')
        folder = self.folder(identity); files = {}
        state = self.load(identity)
        required = {'session.json'} | {c[k] for c in state['captures'] for k in ('image', 'mask')}
        artifacts = {a['path']: a['sha256'] for a in experiment_artifacts(state)}
        required.update(artifacts)
        if state.get('result'):
            required.update(state['result'][k] for k in ('full_mesh', 'frontal_undistorted'))
        if state.get('calibrated', {}).get('full_mesh'):
            required.add(state['calibrated']['full_mesh'])
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob('*')):
                if path.is_file() and not path.is_symlink():
                    name = path.relative_to(folder).as_posix()
                    if name not in required and path.name not in ('processing.log', 'cameras.txt', 'images.txt', 'points3D.txt', 'rigs.txt', 'frames.txt') and path.parent.name != 'dense_masks':
                        continue
                    data = path.read_bytes()
                    if name in artifacts and digest(data) != artifacts[name]:
                        raise ValueError('Experiment artifact changed; cannot export inconsistent provenance.')
                    files[name] = digest(data); archive.writestr(name, data)
            if not required.issubset(files):
                raise ValueError('Required session artifacts are missing; cannot export an incomplete bundle.')
            archive.writestr('bundle.json', json.dumps({'version': VERSION, 'files': files}))
        return output.getvalue()

    def restore(self, encoded):
        data = encoded if isinstance(encoded, bytes) else base64.b64decode(encoded, validate=True)
        if len(data) > 2_000_000_000: raise ValueError('Session archive exceeds the 2 GB upload limit.')
        archive = zipfile.ZipFile(io.BytesIO(data)); infos = archive.infolist()
        if len(infos) > 20000 or sum(i.file_size for i in infos) > 8_000_000_000 or len({i.filename for i in infos}) != len(infos):
            raise ValueError('Archive too large or contains duplicate files.')
        manifest = json.loads(archive.read('bundle.json'))
        if manifest['version'] != VERSION or set(manifest['files']) != {i.filename for i in infos}-{'bundle.json'}:
            raise ValueError('Unsupported or incomplete session bundle.')
        for name, expected in manifest['files'].items():
            if not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or name.startswith('/') or any(p in ('..', '.') for p in name.split('/')) or digest(archive.read(name)) != expected:
                raise ValueError('Invalid session archive path/hash.')
        state = json.loads(archive.read('session.json'))
        if state.get('version') != VERSION or state.get('status') == 'processing':
            raise ValueError('Unsupported or active session.')
        if any(run.get('status')=='processing' for key in ('depth_experiments','refinement_experiments') for run in state.get(key,{}).get('runs',[])):
            raise ValueError('Cannot reload an active experiment bundle.')
        # Never trust manifest-provided file references, even with matching hashes.
        refs = [c[k] for c in state['captures'] for k in ('image', 'mask')]
        if state.get('result'):
            refs += [state['result'][k] for k in ('frontal_undistorted', 'full_mesh')]
        if state.get('calibrated', {}).get('full_mesh'):
            refs.append(state['calibrated']['full_mesh'])
        artifacts = experiment_artifacts(state)
        refs += [a['path'] for a in artifacts]
        if any(ref not in manifest['files'] for ref in refs):
            raise ValueError('Session references files outside its bundle.')
        if any(manifest['files'][a['path']] != a['sha256'] for a in artifacts):
            raise ValueError('Experiment artifact hash does not match its provenance.')
        identity = uuid.uuid4().hex; folder = self.root/identity; folder.mkdir(mode=0o700)
        try:
            for name in manifest['files']:
                path = folder/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(archive.read(name))
            state['imported_from_id'] = state['id']; state['id'] = identity
            self.save(state)
        except Exception:
            shutil.rmtree(folder); raise
        return state


class Handler(BaseHTTPRequestHandler):
    store = None

    def permitted(self):
        return self.headers.get('Host') in {f'{h}:{self.server.server_port}' for h in ('127.0.0.1', 'localhost')} and self.headers.get('Origin') in ORIGINS

    def reply(self, code, payload, content_type='application/json'):
        data = json.dumps(payload, allow_nan=False).encode() if content_type == 'application/json' else payload
        self.send_response(code)
        if self.headers.get('Origin') in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', self.headers['Origin']); self.send_header('Vary', 'Origin')
        self.send_header('Content-Type', content_type); self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store'); self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_OPTIONS(self):
        if not self.permitted():
            self.reply(403, {'error': 'Exact local origin and Host required.'}); return
        self.send_response(204); self.send_header('Access-Control-Allow-Origin', self.headers['Origin'])
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type'); self.end_headers()

    def do_GET(self):
        if not self.permitted():
            self.reply(403, {'error': 'Exact local origin and Host required.'}); return
        try:
            if self.path == '/diagnostics':
                self.reply(200, diagnostics()); return
            if self.path == '/diagnostics/refinement':
                self.reply(200, diagnostics(include_refinement=True)); return
            comparison = re.fullmatch(r'/sessions/([a-f0-9]{32})/mesh-comparison(?:\?variant=([a-z0-9_-]{1,40})(?:&reference=(analysis|raw))?)?', self.path)
            if comparison:
                # Snapshot under the lock; do not block cancellation or session reads
                # while the read-only nearest-surface queries run.
                identity = comparison.group(1)
                with self.store.lock:
                    folder = self.store.folder(identity); state = self.store.load(identity)
                self.reply(200, compare_session(folder, state, variant=comparison.group(2) or 'raw', reference=comparison.group(3) or 'analysis')); return
            projection = re.fullmatch(r'/sessions/([a-f0-9]{32})/refinement-projection/([a-z0-9_-]{1,40})', self.path)
            if projection:
                identity, variant_id = projection.groups()
                with self.store.lock:
                    state = self.store.load(identity)
                    row = next((v for v in experiment_variants(state) if v['id']==variant_id and v['kind']=='image_refined'), None)
                    if row is None: raise ValueError('Unknown completed refinement.')
                    artifact = next((a for a in row['artifacts'] if a['path']==row.get('projection')), None)
                    if artifact is None: raise ValueError('Missing projection provenance.')
                    path = (self.store.folder(identity)/artifact['path']).resolve(); path.relative_to(self.store.folder(identity))
                    data = path.read_bytes()
                if digest(data)!=artifact['sha256']: raise ValueError('Refinement projection hash changed.')
                self.reply(200, data, 'application/octet-stream'); return
            variant = re.fullmatch(r'/sessions/([a-f0-9]{32})/mesh-variant/([a-z0-9_-]{1,40})', self.path)
            if variant:
                identity, variant_id = variant.groups()
                with self.store.lock:
                    state = self.store.load(identity)
                    row = next((v for v in experiment_variants(state) if v['id'] == variant_id), None)
                    if row is None: raise ValueError('Unknown completed experiment variant.')
                    path = (self.store.folder(identity)/row['full_mesh']).resolve(); path.relative_to(self.store.folder(identity))
                    data = path.read_bytes()
                if digest(data) != row['sha256']: raise ValueError('Experiment mesh hash changed.')
                self.reply(200, data, 'application/octet-stream'); return
            with self.store.lock:
                if self.path == '/sessions':
                    rows = [self.store.load(p.name) for p in self.store.root.iterdir() if p.is_dir() and re.fullmatch(r'[a-f0-9]{32}', p.name)]
                    self.reply(200, [{'id': s['id'], 'created_at': s['created_at'], 'status': s['status'],
                                      'capture_context': s.get('capture_context'), 'capture_count': len(s['captures'])} for s in rows]); return
                capture = re.fullmatch(r'/sessions/([a-f0-9]{32})/captures/(front|turn_(?:0[0-9]|[1-5][0-9]))/(image|mask)', self.path)
                if capture:
                    identity, slot, kind = capture.groups()
                    state = self.store.load(identity)
                    row = next((c for c in state['captures'] if c['slot'] == slot), None)
                    if row is None:
                        raise ValueError('Capture has not been saved.')
                    path = (self.store.folder(identity)/row[kind]).resolve()
                    path.relative_to(self.store.folder(identity))
                    self.reply(200, path.read_bytes(), 'image/png'); return
                match = re.fullmatch(r'/sessions/([a-f0-9]{32})(?:/(export|frontal|mesh|mesh-mm))?', self.path)
                if not match:
                    self.reply(404, {'error': 'Unknown endpoint.'}); return
                identity, artifact = match.groups(); state = self.store.load(identity)
                if artifact == 'export':
                    self.reply(200, self.store.export(identity), 'application/zip')
                elif artifact:
                    key = 'frontal_undistorted' if artifact == 'frontal' else 'full_mesh'
                    reference = state['calibrated']['full_mesh'] if artifact == 'mesh-mm' else state['result'][key]
                    path = (self.store.folder(identity)/reference).resolve()
                    path.relative_to(self.store.folder(identity))
                    self.reply(200, path.read_bytes(), 'image/png' if artifact == 'frontal' else 'application/octet-stream')
                else:
                    self.reply(200, state)
        except (ValueError, KeyError, OSError, TypeError, MemoryError) as error:
            self.reply(422, {'error': str(error)})

    def do_POST(self):
        content_type = self.headers.get('Content-Type', '').split(';')[0]
        archive_upload = self.path == '/restore' and content_type == 'application/zip'
        if not self.permitted() or (content_type != 'application/json' and not archive_upload):
            self.reply(403, {'error': 'JSON from an exact local origin and Host required.'}); return
        try:
            size = int(self.headers.get('Content-Length', 0))
            limit = 2_000_000_000 if self.path == '/restore' else 45_000_000
            if not 0 < size <= limit:
                self.reply(413, {'error': 'Request exceeds size limit.'}); return
            if archive_upload:
                data = self.rfile.read(size)
                with self.store.lock:
                    self.reply(200, self.store.restore(data))
                return
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError('Expected a JSON object.')
            with self.store.lock:
                if self.path == '/sessions':
                    result = self.store.create(payload)
                elif self.path == '/restore':
                    result = self.store.restore(payload['archive'])
                else:
                    match = re.fullmatch(r'/sessions/([a-f0-9]{32})/(capture|start|cancel|calibrate|decisions|draft|delete|depth-experiments|depth-review|refinement-experiments|refinement-review)', self.path)
                    if not match:
                        self.reply(404, {'error': 'Unknown endpoint.'}); return
                    identity, action = match.groups()
                    if self.store.job == identity and action in ('capture', 'calibrate', 'decisions', 'draft'):
                        raise ValueError('Wait for processing to finish before modifying this session.')
                    if action == 'delete':
                        if self.store.job == identity:
                            raise ValueError('Cancel and wait for the job to stop before deletion.')
                        shutil.rmtree(self.store.folder(identity)); result = {'deleted': identity}
                    elif action in ('start', 'cancel'):
                        result = getattr(self.store, action)(identity)
                    elif action == 'depth-experiments': result = self.store.start_depth_experiments(identity, payload)
                    elif action == 'refinement-experiments': result = self.store.start_depth_experiments(identity, payload, refinement=True)
                    elif action in ('depth-review', 'refinement-review'): result = self.store.depth_review(identity, payload)
                    else:
                        method = {'capture': 'capture', 'calibrate': 'calibration', 'decisions': 'decisions', 'draft': 'draft'}[action]
                        result = getattr(self.store, method)(identity, payload)
                self.reply(200, result)
        except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as error:
            self.reply(422, {'error': str(error)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostics', action='store_true')
    args = parser.parse_args()
    if args.diagnostics:
        print(json.dumps(diagnostics(), indent=2))
    else:
        os.umask(0o077)
        ROOT.mkdir(mode=0o700, exist_ok=True)
        instance_lock = (ROOT/'processor.lock').open('w')
        try:
            fcntl.flock(instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('A webcam processor already owns the private run directory.')
        Handler.store = Store()
        server = ThreadingHTTPServer(('127.0.0.1', 5182), Handler)
        print('Private webcam processor: http://127.0.0.1:5182', flush=True)
        try:
            server.serve_forever()
        finally:
            Handler.store.cancel_event.set()
            process = Handler.store.process
            if process and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
            server.server_close()
