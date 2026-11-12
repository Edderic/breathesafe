import unittest
from dimension_pipeline.tape_linear_checks import linear_check


class LinearCheckTests(unittest.TestCase):
    def test_chord_is_euclidean_and_reference_never_adjusts_scale(self):
        first=linear_check([115.5,114.6,113.9],20,[[0,0,0],[3,4,0]])
        other=linear_check([200],20,[[0,0,0],[3,4,0]])
        self.assertEqual(first['median_mm'],114.6)
        self.assertEqual(first['native_chord_length'],5)
        self.assertEqual(first['estimated_mm'],100)
        self.assertEqual(other['estimated_mm'],100)
        self.assertIsNone(first['accepted_measurement_mm'])

    def test_missing_endpoints_do_not_generate_width_estimate(self):
        result=linear_check([35,36,35],66.3)
        self.assertEqual(result['median_mm'],35)
        self.assertIsNone(result['estimated_mm'])
        self.assertIsNone(result['signed_difference_mm'])

    def test_bad_coordinates_and_readings_fail(self):
        for readings,factor,ends in [([],1,None),([35],0,None),([float('nan')],1,None),
                ([35],1,[[0,0,0],[0,0,0]]),([35],1,[[0,0,0],[float('inf'),1,2]])]:
            with self.assertRaises(ValueError):linear_check(readings,factor,ends)
