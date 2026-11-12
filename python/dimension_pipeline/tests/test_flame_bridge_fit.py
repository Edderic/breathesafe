import unittest
import numpy as np
import trimesh
from dimension_pipeline.flame_bridge_fit import bridge_region, fixed_metric, nose_measurements


class BridgeFitTests(unittest.TestCase):
    def fixture(self):
        mesh=trimesh.creation.icosphere(subdivisions=4)
        def anchor(position):
            i=int(np.argmin(np.linalg.norm(mesh.vertices-position,axis=1)))
            return {'attachment':{'kind':'vertex','vertex_index':i},'status':'pending'}
        return mesh,{'sellion':anchor([0,.5,.866]),'pronasale':anchor([0,-.2,.98]),'subnasale':anchor([0,-.4,.916])}

    def test_region_and_weights_are_unit_invariant(self):
        mesh,anchors=self.fixture();ids=np.arange(len(mesh.vertices))
        weights,core,policy=bridge_region(mesh,mesh,ids,anchors,2.,[])
        scaled=mesh.copy();scaled.vertices*=7
        w2,c2,_=bridge_region(scaled,scaled,ids,anchors,14.,[])
        np.testing.assert_allclose(weights,w2,atol=1e-12);np.testing.assert_array_equal(core,c2)
        self.assertGreater(len(core),8);self.assertTrue(np.all((weights>=0)&(weights<=1)))
        self.assertEqual(policy['anchor_statuses']['sellion'],'pending')

    def test_exclusion_and_missing_surface_support_override_weights(self):
        mesh,anchors=self.fixture();ids=np.arange(len(mesh.vertices))
        with self.assertRaisesRegex(ValueError,'Insufficient bridge'):
            bridge_region(mesh,mesh,ids,anchors,2.,[{'center':[0,0,0],'radius':10}])
        distant=mesh.copy();distant.vertices+=[10,0,0]
        with self.assertRaisesRegex(ValueError,'Insufficient bridge'):
            bridge_region(mesh,distant,ids,anchors,2.,[])

    def test_distance_and_forward_projection_are_distinct_and_translation_invariant(self):
        mesh=trimesh.Trimesh([[0,0,0],[0,3,4],[1,0,0]],[[0,1,2]],process=False)
        anchors={name:{'attachment':{'kind':'vertex','vertex_index':i}} for name,i in [('subnasale',0),('pronasale',1)]}
        values=nose_measurements(mesh,anchors,np.array([0,0,1]))
        self.assertEqual(values['subnasale_pronasale_anchor_distance'],5)
        self.assertEqual(values['forward_tip_projection_from_subnasale'],4)
        mesh.vertices+=[4,8,15]
        shifted=nose_measurements(mesh,anchors,np.array([0,0,1]))
        self.assertEqual(values['subnasale_pronasale_anchor_distance'],shifted['subnasale_pronasale_anchor_distance'])

    def test_fixed_metric_does_not_hide_vertices_entering_exclusion(self):
        mesh=trimesh.creation.icosphere(subdivisions=1);ids=np.arange(len(mesh.vertices))
        row=fixed_metric(mesh,ids,mesh,2.,[{'center':[0,0,0],'radius':10}],np.array([0,0,1]))
        self.assertEqual(row['vertices'],len(ids));self.assertEqual(row['moved_inside_exclusion'],len(ids))


if __name__=='__main__':unittest.main()
