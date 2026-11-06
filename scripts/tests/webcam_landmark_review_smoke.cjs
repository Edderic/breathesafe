// Live browser check against an isolated processor/capture copy, never a participant session.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
const sid=process.env.WEBCAM_LANDMARK_SESSION || '768be390de804f5ebfafd36f7897facb';
const testPort=process.env.WEBCAM_LANDMARK_TEST_PORT || '5183';
if(testPort==='5182')throw Error('Use an isolated test processor, not the participant processor.');
(async()=>{
 const original=fs.readFileSync(path.join('.private-webcam-runs',sid,'session.json'));
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{const page=await browser.newPage({viewport:{width:1600,height:1100}});page.setDefaultTimeout(60000);const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('http://127.0.0.1:5182/**',route=>route.continue({url:route.request().url().replace(':5182',':'+testPort)}));
  await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');await page.getByRole('button',{name:'Connect processor',exact:true}).click();await page.getByLabel('Saved session',{exact:true}).selectOption(sid);await page.getByRole('button',{name:'Resume',exact:true}).click();
  await page.getByRole('button',{name:'Review anatomical landmarks',exact:true}).click();const panel=page.getByRole('region',{name:'Anatomical landmark review',exact:true});await panel.getByRole('status').filter({hasText:'Ready.'}).waitFor();
  const canvas=panel.getByRole('img',{name:'Landmark full surface',exact:true});await canvas.waitFor({state:'visible'});
  await panel.getByLabel('Click to place selected landmark',{exact:true}).check();
  const box=await canvas.boundingBox();const pick=page.waitForResponse(r=>r.request().method()==='POST' && r.url().includes('/landmark-review'));
  await canvas.click({position:{x:box.width*.5,y:box.height*.5}});const hit=await (await pick).json();assert.equal(hit.status,'ok');assert.equal(hit.attachment.kind,'barycentric');
  await panel.getByLabel('Landmark review status',{exact:true}).selectOption('uncertain');await panel.getByLabel('Landmark review notes',{exact:true}).fill('Browser workflow test only; not an anatomical review.');
  await panel.getByRole('button',{name:'Save landmark review',exact:true}).click();await panel.getByRole('status').filter({hasText:'saved locally'}).waitFor();
  await panel.getByRole('button',{name:'Right profile',exact:true}).click();await panel.getByRole('button',{name:'From below',exact:true}).click();
  const report=await page.evaluate(async({sid,testPort})=>(await fetch(`http://127.0.0.1:${testPort}/sessions/${sid}/landmark-review`)).json(),{sid,testPort});assert.equal(report.review.points.pronasale.status,'uncertain');assert.equal(report.review.points.pronasale.provenance,'manual_surface_pick');
  const before=JSON.stringify(report.review.points.pronasale);await panel.getByRole('button',{name:'Front',exact:true}).click();const missPromise=page.waitForResponse(r=>r.request().method()==='POST' && r.url().includes('/landmark-review'));await canvas.click({position:{x:2,y:2}});assert.equal((await (await missPromise).json()).status,'missed_surface');await panel.getByRole('status').filter({hasText:'No visible surface hit'}).waitFor();
  const source=panel.getByLabel('Landmark source',{exact:true}),options=await source.locator('option').evaluateAll(rows=>rows.map(r=>r.value));assert.ok(options.length>1);await source.selectOption(options[1]);await panel.getByRole('status').filter({hasText:'Ready.'}).waitFor();
  await panel.getByRole('button',{name:'Use detector suggestion for review',exact:true}).click();await panel.getByLabel('Landmark review status',{exact:true}).selectOption('accepted');await panel.getByRole('button',{name:'Save landmark review',exact:true}).click();await panel.getByRole('status').filter({hasText:'saved locally'}).waitFor();
  await source.selectOption('raw');await panel.getByRole('status').filter({hasText:'Ready.'}).waitFor();assert.equal(await panel.getByLabel('Landmark review status',{exact:true}).inputValue(),'uncertain');
  const after=await page.evaluate(async({sid,testPort})=>(await fetch(`http://127.0.0.1:${testPort}/sessions/${sid}/landmark-review`)).json(),{sid,testPort});assert.equal(JSON.stringify(after.review.points.pronasale),before);
  await panel.getByLabel('Landmark',{exact:true}).selectOption('subnasale');await panel.getByLabel('Landmark review status',{exact:true}).selectOption('unavailable');await panel.getByRole('button',{name:'Save landmark review',exact:true}).click();await panel.getByRole('status').filter({hasText:'saved locally'}).waitFor();
  const output='.private-webcam-runs/capture-comparisons/landmark-browser-runs';await panel.screenshot({path:path.join(output,'landmark-review.png')});assert.deepEqual(errors,[]);assert.deepEqual(fs.readFileSync(path.join('.private-webcam-runs',sid,'session.json')),original);
  console.log('Manual full-surface pick, miss preservation, review save, raw/refined isolation, suggestions and unavailable status: PASS');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
