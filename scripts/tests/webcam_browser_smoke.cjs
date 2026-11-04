// Run after starting the preview and processor; this uses Chrome's fake camera only.
const path=require('node:path');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 await page.addInitScript(()=>{
   window.captureSpeech=[];window.captureSpeechTimes=[];window.captureSpeechCancellations=0;
   Object.defineProperty(window,'SpeechSynthesisUtterance',{value:class {constructor(text){this.text=text;}}});
   Object.defineProperty(window,'speechSynthesis',{value:{
     getVoices:()=>[{localService:true,lang:'en-US'}],
     speak:utterance=>{window.captureSpeech.push(utterance.text);window.captureSpeechTimes.push(performance.now());},
     cancel:()=>window.captureSpeechCancellations++,addEventListener(){},removeEventListener(){},
   }});
 });
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error') console.log('browser:',m.text())});
 await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
 await page.getByRole('button',{name:'Connect processor',exact:true}).click();
 await page.getByText('Connected to private local processor.').waitFor();
 await page.getByRole('button',{name:'New session',exact:true}).click();
 await page.getByRole('button',{name:'Enable camera',exact:true}).waitFor();
 await page.getByRole('button',{name:'Test audio',exact:true}).click();
 await page.getByRole('checkbox',{name:'I consent to storing and processing these captures locally.'}).check();
 await page.getByRole('button',{name:'Enable camera',exact:true}).click();
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.mask-editor')?.width>300 || document.querySelector('[role=alert]'),{},{timeout:60000});
 const alert=await page.locator('[role=alert]').allTextContents(); if(alert.length) throw Error(alert.join('\n'));
 const spoken=await page.evaluate(()=>window.captureSpeech);
 if(JSON.stringify(spoken)!==JSON.stringify(['Frame one.','3','2','1','Frontal captured.']))throw Error('Capture speech did not follow countdown and shutter: '+JSON.stringify(spoken));
 await page.getByRole('checkbox',{name:'Speak countdown and capture cues',exact:true}).uncheck();
 await page.getByRole('checkbox',{name:'Include brush',exact:true}).check();
 const box=await page.locator('.mask-editor').boundingBox();
 await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5,{steps:5});await page.mouse.up();
 await page.getByRole('heading',{name:'Capture and mask review',exact:true}).click();
 await page.keyboard.press('a');
 await page.getByText('1/61 approved images saved locally',{exact:false}).waitFor();
 console.log('fake camera capture + segmentation + brush correction + approval: PASS');
 const reviewSelect=page.getByLabel(/^Capture to review/);
 await page.waitForFunction(()=>[...document.querySelectorAll('select')].some(s=>s.value==='1' && !s.disabled && s.closest('label')?.textContent.startsWith('Capture to review')));
 for(const [key,index] of [['ArrowRight','2'],['ArrowLeft','1'],['ArrowLeft','0']]){
   await page.keyboard.press(key);
   await page.waitForFunction(index=>[...document.querySelectorAll('select')].some(s=>s.value===index && !s.disabled && s.closest('label')?.textContent.startsWith('Capture to review')),index);
 }
 await page.getByRole('button',{name:'Approve and save this head-only mask',exact:true}).waitFor({state:'visible'});
 await page.waitForFunction(()=>![...document.querySelectorAll('button')].find(b=>b.textContent==='Approve and save this head-only mask')?.disabled);
 await reviewSelect.focus();await page.keyboard.press('a');
 if(await reviewSelect.inputValue()!=='0')throw Error('Approval shortcut fired inside dropdown');
 await page.getByRole('heading',{name:'Capture and mask review',exact:true}).click();
 await page.keyboard.press('ArrowLeft');
 if(await reviewSelect.inputValue()!=='0')throw Error('Previous-frame shortcut moved past first frame');
 await page.keyboard.press('a');
 await page.waitForFunction(()=>[...document.querySelectorAll('select')].some(s=>s.value==='1' && s.closest('label')?.textContent.startsWith('Capture to review')));
 await page.keyboard.press('a');
 if(await reviewSelect.inputValue()!=='1')throw Error('An unavailable frame was approved');
 console.log('keyboard previous/next + approve-and-advance + dropdown/boundary guards: PASS');
 await reviewSelect.selectOption('0');
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.getByRole('button',{name:'Approve and save this head-only mask',exact:true}).waitFor({state:'visible'});
 await page.waitForTimeout(5000);
 const alerts=await page.locator('[role=alert]').allTextContents(); if(alerts.length) throw Error(alerts.join('\n'));
 if(await page.evaluate(()=>window.captureSpeech.length)!==spoken.length)throw Error('Muted capture still spoke');
 console.log('spoken capture countdown + shutter cue + mute: PASS');
 console.log('retake capture: PASS');
 await page.getByRole('checkbox',{name:'Speak countdown and capture cues',exact:true}).check();
 if(await page.getByLabel(/^Sweep duration/).inputValue()!=='10')throw Error('Sweep duration does not default to ten seconds');
 const speechStart=await page.evaluate(()=>window.captureSpeech.length);
 await page.getByRole('button',{name:'Capture all 60 frames',exact:true}).click();
 await page.getByRole('button',{name:'Capture all 60 frames',exact:true}).waitFor({state:'visible'});
 await page.waitForFunction(()=>![...document.querySelectorAll('button')].find(b=>b.textContent==='Capture all 60 frames')?.disabled,{},{timeout:25000});
 const sweepCues=await page.evaluate(start=>({words:window.captureSpeech.slice(start),times:window.captureSpeechTimes.slice(start)}),speechStart);
 const expected=['Right profile. Three.','2','1','10','9','8','7','6','Face camera.','4','3','2','1','Left profile. Done.'];
 if(JSON.stringify(sweepCues.words)!==JSON.stringify(expected))throw Error('Unexpected sweep audio: '+JSON.stringify(sweepCues.words));
 const midpoint=sweepCues.times[8]-sweepCues.times[3],duration=sweepCues.times[13]-sweepCues.times[3];
 if(Math.abs(midpoint-5000)>300 || Math.abs(duration-10000)>300)throw Error('Sweep countdown timing drifted');
 const frameCount=await reviewSelect.locator('option').evaluateAll(options=>options.filter(o=>o.value!=='0' && o.textContent.includes('review needed')).length);
 if(frameCount!==60)throw Error(`Expected 60 captured sweep frames, got ${frameCount}`);
 console.log('60-frame ten-second sweep + five-second frontal audio cue: PASS');
 const forbidden=await page.request.get('http://127.0.0.1:5178/.private-webcam-runs/processor.lock');
 if(forbidden.status()!==403) throw Error('Private Vite route status '+forbidden.status());
 const fsForbidden=await page.request.get('http://127.0.0.1:5178/@fs/Users/eddericugaddan/code/breathesafe/.private-webcam-runs/processor.lock');
 if(fsForbidden.status()!==403)throw Error('Private @fs route status '+fsForbidden.status());
 const caseForbidden=await page.request.get('http://127.0.0.1:5178/.PRIVATE-WEBCAM-RUNS/processor.lock');
 if(caseForbidden.status()!==403)throw Error('Case-insensitive private route status '+caseForbidden.status());
 console.log('Vite private directory + @fs denial: PASS');
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Export session',exact:true}).click();const download=await downloadPromise;await download.saveAs('/tmp/breathesafe-fake-webcam-session.zip');
 await page.getByRole('button',{name:'Delete this local session',exact:true}).click();
 await page.getByLabel('Reload exported session').setInputFiles('/tmp/breathesafe-fake-webcam-session.zip');
 await page.getByText('1/61 approved images saved locally',{exact:false}).waitFor();
 console.log('export + delete + reload: PASS');
 await page.screenshot({path:'/tmp/breathesafe-webcam-pilot.png',fullPage:true});
 await page.getByRole('button',{name:'Delete this local session',exact:true}).click();
 // An analytic triangle is a browser-only mock, never a processor reconstruction fallback.
 const id='a'.repeat(32), camera={width:720,height:480,fx:500,fy:500,cx:360,cy:240,k:0,mirrored:false,units:'reconstruction_unit',R:[[1,0,0],[0,1,0],[0,0,1]],t:[0,0,0]};
 const raw=[{x:.5,y:.5,z:0}], point={index:0,raw:raw[0],status:'ok',acceptance:'pending',point:[0,0,5],units:'reconstruction_unit',attachment:{kind:'barycentric',triangle_index:0,weights:[.25,.25,.5]}};
 const fixture={id,created_at:'analytic browser fixture',status:'surface_ready',captures:[],result:{surface:{units:'reconstruction_unit',source:{domain:'analytic'},mesh:{vertices:[[-2,-2,5],[2,-2,5],[0,2,5]],triangles:[[0,1,2]]}},cameras:{front:camera},frontal_camera_key:'front',raw_predictions:raw,projected_points:[point],diagnostics:{}}};
 let draft;
 await page.route('http://127.0.0.1:5182/**',async route=>{
   const request=route.request(), pathname=new URL(request.url()).pathname;
   const headers={'Access-Control-Allow-Origin':'http://127.0.0.1:5178','Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'GET, POST, OPTIONS'};
   if(request.method()==='OPTIONS')return route.fulfill({status:204,headers});
   if(pathname.endsWith('/frontal'))return route.fulfill({headers,contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')});
   let result=fixture;
   if(pathname==='/diagnostics')result={ready:true};
   if(pathname==='/sessions')result=[fixture];
   if(pathname.endsWith('/draft')){draft=request.postDataJSON();fixture.draft=draft;}
   if(pathname.endsWith('/decisions')){point.acceptance=request.postDataJSON().decision;}
   return route.fulfill({headers,contentType:'application/json',body:JSON.stringify(result)});
 });
 await page.getByRole('button',{name:'Connect processor',exact:true}).click();
 await page.getByLabel('Saved session').selectOption(id);await page.getByRole('button',{name:'Resume',exact:true}).click();
 await page.getByRole('heading',{name:'Rotatable surface',exact:true}).waitFor();
 const surface=page.getByRole('img',{name:'Rotate surface; Control-click to trace tape route',exact:true});
 const originalPoints=await surface.locator('polygon').first().getAttribute('points');
 await page.getByRole('button',{name:'¾ view left',exact:true}).click();
 if(await surface.locator('polygon').first().getAttribute('points')===originalPoints)throw Error('Quarter-view control did not rotate surface');
 await page.getByRole('button',{name:'Reset view / fit surface',exact:true}).click();
 if(await surface.locator('polygon').first().getAttribute('points')!==originalPoints)throw Error('Reset did not restore framing');
 await page.getByRole('checkbox',{name:'Show mesh edges',exact:true}).check();
 if(await surface.locator('polygon').first().getAttribute('stroke')==='none')throw Error('Mesh edges did not enable');
 if(!await page.getByRole('checkbox',{name:'Smooth lighting',exact:true}).isChecked())throw Error('Smooth lighting is not enabled by default');
 const originalFill=await surface.locator('polygon').first().getAttribute('fill');
 await page.getByLabel('Light direction',{exact:true}).evaluate(input=>{input.value='80';input.dispatchEvent(new Event('input',{bubbles:true}));});
 if(await surface.locator('polygon').first().getAttribute('fill')===originalFill)throw Error('Light direction did not change shading');
 if(await surface.locator('polygon').first().getAttribute('points')!==originalPoints)throw Error('Lighting changed geometry projection');
 console.log('surface framing + lighting + quarter views + mesh edges: PASS');
 const bounds=await surface.boundingBox();
 for(const [label,x,y] of [['left_tragion',.4,.4],['subnasale',.5,.6],['right_tragion',.6,.4]]){
   await page.getByLabel(/^Next point/).selectOption(label);
   await page.keyboard.down('Control');await page.mouse.click(bounds.x+bounds.width*x,bounds.y+bounds.height*y);await page.keyboard.up('Control');
 }
 await page.getByText('Mesh-edge route:',{exact:false}).waitFor();
 await page.getByRole('button',{name:'Save route draft locally',exact:true}).click();
 await page.getByText('Route draft saved locally.',{exact:true}).waitFor();
 if(!draft || draft.scale_route.length!==3 || draft.scale_route.some(a=>Math.abs(a.weights.reduce((x,y)=>x+y,0)-1)>1e-8))throw Error('Invalid barycentric route draft');
 await page.getByRole('button',{name:'accepted',exact:true}).click();
 await page.getByText('"acceptance": "accepted"',{exact:false}).waitFor();
 console.log('analytic surface rendering + route picking + draft + point review: PASS');
 await browser.close();if(errors.length)throw Error(errors.join('\n'));
})().catch(e=>{console.error(e);process.exit(1)});
