import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from dimension_pipeline.capture_quality import POLICY, capture_quality, capture_context
from dimension_pipeline.capture_quality_report import comparison_report, session_report

REPO = Path(__file__).resolve().parents[3]


class CaptureQualityTests(unittest.TestCase):
    def test_capture_mode_labels_validate_and_persist(self):
        self.assertNotIn('capture_mode',capture_context({'group':'legacy'}))
        with self.assertRaises(ValueError):capture_context({'capture_mode':'unknown'})
        with tempfile.TemporaryDirectory() as temp:
            from dimension_pipeline.webcam_pilot import Store
            store=Store(temp);state=store.create({'capture_context':{'group':'camera-motion','capture_mode':'moving_camera'}})
            self.assertEqual(store.load(state['id'])['capture_context']['capture_mode'],'moving_camera')
            two=store.create({'capture_context':{'capture_mode':'moving_camera_two_pass'}})
            self.assertEqual(store.load(two['id'])['capture_context']['capture_mode'],'moving_camera_two_pass')

    def fixture(self):
        y, x = np.mgrid[:96, :120]
        pattern = np.where((x//3+y//3) % 2, 220, 40).astype('uint8')
        image = Image.fromarray(np.stack([pattern, pattern, pattern], axis=2))
        mask = Image.new('L', image.size); mask.paste(255, (10, 10, 110, 86))
        return image, mask

    def test_blur_reduces_sharpness_without_changing_input_or_excluding_frames(self):
        image, mask = self.fixture(); original = image.tobytes()
        sharp = capture_quality(image, mask); blurred = capture_quality(image.filter(ImageFilter.GaussianBlur(3)), mask)
        self.assertGreater(sharp['sharpness'], blurred['sharpness']*10)
        self.assertIn('low_sharpness_or_low_texture', blurred['flags'])
        self.assertFalse(sharp['policy']['automatic_exclusion']); self.assertEqual(image.tobytes(), original)

    @unittest.skipUnless(shutil.which('node'), 'Node required for browser/Python parity check')
    def test_python_and_browser_metrics_agree_including_downsampling(self):
        image, mask = self.fixture(); image = image.resize((540, 432)); mask = mask.resize(image.size, Image.Resampling.NEAREST)
        code = """
const fs=require('node:fs'),vm=require('node:vm');const input=JSON.parse(fs.readFileSync(0,'utf8'));
const context={qualityPolicy:input.policy};vm.runInNewContext(fs.readFileSync('app/javascript/webcam_capture_quality.js','utf8').replace(/^import .*;\\n/gm,'').replaceAll('export ',''),context);
process.stdout.write(JSON.stringify(context.captureQuality(input.image,input.mask)));
"""
        def rgba(pixels):
            return {'width': pixels.width, 'height': pixels.height, 'data': np.asarray(pixels.convert('RGBA')).reshape(-1).tolist()}
        output = subprocess.run(['node', '-e', code], cwd=REPO, input=json.dumps({'image': rgba(image), 'mask': rgba(mask), 'policy': POLICY}), text=True, capture_output=True, check=True)
        browser = json.loads(output.stdout); python = capture_quality(image, mask)
        self.assertAlmostEqual(browser.pop('sharpness'), python.pop('sharpness'), places=5)
        self.assertEqual(browser, python)

    def test_context_validation_and_empty_masks(self):
        image, _ = self.fixture()
        self.assertEqual(capture_quality(image, Image.new('L', image.size))['status'], 'unavailable')
        with self.assertRaises(ValueError):
            capture_context({'repeat': 0})

    def test_report_preserves_originals_and_does_not_invent_missing_duration_repeats(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); identity = 'a'*32; folder = root/identity; folder.mkdir()
            image, mask = self.fixture(); image.save(folder/'image.png'); mask.save(folder/'mask.png')
            image_hash = hashlib.sha256((folder/'image.png').read_bytes()).hexdigest()
            row = {'slot': 'turn_00', 'role': 'reconstruction', 'timestamp': '2026-11-04T00:00:00Z', 'image': 'image.png', 'mask': 'mask.png', 'sha256': image_hash, 'mask_sha256': hashlib.sha256((folder/'mask.png').read_bytes()).hexdigest()}
            state = {'status': 'capturing', 'captures': [row], 'capture_context': None, 'result': None}
            (folder/'session.json').write_text(json.dumps(state)); before = (folder/'session.json').read_bytes()
            report = comparison_report(root, [identity])
            self.assertIsNone(report['sessions'][0]['duration_seconds'])
            self.assertEqual(report['durations']['20']['sessions'], [])
            self.assertEqual(report['recommendation']['decision'], 'retain_10_second_default_pending_evaluation')
            self.assertTrue(report['comparison_limitations']); self.assertEqual((folder/'session.json').read_bytes(), before)
            self.assertEqual(hashlib.sha256((folder/'image.png').read_bytes()).hexdigest(), image_hash)
            with self.assertRaises(ValueError):
                comparison_report(root, [identity, identity])
            with self.assertRaises(ValueError):
                session_report(root, '../outside')
            (folder/'image.png').write_bytes(b'corrupt')
            self.assertEqual(session_report(root, identity)['summary']['artifact_failures'], 1)

    def test_report_groups_recorded_sweeps_and_marks_legacy_duration_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); identities = []
            image, mask = self.fixture()
            for duration in (10, 20, 30):
                for repeat in (1, 2):
                    identity = f'{duration*10+repeat:032x}'; identities.append(identity)
                    folder = root/identity; folder.mkdir(); image.save(folder/'image.png'); mask.save(folder/'mask.png')
                    base = {'image': 'image.png', 'mask': 'mask.png', 'sha256': hashlib.sha256((folder/'image.png').read_bytes()).hexdigest(),
                            'mask_sha256': hashlib.sha256((folder/'mask.png').read_bytes()).hexdigest(), 'camera_settings': {'width': 120, 'height': 96, 'frameRate': 30}}
                    rows = []
                    for i in range(60):
                        rows.append({**base, 'slot': f'turn_{i:02}', 'role': 'reconstruction',
                                     'timestamp': (datetime(2026, 11, 4, tzinfo=timezone.utc)+timedelta(seconds=i*duration/59)).isoformat(),
                                     'capture_sequence': None if (duration, repeat) == (10, 1) else {'id': identity, 'duration_ms': duration*1000}})
                    rows.append({**base, 'slot': 'front', 'role': 'frontal', 'timestamp': rows[0]['timestamp']})
                    state = {'status': 'capturing', 'result': None, 'captures': rows,
                             'capture_context': {'group': 'fixed-desk', 'conditions': 'test fixture', 'repeat': repeat}}
                    (folder/'session.json').write_text(json.dumps(state))
            report = comparison_report(root, identities)
            self.assertTrue(all(len(g['sessions']) == 2 for g in report['durations'].values()))
            self.assertEqual(report['sessions'][0]['duration_source'], 'inferred_from_legacy_timestamps')
            self.assertEqual(report['sessions'][2]['duration_source'], 'recorded_sequence')
            self.assertTrue(all(row['complete_frame_set'] for row in report['sessions']))
            self.assertTrue(any('reconstruction configurations' in reason for reason in report['comparison_limitations']))
            self.assertTrue(any('automatic setting changes cannot be ruled out' in reason for reason in report['comparison_limitations']))
            self.assertFalse(any('needs at least two' in reason for reason in report['comparison_limitations']))
            self.assertEqual(report['accuracy_status'], 'not_validated')


if __name__ == '__main__':
    unittest.main()
