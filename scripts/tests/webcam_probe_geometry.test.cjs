const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const api=vm.runInNewContext(fs.readFileSync('app/javascript/webcam_probe_geometry.js','utf8').replaceAll('export ','')+';({probeFrame,probeMark,probeSectionPlot})');
test('diagnostic view uses viewer camera signs and exact selection-centered marker',()=>{
 const camera={R:[[1,0,0],[0,1,0],[0,0,1]],t:[0,0,0]},p=[1,2,5],frame=api.probeFrame(p,camera,.5);
 assert.deepEqual(Array.from(frame.center),[1,-2,-5]);assert.equal(frame.scale,340);
 for(const [yaw,pitch] of [[0,0],[65,35],[-45,-30]])assert.deepEqual(Array.from(api.probeMark(p,camera,frame,yaw,pitch,2)),[360,240]);
 const mark=api.probeMark([1.1,2,5],camera,frame,0,0,1);assert.ok(Math.abs(mark[0]-394)<1e-8);assert.equal(mark[1],240);
 assert.throws(()=>api.probeFrame(p,camera,0));
});
test('diagnostic sections preserve equal depth and height display scales',()=>{
 const origin=api.probeSectionPlot([0,0],.2),depth=api.probeSectionPlot([.1,0],.2),height=api.probeSectionPlot([0,.1],.2);
 assert.deepEqual(Array.from(origin),[300,190]);assert.equal(depth[0]-origin[0],origin[1]-height[1]);assert.throws(()=>api.probeSectionPlot([0,0],0));
});
