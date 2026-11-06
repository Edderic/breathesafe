import copy
import hashlib
import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import numpy as np
import trimesh
from PIL import Image

from dimension_pipeline.nose_overlays import catalog,photo_overlay,project_pixels,visible_points,sampled_edges
from dimension_pipeline.webcam_geometry import ray
from dimension_pipeline.webcam_pilot import Handler


class NosePhotoTests(unittest.TestCase):
    def fixture(self,root):
        from dimension_pipeline.tests.test_regional_inspection import RegionalTests
        store,state,mesh,camera=RegionalTests().fixture(root);folder=store.folder(state['id'])
        for i,x in enumerate([-3,-1,0,1,3]):
            slot=f'turn_{i:02}';Image.new('RGB',(200,200),(150,100,80)).save(folder/(slot+'.png'))
            c=copy.deepcopy(camera);c['t']=[-x,0,0];c['k']=.03
            state['result']['cameras']['registered:'+slot+'.png']=c
            state['captures'].append({'slot':slot,'role':'reconstruction','image':slot+'.png','width':200,'height':200,
                                      'sha256':hashlib.sha256((folder/(slot+'.png')).read_bytes()).hexdigest()})
        store.save(state);return store,state,mesh,camera

    def test_original_radial_projection_backprojection_and_world_transform(self):
        c={'R':np.eye(3).tolist(),'t':[0,0,0],'fx':100,'fy':80,'cx':20,'cy':30,'k':.1}
        p=np.array([[1.,2.,5.]]);pixel=project_pixels(c,p)[0];np.testing.assert_allclose(pixel,[40.4,62.64])
        origin,direction=ray(c,pixel);np.testing.assert_allclose(np.cross(p[0]-origin,direction),0,atol=1e-7)
        angle=.4;Q=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]]);shift=np.array([2.,3.,1.])
        moved=copy.deepcopy(c);moved['R']=Q.T.tolist();moved['t']=(-Q.T@shift).tolist()
        np.testing.assert_allclose(project_pixels(moved,p@Q.T+shift),[pixel])
        with self.assertRaises(ValueError):project_pixels(c,[[0,0,-1]])

    def test_visibility_uses_nearest_full_surface_not_hidden_layer(self):
        front=trimesh.Trimesh(vertices=[[-2,-2,5],[2,-2,5],[2,2,5],[-2,2,5]],faces=[[0,1,2],[0,2,3]],process=False)
        back=front.copy();back.apply_translation([0,0,1]);both=trimesh.util.concatenate([back,front])
        camera={'R':np.eye(3).tolist(),'t':[0,0,0]}
        np.testing.assert_equal(visible_points(both,camera,np.array([[.1,.2,5],[.1,.2,6],[5,5,6]]),1e-5),[True,False,False])

    def test_closed_surface_contours_are_prioritized_without_crop_boundaries(self):
        mesh=trimesh.creation.icosphere(subdivisions=2,radius=1);mesh.apply_translation([0,0,5])
        camera={'R':np.eye(3).tolist(),'t':[0,0,0]};region={'chains':[[[0,0,5],[0,0,5.1]]],'radius':2}
        edges,contour=sampled_edges(mesh,region,camera)
        self.assertTrue(contour.any());self.assertLessEqual(len(edges),300)
        for edge in edges[contour]:
            faces=np.flatnonzero(np.isin(mesh.faces,edge).sum(axis=1)==2)
            self.assertEqual(len(faces),2)
            facing=np.einsum('ij,ij->i',mesh.face_normals[faces],-mesh.triangles_center[faces])>0
            self.assertNotEqual(facing[0],facing[1])

    def test_catalog_overlay_hash_guards_and_immutable_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);before=(folder/'session.json').read_bytes();raw=(folder/'full.ply').read_bytes()
            c=catalog(folder,state);self.assertEqual(len(c['views']),5);self.assertEqual(len(c['default_slots']),len(set(c['default_slots'])))
            self.assertNotIn('front',[v['slot'] for v in c['views']]);r=photo_overlay(folder,state,'turn_02')
            self.assertTrue(r['stages'][0]['lines']);self.assertEqual(r['view']['camera']['k'],.03);self.assertFalse(r['calibration_applied'])
            self.assertLessEqual(r['stages'][0]['sampled_edges'],300);self.assertEqual(len(r['algorithm_sha256']),64)
            self.assertGreater(r['crop'][2],0);self.assertLessEqual(r['crop'][0]+r['crop'][2],200)
            r['stages'][0]['lines']=[];self.assertTrue(photo_overlay(folder,state,'turn_02')['stages'][0]['lines'])
            self.assertEqual((folder/'session.json').read_bytes(),before);self.assertEqual((folder/'full.ply').read_bytes(),raw)
            with self.assertRaises(ValueError):photo_overlay(folder,state,'front')
            with self.assertRaises(ValueError):catalog(folder,state,'../../bad')
            (folder/'turn_02.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash'):photo_overlay(folder,state,'turn_02')

    def test_view_camera_dimension_and_missing_region_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id'])
            state['result']['cameras']['registered:turn_00.png']['mirrored']=True
            with self.assertRaisesRegex(ValueError,'mirroring'):catalog(folder,state)
            state['result']['cameras']['registered:turn_00.png']['mirrored']=False
            state['result']['raw_predictions'][4]['x']=.99
            with self.assertRaisesRegex(ValueError,'missing'):catalog(folder,state)

    def test_endpoints_preserve_origin_guards_and_read_only_session(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);before=(folder/'session.json').read_bytes()
            handler=type('PhotoHandler',(Handler,),{'store':store,'log_message':lambda *args:None});server=ThreadingHTTPServer(('127.0.0.1',0),handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                conn=HTTPConnection('127.0.0.1',server.server_port);path=f"/sessions/{state['id']}/nose-overlay/turn_02"
                conn.request('GET',path,headers={'Origin':'https://example.com'});response=conn.getresponse();self.assertEqual(response.status,403);response.read()
                conn.request('GET',path,headers={'Origin':'http://127.0.0.1:5178'});response=conn.getresponse();self.assertEqual(response.status,200);self.assertEqual(json.loads(response.read())['view']['slot'],'turn_02');conn.close()
                self.assertEqual((folder/'session.json').read_bytes(),before)
            finally:server.shutdown();server.server_close();thread.join()
