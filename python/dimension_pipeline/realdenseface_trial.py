"""Prepare a local, hash-verified photo bundle; never launches or uploads to AWS."""
import argparse
import json
import shutil
from pathlib import Path

from .flame_photo_fit import HOLDOUT, TRAIN, digest

SOURCE_COMMIT = '7d855a29931c95cc9016f75d49cead60adbcf0a3'


def prepare(session, report_path, out):
    session, out = Path(session).resolve(), Path(out).resolve()
    report = json.loads(Path(report_path).read_text())
    if report['version'] != 'flame_direct_photo_v1' or report['session_id'] != session.name:
        raise ValueError('Expected a direct-photo report from this session')
    expected = {s: 'train' for s in TRAIN} | {s: 'held_out_shape' for s in HOLDOUT}
    rows = report['views']
    if len(rows) != len(expected) or {v['slot']: v['split'] for v in rows} != expected:
        raise ValueError('Unexpected or overlapping photo split')
    # Validate the complete selection before creating anything.
    for row in rows:
        path = session/(row['slot']+'.png')
        if digest(path) != row['sha256']:
            raise ValueError('Capture hash changed: '+row['slot'])
    out.mkdir(parents=True, exist_ok=False)
    manifest = {'version': 'realdenseface_trial_v1', 'source_commit': SOURCE_COMMIT,
                'session_id': session.name, 'status': 'local_preparation_only',
                'baseline_report_sha256': digest(report_path), 'photos': [],
                'protocol': 'Fit shared identity from train only; freeze it for hold-out camera/expression estimation. Default offline tracker alone does not implement this hold-out protocol.'}
    for row in rows:
        split = 'train' if row['split'] == 'train' else 'holdout'
        folder = out/split
        folder.mkdir(exist_ok=True)
        destination = folder/(row['slot']+'.png')
        shutil.copyfile(session/destination.name, destination)
        manifest['photos'].append({'slot': row['slot'], 'split': split,
                                   'path': str(destination.relative_to(out)), 'sha256': digest(destination)})
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', required=True)
    parser.add_argument('--baseline-report', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    prepare(args.session, args.baseline_report, args.out)
    print(Path(args.out).resolve()/'manifest.json')


if __name__ == '__main__':
    main()
