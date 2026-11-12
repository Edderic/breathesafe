"""Install official pinned macOS arm64 tools under ignored tmp/webcam-tools.

python3 scripts/setup_webcam_native.py
Optional --archives points to an existing directory containing the two named zips.
Downloads and unpacks tools; never modifies Gatekeeper settings or system files.
"""
import argparse
import hashlib
import io
import json
import os
import platform
import stat
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]/'tmp/webcam-tools'
ASSETS = {
    'colmap-arm64-macos.zip': ('https://github.com/colmap/colmap/releases/download/4.2.1/colmap-arm64-macos.zip',
                             '1fe9d65bddd61e0598f3087641cb14c4d4d4c74529e9f58911e8a5238a140a04'),
    'OpenMVS_macOS_arm64.zip': ('https://github.com/cdcseacave/openMVS/releases/download/v2.4.0/OpenMVS_macOS_arm64.zip',
                              '3d4c616c97031b1ab6e2eecb0ddd5614fb99513c0782a32c9350602faf38799b'),
}


def extract(archive, destination):
    for info in archive.infolist():
        path = destination/info.filename
        if not path.resolve().is_relative_to(destination.resolve()):
            raise ValueError('Unsafe archive path.')
        if info.is_dir():
            path.mkdir(parents=True, exist_ok=True); continue
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = info.external_attr >> 16
        data = archive.read(info)
        if stat.S_ISLNK(mode):
            target = data.decode()
            if not (path.parent/target).resolve().is_relative_to(destination.resolve()):
                raise ValueError('Unsafe archive symlink.')
            if not path.is_symlink():
                path.symlink_to(target)
        else:
            path.write_bytes(data); path.chmod(mode & 0o777 or 0o644)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path)
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('Requires native macOS arm64.')
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, (url, expected) in ASSETS.items():
        cache = (args.archives or ROOT)/name
        if not cache.exists():
            print('Downloading '+url, flush=True)
            urllib.request.urlretrieve(url, cache)
        data = cache.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit('Archive checksum mismatch: '+name)
        folder = ROOT/('colmap' if name.startswith('colmap') else 'openmvs'); folder.mkdir(exist_ok=True)
        archive = zipfile.ZipFile(io.BytesIO(data))
        if name.startswith('colmap'):
            archive = zipfile.ZipFile(io.BytesIO(archive.read('COLMAP-mac.zip')))
        extract(archive, folder)
    (ROOT/'bin').mkdir(exist_ok=True)
    for name, source in [('colmap', ROOT/'colmap/COLMAP.app/Contents/MacOS/colmap'),
                         *[(n, ROOT/'openmvs'/n) for n in ('InterfaceCOLMAP', 'DensifyPointCloud', 'ReconstructMesh', 'RefineMesh')]]:
        source.chmod(source.stat().st_mode | 0o111)
        link = ROOT/'bin'/name
        if not link.exists():
            link.symlink_to(source)
    (ROOT/'provenance.json').write_text(json.dumps(ASSETS, indent=2))
    print('Tools cached at '+str(ROOT/'bin')+'. Run processor --diagnostics before capture.')


if __name__ == '__main__':
    main()
