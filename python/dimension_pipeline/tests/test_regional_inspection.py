import copy
import hashlib
import json
import struct
import tempfile
import threading
import unittest
from pathlib import Path
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import numpy as np
import trimesh

from dimension_pipeline.regional_inspection import (POLICY,CACHE,regional_report,local_roughness,read_dense_points,
    ray_hits,define_regions,frontal_support,nose_profile,nose_proxies,segment_capsule_distance)
from dimension_pipeline.mesh_comparison import mesh_identity
from dimension_pipeline.refinement_experiments import ITERATION_POLICY
from dimension_pipeline.webcam_pilot import Store,Handler


class RegionalTests(unittest.TestCase):
    def fixture(self,root):
        store=Store(root);state=store.create();folder=store.folder(state['id'])
        xy=np.linspace(-3,3,31);vertices=np.asarray([[x,y,5.] for y in xy for x in xy]);faces=[]
        for y in range(30):
            for x in range(30):
                a=y*31+x;faces.extend([[a,a+1,a+32],[a,a+32,a+31]])
        mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False);mesh.export(folder/'full.ply')
        analysis={'vertices':(vertices+[0,0,.1]).tolist(),'triangles':faces}
        camera={'width':200,'height':200,'fx':100.,'fy':100.,'cx':100.,'cy':100.,'R':np.eye(3).tolist(),'t':[0.,0.,0.], 'k':0,'mirrored':False,'units':'reconstruction_unit'}
        predictions=[{'x':.5,'y':.5,'z':0.} for _ in range(478)]
        for i,x,y in [(33,.35,.45),(263,.65,.45),(168,.5,.35),(4,.5,.5),(2,.5,.6),
                       (50,.35,.5),(101,.4,.45),(280,.65,.5),(330,.6,.45),(205,.35,.6),(187,.3,.6),
                       (425,.65,.6),(411,.7,.6),(148,.45,.7),(152,.5,.75),(377,.55,.7)]:predictions[i]={'x':x,'y':y,'z':0.}
        state.update(status='surface_ready',result={'full_mesh':'full.ply','surface':{'units':'reconstruction_unit','mesh':analysis},'cameras':{'front':camera},'frontal_camera_key':'front','raw_predictions':predictions})
        store.save(state);return store,state,mesh,camera

    def test_plane_offset_and_proxy_measurements_use_original_coordinates(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);before=copy.deepcopy(state);folder=store.folder(state['id']);original=(folder/'full.ply').read_bytes()
            report=regional_report(folder,state)
            self.assertEqual(report['status'],'ready');self.assertAlmostEqual(report['eye_proxy_span'],3.)
            raw,analysis=report['stages'];self.assertAlmostEqual(raw['nose_proxies']['chord'],1.)
            self.assertAlmostEqual(analysis['nose_proxies']['chord'],1.02)
            for stage in (raw,analysis):
                self.assertIsNone(stage['nose_proxies']['anatomical_nose_protrusion']);self.assertIsNone(stage['nose_proxies']['surface_arc'])
                self.assertGreater(len(stage['nose_profile']['segments']),0);self.assertFalse(stage['nose_profile']['ordered_surface_arc'])
            metrics=analysis['regions']['nose'];self.assertAlmostEqual(metrics['raw_to_stage']['rms'],.1,places=6)
            self.assertLess(raw['regions']['nose']['roughness']['rms'],1e-6)
            self.assertEqual(report['units'],'reconstruction_unit');self.assertFalse(report['calibration_applied'])
            self.assertEqual(state,before);self.assertEqual((folder/'full.ply').read_bytes(),original)
            self.assertEqual(regional_report(folder,state),report)
            # Cache results are detached, and calibrated parent scale is never applied.
            report['units']='changed';state['calibrated']={'report':{'mm_per_reconstruction_unit':100}}
            again=regional_report(folder,state);self.assertEqual(again['units'],'reconstruction_unit')

    def test_original_boundary_edges_exclude_display_crop_cuts(self):
        box=trimesh.creation.icosphere(subdivisions=2);region={'chains':[[[-.1,0,1.],[.1,0,1.]]],'radius':.2}
        metrics,_=local_roughness(box,region,1.)
        self.assertEqual(metrics['original_boundary_edges'],0);self.assertIsNone(metrics['hole_count'])
        self.assertLess(len(metrics['face_indices']),len(box.faces))
        crop=box.submesh([metrics['face_indices']],append=True,repair=False)
        self.assertFalse(crop.is_watertight)

    def test_missing_rays_normalizer_and_surface_coverage_stay_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);pred=copy.deepcopy(state['result']['raw_predictions'])
            pred[4]['x']=.99
            anchors,span,regions=define_regions(mesh,camera,pred)
            self.assertEqual(anchors[4]['status'],'missed_surface');self.assertIsNotNone(span)
            self.assertEqual(regions['nose']['status'],'missing_proxy_anchor')
            pred[33]['x']=.99;state['result']['raw_predictions']=pred
            report=regional_report(store.folder(state['id']),state)
            self.assertEqual(report['status'],'missing_normalizer_proxy_hits')
            region={'chains':[[[-.2,0,5],[.2,0,5]]],'radius':.3}
            complete=frontal_support(mesh,region,camera)
            moved=mesh.copy();moved.apply_translation([0,0,2])
            missing=frontal_support(moved,region,camera)
            self.assertGreater(complete['rays'],0);self.assertEqual(complete['fraction'],1.)
            self.assertEqual(missing['nearest_hits_in_fixed_region'],0)

    def test_exact_segment_distance_handles_crossings_and_parallel_edges(self):
        chains=[[[0,-1,0],[0,1,0]]]
        values=segment_capsule_distance(np.array([[-1,0,0],[-1,0,2],[1,-1,0]]),np.array([[1,0,0],[1,0,2],[1,1,0]]),chains)
        np.testing.assert_allclose(values,[0,2,1])

    def test_dense_visibility_lists_are_read_without_fabricating_faces(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'dense.ply';header=b'ply\nformat binary_little_endian 1.0\nelement vertex 2\nproperty float32 x\nproperty float32 y\nproperty float32 z\nproperty list uint8 uint32 view_indices\nproperty list uint8 float32 view_weights\nend_header\n'
            rows=b''.join(struct.pack('<fffBII Bff',*point,2,1,2,2,.5,.5) for point in [(1,2,3),(4,5,6)])
            p.write_bytes(header+rows);np.testing.assert_allclose(read_dense_points(p),[[1,2,3],[4,5,6]])
            p.write_bytes(header+rows[:-2])
            with self.assertRaises(ValueError):read_dense_points(p)
            p.write_bytes(header+rows+b'bad')
            with self.assertRaises(ValueError):read_dense_points(p)

    def test_session_isolation_and_hash_changes_invalidate_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,_=self.fixture(temp);folder=store.folder(state['id']);first=regional_report(folder,state)
            mesh.apply_translation([0,0,.01]);mesh.export(folder/'full.ply')
            second=regional_report(folder,state);self.assertNotEqual(first['input_fingerprint'],second['input_fingerprint'])
            other=store.create();copy_state=copy.deepcopy(state);copy_state['id']=other['id'];other_folder=store.folder(other['id']);(other_folder/'full.ply').write_bytes((folder/'full.ply').read_bytes());store.save(copy_state)
            third=regional_report(other_folder,copy_state)
            self.assertEqual(third['session_id'],other['id']);self.assertIn(other['id'],third['stages'][0]['mesh_url']);self.assertNotEqual(third['input_fingerprint'],second['input_fingerprint'])
            with self.assertRaises(ValueError):regional_report(folder,state,'../full.ply')
            state['result']['full_mesh']='../outside.ply'
            with self.assertRaises(ValueError):regional_report(folder,state)

    def test_region_endpoint_guards_origin_and_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,_=self.fixture(temp);before=(store.folder(state['id'])/'session.json').read_bytes()
            handler=type('RegionalHandler',(Handler,),{'store':store,'log_message':lambda *args:None})
            server=ThreadingHTTPServer(('127.0.0.1',0),handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            def get(origin='http://127.0.0.1:5178',suffix=''):
                c=HTTPConnection('127.0.0.1',server.server_port);c.request('GET',f"/sessions/{state['id']}/regional-report{suffix}",headers={'Origin':origin});r=c.getresponse();data=r.read();c.close();return r.status,json.loads(data)
            try:
                self.assertEqual(get()[0],200);self.assertEqual(get('https://evil.test')[0],403);self.assertEqual(get(suffix='?variant=unknown')[0],422)
                self.assertEqual((store.folder(state['id'])/'session.json').read_bytes(),before)
            finally:server.shutdown();server.server_close();thread.join()

    def test_refined_full_and_analysis_are_separate_verified_stages(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,_=self.fixture(temp);folder=store.folder(state['id']);run_id='c'*32;work=folder/'refinements'/run_id/'iterations24';work.mkdir(parents=True)
            refined=mesh.copy();refined.apply_translation([0,0,.2]);refined.export(work/'full.ply')
            analysis={'vertices':(mesh.vertices+[0,0,.25]).tolist(),'triangles':mesh.faces.tolist()}
            projection={'surface':{'units':'reconstruction_unit','mesh':analysis}};(work/'projection.json').write_text(json.dumps(projection))
            sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            row={'id':'r'+run_id[:16]+'-iterations24','profile_id':'iterations24','kind':'image_refined','status':'completed','label':'24 iterations',
                 'version':ITERATION_POLICY['version'],'full_mesh':(work/'full.ply').relative_to(folder).as_posix(),'sha256':sha(work/'full.ply'),
                 'projection':(work/'projection.json').relative_to(folder).as_posix(),'analysis_mesh_id':mesh_identity(analysis),'units':'reconstruction_unit','coordinate_transform':'identity',
                 'artifacts':[{'path':p.relative_to(folder).as_posix(),'sha256':sha(p)} for p in work.iterdir()]}
            state['refinement_experiments']={'version':'webcam_refinement_experiments_v1','runs':[{'id':run_id,'variants':[row]}]}
            state['calibrated']={'report':{'mm_per_reconstruction_unit':100}}
            r=regional_report(folder,state,row['id']);self.assertEqual(len(r['stages']),4)
            self.assertAlmostEqual(r['stages'][2]['nose_proxies']['chord'],1.04,places=6)
            self.assertAlmostEqual(r['stages'][3]['nose_proxies']['chord'],1.05,places=6)
            self.assertEqual(r['units'],'reconstruction_unit');self.assertFalse(r['calibration_applied'])
            (work/'projection.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'hash'):regional_report(folder,state,row['id'])

    def test_nose_chord_depth_offset_and_regions_survive_world_coordinate_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            _,state,mesh,camera=self.fixture(temp);mesh.vertices[np.linalg.norm(mesh.vertices[:,:2],axis=1)<.01,2]=4
            predictions=state['result']['raw_predictions'];hits=ray_hits(mesh,camera,predictions,[168,4,2]);p=nose_proxies(hits,camera,3.)
            self.assertAlmostEqual(p['chord'],np.sqrt(2));self.assertAlmostEqual(p['forward_offset'],1.)
            Q=trimesh.transformations.rotation_matrix(.4,[.2,.7,.4])[:3,:3];translation=np.asarray([1.,2.,3.]);transformed=mesh.copy();transformed.vertices=mesh.vertices@Q.T+translation
            other={**camera,'R':Q.T.tolist(),'t':(-Q.T@translation).tolist()}
            moved_hits=ray_hits(transformed,other,predictions,[168,4,2]);after=nose_proxies(moved_hits,other,3.)
            self.assertAlmostEqual(after['chord'],p['chord']);self.assertAlmostEqual(after['forward_offset'],p['forward_offset'])
            a,span,regions=define_regions(transformed,other,predictions);self.assertAlmostEqual(span,3.)


if __name__=='__main__':unittest.main()
