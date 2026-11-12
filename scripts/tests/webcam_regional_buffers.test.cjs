const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('app/javascript/webcam_regional_buffers.js','utf8').replaceAll('export ','');
const api=vm.runInNewContext(source+';({selectInspectionFaces,regionalFrame})',{Float32Array,Uint32Array});
test('regional display extraction preserves source coordinates and face order without changing original topology',()=>{
 const buffers={positions:new Float32Array([0,0,0,1,0,0,0,1,0,1,1,0]),indices:new Uint32Array([0,1,2,1,3,2])},before=Array.from(buffers.indices);
 const region=api.selectInspectionFaces(buffers,[1]);assert.deepEqual(Array.from(region.positions),[1,0,0,1,1,0,0,1,0]);assert.deepEqual(Array.from(region.indices),[0,1,2]);assert.deepEqual(Array.from(buffers.indices),before);
 for(const ids of [[],[2],[-1],[0,0],[.5]])assert.throws(()=>api.selectInspectionFaces(buffers,ids));
});
test('regional framing uses the same fixed raw volume for every geometry stage',()=>{
 const region={chains:[[[0,0,0],[0,2,0]]],radius:1},camera={R:[[1,0,0],[0,1,0],[0,0,1]],t:[1,2,3]};
 const frame=api.regionalFrame(region,camera);assert.deepEqual(Array.from(frame.center),[1,-3,-3]);assert.equal(frame.scale,85);
 assert.throws(()=>api.regionalFrame({chains:[],radius:1},camera));
});
