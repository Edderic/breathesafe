const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const context={};
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../../app/javascript/webcam_camera_controls.js'),'utf8').replaceAll('export ',''),context);
function camera({ignore=false,fail=false}={}) {
 const settings={width:1920,height:1080,focusMode:'continuous',focusDistance:2,exposureMode:'continuous',exposureTime:100};
 let constraints={width:{ideal:1920},height:{ideal:1080}},last;
 return {settings,getSettings:()=>({...settings}),getCapabilities:()=>({focusMode:['continuous','manual'],focusDistance:{min:0,max:10,step:.1},exposureMode:['continuous','manual'],exposureTime:{min:1,max:1000}}),getConstraints:()=>constraints,
   applyConstraints:async value=>{last=value;if(fail)throw Error('Device rejected constraint');constraints=value;if(!ignore)for(const patch of value.advanced)Object.assign(settings,patch);},last:()=>last};
}
test('unsupported controls and unreadable values never claim lock support',()=>{
 const controls=context.inspectCameraControls({getSettings:()=>({width:1920})});
 assert.ok(controls.every(c=>!c.supported));
 const track=camera();delete track.settings.focusDistance;
 assert.equal(context.inspectCameraControls(track).find(c=>c.id==='focus').supported,false);
});
test('manual locks preserve resolution/other locks and restoration verifies original mode',async()=>{
 const track=camera(),initial=context.inspectCameraControls(track),focus=initial.find(c=>c.id==='focus'),exposure=initial.find(c=>c.id==='exposure');
 const first=await context.applyCameraControl(track,focus,{mode:'manual',value:2});assert.equal(first.verified,true);
 const second=await context.applyCameraControl(track,exposure,{mode:'manual',value:100});assert.equal(second.verified,true);
 assert.equal(track.last().width.ideal,1920);assert.equal(track.settings.focusMode,'manual');assert.equal(track.settings.exposureMode,'manual');
 const snapshot=context.cameraControlSnapshot(track,[first,second]);assert.ok(snapshot.attempts.every(a=>a.verified));
 track.settings.focusDistance=3;assert.equal(context.cameraControlSnapshot(track,[first]).attempts[0].status,'changed_since_verification');
 const restored=await context.applyCameraControl(track,focus,{mode:'continuous',value:2});assert.equal(restored.verified,true);assert.equal(track.settings.focusMode,'continuous');
});
test('ignored or rejected constraints report failure/unverified instead of a lock',async()=>{
 for(const options of [{ignore:true},{fail:true}]) {
   const track=camera(options),focus=context.inspectCameraControls(track)[0];
   const result=await context.applyCameraControl(track,focus,{mode:'manual',value:2});
   assert.equal(result.verified,false);assert.ok(result.error);
 }
});
