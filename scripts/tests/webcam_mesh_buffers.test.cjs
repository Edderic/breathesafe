const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('app/javascript/webcam_mesh_buffers.js','utf8').replaceAll('export ','');
const api=vm.runInNewContext(source+';({parseInspectionPLY,analysisBuffers,prepareInspectionMesh,sharedInspectionFrame})',{TextDecoder,Float32Array,Uint32Array,Uint8Array,ArrayBuffer,DataView});
const camera={R:[[0,0,1],[0,1,0],[-1,0,0]],t:[2,3,4]};
const fixture={vertices:[[0,0,0],[2,0,0],[0,2,0]],triangles:[[0,1,2]]};
function ply(body='0 0 0\n2 0 0\n0 2 0\n3 0 1 2'){
 const data=Buffer.from('ply\nformat ascii 1.0\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\nelement face 1\nproperty list uchar uint vertex_indices\nend_header\n'+body);
 return data.buffer.slice(data.byteOffset,data.byteOffset+data.length);
}
test('PLY decoding preserves vertex order/topology and rejects repair or truncated inputs',()=>{
 const parsed=api.parseInspectionPLY(ply());assert.deepEqual(Array.from(parsed.positions),fixture.vertices.flat());assert.deepEqual(Array.from(parsed.indices),[0,1,2]);
 for(const body of ['0 0 0\n2 0 0\n0 2 0\n4 0 1 2 0','0 0 0\n2 0 0\n0 2 0\n3 0 1 9','0 0 0\n2 0 0','NaN 0 0\n2 0 0\n0 2 0\n3 0 1 2'])assert.throws(()=>api.parseInspectionPLY(ply(body)));
 const oversized=Buffer.from(new Uint8Array(ply())).toString().replace('vertex 3','vertex 1000001');
 assert.throws(()=>api.parseInspectionPLY(Uint8Array.from(Buffer.from(oversized)).buffer),/limits/);
});
test('binary little/big endian PLY and optional properties preserve the same geometry',()=>{
 for(const little of [true,false]){
  const header=Buffer.from(`ply\nformat binary_${little?'little':'big'}_endian 1.0\nelement vertex 3\nproperty double x\nproperty double y\nproperty double z\nproperty uchar red\nelement face 1\nproperty list uchar uint vertex_indices\nend_header\n`);
  const bytes=new Uint8Array(header.length+3*25+13);bytes.set(header);const view=new DataView(bytes.buffer);let offset=header.length;
  for(const p of fixture.vertices){for(const v of p){view.setFloat64(offset,v,little);offset+=8;}view.setUint8(offset++,255);}
  view.setUint8(offset++,3);for(const i of [0,1,2]){view.setUint32(offset,i,little);offset+=4;}
  assert.deepEqual(Array.from(api.parseInspectionPLY(bytes.buffer).positions),fixture.vertices.flat());
 }
});
test('shared coordinates and one uniform calibration transform align matching vertices across reordered meshes',()=>{
 const original=JSON.stringify(fixture),other={vertices:[fixture.vertices[2],fixture.vertices[0],fixture.vertices[1]],triangles:[[1,2,0]]};
 const a=api.prepareInspectionMesh(api.analysisBuffers(fixture),camera,10),b=api.prepareInspectionMesh(api.analysisBuffers(other),camera,10);
 assert.deepEqual(Array.from(a.positions.slice(0,3)),Array.from(b.positions.slice(3,6)));
 const frame=api.sharedInspectionFrame([a,b]);
 for(const mesh of [a,b])for(let i=0;i<mesh.positions.length;i+=3)assert.ok(Math.hypot(...frame.center.map((c,j)=>(mesh.positions[i+j]-c)*frame.scale))<=190.0001);
 assert.equal(JSON.stringify(fixture),original);assert.deepEqual(Array.from(a.indices),[0,1,2]);assert.deepEqual(Array.from(b.indices),[1,2,0]);
 const unscaled=api.prepareInspectionMesh(api.analysisBuffers(fixture),{R:camera.R,t:camera.t.map(v=>v/10)},1);
 assert.ok(Math.abs(api.sharedInspectionFrame([unscaled]).scale/frame.scale-10)<1e-6);
});
test('invalid and degenerate display geometry fails without changing the annotation source',()=>{
 const original=JSON.stringify(fixture);
 assert.throws(()=>api.prepareInspectionMesh(api.analysisBuffers(fixture),camera,0));
 assert.throws(()=>api.prepareInspectionMesh(api.analysisBuffers({...fixture,triangles:[[0,0,1]]}),camera));
 assert.throws(()=>api.prepareInspectionMesh(api.analysisBuffers({vertices:[[0,0,0],[1e25,0,0],[0,1e25,0]],triangles:[[0,1,2]]}),camera),/numeric range/);
 assert.equal(JSON.stringify(fixture),original);
});
