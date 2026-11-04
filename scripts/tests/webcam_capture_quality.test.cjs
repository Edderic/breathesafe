const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'../..');
const context={qualityPolicy:JSON.parse(fs.readFileSync(path.join(root,'python/dimension_pipeline/capture_quality_policy.json')))};
vm.runInNewContext(fs.readFileSync(path.join(root,'app/javascript/webcam_capture_quality.js'),'utf8').replace(/^import .*;\n/gm,'').replaceAll('export ',''),context);
function fixture({flat=false,small=false,edge=false,empty=false}={}) {
 const width=80,height=80,data=new Uint8ClampedArray(width*height*4),mask=new Uint8ClampedArray(data.length);
 for(let y=0;y<height;y++)for(let x=0;x<width;x++) {
   const i=(y*width+x)*4,v=flat ? 110:Math.floor(x/3)%2===Math.floor(y/3)%2 ? 40:220;
   data.set([v,v,v,255],i);
   const foreground=!empty && x>=(edge?0:10) && x<70 && y>=10 && y<(small?35:70);
   const m=foreground?255:0;mask.set([m,m,m,255],i);
 }
 return [{width,height,data},{width,height,data:mask}];
}
test('sharp structured image scores above a uniform head; pixels stay unchanged',()=>{
 const [image,mask]=fixture(),copy=Array.from(image.data),result=context.captureQuality(image,mask);
 assert.ok(result.sharpness>40);assert.equal(result.status,'no_flags');
 const flat=context.captureQuality(...fixture({flat:true}));assert.equal(flat.sharpness,0);assert.ok(flat.flags.includes('low_sharpness_or_low_texture'));
 assert.deepEqual(Array.from(image.data),copy);assert.equal(result.policy.automatic_exclusion,false);
});
test('mask framing flags small/edge heads and missing masks stay unavailable',()=>{
 assert.ok(context.captureQuality(...fixture({small:true})).flags.includes('head_small_in_frame'));
 assert.ok(context.captureQuality(...fixture({edge:true})).flags.includes('head_near_image_edge'));
 const empty=context.captureQuality(...fixture({empty:true}));assert.equal(empty.status,'unavailable');assert.equal(empty.sharpness,null);
 assert.throws(()=>context.captureQuality(fixture()[0],{width:1,height:1,data:[]}));
});
