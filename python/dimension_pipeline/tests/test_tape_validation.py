import unittest
from dimension_pipeline.tape_validation import compare_lengths


class TapeValidationTests(unittest.TestCase):
    def test_independent_tape_check_never_changes_scale(self):
        first=compare_lengths(4.,6.,[288.,280.,284.],[380.,390.,380.])
        other=compare_lengths(4.,6.,[288.,280.,284.],[500.])
        self.assertEqual(first['provisional_mm_per_reconstruction_unit'],71.)
        self.assertEqual(first['estimated_perimeter_mm'],426.)
        self.assertEqual(first['signed_difference_mm'],46.)
        self.assertEqual(first['calibration_reading_sensitivity_mm'],[420.,432.])
        self.assertEqual(first['estimated_perimeter_mm'],other['estimated_perimeter_mm'])
        self.assertIsNone(first['accepted_measurement_mm'])

    def test_scaling_native_coordinates_does_not_change_estimated_millimeters(self):
        a=compare_lengths(4.,6.,[284.],[380.])
        b=compare_lengths(12.,18.,[284.],[380.])
        self.assertAlmostEqual(a['estimated_perimeter_mm'],b['estimated_perimeter_mm'])

    def test_invalid_measurements_fail(self):
        for calibration,perimeter,readings,check in [(0,6,[284],[380]),(4,float('nan'),[284],[380]),
                (4,6,[],[380]),(4,6,[284],[]),(4,6,[-1],[380]),(4,6,[284],[float('inf')])]:
            with self.assertRaises(ValueError):compare_lengths(calibration,perimeter,readings,check)
