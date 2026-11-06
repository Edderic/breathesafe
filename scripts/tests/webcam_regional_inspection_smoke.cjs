// Manual live, read-only review of consented local captures. No participant assets are committed.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
const root=path.resolve(__dirname,'../..'),privateRoot=path.join(root,'.private-webcam-runs'),output=path.join(privateRoot,'capture-comparisons/regional-inspection');
const ids=process.env.WEBCAM_REGIONAL_SESSION ? [process.env.WEBCAM_REGIONAL_SESSION] : JSON.parse(fs.readFileSync(path.join(privateRoot,'capture-comparisons/bre18-direct-light-20261105/protocol.json'))).capture_order.map(c=>c.session_id);
(async()=>{
 fs.mkdirSync(output,{recursive:true});const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{const page=await browser.newPage({viewport:{width:1600,height:1100},acceptDownloads:true});page.setDefaultTimeout(90000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const [index,id] of ids.entries()){
  assert.match(id,/^[a-f0-9]{32}$/);const stateFile=path.join(privateRoot,id,'session.json'),before=fs.readFileSync(stateFile);let requests=0;
  page.on('request',request=>{if(request.url().includes('/regional-report'))requests++;});
  await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');await page.getByRole('button',{name:'Connect processor',exact:true}).click();
  await page.getByLabel('Saved session').selectOption(id);await page.getByRole('button',{name:'Resume',exact:true}).click();
  const reportPromise=page.waitForResponse(r=>r.url().includes('/regional-report?'));
  await page.getByRole('button',{name:'Inspect nose and mask-contact regions',exact:true}).click();const data=await (await reportPromise).json();
  assert.equal(data.version,'webcam_regional_inspection_v1');assert.equal(data.units,'reconstruction_unit');assert.equal(data.calibration_applied,false);assert.equal(data.stages.length,4);
  for(const stage of data.stages){assert.equal(stage.nose_proxies.anatomical_nose_protrusion,null);assert.equal(stage.nose_proxies.surface_arc,null);}
  for(const entry of Object.values(data.arkit_paths)){assert.equal(entry.length,null);assert.ok(entry.legacy_segments.length>0);}
  const region=page.getByRole('region',{name:'Regional inspection and measurement report',exact:true});const canvas=page.getByRole('img',{name:'Raw full mesh regional surface',exact:true});await canvas.waitFor({state:'visible'});
  fs.writeFileSync(path.join(output,id+'.json'),JSON.stringify(data));const initialRequests=requests;
  for(const name of ['nose','top_cheek','mid_cheek','chin']){
   await region.getByLabel('Inspect region',{exact:true}).selectOption(name);
   if(data.regions[name].status==='ok')await canvas.waitFor({state:'visible'});
   else await region.getByRole('alert').filter({hasText:'Region unavailable'}).waitFor();
   await region.screenshot({path:path.join(output,`${id}-${name}.png`)});
  }
  assert.equal(requests,initialRequests,'Region changes reuse metrics and preserve one raw ROI definition');
  await region.getByLabel('Inspect region',{exact:true}).selectOption('nose');await canvas.waitFor({state:'visible'});
  for(const [angle,name] of [[-35,'left'],[35,'right']]){await region.getByLabel('Regional yaw',{exact:true}).evaluate((input,value)=>{input.value=String(value);input.dispatchEvent(new Event('input',{bubbles:true}));},angle);await page.waitForTimeout(100);await region.screenshot({path:path.join(output,`${id}-nose-${name}.png`)});}
  assert.equal(requests,initialRequests,'Rotation reuses the same source buffers');
  const downloadPromise=page.waitForEvent('download');await region.getByRole('button',{name:'Download regional report JSON',exact:true}).click();const download=await downloadPromise;const downloaded=JSON.parse(fs.readFileSync(await download.path()));assert.equal(downloaded.input_fingerprint,data.input_fingerprint);
  if(index===0){
   await region.getByLabel('Regional refined variant',{exact:true}).selectOption('raw');await canvas.waitFor({state:'visible'});assert.equal(await region.getByRole('img',{name:/regional surface$/}).count(),2);
   await region.getByLabel('Regional refined variant',{exact:true}).selectOption(data.variant_id);await canvas.waitFor({state:'visible'});
   await page.route('**/regional-report?*',async route=>{await new Promise(r=>setTimeout(r,250));await route.fulfill({contentType:'application/json',body:JSON.stringify(data)}).catch(()=>{});});
   await region.getByRole('button',{name:'Reload regional report',exact:true}).click();await region.getByRole('button',{name:'Cancel regional inspection',exact:true}).click();
   await region.getByRole('status').filter({hasText:'cancelled'}).waitFor();await page.waitForTimeout(300);await page.unroute('**/regional-report?*');
   await region.getByRole('button',{name:'Reload regional report',exact:true}).click();await canvas.waitFor({state:'visible'});
  }
  assert.deepEqual(fs.readFileSync(stateFile),before);console.log(id+': regions, profiles, proxies, export, source isolation PASS');
 }
 assert.deepEqual(errors,[]);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
