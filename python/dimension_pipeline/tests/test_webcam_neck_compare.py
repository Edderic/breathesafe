import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from dimension_pipeline.webcam_neck_compare import align_cameras


class NeckCompareTests(unittest.TestCase):
    def fixtures(self):
        rng=np.random.default_rng(25);rotation=Rotation.from_rotvec([.2,-.3,.1]).as_matrix()
        scale=2.7;translation=np.array([1.,-2.,.5]);old={};new={}
        for i,center in enumerate(rng.normal(size=(60,3))):
            key='registered:turn_'+str(i).zfill(2)+'.png';mapped=scale*rotation@center+translation
            old[key]={'R':np.eye(3).tolist(),'t':(-mapped).tolist()}
            new[key]={'R':rotation.tolist(),'t':(-rotation@center).tolist()}
        return {'result':{'cameras':old}},{'result':{'cameras':new}},scale,rotation,translation

    def test_recovers_camera_gauge_without_fitting_surface_or_arcs(self):
        old,new,s,r,t=self.fixtures();scale,rotation,translation,report=align_cameras(old,new,1.)
        self.assertAlmostEqual(s,scale);np.testing.assert_allclose(r,rotation,atol=1e-12)
        np.testing.assert_allclose(t,translation,atol=1e-12)
        self.assertLess(report['camera_center_rms'],1e-12)
        self.assertLess(report['median_orientation_difference_degrees'],1e-10)

    def test_missing_registered_views_and_poor_alignment_fail(self):
        old,new,*_=self.fixtures()
        few={'result':{'cameras':dict(list(new['result']['cameras'].items())[:5])}}
        with self.assertRaisesRegex(ValueError,'54 matching'):align_cameras(old,few,1.)
        for i,c in enumerate(new['result']['cameras'].values()):c['t'][0]+=(-1)**i*3
        with self.assertRaisesRegex(ValueError,'alignment RMS'):align_cameras(old,new,1.)


if __name__=='__main__':unittest.main()
