// Analytic fixture by default. Set WEBCAM_COMPARISON_SESSION for read-only pilot inspection.
const path=require('node:path'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
const root=path.resolve(__dirname,'../..'),realId=process.env.WEBCAM_COMPARISON_SESSION;
const id=realId || 'a'.repeat(32),camera={width:720,height:480,fx:500,fy:500,cx:360,cy:240,k:0,mirrored:false,units:'reconstruction_unit',R:[[1,0,0],[0,1,0],[0,0,1]],t:[0,0,0]};
const mesh={vertices:[[-2,-2,5],[2,-2,5],[0,2,5]],triangles:[[0,1,2]]};
const point={index:0,raw:{x:.5,y:.5,z:0},status:'ok',acceptance:'pending',point:[0,0,5],units:'reconstruction_unit',attachment:{kind:'barycentric',triangle_index:0,weights:[.25,.25,.5]}};
let fixture={id,created_at:'analytic fixture',status:'surface_ready',captures:[],result:{full_mesh:'full.ply',surface:{units:'reconstruction_unit',mesh},cameras:{front:camera},frontal_camera_key:'front',raw_predictions:[point.raw],projected_points:[point],diagnostics:{}}};
let full=Buffer.from('ply\nformat ascii 1.0\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\nelement face 1\nproperty list uchar uint vertex_indices\nend_header\n2 -2 6\n-2 -2 6\n0 2 6\n3 0 1 2\n');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const stats={sample_count:100,seed:0,rms:1,p95:1,sampled_max:1};
let report={version:'webcam_mesh_comparison_v1',comparison_source_id:'raw',session_id:id,units:'reconstruction_unit',display_scale:1,annotation_mesh_id:'analytic-topology',variants:[
 {id:'raw',kind:'raw',label:'Full reconstruction',mesh_id:'sha256:'+hash(full),sha256:hash(full),byte_length:full.length,vertices:3,triangles:1,mesh_url:`/sessions/${id}/mesh`,provenance:{operation:'analytic_parallel_offset_fixture'}},
 {id:'analysis',kind:'analysis',label:'Bounded analysis mesh',mesh_id:'analytic-topology',vertices:3,triangles:1,provenance:{operation:'analytic_original_triangle'}}],deviation:{full_to_analysis:stats,analysis_to_full:{...stats,seed:1}}};
if(realId){
 assert.match(realId,/^[a-f0-9]{32}$/);fixture=JSON.parse(fs.readFileSync(path.join(root,'.private-webcam-runs',id,'session.json')));
 full=fs.readFileSync(path.join(root,'.private-webcam-runs',id,fixture.result.full_mesh));
 report=JSON.parse(fs.readFileSync(path.join(root,'.private-webcam-runs/capture-comparisons/bre16-original-pilot.json')));
 assert.equal(report.session_id,id);
}
const before=JSON.stringify(fixture),beforeHash=hash(full);
const filtered=realId?null:Buffer.from(full.toString().replaceAll(' -2 6',' -2 7').replace('0 2 6','0 2 7'));
if(!realId)report.variants.push({...report.variants[0],id:'filtered',kind:'depth_filtered',label:'Filtered analytic fixture',mesh_id:'sha256:'+hash(filtered),sha256:hash(filtered),byte_length:filtered.length,mesh_url:`/sessions/${id}/mesh?variant=filtered`,provenance:{operation:'analytic_two_unit_offset_fixture'}});
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{
 const page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[];let failure='',draft,metadataRequests=0,calibrated=false;
 page.setDefaultTimeout(15000);
 page.on('console',message=>{if(message.type()==='error')console.log('browser:',message.text());});
 page.on('pageerror',error=>errors.push(error.message));
 await page.addInitScript(()=>{
  const original=HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext=function(type,...args){
   if(type==='webgl2' && window.failGL)return null;
   const gl=original.call(this,type,...args);
   if(type==='webgl2' && gl && window.failAllocation)return new Proxy(gl,{get(target,key){if(key==='getError')return ()=>target.OUT_OF_MEMORY;const value=target[key];return typeof value==='function'?value.bind(target):value;}});
   return gl;
  };
  const NativeWorker=Worker;window.Worker=class extends NativeWorker{postMessage(...args){if(window.failWorker){queueMicrotask(()=>this.dispatchEvent(new ErrorEvent('error')));return;}return super.postMessage(...args);}};
 });
 await page.route('http://127.0.0.1:5182/**',async route=>{
  const request=route.request(),url=new URL(request.url()),pathname=url.pathname;
  const headers={'Access-Control-Allow-Origin':'http://127.0.0.1:5178','Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'GET, POST, OPTIONS'};
  if(request.method()==='OPTIONS')return route.fulfill({status:204,headers});
  if(pathname.endsWith('/frontal')){
   const body=realId?fs.readFileSync(path.join(root,'.private-webcam-runs',id,fixture.result.frontal_undistorted)):Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64');
   return route.fulfill({headers,contentType:'image/png',body});
  }
  if(pathname.endsWith('/mesh'))return route.fulfill({headers,contentType:'application/octet-stream',body:url.searchParams.get('variant')==='filtered'?filtered:failure==='truncated'?full.subarray(0,full.length-1):full});
  let data=fixture;
  if(calibrated){data={...fixture,status:'calibrated',calibrated:{surface:{...fixture.result.surface,units:'mm',mesh:{...mesh,vertices:mesh.vertices.map(p=>p.map(v=>v*10))}},cameras:{front:{...camera,units:'mm'}},projected_points:[],report:{mm_per_reconstruction_unit:10,scale:{route:[],readings_mm:[1,1,1]},independent_check:{route:[],readings_mm:[1,1,1]}}}};}
  if(pathname==='/diagnostics')data={ready:true};
  else if(pathname==='/sessions')data=[fixture];
  else if(pathname.endsWith('/mesh-comparison')){
   metadataRequests++;data=JSON.parse(JSON.stringify(report));
   if(url.searchParams.get('variant')==='filtered'){data.comparison_source_id='filtered';data.deviation={full_to_analysis:{...stats,rms:2,p95:2,sampled_max:2},analysis_to_full:{...stats,seed:1,rms:2,p95:2,sampled_max:2}};}
   if(calibrated){data.units='mm';data.display_scale=10;for(const direction of ['full_to_analysis','analysis_to_full'])for(const key of ['rms','p95','sampled_max'])data.deviation[direction][key]*=10;}
   if(failure==='hash')data.variants[0].sha256='0'.repeat(64);
   if(failure==='limit')data.variants[0].byte_length=65*1024*1024;
   if(failure==='delay'){await new Promise(resolve=>setTimeout(resolve,300));}
  }else if(pathname.endsWith('/draft')){draft=request.postDataJSON();}
  else assert.equal(request.method(),'GET','Inspection must not mutate a session');
  await route.fulfill({headers,contentType:'application/json',body:JSON.stringify(data)}).catch(error=>{if(!page.isClosed() && failure!=='delay')throw error;});
 });
 await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
 console.log('preview loaded');
 await page.getByRole('button',{name:'Connect processor',exact:true}).click();await page.getByLabel('Saved session').selectOption(id);await page.getByRole('button',{name:'Resume',exact:true}).click();
 await page.getByRole('button',{name:'Compare full and analysis meshes',exact:true}).click();
 console.log('comparison requested');
 const comparison=page.getByRole('region',{name:'Full and analysis mesh comparison',exact:true});
 const fullCanvas=page.getByRole('img',{name:'Full reconstruction inspection',exact:true}),analysisCanvas=page.getByRole('img',{name:'Bounded analysis mesh inspection',exact:true});
 await page.waitForFunction(()=>document.querySelector('.comparison [role="alert"]') || [...document.querySelectorAll('.comparison canvas')].some(c=>c.getBoundingClientRect().width>0),{},{timeout:15000});
 const initialAlerts=await comparison.getByRole('alert').allTextContents();if(initialAlerts.length)throw Error(initialAlerts.join('\n'));
 await fullCanvas.waitFor({state:'visible',timeout:15000});await analysisCanvas.waitFor({state:'visible'});
 await comparison.getByRole('cell',{name:realId?String(report.deviation.full_to_analysis.sample_count)+' / 0':'100 / 0',exact:true}).waitFor();
 const screenshot=()=>fullCanvas.screenshot();const original=await screenshot();
 const requests=metadataRequests;
 await page.getByRole('button',{name:'¾ view left',exact:true}).click();await page.waitForTimeout(150);
 assert.notEqual((await screenshot()).toString('base64'),original.toString('base64'));
 assert.equal(metadataRequests,requests,'Rotation should reuse GPU data');
 await page.getByRole('button',{name:'Reset view / fit surface',exact:true}).click();
 await fullCanvas.scrollIntoViewIfNeeded();
 const box=await fullCanvas.boundingBox();await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.6,box.y+box.height*.55,{steps:4});await page.mouse.up();
 assert.notEqual(await page.getByLabel('Yaw',{exact:true}).inputValue(),'0');
 await page.getByRole('checkbox',{name:'Show mesh edges',exact:true}).check();await page.getByRole('checkbox',{name:'Smooth lighting',exact:true}).uncheck();
 await page.getByLabel('Light direction',{exact:true}).evaluate(input=>{input.value='70';input.dispatchEvent(new Event('input',{bubbles:true}));});
 await page.getByRole('checkbox',{name:'Tap to place route controls',exact:true}).check();
 await fullCanvas.click({modifiers:['Control']});await analysisCanvas.click({modifiers:['Control']});
 await page.getByText('No controls placed',{exact:true}).waitFor();
 if(!realId){await page.getByRole('button',{name:'Save route draft locally',exact:true}).click();await page.getByText('Route draft saved locally.',{exact:true}).waitFor();assert.deepEqual(draft.scale_route,[]);}
 console.log('GPU full/analysis load + shared controls + annotation isolation: PASS');
 if(!realId){
  await comparison.getByLabel('Comparison variant',{exact:true}).selectOption('filtered');
  await page.getByRole('img',{name:'Filtered analytic fixture inspection',exact:true}).waitFor({state:'visible'});
  await comparison.getByRole('cell',{name:'2.000 reconstruction units',exact:true}).first().waitFor();
  await comparison.getByLabel('Comparison variant',{exact:true}).selectOption('raw');await fullCanvas.waitFor({state:'visible'});
  for(const mode of ['hash','truncated','limit','worker','allocation','unsupported']){
   failure=mode;await page.evaluate(mode=>{window.failWorker=mode==='worker';window.failAllocation=mode==='allocation';window.failGL=mode==='unsupported';},mode);
   await comparison.getByRole('button',{name:'Reload comparison',exact:true}).click();await comparison.getByRole('alert').waitFor();
   assert.ok((await comparison.getByRole('alert').textContent()).length>10);
   failure='';await page.evaluate(()=>{window.failWorker=false;window.failAllocation=false;window.failGL=false;});
   await comparison.getByRole('button',{name:'Retry comparison',exact:true}).click();await fullCanvas.waitFor({state:'visible',timeout:15000});
  }
  await fullCanvas.evaluate(canvas=>canvas.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext());
  await comparison.getByRole('alert').filter({hasText:'GPU context lost'}).waitFor();
  await comparison.getByRole('button',{name:'Retry comparison',exact:true}).click();await fullCanvas.waitFor({state:'visible'});
  failure='delay';await comparison.getByRole('button',{name:'Reload comparison',exact:true}).click();
  await comparison.getByRole('button',{name:'Cancel comparison loading',exact:true}).click();await comparison.getByRole('status').filter({hasText:'cancelled'}).waitFor();
  await page.waitForTimeout(400);failure='';await comparison.getByRole('button',{name:'Retry comparison',exact:true}).click();await fullCanvas.waitFor({state:'visible'});
  console.log('hash/size/worker/GPU failures + context loss + cancellation + retry: PASS');
  calibrated=true;
  await page.getByRole('button',{name:'Resume',exact:true}).click();
  await page.getByRole('button',{name:'Compare full and analysis meshes',exact:true}).click();
  await fullCanvas.waitFor({state:'visible'});await comparison.getByRole('cell',{name:'10.00 mm',exact:true}).first().waitFor();
  console.log('future variant provenance + calibrated millimeter display: PASS');
 }
 await page.getByRole('checkbox',{name:'Show mesh edges',exact:true}).uncheck();await page.getByRole('checkbox',{name:'Smooth lighting',exact:true}).check();
 await page.getByRole('button',{name:'Reset view / fit surface',exact:true}).click();
 await comparison.screenshot({path:realId?path.join(root,'.private-webcam-runs/capture-comparisons/bre16-full-analysis-browser.png'):'/tmp/bre16-analytic-comparison.png'});
 await page.getByRole('button',{name:'Close mesh comparison',exact:true}).click();await comparison.waitFor({state:'detached'});
 assert.equal(JSON.stringify(fixture),before);assert.equal(hash(full),beforeHash);assert.deepEqual(errors,[]);
 console.log(realId?'real pilot full PLY + read-only inspection: PASS':'analytic comparison + immutable geometry/topology: PASS');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
