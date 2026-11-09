import unittest
import numpy as np
import trimesh
from dimension_pipeline.all_photo_evaluate import triangulate_bounded, project_all, observation_gate, attach_batched
from dimension_pipeline.realdenseface_local import initial_bbox


class AllPhotoTests(unittest.TestCase):
    def cameras(self):
        return [dict(R=np.eye(3).tolist(),t=[x,0,4.],fx=800.,fy=800.,cx=500.,cy=400.,k=-.04,width=1000,height=800) for x in (-1.,-.3,.3,1.,1.3)]

    def test_bounded_triangulation_ignores_missing_and_bad_observations(self):
        cams=self.cameras();point=np.array([.1,-.2,.3]);xy=project_all(cams,point)[0][:,None,:]
        xy[-1,0]+=[80,60]
        result=triangulate_bounded(cams,xy)[0]
        self.assertEqual(result['status'],'consistent')
        np.testing.assert_allclose(result['point'],point,atol=1e-7)
        self.assertNotIn(4,result['inlier_views'])
        xy[0]=np.nan
        result=triangulate_bounded(cams,xy)[0]
        self.assertEqual(result['status'],'consistent')

    def test_unseen_network_crop_is_rejected_even_when_neck_is_in_photo(self):
        xy=np.array([[50.,80.],[50.,50.],[150.,50.]])
        inside,crop,mask=observation_gate(xy,[20,20,80,70],100,100,np.ones((100,100),bool))
        self.assertEqual(inside.tolist(),[True,True,False])
        self.assertEqual(crop.tolist(),[False,True,False])
        self.assertEqual(mask.tolist(),[True,True,False])

    def test_explicit_mask_box_and_landmark_box_are_checked(self):
        np.testing.assert_array_equal(initial_bbox({'initial_bbox_pixels':[10,20,80,90]},100,100),[10,20,80,90])
        with self.assertRaises(ValueError):initial_bbox({'initial_bbox_pixels':[80,20,10,90]},100,100)

    def test_batched_surface_visibility_rejects_hidden_back_plane(self):
        mesh=trimesh.Trimesh(vertices=[[-1,-1,0],[1,-1,0],[0,1,0],[-1,-1,1],[1,-1,1],[0,1,1]],faces=[[0,1,2],[3,4,5]],process=False)
        cams=self.cameras()[:3]
        for z,status in [(0.,'supported'),(1.,'insufficient_visible_surface_views')]:
            q=np.array([0.,0.,z]);obs=project_all(cams,q)[0][:,None,:]
            records=[{'status':'consistent','point':q.tolist(),'inlier_views':[0,1,2]}]
            attach_batched(mesh,records,cams,obs,1.,np.ones(2,bool))
            self.assertEqual(records[0]['status'],status)
