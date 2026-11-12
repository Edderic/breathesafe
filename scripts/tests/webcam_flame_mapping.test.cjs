const {test}=require('node:test');
const assert=require('node:assert/strict');
const mapping=require('../../python/dimension_pipeline/flame_mapping_ui.js');
test('frontmost triangle picks retain original vertex and triangle indices',()=>{
  const mesh={vertices:[[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,0,1],[0,1,1]],triangles:[[0,1,2],[3,4,5]],original_vertex_ids:[501,7,88,104,205,309],original_triangle_ids:[999,123]};
  const a=mapping.pick(mesh,mesh.vertices,[.2,.3],'barycentric');
  assert.equal(a.triangle_index,123);assert.ok(Math.abs(a.weights[0]-.5)<1e-9);
  assert.deepEqual(mapping.point(mesh,a),[.2,.3,1]);
  assert.deepEqual(mapping.pick(mesh,mesh.vertices,[.05,.05],'vertex'),{kind:'vertex',vertex_index:104});
  assert.equal(mapping.pick(mesh,mesh.vertices,[2,2],'vertex'),null);
  assert.equal(mapping.barycentric2D([0,0],[0,0],[1,1],[2,2]),null);
});
test('mapping reload rejects wrong topology, bad weights, duplicate indices and unplaced review',()=>{
  const report={model:{model_sha256:'m'},flame_topology_id:'t',session_id:'s',source_mesh_id:'a',flame_vertex_count:5023,flame_triangle_count:9976,arkit_analog_catalog:[{arkit_index:14}]};
  const draft={version:'flame-arkit-analogs-v1',model_sha256:'m',topology_id:'t',session_id:'s',source_mesh_id:'a',points:[{arkit_index:14,status:'reviewed',attachment:{kind:'vertex',vertex_index:3564},radius_fraction_eye_span:.12,multiplier:4,notes:''}]};
  assert.equal(mapping.validate(draft,report),draft);
  assert.throws(()=>mapping.validate({...draft,topology_id:'wrong'},report));
  const bad=structuredClone(draft);bad.points[0].attachment=null;assert.throws(()=>mapping.validate(bad,report));
  assert.throws(()=>mapping.validate({...draft,points:[...draft.points,...draft.points]},report));
  const badWeight=structuredClone(draft);badWeight.points[0].multiplier=Infinity;assert.throws(()=>mapping.validate(badWeight,report));
});
