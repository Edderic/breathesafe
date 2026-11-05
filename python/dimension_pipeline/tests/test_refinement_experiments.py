import copy
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import trimesh
from PIL import Image

from dimension_pipeline.refinement_experiments import POLICY, ITERATION_POLICY, selected_profiles, settings, options, frozen_inputs, fresh_analysis, run_refinement_experiments, fixed_registration, save_masked_turn, registration_diagnostics
from dimension_pipeline.depth_experiments import digest
from dimension_pipeline.depth_metrics import geometry_metrics
from dimension_pipeline.depth_variants import experiment_artifacts
from dimension_pipeline.mesh_comparison import compare_session
from dimension_pipeline.webcam_pilot import Store
from dimension_pipeline.webcam_reconstruction import diagnostics


class RefinementTests(unittest.TestCase):
    def fixture(self, root):
        store = Store(root); state = store.create(); folder = store.folder(state['id'])
        mesh = trimesh.Trimesh(vertices=[[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0]], faces=[[0,1,2],[0,2,3]], process=False)
        mesh.export(folder/'full.ply'); Image.new('RGB',(100,80)).save(folder/'front.png')
        camera = {'R':np.eye(3).tolist(),'t':[0.,0.,5.],'width':100,'height':80,'fx':100.,'fy':100.,'cx':50.,'cy':40.,'k':0.,'mirrored':False,'units':'reconstruction_unit','observations':0}
        state.update(status='surface_ready', result={'full_mesh':'full.ply','frontal_undistorted':'front.png','cameras':{'front':camera},'frontal_camera_key':'front',
                     'surface':{'units':'reconstruction_unit','mesh':{'vertices':mesh.vertices.tolist(),'triangles':mesh.faces.tolist()}},'projected_points':[]})
        store.save(state); return store,state,mesh,camera

    def test_one_factor_and_no_automatic_cleanup(self):
        rows=[dict(zip(options(p)[::2],options(p)[1::2])) for p in POLICY['profiles']]
        for row in rows:
            for key in ('close-holes','ensure-edge-size','max-face-area','planar-vertex-ratio'): self.assertEqual(row['--'+key],'0')
            self.assertEqual(row['--decimate'],'1'); self.assertEqual(row['--gradient-step'],'8.05')
        self.assertEqual({k for k in rows[0] if rows[0][k]!=rows[1][k]}, {'--regularity-weight'})

    def test_iteration_budget_keeps_weight_step_and_geometry_options_fixed(self):
        rows=[dict(zip(options(p,'iterations')[::2],options(p,'iterations')[1::2])) for p in ITERATION_POLICY['profiles']]
        self.assertEqual({k for k in rows[0] if rows[0][k]!=rows[1][k]}, {'--gradient-step'})
        for profile,expected in [('iterations08',8),('iterations24',24)]:
            fixed,opt=settings(profile,'iterations')
            self.assertEqual(opt['iterations'],expected);self.assertEqual(opt['initial_gradient_step'],.5)
            self.assertEqual(opt['step_decay'],.98);self.assertTrue(opt['independent_raw_starts'])
            self.assertTrue(opt['native_budget_dependent_rigidity_phase'])
            self.assertEqual(ITERATION_POLICY['profiles'][profile]['regularity-weight'],.2)
            self.assertEqual(fixed['close-holes'],0);self.assertEqual(fixed['decimate'],1)
        self.assertEqual(rows[0],dict(zip(options('regularity020')[::2],options('regularity020')[1::2])))
        with self.assertRaises(ValueError):options('iterations24','regularity')

    def test_iteration_suite_selection_rejects_overrides_and_dispatches_fixed_suite(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,_=self.fixture(temp);state['captures']=[{}]*61;store.save(state)
            for payload in [{'suite':'custom'},{'suite':'iterations','gradient-step':500},{'suite':None},
                            {'suite':'iterations','profiles':None},{'suite':'iterations','profiles':[]},
                            {'suite':'iterations','profiles':['iterations24','iterations24']},
                            {'suite':'iterations','profiles':['regularity020']},{'suite':'iterations','profiles':[{'iterations':24}]}]:
                with self.assertRaises(ValueError):store.start_depth_experiments(state['id'],payload,refinement=True)
            with patch('dimension_pipeline.webcam_pilot.run_refinement_experiments') as native:
                store.start_depth_experiments(state['id'],{'suite':'iterations'},refinement=True)
                deadline=time.monotonic()+2
                while store.job and time.monotonic()<deadline:time.sleep(.01)
                self.assertIsNone(store.job);self.assertEqual(native.call_args.kwargs,{'suite':'iterations'})
            run=store.load(state['id'])['refinement_experiments']['runs'][-1]
            self.assertEqual(run['suite'],'iterations');self.assertEqual(run['quality_version'],ITERATION_POLICY['version'])
            self.assertEqual(selected_profiles('iterations',['iterations24','iterations08']),['iterations08','iterations24'])
            with patch('dimension_pipeline.webcam_pilot.run_refinement_experiments') as native:
                store.start_depth_experiments(state['id'],{'suite':'iterations','profiles':['iterations24']},refinement=True)
                deadline=time.monotonic()+2
                while store.job and time.monotonic()<deadline:time.sleep(.01)
                self.assertIsNone(store.job);self.assertEqual(native.call_args.kwargs,{'suite':'iterations','profiles':['iterations24']})
            self.assertEqual(store.load(state['id'])['refinement_experiments']['runs'][-1]['selected_profiles'],['iterations24'])

    def test_mask_compositing_preserves_pixels_and_native_dimensions(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp); image=p/'image.png'; mask=p/'mask.png'; output=p/'out.png'
            Image.new('RGB',(2,2),(100,150,200)).save(image)
            Image.fromarray(np.array([[0,255],[255,0]],dtype=np.uint8)).save(mask)
            save_masked_turn(image,mask,{'width':2,'height':2},output)
            result=np.asarray(Image.open(output));self.assertEqual(result.shape,(2,2,3))
            self.assertEqual(result[0,0].tolist(),[0,0,0]);self.assertEqual(result[0,1].tolist(),[100,150,200])
            with self.assertRaisesRegex(ValueError,'dimensions'):save_masked_turn(image,mask,{'width':4,'height':4},output)
            Image.new('L',(2,2),127).save(mask)
            with self.assertRaisesRegex(ValueError,'binary'):save_masked_turn(image,mask,{'width':2,'height':2},output)

    def test_registration_diagnostics_are_independent_of_surface_ray_hits(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);(p/'points3D.txt').write_text('1 0 0 0 0 0 0 0\n2 0 0 0 0 0 0 0\n')
            (p/'images.txt').write_text('1 1 0 0 0 0 0 5 1 front.png\n50 40 1 55 40 2\n')
            camera={'R':np.eye(3).tolist(),'t':[0,0,5],'fx':100,'fy':100,'cx':50,'cy':40,'k':0}
            result=registration_diagnostics(p,camera)
            self.assertEqual(result['observations'],2);self.assertAlmostEqual(result['rms_px'],np.sqrt(12.5));self.assertEqual(result['max_px'],5.)

    def test_optional_tool_diagnostics_does_not_break_raw_reconstruction(self):
        def native(command,**kwargs):
            output = 'Mach-O 64-bit executable arm64' if command[0]=='file' else ('OpenMVS 2.3.0' if command[0]=='/fixture/RefineMesh' else 'COLMAP 4.2.1 OpenMVS 2.4.0')
            return type('Result',(),{'stdout':output,'stderr':''})()
        with patch('dimension_pipeline.webcam_reconstruction.executable',side_effect=lambda name: None if name=='RefineMesh' else '/fixture/'+name), \
             patch('dimension_pipeline.webcam_reconstruction.subprocess.run',side_effect=native), \
             patch('dimension_pipeline.webcam_reconstruction.platform.system',return_value='Darwin'), \
             patch('dimension_pipeline.webcam_reconstruction.platform.machine',return_value='arm64'), \
             patch('dimension_pipeline.webcam_reconstruction.platform.platform',return_value='Darwin-arm64'):
            self.assertTrue(diagnostics()['ready']); self.assertFalse(diagnostics(include_refinement=True)['ready'])
            with patch('dimension_pipeline.webcam_reconstruction.executable',side_effect=lambda name:'/fixture/'+name):
                result=diagnostics(include_refinement=True)
                self.assertFalse(result['ready']);self.assertFalse(result['tools']['RefineMesh']['ok'])

    def test_heldout_image_rejected_from_geometry_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,camera=self.fixture(temp)
            state['captures']=[{'role':'reconstruction','slot':f'turn_{i:02}'} for i in range(60)]
            with patch('dimension_pipeline.refinement_experiments.read_model',return_value={'front.png':camera}), self.assertRaisesRegex(ValueError,'held out'):
                frozen_inputs(store.folder(state['id']),state,lambda:False)
            model={f'turn_{i:02}.png':{**camera,'camera_id':1,'k':.01} for i in range(60)}
            with patch('dimension_pipeline.refinement_experiments.read_model',return_value=model), self.assertRaisesRegex(ValueError,'undistorted'):
                frozen_inputs(store.folder(state['id']),state,lambda:False)
            state['result']['surface']['units']='mm'
            with self.assertRaisesRegex(ValueError,'unscaled'):frozen_inputs(store.folder(state['id']),state,lambda:False)

    def test_fresh_projection_topology_and_scale_are_independent(self):
        with tempfile.TemporaryDirectory() as temp:
            _,state,mesh,camera=self.fixture(temp)
            state['calibrated']={'report':{'mm_per_reconstruction_unit':100.}}
            state['draft']={'scale_route':[{'triangle_index':0}]}
            before=copy.deepcopy(state)
            shifted=trimesh.Trimesh(vertices=mesh.vertices+[0,0,1],faces=mesh.faces[:,::-1],process=False)
            result=fresh_analysis(shifted,state,camera,[{'x':.5,'y':.5,'z':0.},{'x':0.,'y':0.,'z':0.}], 'variant')
            self.assertEqual(result['projected_points'][0]['status'],'ok')
            self.assertAlmostEqual(result['projected_points'][0]['point'][2],1.)
            self.assertEqual(result['projected_points'][1]['status'],'missed_surface')
            self.assertTrue(all(p['acceptance']=='pending' for p in result['projected_points']))
            self.assertIsNone(result['calibration']); self.assertEqual(result['routes'],[])
            self.assertEqual(result['surface']['scale']['status'],'uncalibrated'); self.assertEqual(state,before)

    def test_refinement_export_reload_and_calibrated_comparison(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp); folder=store.folder(state['id']); run_id='c'*32; profile='regularity020'
            path=folder/'refinements'/run_id/profile/'full.ply';path.parent.mkdir(parents=True);mesh.export(path)
            row={'id':'r'+run_id[:16]+'-'+profile,'profile_id':profile,'status':'completed','kind':'image_refined','label':'Refined',
                 'full_mesh':path.relative_to(folder).as_posix(),'sha256':digest(path),'source_full_mesh_sha256':digest(folder/'full.ply'),
                 'version':POLICY['version'],'quality':POLICY['profiles'][profile],'input_manifest_sha256':'0'*64,
                 'coordinate_transform':'identity','units':'reconstruction_unit','attachment_status':'fresh_required',
                 'recommendation':{'decision':'pending_manual_review'},'coverage_status':'manual_review_required',
                 'metrics':geometry_metrics(mesh,mesh,camera,[]),'artifacts':[{'path':path.relative_to(folder).as_posix(),'sha256':digest(path)}]}
            projection=path.with_name('projection.json');projection.write_text(json.dumps(fresh_analysis(mesh,state,camera,[],row['id'])))
            row.update(projection=projection.relative_to(folder).as_posix(),analysis_mesh_id=json.loads(projection.read_text())['surface']['topology_id'])
            row['artifacts'].append({'path':row['projection'],'sha256':digest(projection)})
            state['calibrated']={'report':{'mm_per_reconstruction_unit':100.},'cameras':{'front':{**camera,'t':[0,0,500],'units':'mm'}}}
            state['refinement_experiments']={'version':'webcam_refinement_experiments_v1','runs':[{'id':run_id,'status':'completed','variants':[row]}]}
            store.save(state); original=copy.deepcopy(state)
            report=compare_session(folder,state,40,row['id'],'raw')
            self.assertEqual(report['units'],'reconstruction_unit');self.assertEqual(report['display_scale'],1.)
            self.assertEqual(report['display_camera']['t'],camera['t'])
            restored=store.restore(store.export(state['id']))
            self.assertEqual(restored['refinement_experiments'],state['refinement_experiments']);self.assertEqual(restored['result'],state['result'])
            self.assertEqual(state,original)
            # Both historical regularity and new iteration records remain loadable.
            row.update(id='r'+run_id[:16]+'-iterations24',profile_id='iterations24',version=ITERATION_POLICY['version'],quality=ITERATION_POLICY['profiles']['iterations24'])
            store.save(state);restored=store.restore(store.export(state['id']))
            self.assertEqual(restored['refinement_experiments'],state['refinement_experiments'])
            row['version']='unsupported';store.save(state)
            with self.assertRaises(ValueError):store.export(state['id'])
            row['version']=ITERATION_POLICY['version']
            row['artifacts'][0]['path']='../full.ply'
            with self.assertRaises(ValueError):experiment_artifacts(state)

    def test_cancel_single_job_and_recovery_preserve_sessions(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,_=self.fixture(temp); state['captures']=[{}]*61;store.save(state)
            other=store.create();other_bytes=(store.folder(other['id'])/'session.json').read_bytes();entered=threading.Event()
            def fake(folder,snapshot,run_id,run,update,publish,cancelled):
                entered.set();run('refine_native',[sys.executable,'-c','import time;time.sleep(30)'],folder)
            with patch('dimension_pipeline.webcam_pilot.run_refinement_experiments',fake):
                store.start_depth_experiments(state['id'],{},refinement=True);self.assertTrue(entered.wait(2))
                with self.assertRaisesRegex(ValueError,'One'):store.start_depth_experiments(other['id'],{})
                deadline=time.monotonic()+3
                while store.process is None and time.monotonic()<deadline:time.sleep(.01)
                store.cancel(state['id'])
                while store.job and time.monotonic()<deadline:time.sleep(.01)
            final=store.load(state['id']);self.assertIsNone(store.job)
            self.assertEqual(final['refinement_experiments']['runs'][-1]['status'],'cancelled');self.assertEqual(final['result'],state['result'])
            final['refinement_experiments']['runs'][-1]['status']='processing';store.save(final)
            recovered=Store(temp).load(state['id']);self.assertEqual(recovered['refinement_experiments']['runs'][-1]['status'],'interrupted')
            self.assertEqual((store.folder(other['id'])/'session.json').read_bytes(),other_bytes)

    def test_direct_iteration_comparison_checks_reference_hash_and_never_uses_old_scale(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);run_id='e'*32;rows=[]
            for profile,z in [('iterations08',1),('iterations24',2)]:
                variant_id='r'+run_id[:16]+'-'+profile;work=folder/'refinements'/run_id/profile;work.mkdir(parents=True)
                candidate=trimesh.Trimesh(vertices=mesh.vertices+[0,0,z],faces=mesh.faces,process=False);candidate.export(work/'full.ply')
                projection=fresh_analysis(candidate,state,camera,[],variant_id);(work/'projection.json').write_text(json.dumps(projection))
                rows.append({'id':variant_id,'profile_id':profile,'status':'completed','kind':'image_refined','label':profile,
                    'full_mesh':(work/'full.ply').relative_to(folder).as_posix(),'sha256':digest(work/'full.ply'),
                    'source_full_mesh_sha256':digest(folder/'full.ply'),'version':ITERATION_POLICY['version'],'quality':ITERATION_POLICY['profiles'][profile],
                    'input_manifest_sha256':'0'*64,'coordinate_transform':'identity','units':'reconstruction_unit','attachment_status':'fresh',
                    'projection':(work/'projection.json').relative_to(folder).as_posix(),'analysis_mesh_id':projection['surface']['topology_id'],
                    'recommendation':{'decision':'pending'},'coverage_status':'manual_review_required',
                    'metrics':{'vertices':len(candidate.vertices),'faces':len(candidate.faces)},
                    'artifacts':[{'path':p.relative_to(folder).as_posix(),'sha256':digest(p)} for p in work.iterdir()]})
            state['refinement_experiments']={'version':'webcam_refinement_experiments_v1','runs':[{'id':run_id,'status':'completed','variants':rows}]}
            state['calibrated']={'report':{'mm_per_reconstruction_unit':100.}}
            report=compare_session(folder,state,40,rows[1]['id'],rows[0]['id'])
            self.assertAlmostEqual(report['deviation']['source_to_reference']['rms'],1.)
            self.assertEqual(report['comparison_reference_id'],rows[0]['id']);self.assertEqual(report['display_scale'],1.)
            report=compare_session(folder,state,40,'raw',rows[0]['id'])
            self.assertEqual(report['units'],'reconstruction_unit');self.assertAlmostEqual(report['deviation']['source_to_reference']['rms'],1.)
            with self.assertRaises(ValueError):compare_session(folder,state,40,rows[1]['id'],'unknown')
            (folder/rows[0]['full_mesh']).write_bytes(b'changed')
            with self.assertRaises(ValueError):compare_session(folder,state,40,rows[1]['id'],rows[0]['id'])

    def test_native_failure_is_recorded_without_fabricated_geometry(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,_=self.fixture(temp);folder=store.folder(state['id']);source=folder/'source'
            (source/'dense/sparse').mkdir(parents=True); before=copy.deepcopy(state)
            manifest={'files':{'full.ply':digest(folder/'full.ply')}}; published=[]
            def native(stage,command,cwd):
                if stage.endswith(':import_turns'):raise ValueError('native import failed')
            with patch('dimension_pipeline.refinement_experiments.diagnostics',return_value={'ready':True,'tools':{}}), \
                 patch('dimension_pipeline.refinement_experiments.frozen_inputs',return_value=(source,{},manifest)):
                run_refinement_experiments(folder,state,'d'*32,native,lambda _:None,lambda row:published.append(copy.deepcopy(row)),lambda:False)
            completed=[r for r in published if r['status']!='processing']
            self.assertEqual(len(completed),3);self.assertTrue(all(r['status']=='failed' and 'full_mesh' not in r for r in completed))
            self.assertEqual(state,before);self.assertEqual(digest(folder/'full.ply'),manifest['files']['full.ply'])

    def test_iteration_runner_uses_independent_raw_starts_and_records_effective_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,mesh,camera=self.fixture(temp);folder=store.folder(state['id']);source=folder/'source'
            (source/'dense/sparse').mkdir(parents=True);Image.new('L',(100,80),255).save(folder/'front-mask.png')
            state['captures']=[{'role':'frontal','image':'front.png','mask':'front-mask.png'}]
            manifest={'files':{'full.ply':digest(folder/'full.ply')}};published=[];commands=[]
            def native(stage,command,cwd):
                if stage.endswith(':image_refinement'):
                    self.assertEqual(digest(cwd/'input.ply'),manifest['files']['full.ply'])
                    commands.append(command);mesh.export(cwd/'full.ply')
                if stage.endswith(':undistort_heldout'):
                    path=cwd/'frontal_undistorted/images';path.mkdir(parents=True)
                    Image.new('RGB',(100,80)).save(path/'front.png')
            with patch('dimension_pipeline.refinement_experiments.diagnostics',return_value={'ready':True,'tools':{}}), \
                 patch('dimension_pipeline.refinement_experiments.frozen_inputs',return_value=(source,{},manifest)), \
                 patch('dimension_pipeline.refinement_experiments.fixed_registration',side_effect=lambda source,work,run,stage:(work/'registered',camera)), \
                 patch('dimension_pipeline.refinement_experiments.registration_diagnostics',return_value={'observations':0}), \
                 patch('dimension_pipeline.refinement_experiments.read_model',return_value={'front.png':camera}), \
                 patch('dimension_pipeline.refinement_experiments.detect',return_value=([{'x':.5,'y':.5,'z':0}],{'fixture':True})):
                run_refinement_experiments(folder,state,'f'*32,native,lambda _:None,lambda row:published.append(copy.deepcopy(row)),lambda:False,suite='iterations')
                selected=[];commands_before=len(commands)
                run_refinement_experiments(folder,state,'0'*32,native,lambda _:None,lambda row:selected.append(copy.deepcopy(row)),lambda:False,suite='iterations',profiles=['iterations24'])
                self.assertEqual(len(commands)-commands_before,1)
                self.assertEqual(selected[-1]['status'],'completed');self.assertEqual(selected[-1]['optimization']['iterations'],24)
            rows=[row for row in published if row['status']!='processing']
            self.assertEqual([row['status'] for row in rows],['completed','completed'])
            self.assertEqual([row['optimization']['iterations'] for row in rows],[8,24])
            self.assertEqual([cmd[cmd.index('--gradient-step')+1] for cmd in commands[:2]],['8.05','24.05'])
            self.assertEqual(len({row['input_manifest_sha256'] for row in rows}),1)
            self.assertTrue(all(row['quality']['regularity-weight']==.2 and row['projection_hits']==1 for row in rows))
            state['refinement_experiments']={'version':'webcam_refinement_experiments_v1','runs':[{'id':'f'*32,'status':'completed','variants':rows}]}
            store.save(state);restored=store.restore(store.export(state['id']))
            self.assertEqual(restored['refinement_experiments'],state['refinement_experiments'])

    def test_registration_rejects_changes_to_fixed_geometry(self):
        with tempfile.TemporaryDirectory() as temp:
            store,state,_,camera=self.fixture(temp);folder=store.folder(state['id']);source=folder/'source';source.mkdir()
            state['result']['diagnostics']={'sparse_model_selection':{'selected_model':'0'}};store.save(state)
            model=source/'sparse/0';model.mkdir(parents=True);(model/'points3D.txt').write_text('1 0 0 0 0 0 0 0\n')
            (source/'database.db').write_bytes(b'fixture');work=folder/'evaluate';work.mkdir()
            before={'turn_00.png':{**camera,'camera_id':1}};after=copy.deepcopy(before);after['front.png']=camera
            def native(stage,command,cwd):
                if stage.endswith(':register_heldout'):(work/'registered/points3D.txt').write_text('1 0 0 1 0 0 0 0\n')
            with patch('dimension_pipeline.refinement_experiments.read_model',side_effect=[before,after]), self.assertRaisesRegex(ValueError,'changed sparse geometry'):
                fixed_registration(source,work,native,'fixture')


if __name__=='__main__':unittest.main()
