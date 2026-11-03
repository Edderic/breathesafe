const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '../..'), context = {};
for (const file of ['dimension_fixture_geometry.js', 'face_annotation_geometry.js', 'face_mediapipe_geometry.js']) {
  vm.runInNewContext(fs.readFileSync(path.join(root, 'app/javascript', file), 'utf8').replace(/^import .*;\n/gm, '').replace(/export /g, ''), context);
}
const mesh = { mesh: { vertices: [[-10,-10,0],[10,-10,0],[0,10,0],[-10,-10,2],[10,-10,2],[0,10,2]], triangles: [[0,1,2],[3,4,5]] } };
const camera = { projection: 'orthographic', center_mm: [0,0,0], yaw: 0, pitch: 0, pixels_per_mm: 5, width: 720, height: 480, mirrored: false, distortion: 'none' };
const attach = triangle_index => ({ attachment: { kind: 'barycentric', triangle_index, weights: [0.25,0.25,0.5] } });
const points = context.projectMesh(mesh, camera.center_mm, 0, 0, 5);

test('image coordinates project to the nearest visible surface, independent of MediaPipe depth', () => {
  const a = context.projectDetection(mesh, points, {x:.5,y:.5,z:-100}, 1);
  const b = context.projectDetection(mesh, points, {x:.5,y:.5,z:100}, 1);
  assert.equal(a.status,'ok');assert.equal(a.attachment.triangle_index,1);
  assert.deepEqual(Array.from(a.point_mm),[0,0,2]);
  assert.deepEqual(a.attachment,b.attachment);
  assert.equal(context.projectDetection(mesh,points,{x:-.01,y:.5},0).status,'outside_image');
  assert.equal(context.projectDetection(mesh,points,{x:null,y:.5},0).status,'invalid_coordinates');
  assert.equal(context.projectDetection(mesh,points,{x:.01,y:.01},0).status,'missed_surface');
});

test('surface projection round trips under all seven existing cameras without mirroring', () => {
  const record={mesh:{vertices:[[-10,-10,0],[10,-10,0],[0,10,0],[0,0,15]],triangles:[[0,1,2],[0,3,1],[1,3,2],[2,3,0]]}};
  const views=JSON.parse(fs.readFileSync(path.join(root,'python/dimension_pipeline/assets/head_views.json')));
  for(const view of views){
    const projected=context.projectMesh(record,[0,0,0],view.yaw,view.pitch,5);
    const face=record.mesh.triangles[1], center=[0,1,2].map(axis=>face.reduce((s,i)=>s+record.mesh.vertices[i][axis]/3,0));
    const p=context.projectPoint(center,[0,0,0],view.yaw,view.pitch,5);
    const hit=context.projectDetection(record,projected,{x:p.x/720,y:p.y/480,z:999},3);assert.equal(hit.status,'ok');
    const q=context.projectPoint(hit.point_mm,[0,0,0],view.yaw,view.pitch,5);
    assert.ok(Math.hypot(q.x-p.x,q.y-p.y)<1e-8,view.id);
  }
  assert.ok(context.projectPoint([10,0,0],[0,0,0],0,0,5).x>360);
});

test('reference occlusion and failures remain statuses, not zero-distance samples', () => {
  const result={view_id:'front',camera,status:'ok',detections:[context.projectDetection(mesh,points,{x:.5,y:.5,z:0},1)]};
  const refs=[{id:'back',label:'Back',landmarks:{tip:attach(0)}},{id:'front',label:'Front',landmarks:{tip:attach(1)}}];
  const rows=context.comparisonRows(mesh,[result,{...result,view_id:'profile',status:'no_detection',detections:[]}],{tip:1,missing:1},refs);
  assert.equal(rows.length,8);
  assert.equal(rows[0].status,'reference_occluded');assert.equal(rows[1].distance_mm,0);
  assert.equal(rows[2].status,'missing_reference');
  assert.equal(rows[4].status,'no_detection');assert.equal(rows[4].distance_mm,undefined);
  const summary=context.distanceSummary([[0,0,0],[3,0,0],[0,4,0]]);
  assert.equal(summary.median_mm,4);assert.equal(summary.maximum_mm,5);
  assert.equal(context.distanceSummary([[0,0,0]]).maximum_mm,null);
});

test('candidate maps and experiment reload reject wrong meshes and invalid cameras', () => {
  assert.throws(()=>context.validateMappings({ear:478},['ear']));
  assert.throws(()=>context.validateMappings({unknown:1},['ear']));
  const record={record_id:'face',topology_id:'topology'};
  const bundle={experiment_version:'1.0.0',record_id:'face',topology_id:'topology',mesh_sha256:'hash',units:'mm',mappings:{},results:[{view_id:'front',camera,status:'no_detection',raw_landmarks:[]}]};
  assert.equal(context.validateExperiment(bundle,record,'hash',[]),bundle);
  assert.throws(()=>context.validateExperiment(bundle,record,'other',[]));
  assert.throws(()=>context.validateExperiment({...bundle,results:[{...bundle.results[0],camera:{...camera,mirrored:true}}]},record,'hash',[]));
});
