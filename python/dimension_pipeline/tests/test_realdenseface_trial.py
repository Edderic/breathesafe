import json
import tempfile
import unittest
from pathlib import Path

from dimension_pipeline.flame_photo_fit import HOLDOUT, TRAIN, digest
from dimension_pipeline.realdenseface_trial import prepare


class TrialBundleTest(unittest.TestCase):
    def test_bundle_exact_split_and_reject_changed_capture(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            session = root/'session'
            session.mkdir()
            rows = []
            for i, slot in enumerate(TRAIN+HOLDOUT):
                image = session/(slot+'.png')
                image.write_bytes(('fixture '+slot).encode())
                rows.append({'slot': slot, 'split': 'train' if slot in TRAIN else 'held_out_shape', 'sha256': digest(image)})
            report = root/'report.json'
            report.write_text(json.dumps({'version': 'flame_direct_photo_v1', 'session_id': 'session', 'views': rows}))
            manifest = prepare(session, report, root/'bundle')
            self.assertEqual(len(manifest['photos']), 13)
            self.assertEqual(len(list((root/'bundle/train').glob('*.png'))), 9)
            self.assertEqual(len(list((root/'bundle/holdout').glob('*.png'))), 4)
            (session/'front.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                prepare(session, report, root/'rejected')
            self.assertFalse((root/'rejected').exists())

    def test_reject_duplicate_or_wrong_split_before_copy(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            session = root/'session'
            session.mkdir()
            report = root/'report.json'
            report.write_text(json.dumps({'version': 'flame_direct_photo_v1', 'session_id': 'session', 'views': []}))
            with self.assertRaisesRegex(ValueError, 'split'):
                prepare(session, report, root/'rejected')
            self.assertFalse((root/'rejected').exists())
