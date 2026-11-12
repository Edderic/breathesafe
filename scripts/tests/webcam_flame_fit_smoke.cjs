// Verify a generated private comparison without serving or uploading its data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async () => {
  const folder = path.resolve(process.argv[2] || '.private-webcam-runs/flame-fits/c79e26de-first');
  const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1400,height:1200},acceptDownloads:true});
    const errors = [], external = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => {if (/^https?:/.test(request.url())) external.push(request.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
    await page.getByRole('status').filter({hasText:'Completed'}).waitFor();
    assert.equal(await page.locator('#metrics tr').count(),3);
    // Canvas has its accessible name but no implicit img role in every browser.
    const initial = await page.locator('#fit').evaluate(c => c.toDataURL());
    await page.screenshot({path:path.join(folder,'front.png')});
    await page.getByRole('button',{name:'Left profile',exact:true}).click();
    await page.waitForFunction(before => document.getElementById('fit').toDataURL() !== before, initial);
    await page.screenshot({path:path.join(folder,'profile.png')});
    await page.getByRole('combobox',{name:'Shape components'}).selectOption('300');
    await page.getByRole('heading',{name:'FLAME · 300 shape components'}).waitFor();
    await page.getByLabel('Show analysis / comparison mesh',{exact:true}).check();
    await page.getByRole('checkbox',{name:'Show only fitting target on left'}).uncheck();
    await page.getByRole('heading',{name:'Analysis mesh · original bounded surface'}).waitFor();
    const downloaded = page.waitForEvent('download');
    await page.getByRole('button',{name:'Download fit report'}).click();
    const report = JSON.parse(fs.readFileSync(await (await downloaded).path()));
    assert.equal(report.version,'webcam-flame-analysis-fit-v1');
    assert.equal(report.variants.length,3);
    assert.deepEqual(errors,[]); assert.deepEqual(external,[]);
    console.log('FLAME comparison: render, profiles, variants, source toggle, report download and no network PASS');
  } finally {await browser.close();}
})().catch(error => {console.error(error);process.exitCode=1;});
