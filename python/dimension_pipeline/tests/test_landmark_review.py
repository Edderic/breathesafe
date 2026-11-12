import copy
import json
import tempfile
import unittest

import numpy as np
import trimesh

from dimension_pipeline.landmark_review import metadata, operate, attached


class LandmarkTests(unittest.TestCase):
    def fixture(self, root):
        from dimension_pipeline.tests.test_regional_inspection import RegionalTests
        return RegionalTests().fixture(root)

    def test_pick_matches_rotated_gpu_view_and_nearest_visible_surface(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);info=metadata(folder,state)
            # Two depth layers: positive display z is nearer; back layer must not win.
            back=mesh.copy();back.apply_translation([0,0,1]);both=trimesh.util.concatenate([back,mesh]);both.export(folder/'full.ply');info=metadata(folder,state)
            for yaw,pitch in [(0,0),(35,20),(-45,-25)]:
                # A known point transformed with the exact shader equations.
                a,b=np.cos(np.deg2rad(yaw)),np.sin(np.deg2rad(yaw));c,d=np.cos(np.deg2rad(pitch)),np.sin(np.deg2rad(pitch))
                rotation=np.array([[a,0,b],[d*b,c,-d*a],[-c*b,d,c*a]])
                display=np.array([.3,-.4,-5]);center=np.array([0,0,-5.5]);q=rotation@(display-center);scale=60;zoom=1.5
                view={'center':center.tolist(),'scale':scale,'zoom':zoom,'yaw':yaw,'pitch':pitch,'x':.5+q[0]*scale*zoom/720,'y':.5-q[1]*scale*zoom/480}
                view=json.loads(json.dumps(view))
                hit,changed=operate(folder,state,{'op':'pick','sha256':info['sha256'],'view':view})
                self.assertFalse(changed);self.assertEqual(hit['status'],'ok');np.testing.assert_allclose(hit['point'],[.3,.4,5],atol=1e-7)
                np.testing.assert_allclose(attached(both,hit['attachment']),hit['point'])
            view.update(x=0,y=0)
            self.assertEqual(operate(folder,state,{'op':'pick','sha256':info['sha256'],'view':view})[0]['status'],'missed_surface')

    def test_review_history_revision_hash_and_units_are_isolated(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);before=copy.deepcopy(state['result']);raw=(folder/'full.ply').read_bytes();info=metadata(folder,state)
            suggestion=info['suggestions']['pronasale'];payload={'op':'review','sha256':info['sha256'],'revision':0,'landmark':'pronasale','status':'accepted','attachment':suggestion['attachment'],'note':'Reviewed in profile','provenance':'detector_suggestion'}
            saved,changed=operate(folder,state,payload);self.assertTrue(changed);self.assertEqual(saved['revision'],1);self.assertEqual(saved['points']['pronasale']['units'],'reconstruction_unit')
            with self.assertRaisesRegex(ValueError,'changed'):operate(folder,state,payload)
            payload.update(revision=1,status='unavailable');operate(folder,state,payload)
            row=state['landmark_review']['sources']['raw']['points']['pronasale'];self.assertIsNone(row['point']);self.assertIsNone(row['attachment']);self.assertEqual(row['history'][0]['status'],'accepted')
            store.save(state);self.assertEqual(metadata(folder,store.load(state['id']))['review']['revision'],2)
            self.assertEqual(state['result'],before);self.assertEqual((folder/'full.ply').read_bytes(),raw)
            payload['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'hash'):operate(folder,state,payload)

    def test_invalid_attachments_statuses_and_missing_suggestions(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);info=metadata(folder,state)
            for attachment in [{'kind':'barycentric','triangle_index':-1,'weights':[1,0,0]}, {'kind':'barycentric','triangle_index':0,'weights':[float('nan'),0,1]}, {'kind':'barycentric','triangle_index':0,'weights':[2,-1,0]}]:
                with self.assertRaises(ValueError):attached(mesh,attachment)
            payload={'op':'review','sha256':info['sha256'],'revision':0,'landmark':'pronasale','status':'accepted','attachment':None}
            with self.assertRaises(ValueError):operate(folder,state,payload)
            payload.update(status='uncertain');saved,_=operate(folder,state,payload);self.assertIsNone(saved['points']['pronasale']['point'])
            state['result']['raw_predictions'][4]['x']=.99
            self.assertEqual(metadata(folder,state)['suggestions']['pronasale']['status'],'missed_surface')
            with self.assertRaises(ValueError):metadata(folder,state,'../../bad')

    def test_export_reload_retains_source_attachments_and_review(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);(folder/'front.png').write_bytes(b'frontal fixture');state['result']['frontal_undistorted']='front.png';info=metadata(folder,state)
            operate(folder,state,{'op':'review','sha256':info['sha256'],'revision':0,'landmark':'sellion','status':'uncertain','attachment':info['suggestions']['sellion']['attachment']});store.save(state)
            restored=store.restore(store.export(state['id']));self.assertNotEqual(restored['id'],state['id'])
            loaded=metadata(store.folder(restored['id']),restored)
            self.assertEqual(loaded['review'],info['review'] | {'revision':1,'points':state['landmark_review']['sources']['raw']['points']})
            self.assertIn(restored['id'],loaded['mesh_url'])
