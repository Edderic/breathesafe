// Capture actual prototype surfaces, check the standalone deck, and export its PDF.
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const workspace=process.env.NASEM_SOURCE_ROOT||root;
const {chromium}=require(path.join(process.env.NASEM_PLAYWRIGHT_ROOT||workspace,'tmp/webcam-browser/node_modules/playwright'));
const deck=path.join(root,'prompts/2026-11-17-nasem'),assets=path.join(deck,'assets/prototype');
(async()=>{
fs.mkdirSync(path.join(root,'tmp/nasem-preview'),{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1366,height:900},deviceScaleFactor:1}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url()),'Unexpected external request: '+r.url()));
 if(process.argv.includes('--capture-sources')){
  fs.mkdirSync(assets,{recursive:true});
  const capture=async(selector,name)=>{await page.addStyleTag({content:'.controls{display:none!important}'});await page.locator(selector).screenshot({path:path.join(assets,name+'.jpg'),type:'jpeg',quality:92})};
  await page.goto('file://'+path.join(workspace,'.private-webcam-runs/gaussian-volume/expanded-neck-selected-003-v1/comparison.html'));
  await page.waitForFunction(()=>document.querySelectorAll('#rows tr').length===2);await page.selectOption('#variant','1');await page.selectOption('#shade','smooth');await page.click('#front');
  await capture('#raw','raw-headform');await capture('#candidate','smoothed-headform');
  await page.goto('file://'+path.join(workspace,'.private-webcam-runs/tape-validation/neck-003-width-endpoints-v4/review.html'));
  await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));await capture('#view','landmark-widths');
  await page.goto('file://'+path.join(workspace,'.private-webcam-runs/mask-route-review/trifold-neck-003-v1/review.html'));
  await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));await page.click('#below');await capture('#view','under-chin-route');
  await page.goto('file://'+path.join(workspace,'.private-webcam-runs/tape-validation/neck-003-v1/calibration-route.html'));
  await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));await page.check('#points');await capture('#view','calibration-arc');
  assert.deepEqual(errors,[]);console.log('Captured five actual prototype surface views.');return;
 }
 const file=path.join(deck,'presentation.html');
 await page.setViewportSize({width:1366,height:768});await page.goto('file://'+file);await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth));
 const count=await page.locator('.slide').count();assert.equal(count,18);assert(!(await page.locator('main').innerText()).includes('Unresolved difference'));
 const overflow=[];
 for(let i=0;i<count;i++){
  await page.goto('file://'+file+'#slide-'+(i+1));
  const info=await page.locator('.slide.active').evaluate(s=>({title:s.querySelector('h1').textContent,height:s.getBoundingClientRect().height,bottom:s.querySelector('footer').getBoundingClientRect().bottom,width:s.scrollWidth,client:s.clientWidth}));
  if(info.bottom>769||info.width>info.client+1)overflow.push({slide:i+1,...info});
  if([3,4,8,9,10].includes(i))await page.screenshot({path:path.join(root,'tmp/nasem-preview/slide-'+(i+1)+'.png')});
 }
 if(overflow.length)console.log(JSON.stringify(overflow,null,2));assert.deepEqual(overflow,[],'Screen overflow');
 await page.goto('file://'+file+'#slide-1');await page.locator('#next').click();assert.equal(await page.locator('.slide.active').count(),1);assert.equal(await page.locator('#counter').textContent(),'2 / '+count);
 await page.locator('body').click({position:{x:5,y:100}});await page.keyboard.press('End');assert.equal(await page.locator('#counter').textContent(),count+' / '+count);await page.keyboard.press('Home');assert.equal(await page.locator('#counter').textContent(),'1 / '+count);
 await page.click('#overview');assert.equal(await page.locator('.slide:visible').count(),count);await page.click('#overview');
 await page.emulateMedia({media:'print'});
 const printOverflow=await page.locator('.slide').evaluateAll(slides=>slides.flatMap((s,i)=>s.scrollHeight>s.clientHeight+2?[{slide:i+1,height:s.clientHeight,scroll:s.scrollHeight}]:[]));if(printOverflow.length)console.log(JSON.stringify(printOverflow,null,2));assert.deepEqual(printOverflow,[],'Print overflow');
 await page.pdf({path:path.join(deck,'presentation.pdf'),preferCSSPageSize:true,printBackground:true,displayHeaderFooter:false});
 await page.emulateMedia({media:'screen'});await page.setViewportSize({width:390,height:844});
 for(const i of [3,4,8,9,10]){await page.goto('file://'+file+'#slide-'+(i+1));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'Mobile horizontal overflow on '+(i+1))}
 assert.deepEqual(errors,[]);console.log(count+' slides: offline assets, desktop/mobile layout, navigation, print bounds and PDF export passed.');
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
