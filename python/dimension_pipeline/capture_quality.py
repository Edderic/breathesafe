"""Reproducible advisory image checks; original PNGs and masks are never changed."""
import json
import math
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name('capture_quality_policy.json').read_text())


def capture_quality(image, mask, policy=None):
    import numpy as np
    policy = dict(policy or POLICY)
    rgb = np.asarray(image.convert('RGB'), dtype=float)
    binary = np.asarray(mask.convert('L')) >= 128
    height, width = rgb.shape[:2]
    if binary.shape != (height, width):
        raise ValueError('Quality checks require matching native image and mask dimensions.')
    result = {'policy': policy, 'image_size': [width, height], 'head_bbox': None, 'head_size_px': None,
              'sharpness': None, 'sample_size': None, 'interior_samples': 0, 'status': 'unavailable', 'flags': []}
    ys, xs = np.nonzero(binary)
    if not len(xs):
        result['flags'] = ['empty_head_mask']; return result
    left, top, right, bottom = int(xs.min()), int(ys.min()), int(xs.max())+1, int(ys.max())+1
    w, h = right-left, bottom-top
    result.update(head_bbox=[left, top, right, bottom], head_size_px=[w, h],
                  head_height_fraction=round(h/height, 6), mask_area_fraction=round(float(binary.mean()), 6),
                  border_fraction=round(min(left/width, top/height, (width-right)/width, (height-bottom)/height), 6))
    if result['head_height_fraction'] < policy['head_height_warning_below']:
        result['flags'].append('head_small_in_frame')
    if result['border_fraction'] < policy['border_warning_below']:
        result['flags'].append('head_near_image_edge')
    scale = min(1., policy['max_sample_side']/max(w, h))
    sw, sh = max(1, math.floor(w*scale+.5)), max(1, math.floor(h*scale+.5))
    result['sample_size'] = [sw, sh]
    sx, sy = np.meshgrid(np.clip(left+(np.arange(sw)+.5)*w/sw-.5, 0, width-1),
                         np.clip(top+(np.arange(sh)+.5)*h/sh-.5, 0, height-1))
    x0, y0 = np.floor(sx).astype(int), np.floor(sy).astype(int)
    x1, y1 = np.minimum(width-1, x0+1), np.minimum(height-1, y0+1)
    dx, dy = sx-x0, sy-y0
    luma = rgb[:, :, 0]*.2126+rgb[:, :, 1]*.7152+rgb[:, :, 2]*.0722
    gray = (1-dy)*((1-dx)*luma[y0, x0]+dx*luma[y0, x1])+dy*((1-dx)*luma[y1, x0]+dx*luma[y1, x1])
    inside = binary[np.floor(sy+.5).astype(int), np.floor(sx+.5).astype(int)]
    valid = inside[1:-1, 1:-1] & inside[1:-1, :-2] & inside[1:-1, 2:] & inside[:-2, 1:-1] & inside[2:, 1:-1]
    lap = (gray[1:-1, :-2]+gray[1:-1, 2:]+gray[:-2, 1:-1]+gray[2:, 1:-1]-4*gray[1:-1, 1:-1])[valid]
    result['interior_samples'] = len(lap)
    if len(lap) < policy['minimum_interior_samples']:
        result['flags'].append('insufficient_head_pixels'); return result
    result['sharpness'] = round(float(np.var(lap)), 6)
    if result['sharpness'] < policy['sharpness_warning_below']:
        result['flags'].append('low_sharpness_or_low_texture')
    result['status'] = 'review_recommended' if result['flags'] else 'no_flags'
    return result


def capture_context(payload):
    """Small, explicit development-study labels; not participant identities."""
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError('Capture context must be an object.')
    group, conditions, repeat = payload.get('group', ''), payload.get('conditions', ''), payload.get('repeat', 1)
    if not isinstance(group, str) or len(group) > 80 or not isinstance(conditions, str) or len(conditions) > 1000 or type(repeat) is not int or not 1 <= repeat <= 10:
        raise ValueError('Provide a comparison group (up to 80 characters), conditions (up to 1000), and repeat 1–10.')
    result = {'group': group.strip(), 'conditions': conditions.strip(), 'repeat': repeat}
    if 'capture_mode' in payload:
        if payload['capture_mode'] not in ('head_turn', 'moving_camera', 'moving_camera_two_pass'):
            raise ValueError('Unknown capture mode.')
        result['capture_mode'] = payload['capture_mode']
    return result
