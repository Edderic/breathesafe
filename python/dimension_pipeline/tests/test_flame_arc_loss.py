import unittest

import numpy as np
import trimesh

from dimension_pipeline.flame_arc_loss import length_jacobian, supported_edges, prepare_constraints
from dimension_pipeline.flame_fit import fit


class FlameArcTests(unittest.TestCase):
    def test_length_gradient_matches_finite_difference(self):
        rng=np.random.default_rng(13)
        template=rng.normal(size=(12,3));basis=rng.normal(size=(12,3,50))*.02
        edges=np.column_stack([np.arange(11),np.arange(1,12)])
        beta=rng.normal(size=50)*.1
        length,gradient=length_jacobian(template,basis,edges,beta,2.3)
        numeric=[]
        for i in range(50):
            delta=np.eye(50)[i]*1e-5
            numeric.append((length_jacobian(template,basis,edges,beta+delta,2.3)[0]-
                            length_jacobian(template,basis,edges,beta-delta,2.3)[0])/2e-5)
        np.testing.assert_allclose(gradient,numeric,atol=1e-8)
        self.assertGreater(length,0)

    def test_no_bridge_across_missing_or_jumping_projection(self):
        points=np.column_stack([np.arange(15)*.03,np.zeros((15,2))])
        projected=points.copy();projected[10:]+=np.array([0,2,0])
        valid=np.ones(15,dtype=bool);valid[5]=False
        edges=supported_edges(points,projected,valid,1.)
        self.assertFalse(any(5 in e for e in edges))
        self.assertFalse(any(np.array_equal(e,[9,10]) for e in edges))
        self.assertTrue(len(edges)>0)

    def test_exclusion_overrides_perimeter_support(self):
        mesh=trimesh.creation.icosphere(subdivisions=2)
        points=mesh.vertices[mesh.faces[0]]
        row={'id':'p','name':'loop','style':'bifold','review_status':'pending','mirrored':False,
             'points':np.vstack([points,points[0]]),'source_ui_length':999.}
        with self.assertRaisesRegex(ValueError,'No arc coverage'):
            prepare_constraints([row],mesh,mesh,mesh.vertices,np.zeros((len(mesh.vertices),3,300)),
                                np.arange(len(mesh.vertices)),2.,[{'center':[0,0,0],'radius':10}])

    def test_arc_loss_moves_scale_and_preserves_unit_invariance(self):
        mesh=trimesh.creation.icosphere(subdivisions=2)
        template=mesh.vertices.copy();basis=np.zeros((len(template),3,300))
        edges=mesh.edges_unique[:30]
        target_length=length_jacobian(template,basis,edges,np.zeros(50),1.15)[0]
        constraint={'template':template,'basis':basis,'edges':edges,'target_length':target_length}
        def trial(factor,weight):
            target=trimesh.Trimesh(template*factor,mesh.faces,process=False)
            return fit(template,basis,mesh.faces,np.arange(len(template)),target,
                       (factor,np.eye(3),np.zeros(3)),2*factor,[],50,8,
                       arc_constraints=[{**constraint,'target_length':target_length*factor}],arc_weight=weight)
        baseline,_=trial(1,0);weighted,row=trial(1,.5);scaled,scaled_row=trial(5,.5)
        self.assertGreater(np.linalg.norm(weighted,axis=1).mean(),np.linalg.norm(baseline,axis=1).mean()+.01)
        np.testing.assert_allclose(scaled,5*weighted,atol=1e-8)
        np.testing.assert_allclose(row['shape_coefficients'],scaled_row['shape_coefficients'],atol=1e-8)


if __name__=='__main__':unittest.main()
