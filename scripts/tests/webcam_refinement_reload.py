"""Manual local integration check: real binary HTTP archive reload into a temporary private Store.

PYTHONPATH=python tmp/webcam-pilot-venv/bin/python scripts/tests/webcam_refinement_reload.py
Does not add a session to the user's running processor or start reconstruction.
"""
import json
import tempfile
import threading
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

from dimension_pipeline.webcam_pilot import Store, Handler, REPO
from dimension_pipeline.mesh_comparison import compare_session
from dimension_pipeline.depth_variants import experiment_artifacts

archive_path = REPO/'.private-webcam-runs/capture-comparisons/bre18-session-export.zip'
data = archive_path.read_bytes()
with zipfile.ZipFile(archive_path) as archive:
    original = json.loads(archive.read('session.json'))
with tempfile.TemporaryDirectory(prefix='bre18-reload-', dir=archive_path.parent) as root:
    class TemporaryHandler(Handler):
        store = Store(root)
    server = ThreadingHTTPServer(('127.0.0.1',0),TemporaryHandler)
    thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        request = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/restore',data=data,
            headers={'Origin':'http://127.0.0.1:5178','Content-Type':'application/zip'},method='POST')
        with urllib.request.urlopen(request,timeout=180) as response:
            state = json.load(response)
        for key in ('result','captures','calibrated','draft','depth_experiments','refinement_experiments'):
            assert state.get(key)==original.get(key), key
        rows = state['refinement_experiments']['runs'][-1]['variants']
        assert len(rows)==3 and all(row['status']=='completed' for row in rows)
        store = TemporaryHandler.store; folder = store.folder(state['id'])
        for row in rows:
            projection = json.loads((folder/row['projection']).read_text())
            assert projection['surface']['topology_id']==row['analysis_mesh_id']
            assert projection['calibration'] is None and projection['routes']==[]
            assert all(p['acceptance']=='pending' for p in projection['projected_points'])
            report = compare_session(folder,state,100,row['id'],'raw')
            assert report['units']=='reconstruction_unit' and report['display_scale']==1.
        print(f'Binary HTTP reload PASS: {len(data):,} bytes, {len(experiment_artifacts(state))} experiment artifacts, 3 variant geometries/projections')
    finally:
        server.shutdown();server.server_close();thread.join()
