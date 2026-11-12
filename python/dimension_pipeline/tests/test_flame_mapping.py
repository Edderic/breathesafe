import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh

from dimension_pipeline.flame_mapping import VERSION, attachment_point, catalog, regions, topology_id, validate
from dimension_pipeline.flame_fit import fit, nearest, run
from dimension_pipeline.mesh_comparison import mesh_identity


class MappingTests(unittest.TestCase):
    def setUp(self):
        self.mesh=trimesh.creation.icosphere(subdivisions=2)
        self.mapping={'version':VERSION,'model_sha256':'model','topology_id':topology_id(self.mesh.faces),
                      'session_id':'session','source_mesh_id':'analysis','points':[
                          {'arkit_index':14,'status':'reviewed','attachment':{'kind':'vertex','vertex_index':4},
                           'notes':'approximate counterpart','radius_fraction_eye_span':.3,'multiplier':4}]}

    def validate(self,mapping):
        return validate(mapping,'model',self.mesh.faces,self.mesh.vertices,'session','analysis')

    def test_validation_identity_review_and_original_indices(self):
        self.validate(self.mapping)
        for field in ('model_sha256','topology_id','session_id','source_mesh_id'):
            bad=copy.deepcopy(self.mapping);bad[field]='different'
            with self.assertRaises(ValueError): self.validate(bad)
        for attachment in ({'kind':'vertex','vertex_index':len(self.mesh.vertices)},
                           {'kind':'vertex','vertex_index':True},
                           {'kind':'barycentric','triangle_index':0,'weights':[.5,.5,.5]}):
            bad=copy.deepcopy(self.mapping);bad['points'][0]['attachment']=attachment
            with self.assertRaises(ValueError): self.validate(bad)
        bad=copy.deepcopy(self.mapping);bad['points']*=2
        with self.assertRaisesRegex(ValueError,'duplicate'): self.validate(bad)
        bad=copy.deepcopy(self.mapping);bad['points'][0]['attachment']=None
        with self.assertRaisesRegex(ValueError,'needs'): self.validate(bad)
        bad['points'][0]['status']='pending';self.validate(bad)
        self.assertEqual(next(c for c in catalog() if c['arkit_index']==160)['paths'],['nose','top_cheek'])

    def test_geodesic_falloff_overlap_and_pending_exclusion(self):
        ids=np.arange(len(self.mesh.vertices))
        weights,rows=regions(self.mapping,self.mesh.vertices,self.mesh.faces,ids,2.)
        self.assertEqual(weights[4],4.)
        self.assertTrue(np.any((weights>1)&(weights<4)))
        self.assertTrue(np.any(weights==1))
        self.assertIn(4,rows[0]['vertex_ids'])
        duplicated=copy.deepcopy(self.mapping);second=copy.deepcopy(duplicated['points'][0]);second['arkit_index']=371;duplicated['points'].append(second)
        np.testing.assert_array_equal(weights,regions(duplicated,self.mesh.vertices,self.mesh.faces,ids,2.)[0])
        duplicated['points'][0]['status']='pending';duplicated['points'][1]['status']='uncertain'
        with self.assertRaisesRegex(ValueError,'Review at least one'): regions(duplicated,self.mesh.vertices,self.mesh.faces,ids,2.)
        # Geodesic weights do not leak to a disconnected, spatially coincident component.
        doubled_vertices=np.vstack([self.mesh.vertices,self.mesh.vertices])
        doubled_faces=np.vstack([self.mesh.faces,self.mesh.faces+len(ids)])
        doubled,_=regions(self.mapping,doubled_vertices,doubled_faces,np.arange(len(doubled_vertices)),2.)
        np.testing.assert_array_equal(doubled[len(ids):],1.)

    def test_barycentric_and_outside_crop(self):
        point,seeds=attachment_point(self.mesh.vertices,self.mesh.faces,{'kind':'barycentric','triangle_index':5,'weights':[.2,.3,.5]})
        np.testing.assert_allclose(point,np.array([.2,.3,.5])@self.mesh.vertices[self.mesh.faces[5]])
        self.assertEqual(seeds,self.mesh.faces[5].tolist())
        with self.assertRaisesRegex(ValueError,'Review at least one'):
            regions(self.mapping,self.mesh.vertices,self.mesh.faces,np.array([0,1,2]),2.)

    def test_weighted_fit_prioritizes_selected_region(self):
        template=self.mesh.vertices.copy();basis=np.zeros((len(template),3,300));basis[:,2,0]=template[:,2]*.15
        chosen=(template[:,1]>.3)&(template[:,2]>0)
        target_vertices=template.copy();target_vertices[chosen,2]+=basis[chosen,2,0]*.8
        target=trimesh.Trimesh(target_vertices,self.mesh.faces,process=False)
        args=(template,basis,self.mesh.faces,np.arange(len(template)),target,(1.,np.eye(3),np.zeros(3)),2.,[])
        ordinary,_=fit(*args,components=50,iterations=30)
        weighted,_=fit(*args,components=50,iterations=30,importance=np.where(chosen,10.,1.))
        a=nearest(target,ordinary[chosen])[1];b=nearest(target,weighted[chosen])[1]
        self.assertLess(np.mean(b*b),np.mean(a*a)*.9)

    def test_matched_run_exports_original_topology_and_preserves_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'session';folder.mkdir();out=Path(tmp)/'comparison'
            vertices=np.asarray(self.mesh.vertices);faces=np.asarray(self.mesh.faces)
            raw={'vertices':vertices.tolist(),'triangles':faces.tolist()}
            state={'id':'a'*32,'result':{'surface':{'mesh':raw}}}
            original=json.dumps(state).encode();(folder/'session.json').write_bytes(original)
            mapping=copy.deepcopy(self.mapping);mapping.update(session_id=state['id'],source_mesh_id=mesh_identity(raw))
            mapping_path=Path(tmp)/'mapping.json';mapping_path.write_text(json.dumps(mapping))
            basis=np.zeros((len(vertices),3,300));basis[:,2,0]=vertices[:,2]*.1
            prepared=(self.mesh,self.mesh,np.arange(len(vertices)),np.arange(len(faces)),
                      (1.,np.eye(3),np.zeros(3)),2.,[],{'R':np.eye(3).tolist()})
            with patch('dimension_pipeline.flame_fit.load_model',return_value=(vertices,basis,faces,{'model_sha256':'model'})),patch('dimension_pipeline.flame_fit.prepare',return_value=prepared),contextlib.redirect_stdout(io.StringIO()):
                report=run(folder,'unused',out,counts=(50,),iterations=8,mapping_path=mapping_path)
            self.assertEqual([r['weighting'] for r in report['variants']],['ordinary','regional'])
            self.assertEqual([r['id'] for r in report['variants']],['50','50-regional'])
            self.assertEqual((folder/'session.json').read_bytes(),original)
            self.assertEqual(json.loads((out/'face-topology.json').read_text())['original_triangles'],faces.tolist())
            self.assertTrue(all(r['regional_metrics'][0]['status']=='ok' for r in report['variants']))
            self.assertTrue((out/'flame-50-regional.ply').is_file())
            self.assertIn('original_vertex_ids',(out/'comparison.html').read_text())
            self.assertEqual(report['regional_mapping'],mapping)


if __name__=='__main__': unittest.main()
