"""Build a pseudonymous paired-cohort table; identity lookup remains in ignored tmp."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import uuid


def age_band(year, reference=2026):
    try:
        age = reference-int(year)
    except (TypeError, ValueError):
        return 'Not reported'
    for lower, upper in [(0, 5), (6, 17), (18, 29), (30, 39), (40, 49), (50, 64), (65, 120)]:
        if lower <= age <= upper:
            return f'{lower}–{upper}' if upper < 120 else '65+'
    return 'Not reported'


def gender_group(value):
    return {'Cisgender male': 'Male', 'Cisgender female': 'Female',
            'MTF transgender': 'Female', 'FTM transgender': 'Male'}.get(value, 'Other / not reported')


def build(predictions_path, demographics_path, lookup_path, output, corrections_path=None):
    runs = json.loads(predictions_path.read_text())
    rows = runs[0]['arms']['traditional_direct']
    keys = lambda values: sorted((r['user_id'], r['fit_test_id'], r['mask_id'], r['label']) for r in values)
    for run in runs:
        for values in run['arms'].values():
            assert keys(values) == keys(rows), 'Participant/test cohort differs'
    counts = Counter(r['user_id'] for r in rows)
    positives = Counter(r['user_id'] for r in rows if r['label'] == 1)
    assert len(counts) == 7 and len(rows) == 421 and sum(positives.values()) == 115
    demographics = {r['user_id']: r for r in json.loads(demographics_path.read_text())}
    lookup = json.loads(lookup_path.read_text()) if lookup_path.exists() else {}
    for user in counts:
        lookup.setdefault(str(user), str(uuid.uuid4()))
    lookup_path.write_text(json.dumps(lookup, indent=2)+'\n')
    participants = []
    for user, tests in counts.items():
        profile = demographics.get(user, {})
        participants.append(dict(study_uuid=lookup[str(user)],
            age_band=age_band(profile.get('year_of_birth')),
            gender_group=gender_group(profile.get('gender_and_sex')),
            race_ethnicity=profile.get('race_ethnicity') or 'Not reported',
            test_count=tests, positive_labels=positives[user], negative_labels=tests-positives[user]))
    participants.sort(key=lambda p: (-p['test_count'], p['study_uuid']))
    assert len({r['study_uuid'][:8] for r in participants}) == 7
    corrections = json.loads(corrections_path.read_text()) if corrections_path and corrections_path.exists() else []
    by_uuid = {p['study_uuid']: p for p in participants}
    for correction in corrections:
        assert correction['study_uuid'] in by_uuid, 'Correction references an unknown study participant'
        assert correction['gender_group'] in ('Male', 'Female', 'Other / not reported')
        by_uuid[correction['study_uuid']]['gender_group'] = correction['gender_group']
    result = dict(people=7, tests=421, positive_labels=115, negative_labels=306,
        demographic_snapshot='Local profile snapshot, November 14, 2026',
        age_definition='Approximate age band in 2026 from reported birth year, not age at measurement or fit test.',
        identifier_definition='Random study UUIDs, unrelated to database IDs; eight-character prefixes displayed. Identity lookup stays in ignored local tmp.',
        gender_definition='Broadly grouped reported gender categories; cis/trans status is not displayed.',
        participant_corrections=corrections,
        count_definition='Same 421 held-out analyzed observations as slide 10, including repeat person-mask tests and mixed label sources; three model seeds do not triple counts.',
        participants=participants,
        source_hashes={name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for name, path in [('predictions', predictions_path), ('demographics', demographics_path)]})
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print('Saved seven pseudonymous participant rows; no names, database IDs, contact details or exact birth years exported.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--demographics', type=Path, required=True)
    parser.add_argument('--lookup', type=Path, default=Path('tmp/private-paired-cohort-uuid-lookup.json'))
    parser.add_argument('--output', type=Path, default=Path('prompts/2026-11-17-nasem/paired-cohort-evidence.json'))
    parser.add_argument('--corrections', type=Path, default=Path('prompts/2026-11-17-nasem/paired-cohort-corrections.json'))
    args = parser.parse_args()
    build(args.predictions, args.demographics, args.lookup, args.output, args.corrections)
