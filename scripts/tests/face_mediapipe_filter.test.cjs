const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '../..');
const canonicalRegions = JSON.parse(fs.readFileSync(path.join(root, 'python/dimension_pipeline/assets/mediapipe_regions.json')));
const context = { canonicalRegions };
vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/face_mediapipe_filter.js'),'utf8').replace(/^import .*;\n/gm,'').replace(/export /g,''),context);
const { filterObservation, filterResults, validateViewFilter } = context;
const hit = index => ({ index, status:'ok', raw:{x:.5,y:.5,z:0}, point_mm:[0,0,1], attachment:{kind:'barycentric',triangle_index:0,weights:[1,0,0]} });
const camera = (yaw=0,pitch=0)=>({yaw,pitch});

test('canonical regions cover all 478 indices once with known side and midline anchors',()=>{
 const all=Object.values(canonicalRegions.regions).flat();assert.equal(all.length,478);assert.equal(new Set(all).size,478);
 assert.ok(canonicalRegions.regions.central.includes(1));assert.ok(canonicalRegions.regions.central.includes(152));
 assert.ok(canonicalRegions.regions.right.includes(33));assert.ok(canonicalRegions.regions.left.includes(263));
 assert.ok(canonicalRegions.regions.left.includes(423));
 for(let i=468;i<473;i++)assert.ok(canonicalRegions.regions.right.includes(i));
 for(let i=473;i<478;i++)assert.ok(canonicalRegions.regions.left.includes(i));
});
test('frontal keeps both sides; oblique keeps subject near side, independent of predicted screen position',()=>{
 for(const i of [1,33,263])assert.equal(filterObservation(hit(i),camera()).observation_status,'accepted');
 assert.equal(filterObservation(hit(263),camera(-45)).observation_status,'accepted');
 assert.equal(filterObservation(hit(33),camera(-45)).rejection_reason,'far_side');
 assert.equal(filterObservation(hit(33),camera(45)).observation_status,'accepted');
 assert.equal(filterObservation(hit(263),camera(45)).rejection_reason,'far_side');
 assert.equal(filterObservation(hit(1),camera(45)).rejection_reason,'central_requires_frontal');
 const moved={...hit(33),raw:{x:.99,y:.01,z:-99},point_mm:[999,999,999]};
 assert.equal(filterObservation(moved,camera(-45)).rejection_reason,'far_side');
});
test('view limits are explicit; raw mode retains successful hits without repairing missing geometry',()=>{
 assert.equal(filterObservation(hit(1),camera(15,20)).observation_status,'accepted');
 assert.equal(filterObservation(hit(1),camera(15.01)).rejection_reason,'central_requires_frontal');
 assert.equal(filterObservation(hit(263),camera(-60)).observation_status,'accepted');
 assert.equal(filterObservation(hit(263),camera(-60.01)).rejection_reason,'yaw_outside_policy');
 assert.equal(filterObservation(hit(263),camera(-45,20.01)).rejection_reason,'tilt_outside_policy');
 assert.equal(filterObservation(hit(1),camera(0,35)).rejection_reason,'tilt_outside_policy');
 assert.equal(filterObservation(hit(999),camera()).rejection_reason,'unknown_index_region');
 assert.equal(filterObservation(hit(33),camera(-90,40),'raw').observation_status,'accepted');
 assert.equal(filterObservation({...hit(1),status:'missed_surface'},camera(),'raw').observation_status,'not_projected');
});
test('filtering is reversible, preserves raw attachments, and does not consume manual annotations',()=>{
 const results=[{camera:camera(-45),detections:[hit(33),hit(263)]}], before=JSON.stringify(results);
 const filtered=filterResults(results,'conservative');assert.equal(filtered[0].detections[0].status,'ok');
 assert.equal(filtered[0].detections[0].observation_status,'rejected');assert.equal(filtered[0].detections[1].observation_status,'accepted');
 assert.equal(JSON.stringify(results),before);
 const baseline=filterResults(results,'raw');assert.equal(baseline[0].detections[0].observation_status,'accepted');
 assert.deepEqual(baseline[0].detections[0].attachment,filtered[0].detections[0].attachment);
});
test('legacy reports retain raw mode and edited policy settings are rejected',()=>{
 assert.equal(validateViewFilter(undefined),'raw');
 const policy=vm.runInNewContext('viewFilterPolicy',context);
 assert.equal(validateViewFilter({...policy,mode:'conservative'}),'conservative');
 assert.throws(()=>validateViewFilter({...policy,mode:'conservative',frontal_yaw_degrees:90}));
 assert.throws(()=>validateViewFilter({...policy,mode:'invented'}));
});
