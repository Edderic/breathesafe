import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('cohort', Path(__file__).parents[1]/'presentations/build_paired_cohort.py')
cohort = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cohort)


class CohortTests(unittest.TestCase):
    def test_age_bands_and_broad_gender(self):
        self.assertEqual(cohort.age_band('2023'), '0–5')
        self.assertEqual(cohort.age_band('2015'), '6–17')
        self.assertEqual(cohort.age_band(None), 'Not reported')
        self.assertEqual(cohort.gender_group('MTF transgender'), 'Female')

    def test_stable_random_pseudonyms_preserve_counts_without_identifiers(self):
        rows = []
        for user, (tests, positives) in enumerate(zip([166, 130, 36, 36, 36, 15, 2], [85, 0, 7, 8, 3, 11, 1]), 100):
            for i in range(tests):
                rows.append(dict(user_id=user, fit_test_id=user*1000+i, mask_id=1, label=int(i < positives)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, demographics, lookup, output = [root/name for name in ['p.json', 'd.json', 'private.json', 'out.json']]
            predictions.write_text(json.dumps([{'arms': {'traditional_direct': rows, 'production_arkit': rows}}]))
            demographics.write_text(json.dumps([dict(user_id=u, year_of_birth='1990', gender_and_sex='Cisgender male',
                                                       race_ethnicity='Not reported') for u in range(100, 107)]))
            cohort.build(predictions, demographics, lookup, output)
            first = json.loads(output.read_text())
            cohort.build(predictions, demographics, lookup, output)
            self.assertEqual(first, json.loads(output.read_text()))
            self.assertEqual(sum(r['test_count'] for r in first['participants']), 421)
            self.assertEqual(sum(r['positive_labels'] for r in first['participants']), 115)
            self.assertEqual(len({r['study_uuid'] for r in first['participants']}), 7)
            for row in first['participants']:
                self.assertNotIn('user_id', row)
                self.assertNotIn('year_of_birth', row)
                self.assertNotIn('name', row)
                self.assertNotIn(row['study_uuid'], [str(u) for u in range(100, 107)])
            corrections = root/'corrections.json'
            correction = dict(study_uuid=first['participants'][0]['study_uuid'], gender_group='Female',
                              reason='Participant correction')
            corrections.write_text(json.dumps([correction]))
            cohort.build(predictions, demographics, lookup, output, corrections)
            corrected = json.loads(output.read_text())
            self.assertEqual(corrected['participants'][0]['gender_group'], 'Female')
            self.assertEqual(corrected['participants'][1:], first['participants'][1:])
            self.assertEqual(corrected['participant_corrections'], [correction])


if __name__ == '__main__':
    unittest.main()
