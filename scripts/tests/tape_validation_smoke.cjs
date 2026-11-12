const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tmp/webcam-browser/node_modules/playwright');
(async()=>{
const file=path.resolve(process.argv[2]||'.private-webcam-runs/tape-validation/neck-003-v1/review.html');
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1500,height:1100}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url())));
 await page.goto('file://'+file);assert((await page.locator('table').innerText()).includes('380.0 mm'));
 for(const href of await page.locator('a').evaluateAll(items=>items.map(a=>a.getAttribute('href'))))assert(fs.existsSync(path.resolve(path.dirname(file),href)));
 await page.screenshot({path:path.join(path.dirname(file),'review.png'),fullPage:true});
 await page.click('a[href="calibration-route.html"]');await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));
 assert.equal(await page.locator('#segments tr').count(),2);assert.equal(await page.locator('#controlRows tr').count(),3);
 const canvas=page.locator('#view'),before=await canvas.screenshot();await page.uncheck('#route');assert(!(await canvas.screenshot()).equals(before));
 await page.check('#route');await page.check('#points');await page.click('#left');assert(!(await canvas.screenshot()).equals(before));
 await canvas.screenshot({path:path.join(path.dirname(file),'calibration-profile.png')});
 assert.deepEqual(errors,[]);console.log('Tape comparison, local links, three-anchor surface arc, route toggle and profile view passed.');
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
