"""Isolated loopback API for fake-camera tests; never opens participant sessions."""
import argparse
import tempfile
from http.server import ThreadingHTTPServer

from dimension_pipeline.webcam_pilot import Handler, Store

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=5183)
args = parser.parse_args()
with tempfile.TemporaryDirectory(prefix='webcam-api-test-') as root:
    Handler.store = Store(root)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Isolated test processor: {args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
