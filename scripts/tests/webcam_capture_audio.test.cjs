const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = {};
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../../app/javascript/webcam_capture_audio.js'),'utf8').replaceAll('export ',''),context);
function setup(voices) {
  const spoken=[], messages=[], listeners=new Set(), timers=new Set(); let cancellations=0;
  const synth={getVoices:()=>voices, cancel:()=>cancellations++, speak:u=>spoken.push(u),
    addEventListener:(_,fn)=>listeners.add(fn),removeEventListener:(_,fn)=>listeners.delete(fn)};
  const env={speechSynthesis:synth,SpeechSynthesisUtterance:function(text){this.text=text;},
    setTimeout:fn=>{timers.add(fn);return fn;}, clearTimeout:fn=>timers.delete(fn)};
  return {audio:context.createCaptureAudio(env,m=>messages.push(m)),spoken,messages,listeners,timers,cancelCount:()=>cancellations};
}
const local={localService:true,lang:'en-US'};
test('manual frame cues number the full sweep and identify the frontal photo',()=>{
  assert.equal(context.capturedFrameCue(0),'Frontal captured.');
  for(const [index,number] of [[1,1],[30,30],[31,31],[60,60]]) assert.equal(context.capturedFrameCue(index),`Frame ${number}.`);
  assert.equal(context.capturedFrameCue(30,true),'30.');
  assert.equal(context.capturedFrameCue(31,true),'31.');
  assert.equal(context.capturedFrameCue(0,true),'Frontal captured.');
});
test('cues use a local English voice and replace queued speech',()=>{
  const s=setup([{localService:false,lang:'en-US'},local]);
  s.audio.speak('3');s.audio.speak('Frame 1.');
  assert.deepEqual(s.spoken.map(u=>u.text),['3','Frame 1.']);assert.equal(s.spoken[1].voice,local);
  assert.equal(s.cancelCount(),2);assert.equal(s.timers.size,0);assert.equal(s.listeners.size,0);
  s.audio.cancel();assert.equal(s.cancelCount(),3);
  s.audio.speak('30.',2.2);assert.equal(s.spoken.at(-1).rate,2.2);
});
test('delayed voice loading cannot speak a cue after cancellation',()=>{
  const voices=[],s=setup(voices);s.audio.speak('Frame 1.');
  const stale=[...s.listeners][0];s.audio.cancel();voices.push(local);stale();
  assert.equal(s.spoken.length,0);assert.equal(s.listeners.size,0);assert.equal(s.timers.size,0);
});
test('voice loading succeeds without remote fallback and reports missing local voices',()=>{
  const voices=[],s=setup(voices);s.audio.speak('Frame 1.');voices.push(local);[...s.listeners][0]();assert.equal(s.spoken.length,1);
  const missing=setup([{localService:false,lang:'en-US'}]);missing.audio.speak('Frame 2.');[...missing.timers][0]();
  assert.equal(missing.spoken.length,0);assert.match(missing.messages[0],/No local English voice/);
  const messages=[];context.createCaptureAudio({},m=>messages.push(m)).speak('3');assert.match(messages[0],/unavailable/);
});
