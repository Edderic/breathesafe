// Requires the research Vite server and scripts/tests/webcam_test_processor.py on 5183.
const path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 await page.route('http://127.0.0.1:5182/**',async route=>{
   const request=route.request();
   const response=await route.fetch({url:request.url().replace(':5182',':5183'),headers:{...request.headers(),host:'127.0.0.1:5183'}});
   await route.fulfill({response});
 });
 await page.route('**/mediapipe/webcam_mask_worker.js',route=>route.fulfill({contentType:'application/javascript',body:`self.onmessage=({data:{id,image}})=>{const values=new Uint8ClampedArray(64);for(let y=2;y<6;y++)for(let x=2;x<6;x++)values[y*8+x]=255;self.postMessage({id,width:8,height:8,values,provenance:{model_sha256:'quality-test-fixture'}});image.close();};`}));
 await page.addInitScript(()=>{
   const original=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
   navigator.mediaDevices.getUserMedia=async constraints=>{
     const stream=await original(constraints),track=stream.getVideoTracks()[0];
     const settings=track.getSettings.bind(track),capabilities=track.getCapabilities.bind(track),base=track.getConstraints.bind(track);
     const state={focusMode:'continuous',focusDistance:2,exposureMode:'continuous',exposureTime:100};let current=base();
     track.getSettings=()=>({...settings(),...state});
     track.getCapabilities=()=>({...capabilities(),focusMode:['continuous','manual'],focusDistance:{min:0,max:10,step:.1},exposureMode:['continuous','manual'],exposureTime:{min:1,max:1000},whiteBalanceMode:[]});
     track.getConstraints=()=>current;
     track.applyConstraints=async value=>{current=value;for(const patch of value.advanced||[])if(patch.focusMode){state.focusMode=patch.focusMode;if(patch.focusDistance!==undefined)state.focusDistance=patch.focusDistance;}};
     return stream;
   };
 });
 await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
 await page.getByText('Optional capture-comparison labels',{exact:true}).click();
 await page.getByLabel('Comparison group',{exact:true}).fill('BRE15-browser-fixture');
 await page.getByLabel('Conditions',{exact:true}).fill('Fake camera; deterministic mask; fixed test settings');
 await page.getByLabel('Repeat',{exact:true}).fill('1');
 await page.getByRole('button',{name:'New session',exact:true}).click();
 const identity=await page.locator('p').filter({hasText:/^Session [a-f0-9]{32}/}).evaluate(el=>el.textContent.match(/Session ([a-f0-9]{32})/)[1]);
 await page.getByRole('checkbox',{name:'Speak countdown and capture cues',exact:true}).uncheck();
 await page.getByRole('checkbox',{name:'I consent to storing and processing these captures locally.'}).check();
 await page.getByRole('button',{name:'Enable camera',exact:true}).click();
 await page.getByRole('button',{name:'Lock selected camera settings',exact:true}).click();
 await page.getByRole('checkbox',{name:/Focus: Locked \(verified\)/}).waitFor();
 await page.getByRole('checkbox',{name:/Exposure: unverified:/}).waitFor();
 await page.getByRole('checkbox',{name:/White balance: Unavailable/}).waitFor();
 await page.getByRole('button',{name:'Restore initial camera settings',exact:true}).click();
 await page.getByText(/Focus: initial mode restored/).waitFor();
 await page.getByRole('checkbox',{name:/Exposure:/}).uncheck();
 await page.getByRole('button',{name:'Lock selected camera settings',exact:true}).click();
 await page.getByRole('checkbox',{name:/Focus: Locked \(verified\)/}).waitFor();
 assert.equal(await page.getByLabel(/^Sweep duration/).inputValue(),'10');
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.getByRole('region',{name:'Frame quality',exact:true}).waitFor();
 assert.equal(await page.getByRole('button',{name:'Lock selected camera settings',exact:true}).isDisabled(),true);
 await page.getByText(/Head is small in the image/).waitFor();
 await page.getByRole('button',{name:'Approve and save this head-only mask',exact:true}).click();
 await page.getByText('1/61 approved images saved locally',{exact:false}).waitFor();
 const row=await page.evaluate(async id=>(await fetch('http://127.0.0.1:5182/sessions/'+id)).json(),identity);
 const frame=row.captures[0];assert.equal(row.capture_context.group,'BRE15-browser-fixture');
 assert.equal(frame.capture_quality.policy.version,'webcam_capture_quality_v1');assert.equal(frame.capture_quality.policy.automatic_exclusion,false);
 assert.equal(frame.camera_controls.attempts.find(a=>a.id==='focus').verified,true);
 assert.equal(frame.camera_settings.focusMode,'manual');assert.deepEqual(frame.capture_quality.image_size,[frame.width,frame.height]);
 await page.getByLabel(/^Capture to review/).selectOption('0');
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.waitForFunction(()=>![...document.querySelectorAll('button')].find(b=>b.textContent==='Approve and save this head-only mask')?.disabled);
 await page.getByRole('button',{name:'Accept all frames',exact:true}).click();
 await page.getByText('Accepted: 1 / 1 frames saved. 60 captures still need to be saved.',{exact:true}).waitFor();
 const retaken=await page.evaluate(async id=>(await fetch('http://127.0.0.1:5182/sessions/'+id)).json(),row.id);
 assert.equal(retaken.captures.length,1);assert.notEqual(retaken.captures[0].timestamp,frame.timestamp);
 assert.ok(retaken.captures[0].capture_quality);assert.deepEqual(errors,[]);
 console.log('quality warnings + verified/ignored/unsupported controls + restore + metadata + retake: PASS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
