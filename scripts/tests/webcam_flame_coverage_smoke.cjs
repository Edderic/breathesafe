const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
  const folder=path.resolve(process.argv[2]),report=JSON.parse(fs.readFileSync(path.join(folder,'report.json')));
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1500,height:1100},acceptDownloads:true}),errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'coverage.html')).href);
    await page.waitForFunction(()=>document.getElementById('seed').arcSegments?.length>0);
    assert.equal(await page.locator('#coverage tr').count(),report.arcs.length);
    await page.locator('#target').selectOption('cropped');
    await page.waitForFunction(()=>document.getElementById('targetLabel').textContent.startsWith(report.targets.cropped.label));
    const original=await page.locator('#surface').evaluate(c=>c.toDataURL());
    await page.locator('#target').selectOption('broader');
    await page.waitForFunction(before=>document.getElementById('surface').toDataURL()!==before,original);
    await page.locator('#targetLabel').filter({hasText:report.targets.broader.label}).waitFor();
    await page.screenshot({path:path.join(folder,'broader-front.png'),fullPage:true});
    await page.locator('#arc').selectOption('0');
    await page.waitForFunction(()=>document.getElementById('seed').arcSegments.every(s=>s.ai===0));
    const before=await page.locator('#seed').evaluate(c=>c.toDataURL());
    await page.locator('#color').selectOption('change');
    await page.waitForFunction(old=>document.getElementById('seed').toDataURL()!==old,before);
    const position=await page.locator('#seed').evaluate(c=>{const s=c.arcSegments[20],r=c.getBoundingClientRect();return {x:r.left+(s.a[0]+s.b[0])/2*r.width/c.width,y:r.top+(s.a[1]+s.b[1])/2*r.height/c.height};});
    await page.mouse.move(position.x,position.y);
    await page.locator('#edgeInfo').filter({hasText:'endpoint distances / eye span'}).waitFor();
    await page.locator('#below').click();
    await page.screenshot({path:path.join(folder,'broader-below.png'),fullPage:true});
    const download=page.waitForEvent('download');await page.locator('#download').click();
    const exported=JSON.parse(fs.readFileSync(await(await download).path()));
    assert.deepEqual(exported,report);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('Coverage diagnostic: target switch, reason colors, change colors, arc filtering, hover, rotation, export and no network PASS');
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
