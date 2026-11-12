const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tmp/webcam-browser/node_modules/playwright');
(async()=>{
 const file=path.resolve(process.argv[2]||'.private-webcam-runs/tape-validation/neck-003-width-endpoints-v1/review.html');
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
 const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url())));
 await page.goto('file://'+file);await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));
 assert.equal(await page.locator('#widths tr').count(),2);assert.equal(await page.locator('#endpoints tr').count(),4);
 const canvas=page.locator('#view'),before=await canvas.screenshot();await page.uncheck('#route');assert(!(await canvas.screenshot()).equals(before));await page.check('#route');await canvas.screenshot({path:path.join(path.dirname(file),'endpoints-front.png')});await page.click('#left');await canvas.screenshot({path:path.join(path.dirname(file),'endpoints-profile.png')});
 await page.waitForFunction(()=>document.querySelectorAll('#photos img').length>=6&&[...document.querySelectorAll('#photos img')].every(i=>i.complete&&i.naturalWidth>0));
 const first=page.locator('#photos img').first(),overlay=await first.getAttribute('src');await page.uncheck('#overlay');assert.notEqual(await first.getAttribute('src'),overlay);await page.check('#overlay');
 assert.deepEqual(errors,[]);console.log('Two widths, four endpoints, WebGL rotation/toggles and source-photo overlays passed.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
