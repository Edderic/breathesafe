const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
test('native webcam pixels never mirror or upscale; metadata records actual dimensions', () => {
  const calls = [], canvas = { getContext: () => ({ drawImage: (...args) => calls.push(args) }) };
  const context = { document: { createElement: () => canvas } };
  vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture.js'),'utf8').replaceAll('export ',''),context);
  const video = {videoWidth:1280,videoHeight:720};
  const result = context.captureNativeFrame(video,{width:1280});
  assert.equal(canvas.width,1280); assert.equal(canvas.height,720); assert.equal(result.mirrored,false);
  assert.deepEqual(calls[0],[video,0,0,1280,720]);
  assert.throws(()=>context.captureNativeFrame({videoWidth:0,videoHeight:0},{}));
});
test('both capture passes preserve frame roles and provide chin-lift guidance', () => {
  const context={};
  vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture.js'),'utf8').replaceAll('export ',''),context);
  assert.match(context.captureGuidance(0),/Designated frontal/);
  assert.match(context.captureGuidance(1),/Pass 1, frame 1/);
  assert.match(context.captureGuidance(31),/Pass 2, frame 1.*lift your chin/);
  assert.match(context.captureGuidance(60),/frame 30\/30/);
});
test('unscaled routes never publish millimeter fields', () => {
  const geometry={}; vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/face_annotation_geometry.js'),'utf8').replace(/^import .*;\n/gm,'').replace(/export (async )?function /g,'$1function '),geometry);
  const context={attachmentPoint:geometry.attachmentPoint}; vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/face_surface_paths.js'),'utf8').replace(/^import .*;\n/gm,'').replace(/export function /g,'function '),context);
  const record={units:'reconstruction_unit',mesh:{vertices:[[0,0,0],[1,0,0],[0,1,0]],triangles:[[0,1,2]]}};
  const a={kind:'barycentric',triangle_index:0,weights:[1,0,0]},b={...a,weights:[0,1,0]};
  const result=context.surfacePath(record,context.buildSurfaceGraph(record),a,b);
  assert.equal(result.unit,'reconstruction_unit'); assert.equal(result.length,1);
  assert.equal('length_mm' in result,false); assert.equal('chord_mm' in result,false);
});
