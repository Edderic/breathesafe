"""Validated, session-scoped artifact references for optional experiment records."""
import re
from pathlib import PurePosixPath

from .depth_quality import POLICY


def experiment_artifacts(state):
    experiments = state.get('depth_experiments')
    if not experiments: return []
    if experiments.get('version') != 'webcam_depth_experiments_v1' or not isinstance(experiments.get('runs'), list) or len(experiments['runs']) > 20:
        raise ValueError('Unsupported depth-experiment records.')
    artifacts = {}; ids = set()
    for run in experiments['runs']:
        if not re.fullmatch(r'[a-f0-9]{32}', run.get('id', '')): raise ValueError('Invalid experiment run ID.')
        for row in run.get('variants', []):
            if row.get('profile_id') not in POLICY['profiles'] or row.get('id') != 'q'+run['id'][:16]+'-'+row['profile_id'] or row['id'] in ids:
                raise ValueError('Invalid or duplicate experiment variant ID.')
            ids.add(row['id'])
            for artifact in row.get('artifacts', []):
                name = artifact.get('path', ''); parts = PurePosixPath(name).parts
                if not name.startswith('experiments/'+run['id']+'/') or '..' in parts or not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or not re.fullmatch(r'[a-f0-9]{64}', artifact.get('sha256', '')):
                    raise ValueError('Invalid experiment artifact reference.')
                if name in artifacts and artifacts[name]['sha256'] != artifact['sha256']:
                    raise ValueError('Conflicting experiment artifact hashes.')
                artifacts[name] = artifact
            if row.get('status') == 'completed':
                if row.get('coordinate_transform') != 'identity' or row.get('units') != 'reconstruction_unit':
                    raise ValueError('Unsupported experiment coordinate transform.')
                name = row.get('full_mesh')
                if name not in artifacts or artifacts[name]['sha256'] != row.get('sha256'):
                    raise ValueError('Completed variant has no matching artifact provenance.')
    return list(artifacts.values())


def experiment_variants(state):
    experiment_artifacts(state)
    return [row for run in state.get('depth_experiments', {}).get('runs', []) for row in run.get('variants', [])
            if row.get('status') == 'completed' and row.get('full_mesh')]
