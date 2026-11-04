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
test('one sweep runs from right profile through frontal to left profile', () => {
  const context={};
  vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture.js'),'utf8').replaceAll('export ',''),context);
  assert.match(context.captureGuidance(0),/Designated frontal/);
  assert.match(context.captureGuidance(1),/Frame 1\/60:.*right.*90/);
  assert.match(context.captureGuidance(30),/face directly toward the camera/);
  assert.match(context.captureGuidance(31),/face directly toward the camera/);
  assert.match(context.captureGuidance(60),/Frame 60\/60:.*left.*90/);
});
test('60 frames span ten seconds without accumulating capture work; midpoint is at five seconds',async()=>{
  const context={};
  vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture.js'),'utf8').replaceAll('export ',''),context);
  let clock=0;const captures=[],cues=[];
  const complete=await context.runCaptureSweep({durationSeconds:10,now:()=>clock,wait:async ms=>{clock+=ms;},cancelled:()=>false,
    capture:(index,timing)=>{captures.push({index,...timing});clock+=7;},countdown:remaining=>cues.push([remaining,clock])});
  assert.equal(complete,true);assert.equal(captures.length,60);
  assert.equal(captures[0].elapsed_ms,0);assert.equal(captures[59].elapsed_ms,10000);
  assert.ok(captures[29].elapsed_ms<5000 && captures[30].elapsed_ms>5000);
  assert.deepEqual(cues.find(([remaining])=>remaining===5),[5,5000]);
  assert.equal(cues.at(-1)[0],0);
  assert.throws(()=>context.sweepSchedule(5));
});
test('sweep cancellation stops frames and missed deadlines fail instead of bursting late captures',async()=>{
  const context={};
  vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture.js'),'utf8').replaceAll('export ',''),context);
  let clock=0,frames=0;
  const complete=await context.runCaptureSweep({durationSeconds:10,now:()=>clock,wait:async ms=>{clock+=ms;},cancelled:()=>frames===3,capture:()=>frames++,countdown:()=>{}});
  assert.equal(complete,false);assert.equal(frames,3);
  clock=0;frames=0;
  await assert.rejects(context.runCaptureSweep({durationSeconds:10,now:()=>clock,wait:async ms=>{clock+=ms+1000;},cancelled:()=>false,capture:()=>frames++,countdown:()=>{}}),/fell behind/);
  assert.equal(frames,1);
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
