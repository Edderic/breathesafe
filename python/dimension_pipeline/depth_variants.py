"""Validated, session-scoped artifact references for optional experiment records."""
import re
from pathlib import PurePosixPath

from .depth_quality import POLICY
from .refinement_experiments import POLICY as REFINEMENT_POLICY, POLICIES as REFINEMENT_POLICIES


def _artifacts(state, key, version, policy, prefix, directory):
    experiments = state.get(key)
    if not experiments: return []
    if experiments.get('version') != version or not isinstance(experiments.get('runs'), list) or len(experiments['runs']) > 20:
        raise ValueError('Unsupported depth-experiment records.')
    artifacts = {}; ids = set()
    for run in experiments['runs']:
        if not re.fullmatch(r'[a-f0-9]{32}', run.get('id', '')): raise ValueError('Invalid experiment run ID.')
        for row in run.get('variants', []):
            row_policy = REFINEMENT_POLICIES.get(row.get('version')) if prefix=='r' else policy
            if row_policy is None or row.get('profile_id') not in row_policy['profiles'] or row.get('id') != prefix+run['id'][:16]+'-'+row['profile_id'] or row['id'] in ids:
                raise ValueError('Invalid or duplicate experiment variant ID.')
            ids.add(row['id'])
            for artifact in row.get('artifacts', []):
                name = artifact.get('path', ''); parts = PurePosixPath(name).parts
                if not name.startswith(directory+'/'+run['id']+'/') or '..' in parts or not re.fullmatch(r'[A-Za-z0-9_./-]+', name) or not re.fullmatch(r'[a-f0-9]{64}', artifact.get('sha256', '')):
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
                if prefix=='r' and (row.get('projection') not in artifacts or not re.fullmatch(r'sha256:[a-f0-9]{64}',row.get('analysis_mesh_id',''))):
                    raise ValueError('Completed refinement requires fresh analysis/projection provenance.')
    return list(artifacts.values())


def experiment_artifacts(state):
    return (_artifacts(state, 'depth_experiments', 'webcam_depth_experiments_v1', POLICY, 'q', 'experiments') +
            _artifacts(state, 'refinement_experiments', 'webcam_refinement_experiments_v1', REFINEMENT_POLICY, 'r', 'refinements'))


def experiment_variants(state):
    experiment_artifacts(state)
    return [row for key in ('depth_experiments','refinement_experiments') for run in state.get(key, {}).get('runs', []) for row in run.get('variants', [])
            if row.get('status') == 'completed' and row.get('full_mesh')]
