const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tmp/webcam-browser/node_modules/playwright');
(async()=>{
const target=path.resolve(process.argv[2]??'.private-webcam-runs/gaussian-volume/c79e26de-sweep-v1/comparison.html');
const report=JSON.parse(fs.readFileSync(path.join(path.dirname(target),'report.json'),'utf8')),expected=report.variants.length,last=String(expected-1);
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>assert(!/^https?:/.test(r.url()),'Unexpected external request'));
 await page.goto('file://'+target);await page.waitForFunction(n=>document.querySelectorAll('#rows tr').length===n,expected);
 assert.equal(await page.locator('#variant option').count(),expected);
 await page.selectOption('#variant','0');
 const before=await page.locator('#candidate').screenshot();await page.selectOption('#variant',last);
 await page.waitForFunction(id=>document.querySelector('#candidateTitle').textContent===id,report.variants[expected-1].id);
 assert(!(await page.locator('#candidate').screenshot()).equals(before),'Variant did not alter the rendered canvas');
 await page.selectOption('#shade','flat');const flat=await page.locator('#raw').screenshot();await page.selectOption('#shade','smooth');
 assert(!(await page.locator('#raw').screenshot()).equals(flat),'Shading toggle did not alter raw rendering');
 const front=await page.locator('#candidate').screenshot();await page.click('#left');
 assert(!(await page.locator('#candidate').screenshot()).equals(front),'Profile rotation had no effect');
 await page.locator('section').first().screenshot({path:path.join(path.dirname(target),'review-profile.png')});
 await page.click('#front');await page.waitForFunction(()=>[...document.querySelectorAll('img')].every(im=>im.complete&&im.naturalWidth>0));
 const href=await page.locator('#mesh').getAttribute('href');assert(fs.existsSync(path.join(path.dirname(target),href)));
 assert.deepEqual(errors,[]);await page.screenshot({path:path.join(path.dirname(target),'review-front.png'),fullPage:true});
 console.log(expected+' variants, WebGL rendering, shading, rotation, photos and local exports passed.');
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
