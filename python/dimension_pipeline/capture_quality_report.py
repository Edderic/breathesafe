"""Private capture-duration comparison; never changes sessions or infers missing captures.

PYTHONPATH=python python -m dimension_pipeline.capture_quality_report --sessions ID ...
"""
import argparse
import hashlib
import json
import re
import statistics
from datetime import datetime
from pathlib import Path

from .capture_quality import POLICY, capture_quality, capture_context

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO/'.private-webcam-runs'


def summary(values):
    values = [v for v in values if v is not None]
    return {'count': len(values), 'minimum': min(values) if values else None,
            'median': statistics.median(values) if values else None,
            'maximum': max(values) if values else None,
            'spread': max(values)-min(values) if values else None}


def stored_file(folder, name):
    path = (folder/name).resolve()
    path.relative_to(folder.resolve())
    if not path.is_file():
        raise ValueError('Missing session artifact: '+name)
    return path


def reconstruction_fingerprint(folder, result):
    if not result:
        return None
    work = stored_file(folder, result['full_mesh']).parent
    log = work/'processing.log'
    if not log.is_file():
        return None
    steps = []
    for line in log.read_text().splitlines():
        if not line.startswith('['):
            continue
        try:
            command = json.loads(line)
        except ValueError:
            continue
        if not isinstance(command, list) or not all(isinstance(v, str) for v in command):
            continue
        tool = Path(command[0]).name
        if tool == 'colmap' and len(command) > 1:
            if command[1] == 'feature_extractor' and any(v.endswith('/frontal.txt') for v in command):
                break
            if command[1] not in ('feature_extractor', 'matches_importer', 'mapper', 'image_undistorter'):
                continue
        elif tool not in ('InterfaceCOLMAP', 'DensifyPointCloud', 'ReconstructMesh'):
            continue
        args = [re.sub(r'\$ATTEMPT/sparse/\d+', '$ATTEMPT/sparse/<selected>', v.replace(str(work), '$ATTEMPT')) for v in command[1:]]
        steps.append({'tool': tool, 'args': args})
    deltas = []
    if not steps:
        return None
    if (work/'pairs.txt').is_file():
        deltas = sorted({int(b)-int(a) for line in (work/'pairs.txt').read_text().splitlines()
                         for a, b in [re.findall(r'turn_(\d+)\.png', line)]})
    tools = result.get('diagnostics', {}).get('tools', {}).get('tools', {})
    config = {'steps': steps, 'matching_frame_deltas': deltas, 'tools': {k: v.get('required') for k, v in tools.items()}}
    return {'sha256': hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(), 'config': config}


def session_report(root, identity, override=None):
    from PIL import Image
    if not re.fullmatch(r'[a-f0-9]{32}', identity):
        raise ValueError('Use session IDs, not paths.')
    folder = (Path(root)/identity).resolve()
    folder.relative_to(Path(root).resolve())
    state = json.loads((folder/'session.json').read_text())
    context = capture_context(override if override is not None else state.get('capture_context'))
    frames = []
    for capture in sorted(state['captures'], key=lambda c: c['slot']):
        item = {'slot': capture['slot'], 'role': capture['role'], 'timestamp': capture['timestamp'], 'quality': None, 'error': None}
        try:
            paths = [stored_file(folder, capture[k]) for k in ('image', 'mask')]
            for path, key in zip(paths, ('sha256', 'mask_sha256')):
                if hashlib.sha256(path.read_bytes()).hexdigest() != capture[key]:
                    raise ValueError('Artifact hash mismatch: '+capture['slot'])
            with Image.open(paths[0]) as image, Image.open(paths[1]) as mask:
                item['quality'] = capture_quality(image, mask)
        except (OSError, ValueError) as error:
            item['error'] = str(error)
        frames.append(item)
    turns = [c for c in state['captures'] if c['role'] == 'reconstruction']
    qualities = [f['quality'] for f in frames if f['role'] == 'reconstruction' and f['quality']]
    sequences = [c.get('capture_sequence') for c in turns]
    duration = None; duration_source = 'unavailable'; actual_duration = None
    if len(turns) == 60:
        try:
            stamps = [datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00')) for c in sorted(turns, key=lambda c: c['slot'])]
            actual_duration = (stamps[-1]-stamps[0]).total_seconds()
        except (ValueError, TypeError):
            duration_source = 'invalid_timestamps'
        if all(sequences) and len({s['id'] for s in sequences}) == 1 and len({s['duration_ms'] for s in sequences}) == 1:
            duration = sequences[0]['duration_ms']/1000; duration_source = 'recorded_sequence'
        elif not any(sequences) and actual_duration is not None:
            nearest = min((10, 20, 30), key=lambda value: abs(actual_duration-value))
            if abs(actual_duration-nearest) <= .5:
                duration = nearest; duration_source = 'inferred_from_legacy_timestamps'
    camera_configs = set()
    for c in turns:
        settings = c.get('camera_settings', {})
        config = {k: settings.get(k) for k in ('width', 'height', 'frameRate', 'focusMode', 'exposureMode', 'whiteBalanceMode')}
        config['device_sha256'] = hashlib.sha256(settings['deviceId'].encode()).hexdigest() if settings.get('deviceId') else None
        config['manual_locks'] = {a['id']: a['requested'] for a in (c.get('camera_controls') or {}).get('attempts', []) if a.get('verified') and a['requested']['mode'] == 'manual'}
        camera_configs.add(json.dumps(config, sort_keys=True))
    result = state.get('result'); diagnostics = (result or {}).get('diagnostics', {})
    check = (state.get('calibrated') or {}).get('report', {}).get('independent_check') if result else None
    return {'session_id': identity, 'status': state['status'], 'context': context,
            'context_source': 'retrospective_manifest' if override is not None else 'recorded_session',
            'capture_count': len(state['captures']), 'turn_count': len(turns), 'duration_seconds': duration,
            'complete_frame_set': len(state['captures']) == 61 and {c['slot'] for c in state['captures']} == {'front', *[f'turn_{i:02}' for i in range(60)]},
            'duration_source': duration_source, 'actual_turn_span_seconds': actual_duration,
            'frames': frames, 'quality_source': 'recomputed_from_hash_verified_originals',
            'summary': {'sharpness': summary([q['sharpness'] for q in qualities]),
                        'head_height_fraction': summary([q.get('head_height_fraction') for q in qualities]),
                        'flagged_turns': sum(bool(q['flags']) for q in qualities), 'assessed_turns': len(qualities),
                        'artifact_failures': sum(bool(f['error']) for f in frames)},
            'camera_configs': [json.loads(c) for c in sorted(camera_configs)],
            'reconstruction': {'registered_fraction': diagnostics.get('registered_fraction'),
                               'processing_seconds': diagnostics.get('processing_seconds'),
                               'mesh': diagnostics.get('mesh'), 'config': reconstruction_fingerprint(folder, result),
                               'surface_completeness': 'manual_ear_nose_chin_review_required'},
            'independent_check': check, 'failure': state.get('error')}


def comparison_report(root, identities, overrides=None):
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate sessions cannot count as repeated captures.')
    rows = [session_report(root, i, (overrides or {}).get(i)) for i in identities]
    reasons = []
    conditions = {(r['context']['group'], r['context']['conditions']) for r in rows if r['context']}
    if len(conditions) != 1 or any(not r['context'] or not r['context']['group'] or not r['context']['conditions'] for r in rows):
        reasons.append('Missing or different comparison group/conditions; do not assume captures are controlled.')
    fingerprints = {r['reconstruction']['config']['sha256'] for r in rows if r['reconstruction']['config']}
    if len(fingerprints) != 1 or any(r['reconstruction']['config'] is None for r in rows):
        reasons.append('Matching reconstruction configurations have not been established for all captures.')
    configs = {json.dumps(r['camera_configs'], sort_keys=True) for r in rows}
    if len(configs) != 1 or any(len(r['camera_configs']) != 1 for r in rows):
        reasons.append('Camera settings differ or changed within a capture; inspect camera provenance.')
    if any(set(c['manual_locks']) != {'focus', 'exposure', 'white_balance'}
           for r in rows for c in r['camera_configs']):
        reasons.append('Focus, exposure and white balance were not all verified as manually locked; automatic setting changes cannot be ruled out from matching reported camera settings.')
    if any(r['summary']['artifact_failures'] or not r['complete_frame_set'] for r in rows):
        reasons.append('Missing, corrupt or incomplete capture data; originals have not been excluded or replaced.')
    groups = {}
    for duration in (10, 20, 30):
        members = [r for r in rows if r['duration_seconds'] == duration]
        repeats = [r['context']['repeat'] for r in members if r['context']]
        if len(members) < 2 or len(set(repeats)) != len(members):
            reasons.append(f'{duration}s needs at least two distinct, labeled repeated captures.')
        groups[str(duration)] = {'sessions': [r['session_id'] for r in members],
                                 'median_frame_sharpness_across_repeats': summary([r['summary']['sharpness']['median'] for r in members]),
                                 'flagged_turns': summary([r['summary']['flagged_turns'] for r in members]),
                                 'registered_fraction': summary([r['reconstruction']['registered_fraction'] for r in members]),
                                 'processing_seconds': summary([r['reconstruction']['processing_seconds'] for r in members]),
                                 'independent_check_mesh_length_mm': summary([(r['independent_check'] or {}).get('mesh_length_mm') for r in members]),
                                 'independent_check_discrepancy_mm': summary([(r['independent_check'] or {}).get('discrepancy_mm') for r in members])}
    return {'version': 'webcam_capture_comparison_v1', 'policy': POLICY, 'sessions': rows, 'durations': groups,
            'comparison_limitations': reasons,
            'recommendation': {'decision': 'retain_10_second_default_pending_evaluation',
                               'reason': 'Insufficient controlled comparison.' if reasons else 'Review surface completeness, detail retention and physical checks before changing the default.'},
            'accuracy_status': 'not_validated', 'repeatability_status': 'image_and_available_check_arc_summaries_only_no_aligned_3d_repeatability',
            'originals_modified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--sessions', nargs='+')
    source.add_argument('--group', help='Read all local sessions labeled with this comparison group')
    parser.add_argument('--output', type=Path, required=True, help='JSON under .private-webcam-runs')
    parser.add_argument('--conditions-manifest', type=Path, help='Optional JSON mapping session IDs to group, conditions, repeat')
    args = parser.parse_args()
    identities = args.sessions
    if args.group is not None:
        identities = []
        for folder in sorted(ROOT.iterdir()):
            if folder.is_dir() and not folder.is_symlink() and re.fullmatch(r'[a-f0-9]{32}', folder.name):
                state = json.loads((folder/'session.json').read_text())
                if (state.get('capture_context') or {}).get('group') == args.group:
                    identities.append(folder.name)
        if not identities:
            raise SystemExit('No sessions found for that comparison group.')
    output = args.output.resolve(); output.relative_to(ROOT.resolve())
    if any(output.is_relative_to((ROOT/i).resolve()) for i in identities):
        raise SystemExit('Write reports outside source session directories to preserve their artifacts.')
    overrides = json.loads(args.conditions_manifest.read_text()) if args.conditions_manifest else None
    report = comparison_report(ROOT, identities, overrides)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'output': str(output), 'sessions': len(report['sessions']), 'recommendation': report['recommendation'], 'limitations': report['comparison_limitations']}, indent=2))


if __name__ == '__main__':
    main()
