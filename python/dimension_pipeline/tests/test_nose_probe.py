import copy
import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import numpy as np
import trimesh

from dimension_pipeline.nose_probe import probe_metadata,inspect_point,point_projection,section
from dimension_pipeline.webcam_pilot import Handler


class NoseProbeTests(unittest.TestCase):
    def fixture(self,root):
        from dimension_pipeline.tests.test_nose_overlays import NosePhotoTests
        return NosePhotoTests().fixture(root)

    def test_exact_attachment_projects_to_each_camera_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);before=(folder/'session.json').read_bytes();raw=(folder/'full.ply').read_bytes()
            meta=probe_metadata(folder,state);source=meta['sources'][0]
            data={'op':'inspect','sha256':source['sha256'],'attachment':source['seed']['attachment'],'slots':['turn_00','turn_02','turn_04']}
            report=inspect_point(folder,state,data)
            self.assertFalse(report['calibration_applied']);self.assertEqual(report['units'],'reconstruction_unit')
            self.assertEqual(report['attachment'],data['attachment']);np.testing.assert_allclose(report['point'],[0,0,5])
            self.assertEqual(report['projections']['turn_02']['status'],'visible');np.testing.assert_allclose(report['projections']['turn_02']['pixel'],[100,100])
            self.assertLess(report['projections']['turn_04']['pixel'][0],100)
            for line in report['sections'][0]['segments']:np.testing.assert_allclose(np.array(line)[:,0],0,atol=1e-10)
            self.assertEqual((folder/'session.json').read_bytes(),before);self.assertEqual((folder/'full.ply').read_bytes(),raw)
            invalid=copy.deepcopy(data);invalid['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'hash'):inspect_point(folder,state,invalid)
            invalid=copy.deepcopy(data);invalid['slots']=['turn_02','turn_02']
            with self.assertRaises(ValueError):inspect_point(folder,state,invalid)
            for change in [{'op':'review'},{'slots':['front']},{'axis':'anatomical'},{'radius_fraction':float('nan')},{'source_id':'refined_full'}]:
                with self.assertRaises(ValueError):inspect_point(folder,state,data|change)

    def test_pick_and_miss_use_existing_gpu_coordinate_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);meta=probe_metadata(folder,state)
            data={'op':'pick','sha256':meta['sources'][0]['sha256'],'slots':['turn_02'],
                  'view':{'center':[0,0,-5],'scale':100,'zoom':1,'yaw':0,'pitch':0,'x':.5,'y':.5}}
            result=inspect_point(folder,state,data);self.assertEqual(result['status'],'ok');np.testing.assert_allclose(result['point'],[0,0,5])
            data['view'].update(x=0,y=0,scale=10)
            self.assertEqual(inspect_point(folder,state,data)['status'],'missed_surface')
            self.assertNotIn('landmark_review',state)

    def test_sections_compare_same_world_location_and_preserve_offset(self):
        camera={'R':np.eye(3).tolist(),'t':[0,0,0]}
        mesh=trimesh.Trimesh(vertices=[[-1,-1,5],[1,-1,5],[1,1,5],[-1,1,5]],faces=[[0,1,2],[0,2,3]],process=False)
        refined=mesh.copy();refined.apply_translation([0,0,.1])
        for axis in ['vertical','horizontal']:
            raw=section(mesh,[0,0,5],camera,.5,axis);other=section(refined,[0,0,5],camera,.5,axis)
            self.assertEqual(raw['status'],'ok');self.assertEqual(other['status'],'ok')
            np.testing.assert_allclose(np.asarray(raw['segments'])[:,:,0],0);np.testing.assert_allclose(np.asarray(other['segments'])[:,:,0],-.1)
        self.assertEqual(section(refined,[0,0,0],camera,.5,'vertical')['status'],'no_section_in_local_volume')

    def test_occluded_outside_and_behind_points_are_not_visible_markers(self):
        front=trimesh.Trimesh(vertices=[[-2,-2,5],[2,-2,5],[2,2,5],[-2,2,5]],faces=[[0,1,2],[0,2,3]],process=False)
        back=front.copy();back.apply_translation([0,0,1]);mesh=trimesh.util.concatenate([front,back])
        camera={'R':np.eye(3).tolist(),'t':[0,0,0],'width':200,'height':200,'fx':100,'fy':100,'cx':100,'cy':100,'k':0}
        self.assertEqual(point_projection(mesh,[0,0,6],camera,1)['status'],'occluded')
        self.assertEqual(point_projection(mesh,[10,0,5],camera,1)['status'],'outside_image')
        self.assertEqual(point_projection(mesh,[0,0,-1],camera,1)['status'],'behind_camera')

    def test_post_endpoint_is_read_only_and_origin_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);before=(folder/'session.json').read_bytes();meta=probe_metadata(folder,state)
            payload={'op':'inspect','sha256':meta['sources'][0]['sha256'],'attachment':meta['sources'][0]['seed']['attachment'],'slots':['turn_02']}
            handler=type('ProbeHandler',(Handler,),{'store':store,'log_message':lambda *args:None});server=ThreadingHTTPServer(('127.0.0.1',0),handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                conn=HTTPConnection('127.0.0.1',server.server_port);path=f"/sessions/{state['id']}/nose-probe"
                for origin,expected in [('https://example.com',403),('http://127.0.0.1:5178',200)]:
                    conn.request('POST',path,json.dumps(payload),{'Origin':origin,'Content-Type':'application/json'});response=conn.getresponse();self.assertEqual(response.status,expected);response.read()
                conn.close();self.assertEqual((folder/'session.json').read_bytes(),before)
            finally:server.shutdown();server.server_close();thread.join()
