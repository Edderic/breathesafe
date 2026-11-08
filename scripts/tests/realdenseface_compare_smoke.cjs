const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const folder=path.resolve(process.argv[2]),browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1550,height:1150},acceptDownloads:true}),errors=[],external=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url())});
  await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
  assert.equal(await page.locator('#variant option').count(),2);
  assert.equal(await page.locator('#lengths tr').count(),6);
  assert.equal(await page.locator('#exportLeft').isDisabled(),true);
  const old=await page.locator('#baseline').evaluate(c=>c.toDataURL()),oldDense=await page.locator('#dense').evaluate(c=>c.toDataURL());
  await page.locator('#left').click();
  assert.notEqual(await page.locator('#baseline').evaluate(c=>c.toDataURL()),old);
  assert.notEqual(await page.locator('#dense').evaluate(c=>c.toDataURL()),oldDense);
  await page.locator('#tape').fill('400');await page.locator('#derive').click();
  const scaleLeft=Number(await page.locator('#scaleLeft').inputValue()),scaleRight=Number(await page.locator('#scaleRight').inputValue());
  assert.ok(scaleLeft>0&&scaleRight>0);assert.equal(await page.locator('#exportLeft').isDisabled(),false);
  const downloading=page.waitForEvent('download');await page.locator('#download').click();
  const record=JSON.parse(fs.readFileSync(await (await downloading).path(),'utf8'));
  for(const m of record.models){assert.ok(Math.abs(m.lengths.find(r=>r.key==='scale').length_mm-400)<1e-6);assert.equal(m.guide_status,'pending_review_on_this_surface');}
  const plyDownloading=page.waitForEvent('download');await page.locator('#exportRight').click();
  const ply=fs.readFileSync(await(await plyDownloading).path(),'utf8');assert.match(ply,/units millimeters/);assert.match(ply,/element vertex 5023/);
  const scaledFirst=ply.split('end_header\n')[1].split('\n')[0].split(' ').map(Number);
  const firstNative=await page.evaluate(()=>data.variants[0].vertices[0]);
  firstNative.forEach((x,i)=>assert.ok(Math.abs(scaledFirst[i]-x*scaleRight)<1e-8));
  await page.locator('#scaleRight').fill('-1');assert.equal(await page.locator('#exportRight').isDisabled(),true);
  await page.locator('#variant').selectOption('1');assert.equal(await page.locator('#scaleRight').inputValue(),'');
  await page.locator('#variant').selectOption('0');await page.locator('#scaleLeft').fill('');await page.locator('#tape').fill('');await page.locator('#guides').uncheck();await page.locator('#front').click();
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(folder,'comparison-front.png')});await page.locator('#left').click();await page.screenshot({path:path.join(folder,'comparison-profile.png')});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log('Dense comparison: shared views, six lengths, tape scaling, JSON and mm mesh exports, invalid input rejection, no network PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
