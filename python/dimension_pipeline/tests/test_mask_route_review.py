import unittest
import numpy as np
from dimension_pipeline.mask_route_review import similarity,sample_polyline


class MaskRouteReviewTests(unittest.TestCase):
    def test_similarity_recovers_camera_frame_without_reflection(self):
        rng=np.random.default_rng(10);x=rng.normal(size=(30,3));rotation=np.array([[0,-1,0],[1,0,0],[0,0,1.]])
        target=1.4*x@rotation.T+[3.,-2.,1.]
        s,r,t,error=similarity(x,target)
        self.assertAlmostEqual(s,1.4);np.testing.assert_allclose(r,rotation,atol=1e-12)
        np.testing.assert_allclose(t,[3,-2,1],atol=1e-12);self.assertLess(error.max(),1e-12)
        self.assertGreater(np.linalg.det(r),.999)

    def test_polyline_samples_preserve_length_without_extra_connections(self):
        p,w=sample_polyline([[0,0,0],[.2,0,0],[.2,.15,0]],.04)
        self.assertAlmostEqual(w.sum(),.35)
        self.assertLessEqual(w.max(),.04)
        self.assertTrue(np.all((np.abs(p[:,1])<1e-12)|(np.abs(p[:,0]-.2)<1e-12)))
        q,v=sample_polyline([[4,0,0]],.04)
        self.assertEqual(len(q),0);self.assertEqual(len(v),0)

    def test_source_coverage_requires_three_masked_visible_views(self):
        import trimesh
        from scipy.spatial import cKDTree
        from dimension_pipeline.mask_route_review import source_coverage
        mesh=trimesh.Trimesh(vertices=[[-1,-1,0],[1,-1,0],[0,1,0]],faces=[[0,1,2]],process=False)
        cameras=[{'R':np.eye(3).tolist(),'t':[x,0,4],'fx':200.,'fy':200.,'cx':300.,'cy':200.,'width':600,'height':400,'k':0.} for x in (-.6,0,.6)]
        p=np.array([[0.,0.,0.]])
        masks=[np.ones((400,600),bool) for _ in cameras]
        result=source_coverage(p,cameras,masks,mesh,mesh,cKDTree(p),1.)[0]
        self.assertTrue(result['supported']);self.assertEqual(len(result['witness_views']),3)
        masks[-1][:]=False
        self.assertFalse(source_coverage(p,cameras,masks,mesh,mesh,cKDTree(p),1.)[0]['supported'])

    def test_new_surface_without_raw_depth_agreement_is_not_supported(self):
        import trimesh
        from scipy.spatial import cKDTree
        from dimension_pipeline.mask_route_review import source_coverage
        raw=trimesh.Trimesh(vertices=[[-1,-1,0],[1,-1,0],[0,1,0]],faces=[[0,1,2]],process=False)
        candidate=raw.copy();candidate.vertices[:,2]+=1
        cameras=[{'R':np.eye(3).tolist(),'t':[x,0,4],'fx':200.,'fy':200.,'cx':300.,'cy':200.,'width':600,'height':400,'k':0.} for x in (-.6,0,.6)]
        p=np.array([[0.,0.,1.]])
        result=source_coverage(p,cameras,[np.ones((400,600),bool) for _ in cameras],candidate,raw,cKDTree(p),1.)[0]
        self.assertFalse(result['supported'])
