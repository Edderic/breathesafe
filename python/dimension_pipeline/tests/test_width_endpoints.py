import unittest
import numpy as np
from dimension_pipeline.width_endpoints import regions, anatomical_axes, select_extremum, select_pair


class WidthEndpointTests(unittest.TestCase):
    def test_regions_exclude_ear_neck_and_nasal_midline(self):
        vertices=np.array([[.018,-.02,.05],[-.018,-.02,.05],[.07,0,-.01],[-.07,0,-.01],
            [.105,0,-.05],[.07,-.1,.02],[0,-.02,.07],[.07,.025,0]])
        patches=regions(vertices)
        self.assertEqual(set(patches),{'alar_positive_x','alar_negative_x','zygomatic_positive_x','zygomatic_negative_x'})
        for name,index in [('alar_positive_x',0),('alar_negative_x',1),('zygomatic_positive_x',2),('zygomatic_negative_x',3)]:
            self.assertEqual(patches[name].tolist(),[index])

    def test_axis_is_orthogonal_and_extremum_never_uses_failed_points(self):
        named={k:{'surface_point':v} for k,v in {'left_tragion':[1,0,0],'right_tragion':[-1,0,0],
            'sellion':[.2,1,0],'menton':[0,-1,0]}.items()}
        lateral,up=anatomical_axes(named)
        self.assertAlmostEqual(np.dot(lateral,up),0)
        records=[{'status':'supported','surface_point':[.8,0,0]},
            {'status':'too_far_from_surface','surface_point':[5,0,0]},
            {'status':'supported','surface_point':[-.9,0,0]}]
        self.assertEqual(select_extremum([0,1,2],records,lateral,1),0)
        self.assertEqual(select_extremum([0,1,2],records,lateral,-1),2)
        self.assertIsNone(select_extremum([1],records,lateral,1))

    def test_pair_selection_rejects_nonhorizontal_extreme(self):
        records=[{'status':'supported','surface_point':p} for p in [[2,1,0],[1,0,0],[-1,0,0]]]
        self.assertEqual(select_pair([0,1],[2],records,np.array([1,0,0]),np.array([0,1,0]),.1),(1,2))
        self.assertIsNone(select_pair([0],[2],records,np.array([1,0,0]),np.array([0,1,0]),.1))
