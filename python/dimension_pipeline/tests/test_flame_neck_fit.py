import unittest
import numpy as np
import trimesh
from dimension_pipeline.flame_neck_fit import clean_triangles, metric


class NeckFitTests(unittest.TestCase):
    def test_filter_preserves_closed_fine_mesh_and_discards_large_open_cap(self):
        sphere=trimesh.creation.icosphere(subdivisions=3,radius=.03)
        n=len(sphere.vertices)
        mesh=trimesh.Trimesh(np.vstack([sphere.vertices,[[2,0,0],[3,0,0],[2,.0001,0]]]),
                            np.vstack([sphere.faces,[[n,n+1,n+2]]]),process=False)
        filtered,policy=clean_triangles(mesh,1.)
        self.assertEqual(len(filtered.faces),len(sphere.faces))
        self.assertEqual(policy['long_edge_triangles'],1)
        self.assertEqual(policy['open_boundary_incident_triangles'],1)
        self.assertTrue(policy['thin_triangles']>=1)
        self.assertEqual(len(mesh.faces),len(sphere.faces)+1)

    def test_insufficient_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Insufficient'):
            clean_triangles(trimesh.creation.icosphere(subdivisions=1),1.)

    def test_common_region_metric_respects_exclusion_and_units(self):
        mesh=trimesh.creation.icosphere(subdivisions=1)
        report=metric(mesh,np.arange(len(mesh.vertices)),mesh,2.,[])
        self.assertLess(report['rms'],1e-12)
        self.assertEqual(report['vertices'],len(mesh.vertices))
        with self.assertRaisesRegex(ValueError,'No evaluable'):
            metric(mesh,np.arange(len(mesh.vertices)),mesh,2.,[{'center':[0,0,0],'radius':10}])


if __name__=='__main__':unittest.main()
