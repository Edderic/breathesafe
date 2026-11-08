const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async () => {
  const folder=path.resolve(process.argv[2]);
  const report=JSON.parse(fs.readFileSync(path.join(folder,'report.json')));
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1500,height:1100},acceptDownloads:true});
    const errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
    await page.locator('#status').filter({hasText:'Completed'}).waitFor();
    assert.equal(await page.locator('#arcMetrics tr').count(),report.variants.length*report.arc_experiment.definition_count);
    const baseline=await page.locator('#fit').evaluate(c=>c.toDataURL());
    await page.locator('#arcGuides').uncheck();
    await page.waitForFunction(before=>document.getElementById('fit').toDataURL()!==before,baseline);
    await page.locator('#arcGuides').check();
    for(const row of report.variants){
      await page.locator('#variant').selectOption(row.id);
      await page.getByRole('heading',{name:'FLAME · '+row.label,exact:true}).waitFor();
    }
    await page.locator('#variant').selectOption(report.variants[report.bridge_experiment?report.variants.length-1:1].id);
    await page.locator('#showAnalysis').check();
    await page.locator('#reference').selectOption('100');
    await page.getByRole('heading',{name:'FLAME · '+report.variants[0].label,exact:true}).waitFor();
    await page.screenshot({path:path.join(folder,'arc-comparison-front.png'),fullPage:true});
    await page.locator('#left').click();
    await page.screenshot({path:path.join(folder,'arc-comparison-profile.png'),fullPage:true});
    const download=page.waitForEvent('download');await page.locator('#download').click();
    const exported=JSON.parse(fs.readFileSync(await(await download).path()));
    assert.equal(exported.arc_experiment.saved_lengths_are_ground_truth,false);
    assert.equal(exported.variants.length,report.variants.length);
    if(report.neck_experiment){assert.equal(await page.locator('#neckMetrics tr').count(),report.variants.length);if(!report.bridge_experiment)assert.ok(report.variants[1].fitted_vertex_ids.length>report.variants[0].fitted_vertex_ids.length);}
    if(report.bridge_experiment){
      assert.equal(await page.locator('#bridgeMetrics tr').count(),report.variants.length);
      const before=await page.locator('#fit').evaluate(c=>c.toDataURL());
      await page.locator('#bridgeRegion').uncheck();
      await page.waitForFunction(old=>document.getElementById('fit').toDataURL()!==old,before);
      for(const row of report.variants){assert.deepEqual(row.fitted_vertex_ids,report.variants[0].fitted_vertex_ids);assert.ok(Number.isFinite(row.nose_measurements.forward_tip_projection_from_subnasale));}
    }
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('Arc comparison: variants, guides, shared views, coverage report, export and no network PASS');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
