// Fake webcam and deterministic masks exercise batch acceptance against the local processor.
const path=require('node:path');
const assert=require('node:assert/strict');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],attempts=[];
 let identity;
 page.on('pageerror',e=>errors.push(e.message));
 const worker=`self.onmessage=({data:{id,image}})=>{const values=new Uint8ClampedArray(64);for(let y=2;y<6;y++)for(let x=2;x<6;x++)values[y*8+x]=255;self.postMessage({id,width:8,height:8,values,provenance:{sdk_version:'browser-test',model_sha256:'deterministic-test-mask',correction:'none'}});image.close();};`;
 await page.route('**/mediapipe/webcam_mask_worker.js',r=>r.fulfill({contentType:'application/javascript',body:worker}));
 let failOnce=true,slowOnce=true,slowSave;
 const slowRequest=new Promise(resolve=>{slowSave=resolve;});
 await page.route('http://127.0.0.1:5182/sessions/*/capture',async route=>{
   if(route.request().method()!=='POST')return route.continue();
   const payload=route.request().postDataJSON();attempts.push(payload.slot);
   if(payload.slot==='turn_01' && slowOnce){slowOnce=false;slowSave();await new Promise(resolve=>setTimeout(resolve,500));}
   if(payload.slot==='turn_02' && failOnce){failOnce=false;return route.fulfill({status:422,contentType:'application/json',headers:{'Access-Control-Allow-Origin':'http://127.0.0.1:5178'},body:JSON.stringify({error:'Injected test save failure'})});}
   return route.continue();
 });
 try{
   await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
   await page.getByRole('button',{name:'New session',exact:true}).click();
   await page.getByRole('button',{name:'Enable camera',exact:true}).waitFor();
   identity=await page.locator('p').filter({hasText:/^Session [a-f0-9]{32}/}).evaluate(el=>el.textContent.match(/Session ([a-f0-9]{32})/)[1]);
   await page.getByRole('checkbox',{name:'Speak countdown and capture cues',exact:true}).uncheck();
   await page.getByRole('checkbox',{name:'I consent to storing and processing these captures locally.'}).check();
   await page.getByRole('button',{name:'Enable camera',exact:true}).click();
   await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
   await page.waitForFunction(()=>![...document.querySelectorAll('button')].find(b=>b.textContent==='Approve and save this head-only mask')?.disabled);
   await page.getByRole('checkbox',{name:'Include brush',exact:true}).check();
   const box=await page.locator('.mask-editor').boundingBox();
   await page.mouse.click(box.x+box.width*.1,box.y+box.height*.1);
   await page.getByRole('button',{name:'Accept all frames',exact:true}).click();
   await page.getByText('Accepted: 1 / 1 frames saved. 60 captures still need to be saved.',{exact:true}).waitFor();
   const getState=()=>page.evaluate(async id=>{const response=await fetch('http://127.0.0.1:5182/sessions/'+id);return response.json();},identity);
   let state=await getState();assert.equal(state.captures.length,1);
   assert.equal(state.captures[0].mask_provenance.acceptance_method,'bulk');assert.equal(state.captures[0].mask_provenance.manual_edits,true);
   assert.equal(state.captures[0].mask_provenance.review_status,'accepted_without_individual_review');
   const edited=await page.evaluate(async id=>{const image=await createImageBitmap(await(await fetch(`http://127.0.0.1:5182/sessions/${id}/captures/front/mask`)).blob());const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);return ctx.getImageData(Math.floor(image.width*.1),Math.floor(image.height*.1),1,1).data[0];},identity);
   assert.equal(edited,255);console.log('bulk acceptance saves available frames, preserves brush edits and records provenance: PASS');
   await page.getByRole('button',{name:'Capture all 60 frames',exact:true}).click();
   await page.waitForFunction(()=>![...document.querySelectorAll('button')].find(b=>b.textContent==='Capture all 60 frames')?.disabled,{},{timeout:25000});
   await page.getByRole('button',{name:'Accept all frames',exact:true}).click();await slowRequest;
   await page.getByRole('button',{name:'Stop accepting',exact:true}).click();
   await page.getByText(/Stopped accepting: 2 \/ 60 frames saved/).waitFor();
   state=await getState();assert.equal(state.captures.length,3);assert.equal(attempts.filter(slot=>slot==='front').length,1);
   console.log('batch cancellation retains completed saves and skips already saved frames: PASS');
   await page.getByRole('button',{name:'Accept all frames',exact:true}).click();
   await page.getByRole('alert').filter({hasText:'Injected test save failure'}).waitFor();
   state=await getState();assert.equal(state.captures.length,3);
   console.log('batch failure stops at the affected frame without discarding earlier saves: PASS');
   await page.getByRole('button',{name:'Accept all frames',exact:true}).click();
   await page.getByText('Accepted: 58 / 58 frames saved. 0 captures still need to be saved.',{exact:true}).waitFor({timeout:120000});
   state=await getState();assert.equal(state.captures.length,61);
   assert.equal(attempts.filter(slot=>slot==='turn_00').length,1);assert.equal(attempts.filter(slot=>slot==='turn_01').length,1);assert.equal(attempts.filter(slot=>slot==='turn_02').length,2);
   assert.equal(await page.getByRole('button',{name:'Reconstruct approved images',exact:true}).isEnabled(),true);
   assert.deepEqual(errors,[]);console.log('retry accepts all remaining frames and enables reconstruction: PASS');
 }finally{
   if(identity)await page.evaluate(async id=>fetch(`http://127.0.0.1:5182/sessions/${id}/delete`,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}),identity);
   await browser.close();
 }
})().catch(error=>{console.error(error);process.exitCode=1;});
