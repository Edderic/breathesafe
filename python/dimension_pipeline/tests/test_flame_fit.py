import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial.transform import Rotation

from dimension_pipeline.flame_fit import fit, outside, similarity, run


class FlameFitTests(unittest.TestCase):
    def test_similarity_recovers_proper_transform(self):
        x = np.random.default_rng(4).normal(size=(40, 3))
        rotation = Rotation.from_rotvec([.3, -.5, .2]).as_matrix()
        target = 7.2*x @ rotation.T+[2., -4., 1.]
        s, r, t = similarity(x, target)
        np.testing.assert_allclose(s*x @ r.T+t, target, atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(r), 1.)
        self.assertAlmostEqual(s, 7.2)

    def test_exclusion_and_shape_fit_keep_world_units(self):
        mesh = trimesh.creation.icosphere(subdivisions=2)
        template = mesh.vertices.copy()
        template *= [1., 1.2, .8]
        basis = np.zeros((len(template),3,300))
        basis[:,2,0] = template[:,2]*.08
        target = trimesh.Trimesh(template+basis[:,:,0]*.7,mesh.faces,process=False)
        initial = (1.03,np.eye(3),np.array([.01,-.01,.01]))
        vertices, row = fit(template,basis,mesh.faces,np.arange(len(template)),target,
                            initial,2.,[],50,25,regularity=1e-8)
        self.assertEqual(len(row['shape_coefficients']),300)
        self.assertTrue(np.isfinite(vertices).all())
        self.assertLess(row['residual']['rms'],.004)
        self.assertLess(abs(row['shape_coefficients'][0]-.7),.12)
        self.assertTrue(np.all(np.abs(row['shape_coefficients'])<=3))
        self.assertEqual(outside(np.array([[0,0,0],[1,0,0]]),[{'center':[0,0,0],'radius':.5}]).tolist(),[False,True])
        # A uniform change of reconstruction units must change vertices and
        # translation, not the inferred identity coefficients.
        transformed, row2 = fit(template,basis,mesh.faces,np.arange(len(template)),
                                trimesh.Trimesh(target.vertices*5,target.faces,process=False),
                                (initial[0]*5,initial[1],initial[2]*5),10.,[],50,25,regularity=1e-8)
        # Closest triangles can tie on the symmetric fixture; tolerate 1e-5
        # of its scaled diameter while still catching unit/translation errors.
        np.testing.assert_allclose(transformed,vertices*5,atol=1e-4)
        np.testing.assert_allclose(row2['shape_coefficients'],row['shape_coefficients'],atol=1e-4)

    def test_rejects_missing_coverage(self):
        mesh=trimesh.creation.icosphere(subdivisions=2)
        with self.assertRaisesRegex(ValueError,'Insufficient'):
            fit(mesh.vertices,np.zeros((len(mesh.vertices),3,300)),mesh.faces,
                np.arange(len(mesh.vertices)),mesh,(1.,np.eye(3),np.zeros(3)),2.,
                [{'center':[0,0,0],'radius':5.}],50,2,importance=np.full(len(mesh.vertices),10.))

    def test_run_is_separate_and_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'session';folder.mkdir();out=Path(tmp)/'fit'
            state={'id':'a'*32,'result':{'surface':{'mesh':{'vertices':[[0,0,0],[1,0,0],[0,1,0]],'triangles':[[0,1,2]]}}}}
            original=json.dumps(state).encode();(folder/'session.json').write_bytes(original)
            with self.assertRaisesRegex(ValueError,'outside'):
                run(folder,'unused',folder/'nested')
            out.mkdir()
            with self.assertRaisesRegex(ValueError,'already exists'):
                run(folder,'unused',out)
            self.assertEqual((folder/'session.json').read_bytes(),original)


if __name__ == '__main__': unittest.main()
