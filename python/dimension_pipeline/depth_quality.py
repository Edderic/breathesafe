"""Explicit pinned defaults and one-factor-at-a-time frozen-depth profiles."""
import json
from pathlib import Path

POLICY = json.loads(Path(__file__).with_name('depth_quality_policy.json').read_text())


def dense_options(profile=None):
    if profile is not None and profile not in POLICY['profiles']:
        raise ValueError('Unknown depth-quality profile.')
    selected = POLICY['baseline'] if profile is None else POLICY['profiles'][profile]
    options = {**POLICY['fixed'], **{k: v for k, v in selected.items() if k != 'label'}}
    if options['postprocess-dmaps'] & 2:
        raise ValueError('Depth gap filling is disabled.')
    return [str(v) for key, value in options.items() for v in ('--'+key, value)]


def mesh_options():
    return [str(v) for key, value in POLICY['meshing'].items() for v in ('--'+key, value)]
