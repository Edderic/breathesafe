import unittest
import numpy as np
import trimesh
from dimension_pipeline.gaussian_validation import forward_shift, matched_routes


class GaussianValidationTests(unittest.TestCase):
    def test_forward_direction_uses_camera_axes(self):
        camera={'R':[[0,0,1],[0,1,0],[-1,0,0]]}
        self.assertEqual(forward_shift([.2,0,0],camera),.2)
        self.assertEqual(forward_shift([0,0,.2],camera),0)

    def test_partial_routes_use_identical_supported_edges(self):
        mesh=trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0]],faces=[[0,1,2]],process=False)
        a={0:{'triangle_index':0,'weights':[1,0,0]},1:{'triangle_index':0,'weights':[0,1,0]},2:{'triangle_index':0,'weights':[0,0,1]}}
        routes=[{'name':'test','pairs':[(0,1),(1,2)]}]
        result=matched_routes({'raw':mesh,'candidate':mesh},{'raw':a,'candidate':{0:a[0],1:a[1]}},routes)[0]
        self.assertEqual(result['common_supported_edges'],1)
        self.assertEqual(result['variants']['raw']['matched_partial_mesh_edge_length'],1.)
        self.assertIsNone(result['variants']['raw']['complete_mesh_edge_length'])
        self.assertEqual(result['variants']['candidate']['mesh_edge_change_percent_vs_raw'],0.)

    def test_disconnected_route_is_unavailable_for_all_comparisons(self):
        mesh=trimesh.Trimesh(vertices=[[0,0,0],[1,0,0],[0,1,0],[4,0,0],[5,0,0],[4,1,0]],faces=[[0,1,2],[3,4,5]],process=False)
        a={0:{'triangle_index':0,'weights':[1,0,0]},1:{'triangle_index':1,'weights':[1,0,0]}}
        row=matched_routes({'raw':mesh,'candidate':mesh},{'raw':a,'candidate':a},[{'name':'gap','pairs':[(0,1)]}])[0]
        self.assertEqual(row['common_supported_edges'],0)
        self.assertIsNone(row['variants']['raw']['matched_partial_mesh_edge_length'])

    def test_threshold_audit_excludes_occluded_and_original_outlier_views(self):
        from dimension_pipeline.gaussian_point_audit import third_visible_error
        self.assertEqual(third_visible_error([1,2,3,6.4,8],[True,False,True,True,True],[False,True,True,True,True]),8)
        self.assertIsNone(third_visible_error([1,2],[True,True],[True,True]))
