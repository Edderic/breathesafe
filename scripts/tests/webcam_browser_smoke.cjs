// Run after starting the preview and processor; this uses Chrome's fake camera only.
const path=require('node:path');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error') console.log('browser:',m.text())});
 await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
 await page.getByRole('button',{name:'Connect processor',exact:true}).click();
 await page.getByText('Connected to private local processor.').waitFor();
 await page.getByRole('button',{name:'New session',exact:true}).click();
 await page.getByRole('button',{name:'Enable camera',exact:true}).waitFor();
 await page.getByRole('checkbox',{name:'I consent to storing and processing these captures locally.'}).check();
 await page.getByRole('button',{name:'Enable camera',exact:true}).click();
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.mask-editor')?.width>300 || document.querySelector('[role=alert]'),{},{timeout:60000});
 const alert=await page.locator('[role=alert]').allTextContents(); if(alert.length) throw Error(alert.join('\n'));
 await page.getByRole('checkbox',{name:'Include brush',exact:true}).check();
 const box=await page.locator('.mask-editor').boundingBox();
 await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.6,box.y+box.height*.5,{steps:5});await page.mouse.up();
 await page.getByRole('button',{name:'Approve and save this head-only mask',exact:true}).click();
 await page.getByText('1/61 approved images saved locally',{exact:false}).waitFor();
 console.log('fake camera capture + segmentation + brush correction + approval: PASS');
 await page.locator('select').nth(1).selectOption('0');
 await page.getByRole('button',{name:'Capture frontal',exact:true}).click();
 await page.getByRole('button',{name:'Approve and save this head-only mask',exact:true}).waitFor({state:'visible'});
 await page.waitForTimeout(5000);
 const alerts=await page.locator('[role=alert]').allTextContents(); if(alerts.length) throw Error(alerts.join('\n'));
 console.log('retake capture: PASS');
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
