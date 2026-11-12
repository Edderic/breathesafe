const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
  const folder=path.resolve(process.argv[2]);
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1500,height:1050}});
    const errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
    assert.equal(await page.locator('#photo option').count(),13);
    assert.equal(await page.locator('#cards article').count(),13);
    const before=await page.locator('#mesh').evaluate(c=>c.toDataURL());
    await page.locator('#left').click();
    assert.notEqual(await page.locator('#mesh').evaluate(c=>c.toDataURL()),before);
    await page.locator('#photo').selectOption('turn_20');
    assert.match(await page.locator('#overlay').getAttribute('src'),/turn_20/);
    await page.locator('#front').click();
    await page.screenshot({path:path.join(folder,'review-front.png')});
    await page.locator('#left').click();
    await page.screenshot({path:path.join(folder,'review-profile.png')});
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('Photo review: all splits, photo selection, shared identity rotation, no network PASS');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
