import unittest
import numpy as np
from dimension_pipeline.gaussian_volume import implicit_grid, filtered_field, extract


class GaussianVolumeTests(unittest.TestCase):
    def test_normalized_filter_preserves_constant_field_at_unknown_boundary(self):
        field=np.full((20,20,20),.25,dtype=np.float32)
        weight=np.zeros_like(field);weight[5:15,5:15,5:15]=1
        result,support=filtered_field(field,weight,2.)
        np.testing.assert_allclose(result[support>.01],.25,atol=1e-6)

    def test_plane_stays_within_five_percent_of_voxel(self):
        x,y=np.meshgrid(np.linspace(-1,1,35),np.linspace(-1,1,35))
        points=np.c_[x.ravel(),y.ravel(),np.zeros(x.size)]
        normals=np.tile([0,0,1.],(len(points),1))
        f,w,d,origin,step=implicit_grid(points,normals,1.,40,.03)
        blurred,density=filtered_field(f,w,.03/step)
        mesh=extract(blurred,(density>.25)&(d<.1),origin,step)
        self.assertGreater(len(mesh.faces),100)
        self.assertLess(np.abs(mesh.vertices[:,2]).max(),step*.05)

    def test_zero_sigma_is_an_independent_copy(self):
        f=np.arange(27,dtype=np.float32).reshape(3,3,3);w=np.ones_like(f)
        result,support=filtered_field(f,w,0)
        np.testing.assert_array_equal(result,f)
        result[0,0,0]=99
        self.assertEqual(f[0,0,0],0)

    def test_grid_budget_checked_before_allocation(self):
        with self.assertRaisesRegex(ValueError,'budget'):
            implicit_grid(np.array([[0,0,0],[1,1,1]]),np.array([[0,0,1],[0,0,1]]),1.,200,.03,max_voxels=100)

    def test_extraction_does_not_keep_triangles_in_unknown_columns(self):
        field=np.broadcast_to(np.arange(12,dtype=np.float32)[None,None,:]-5.5,(12,12,12)).copy()
        mask=np.ones_like(field,dtype=bool);mask[:5]=False
        mesh=extract(field,mask,np.zeros(3),1.)
        self.assertGreaterEqual(mesh.vertices[:,0].min(),5.)
        self.assertLess(np.abs(mesh.vertices[:,2]-5.5).max(),1e-6)
