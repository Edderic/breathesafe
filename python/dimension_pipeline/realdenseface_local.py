"""Local CPU/MPS neural-prior trial; intentionally excludes the CUDA FLAME solver.

Loads the official network with weights_only=True, preserving upstream crop,
normalization, UV sampling and bbox refinement. Uses cached MediaPipe only for
an initial face box. CUDA rasterized visibility is NOT reproduced here.
"""
import argparse
import hashlib
import html
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from .realdenseface_trial import SOURCE_COMMIT

WEIGHTS_SHA256 = '9644fb9c7b7b8b5b6ca0d06fdebae418c154f1f4224a1ef5298777cc399ea15c'
ASSETS_SHA256 = '922cb76f3afef0c2e9801a63991de269a98e6b67b1728232493f851589151dd3'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_source(source):
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != SOURCE_COMMIT:
        raise ValueError('Expected audited RealDenseFace source revision '+SOURCE_COMMIT)
    return commit


def check_asset(path, expected):
    if sha(path) != expected:
        raise ValueError('Asset differs from the published RealDenseFace checksum: '+str(path))


def initial_bbox(record, width, height):
    if 'initial_bbox_pixels' in record:
        bbox = np.asarray(record['initial_bbox_pixels'], dtype=float)
    else:
        points = np.array([[p['x']*width, p['y']*height] for p in record['landmarks'][:468]])
        bbox = np.r_[points.min(axis=0), points.max(axis=0)]
    if bbox.shape != (4,) or not np.isfinite(bbox).all() or not (bbox[2]>bbox[0] and bbox[3]>bbox[1]):
        raise ValueError('Invalid initial face crop')
    return bbox


def infer(args):
    import torch
    import torch.nn.functional as functional
    import yaml
    from PIL import Image, ImageDraw
    source = Path(args.source).resolve()
    check_source(source)
    check_asset(args.weights, WEIGHTS_SHA256)
    check_asset(args.assets, ASSETS_SHA256)
    sys.path.insert(0, str(source))
    from models.realdenseface import RealDenseFace
    # Load just preprocessing: importing tracker would eagerly import CUDA code.
    spec = importlib.util.spec_from_file_location('rdf_crop', source/'tracker/inference/preprocess.py')
    crop = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crop)
    device = torch.device(args.device)
    if args.device == 'mps' and not torch.backends.mps.is_available():
        raise ValueError('MPS unavailable in this execution context; try native execution or CPU')
    torch.set_num_threads(4)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    config = yaml.safe_load((source/'configs/model/vits.yaml').read_text())
    config['dino_pretrained'] = False
    started = time.monotonic()
    model = RealDenseFace(**config)
    model.load_state_dict(torch.load(args.weights, map_location='cpu', weights_only=True), strict=True)
    model.to(device).eval()
    model.build_inference_cache()
    assets = np.load(args.assets, allow_pickle=False)
    uv = torch.from_numpy(assets['vertex_uvs'].copy()).to(device)[None, :, None]*2-1
    key_ids = np.unique(assets['vis_edges'])
    mean = torch.tensor([.485, .456, .406], device=device)[None, :, None, None]
    std = torch.tensor([.229, .224, .225], device=device)[None, :, None, None]
    def sync():
        if device.type == 'mps':
            torch.mps.synchronize()
    sync()
    load_seconds = time.monotonic()-started
    baseline = json.loads(Path(args.baseline_report).read_text())
    folder = Path(args.session)
    cached = json.loads(Path(args.landmarks).read_text())
    report = {'version': 'realdenseface_local_neural_v1', 'device': args.device, 'torch': torch.__version__,
              'source_commit': SOURCE_COMMIT, 'weights_sha256': sha(args.weights), 'assets_sha256': sha(args.assets),
              'model_load_seconds': load_seconds, 'flame_fitting': 'not_run; upstream solver requires CUDA',
              'visibility': 'unfiltered; CUDA rasterization not reproduced',
              'initial_crop': 'cached MediaPipe bounds or explicit approved head-mask fallback; refined once using official network', 'views': []}
    slots = [v['slot'] for v in baseline['views']] if args.slots == 'all' else args.slots.split(',')
    for slot in slots:
        if not slot or Path(slot).name != slot:
            raise ValueError('Photo slots must be simple names')
        record = next(v for v in baseline['views'] if v['slot'] == slot)
        path = folder/(slot+'.png')
        if sha(path) != record['sha256'] or cached[slot]['sha256'] != record['sha256']:
            raise ValueError('Capture/cache hash changed')
        image = np.asarray(Image.open(path).convert('RGB'))
        height, width = image.shape[:2]
        bbox = initial_bbox(cached[slot], width, height)
        passes = []
        for step in range(2):
            bbox[[0, 2]] = np.clip(bbox[[0, 2]], 0, width)
            bbox[[1, 3]] = np.clip(bbox[[1, 3]], 0, height)
            square = crop.make_bbox_square(crop.enlarge_bbox(bbox, 1.3))
            resized, square = crop.crop_and_resize_image(image, square, int(config['target_size']))
            tensor = torch.from_numpy(resized.copy()).to(device).permute(2, 0, 1)[None].float()/255
            tensor = (tensor-mean)/std
            sync()
            start = time.monotonic()
            with torch.inference_mode():
                coords, coord_logvar, depths, depth_logvar = model(tensor)
                maps = [coords*.5+.5, coord_logvar.clamp(-8, 3), depths/config.get('scale_depth', 1), depth_logvar.clamp(-8, 3)]
                sampled = [functional.grid_sample(m.float(), uv, mode='bilinear', align_corners=False).squeeze(0).squeeze(-1).T for m in maps]
            sync()
            passes.append(time.monotonic()-start)
            arrays = [v.detach().cpu().numpy() for v in sampled]
            if not all(np.isfinite(a).all() for a in arrays):
                raise ValueError('Non-finite network output')
            xy = arrays[0]*(square[2:]-square[:2])+square[:2]
            bbox = np.r_[xy[key_ids].min(axis=0), xy[key_ids].max(axis=0)]
        np.savez(out/(slot+'.npz'), vertex_coord=xy, vertex_coord_log_var=arrays[1],
                 vertex_depth=arrays[2], vertex_depth_log_var=arrays[3], crop=square,
                 visibility_filtered=np.array(False))
        preview = Image.fromarray(image)
        draw = ImageDraw.Draw(preview)
        for x, y in xy[key_ids]:
            draw.ellipse((x-2, y-2, x+2, y+2), fill='#00ddcc')
        preview.thumbnail((960, 540))
        preview.save(out/(slot+'-prediction.jpg'))
        report['views'].append({'slot': slot, 'image_sha256': record['sha256'], 'seconds_per_forward': passes,
                                'vertex_count': len(xy), 'finite': True, 'crop': square.tolist(),
                                'initial_crop_source': cached[slot].get('crop_source', 'cached_mediapipe')})
        (out/'report.json').write_text(json.dumps(report, indent=2))
        print(slot, args.device, passes, flush=True)
    cards = ''.join('<article><h2>'+html.escape(v['slot'])+'</h2><img src="'+
                    html.escape(v['slot'], quote=True)+'-prediction.jpg"><p>Forward times: '+
                    ', '.join(f'{t:.3f} s' for t in v['seconds_per_forward'])+'</p></article>'
                    for v in report['views'])
    (out/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Local RealDenseFace predictions</title>'
        '<style>body{font:17px system-ui;max-width:1400px;margin:30px auto;color:#243b46}'
        'main{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%}</style>'
        '<h1>Local RealDenseFace neural predictions · '+html.escape(args.device)+'</h1>'
        '<p>Dense 2D correspondence previews. Visibility unfiltered; occluded vertices can appear here. '
        'No fitted FLAME head or physical measurements yet. No CUDA code or cloud instance used.</p>'
        '<p><a href="report.json">Timing and provenance report</a></p><main>'+cards+'</main>')
    print(out/'report.json', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'weights', 'assets', 'session', 'baseline-report', 'landmarks', 'out'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--device', choices=('cpu', 'mps'), default='cpu')
    parser.add_argument('--slots', default='front')
    infer(parser.parse_args())


if __name__ == '__main__':
    main()
