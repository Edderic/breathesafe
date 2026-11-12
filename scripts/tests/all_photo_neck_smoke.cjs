const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tmp/webcam-browser/node_modules/playwright');
(async()=>{
 const root=path.resolve('.private-webcam-runs/all-photo-coverage/expanded-neck-all61-v1'),file=path.join(root,'review.html');
 const report=JSON.parse(fs.readFileSync(path.join(root,'report.json'),'utf8'));
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url()),'Unexpected external request'));
  await page.goto('file://'+file);await page.waitForFunction(()=>document.querySelectorAll('#summary tr').length===4);
  assert.equal(report.image_count,61);assert.equal(await page.locator('#named tr').count(),6);
  await page.waitForFunction(()=>[...document.querySelectorAll('img')].every(im=>im.complete&&im.naturalWidth>0));
  assert.equal(await page.locator('img').count(),6);
  await page.screenshot({path:path.join(root,'review.png'),fullPage:true});
  const link=await page.locator('#neck').getAttribute('href'),neck=path.resolve(root,link);assert(fs.existsSync(neck));
  await page.goto('file://'+neck);await page.waitForFunction(()=>document.querySelectorAll('#rows tr').length===2);
  assert((await page.locator('h1').textContent()).includes('upper-neck'));
  assert((await page.locator('#neckInputs').textContent()).includes('61'));
  const sheet=await page.locator('#neckInputs a').getAttribute('href');assert(fs.existsSync(path.resolve(path.dirname(neck),sheet)));
  await page.click('#left');await page.locator('section').first().screenshot({path:path.join(path.dirname(neck),'neck-profile.png')});
  assert.deepEqual(errors,[]);
  console.log('61-photo tables, six neck overlays, source masks, upper-neck viewer and profile rendering passed.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
