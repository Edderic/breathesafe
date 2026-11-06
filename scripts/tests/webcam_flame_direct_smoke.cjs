// Interaction fixtures only; these placements and tape values are not participant measurements.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
  const folder=path.resolve(process.argv[2]||'.private-webcam-runs/flame-fits/c79e26de-analog-review');
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1500,height:1300},acceptDownloads:true});page.setDefaultTimeout(15000);
    const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
    await page.getByRole('status').filter({hasText:'Completed'}).waitFor();
    assert.equal(await page.getByLabel('Show full FLAME head, ears and lower chin',{exact:true}).isChecked(),true);
    const visible=await page.locator('#fit').evaluate(c=>({count:c.pickFrame.mesh.vertices.length,ids:c.pickFrame.mesh.original_vertex_ids}));
    assert.equal(visible.count,5023);assert.equal(visible.ids[5022],5022);
    await page.getByLabel('Click to place direct FLAME point',{exact:true}).check();
    const canvas=page.locator('#fit');
    for(const [name,x,y]of[['left_tragion',.36,.5],['subnasale',.5,.55],['right_tragion',.64,.5],['menton',.5,.68],['pronasale',.5,.49]]){
      await page.getByLabel('Direct point',{exact:true}).selectOption(name);await canvas.scrollIntoViewIfNeeded();
      const p=await canvas.evaluate((c,{x,y})=>{const f=c.pickFrame;return {x:c.clientWidth*x,y:c.clientHeight*y,hit:FlameMapping.pick(f.mesh,f.vertices,[(f.w*x-f.w/2)/f.scale,-(f.h*y-f.h/2)/f.scale],'barycentric')};},{x,y});
      assert.ok(p.hit,'visible hit for '+name);await canvas.click({position:{x:p.x,y:p.y}});
      await page.getByLabel('Point notes',{exact:true}).fill('AUTOMATED FIXTURE ONLY, not anatomical review.');
      await page.getByLabel('Direct review',{exact:true}).selectOption('reviewed');
    }
    await page.getByLabel('Scale tape readings (mm, three comma-separated values)',{exact:true}).fill('300, 301, 299');
    await page.getByLabel('Independent check readings (mm, three comma-separated values)',{exact:true}).fill('320, 321, 319');
    assert.equal(await page.getByRole('button',{name:'Download calibrated FLAME mesh',exact:true}).isDisabled(),true);
    assert.equal(await page.getByRole('button',{name:'Download direct measurements',exact:true}).isDisabled(),true);
    await page.getByRole('button',{name:'Apply tape readings',exact:true}).click();
    await page.locator('#directResults').filter({hasText:'mm per reconstruction unit'}).waitFor();
    assert.equal(await page.getByRole('button',{name:'Download calibrated FLAME mesh',exact:true}).isEnabled(),true);
    const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'Download direct measurements',exact:true}).click();
    const draft=JSON.parse(fs.readFileSync(await(await downloaded).path()));assert.equal(draft.version,'flame-direct-measurements-v1');assert.ok(draft.measurements.calibration.mm_per_reconstruction_unit>0);assert.equal(draft.measurements.calibration.scale.median_mm,300);
    const calibrated=page.waitForEvent('download');await page.getByRole('button',{name:'Download calibrated FLAME mesh',exact:true}).click();
    const output=JSON.parse(fs.readFileSync(await(await calibrated).path()));assert.equal(output.units,'mm');assert.equal(output.mesh.vertices.length,5023);
    const check=await page.evaluate(({scale,vertices,camera})=>{
      const original=data.full_variants[document.getElementById('variant').value].world_vertices;
      return Math.abs(vertices[100][0]-original[100][0]*scale)<1e-10&&camera.t.every((v,i)=>Math.abs(v-data.camera.t[i]*scale)<1e-10);
    },{scale:output.calibration.mm_per_reconstruction_unit,vertices:output.mesh.vertices,camera:output.camera});assert.ok(check);
    await page.getByLabel('Shape components',{exact:true}).selectOption('300');
    assert.equal(await page.getByRole('button',{name:'Download calibrated FLAME mesh',exact:true}).isDisabled(),true);
    await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles({name:'wrong-variant.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(draft))});
    await page.locator('#directError').filter({hasText:'different fitted mesh'}).waitFor();
    await page.getByLabel('Shape components',{exact:true}).selectOption('100');
    await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles({name:'measurements.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(draft))});
    await page.locator('#directResults').filter({hasText:'mm per reconstruction unit'}).waitFor();
    assert.equal(await page.locator('#directError').textContent(),'');
    await page.getByLabel('Scale tape readings (mm, three comma-separated values)',{exact:true}).fill('300, nope, 299');
    await page.getByRole('button',{name:'Apply tape readings',exact:true}).click();assert.equal(await page.getByRole('button',{name:'Download calibrated FLAME mesh',exact:true}).isDisabled(),true);
    await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles({name:'measurements.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(draft))});
    await page.getByRole('button',{name:'Left profile',exact:true}).click();await canvas.screenshot({path:path.join(folder,'full-head-direct-test.png')});
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('Direct FLAME: full original topology, point placement, routes, chords, calibration/check, mesh/camera scaling, reload, per-variant isolation, invalid inputs and no network PASS');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
