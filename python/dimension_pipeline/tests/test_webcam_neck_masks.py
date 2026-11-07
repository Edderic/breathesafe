import unittest
import numpy as np
from dimension_pipeline.webcam_neck_masks import expand_mask


class NeckMaskTests(unittest.TestCase):
    def test_preserves_original_and_only_adds_connected_bounded_body_skin(self):
        original=np.zeros((100,100),dtype=np.uint8);original[10:70,20:80]=255
        categories=np.zeros_like(original)
        categories[60:90,40:60]=2  # Attached neck extends beyond permitted depth.
        categories[75:78,24:28]=2  # Disconnected skin must not join.
        categories[60:75,5:15]=2  # Outside horizontal bounds.
        categories[60:80,65:70]=4  # Clothes must not join.
        expanded,info=expand_mask(original,categories)
        self.assertTrue(np.all(expanded[original>0]==255))
        self.assertTrue(np.all(expanded[70:79,40:60]==255))
        self.assertFalse(expanded[79:].any())
        self.assertFalse(expanded[75:78,24:28].any())
        self.assertFalse(expanded[70:75,65:70].any())
        self.assertEqual(info['added_pixels'],9*20)
        self.assertEqual(set(np.unique(expanded)),{0,255})

    def test_empty_or_mismatched_masks_fail(self):
        with self.assertRaises(ValueError):expand_mask(np.zeros((5,5)),np.zeros((5,5)))
        with self.assertRaises(ValueError):expand_mask(np.ones((5,5))*255,np.zeros((6,5)))


if __name__=='__main__':unittest.main()
