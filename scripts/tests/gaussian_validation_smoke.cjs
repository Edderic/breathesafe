const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tmp/webcam-browser/node_modules/playwright');
(async()=>{
 const file=path.resolve(process.argv[2]??'.private-webcam-runs/gaussian-validation/c79e26de-selected-003-v1/review.html');
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 try{
  const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url()),'Unexpected external request'));
  await page.goto('file://'+file);
  await page.waitForFunction(()=>document.querySelectorAll('canvas[data-ready="true"]').length===6);
  assert.equal(await page.locator('#sections svg').count(),2);
  assert.equal(await page.locator('#support tr').count(),4);
  assert.equal(await page.locator('#routes tr').count(),4);
  assert.equal(await page.locator('#tipAudit tr').count(),4);
  assert.equal(await page.locator('#surfaceRoutes tr').count(),4);
  const photo=page.locator('#photos canvas').first(),before=await photo.screenshot();
  await page.uncheck('#rawOn');await page.uncheck('#selectedOn');
  assert(!(await photo.screenshot()).equals(before),'Photo-only toggle had no effect');
  assert(await page.locator('#sections path').evaluateAll(paths=>paths.filter(p=>p.style.display==='none').length)>=4);
  await page.check('#rawOn');await page.check('#selectedOn');await page.check('#coarseOn');
  assert(await page.locator('#sections path').evaluateAll(paths=>paths.some(p=>p.getAttribute('stroke')==='#9650b4'&&p.style.display!=='none')));
  const href=await page.locator('#viewer').getAttribute('href');assert(fs.existsSync(path.resolve(path.dirname(file),href)));
  assert.deepEqual(errors,[]);
  await page.screenshot({path:path.join(path.dirname(file),'review.png'),fullPage:true});
  console.log('Validation tables, two section plots, six photo overlays, toggles and local links passed.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
