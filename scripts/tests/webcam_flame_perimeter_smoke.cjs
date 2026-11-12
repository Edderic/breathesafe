// Automated trace fixtures; no anatomical contact route or seal is inferred.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
  const folder=path.resolve(process.argv[2]||'.private-webcam-runs/flame-fits/c79e26de-analog-review');
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1500,height:1100},acceptDownloads:true});page.setDefaultTimeout(20000);
    const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);await page.getByRole('status').filter({hasText:'Completed'}).waitFor();
    const snapshot=()=>page.evaluate(()=>structuredClone(directDraft().perimeters));
    const trace=async(x1,y1,x2,y2)=>{const canvas=page.locator('#fit');await canvas.scrollIntoViewIfNeeded();const b=await canvas.boundingBox();await page.mouse.move(b.x+b.width*x1,b.y+b.height*y1);await page.mouse.down();await page.mouse.move(b.x+b.width*x2,b.y+b.height*y2,{steps:30});await page.mouse.up();};
    await page.getByLabel('Mask style',{exact:true}).selectOption('bifold');await page.getByLabel('Perimeter name',{exact:true}).fill('Automated bifold fixture');await page.getByRole('button',{name:'Add perimeter',exact:true}).click();
    await page.getByRole('button',{name:'Mirror half to opposite side',exact:true}).click();
    await page.locator('#mirrorFeedback').filter({hasText:'Could not mirror:'}).waitFor();assert.equal((await snapshot()).length,1);
    let feedbackBox=await page.locator('#mirrorFeedback').boundingBox();assert.ok(feedbackBox.y>=0&&feedbackBox.y+feedbackBox.height<=1100,'mirror failure is on screen beside the buttons');
    assert.equal(await page.getByLabel('Drag to trace active perimeter',{exact:true}).isChecked(),true);assert.equal(await page.getByLabel('Click to place direct FLAME point',{exact:true}).isChecked(),false);
    const view=await page.evaluate(()=>({yaw,pitch}));await trace(.32,.58,.4,.63);
    let before=await snapshot();assert.ok(before[0].strokes.flat().length>=3);assert.deepEqual(await page.evaluate(()=>({yaw,pitch})),view);
    assert.equal(before[0].smoothing,'surface');
    const smoothing=await page.evaluate(()=>{const p=activePerimeter();return {smooth:FlameMeasurements.measurePerimeter(p,directMesh(),directEdges(),report.eye_proxy_span*.15),raw:FlameMeasurements.measurePerimeter({...p,smoothing:'edges'},directMesh(),directEdges(),report.eye_proxy_span*.15)};});
    assert.ok(smoothing.smooth.surface_segments>0);assert.ok(smoothing.smooth.length<smoothing.raw.length);
    await page.getByLabel('Smooth surface route',{exact:true}).uncheck();assert.equal((await snapshot())[0].smoothing,'edges');
    await page.keyboard.press('Meta+z');assert.equal((await snapshot())[0].smoothing,'surface');
    const legacy=await page.evaluate(()=>structuredClone(directDraft()));delete legacy.perimeters[0].smoothing;
    await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles({name:'legacy-edge-route.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(legacy))});
    await page.waitForFunction(()=>activePerimeter().smoothing===undefined);assert.equal(await page.getByLabel('Smooth surface route',{exact:true}).isChecked(),false);
    await page.getByLabel('Smooth surface route',{exact:true}).check();await page.evaluate(()=>document.activeElement.blur());await page.keyboard.press('Meta+z');assert.equal(await page.getByLabel('Smooth surface route',{exact:true}).isChecked(),false);
    await page.getByLabel('Smooth surface route',{exact:true}).check();
    await page.getByLabel('Perimeter review',{exact:true}).selectOption('reviewed');
    await page.getByRole('button',{name:'Remove last control',exact:true}).click();assert.equal((await snapshot())[0].status,'pending');
    await page.keyboard.press('Meta+z');assert.equal((await snapshot())[0].strokes.flat().length,before[0].strokes.flat().length);
    await page.getByRole('button',{name:'Remove last control',exact:true}).click();await page.keyboard.press('Control+z');assert.equal((await snapshot())[0].strokes.flat().length,before[0].strokes.flat().length);
    const nativeBefore=(await snapshot())[0].strokes;await page.getByLabel('Perimeter notes',{exact:true}).fill('Automated fixture');await page.getByLabel('Perimeter notes',{exact:true}).press('End');await page.keyboard.type(' text undo');await page.keyboard.press('Meta+z');assert.deepEqual((await snapshot())[0].strokes,nativeBefore);
    // Undo during a captured drag cancels only that unfinished drag, and a
    // subsequent pointer move must neither rotate nor commit it.
    await page.evaluate(()=>document.activeElement.blur());let cancelBox=await page.locator('#fit').boundingBox();const cancelBefore=await snapshot(),cancelView=await page.evaluate(()=>({yaw,pitch}));await page.mouse.move(cancelBox.x+cancelBox.width*.35,cancelBox.y+cancelBox.height*.6);await page.mouse.down();await page.mouse.move(cancelBox.x+cancelBox.width*.4,cancelBox.y+cancelBox.height*.62,{steps:8});await page.keyboard.press('Meta+z');await page.mouse.move(cancelBox.x+cancelBox.width*.44,cancelBox.y+cancelBox.height*.62,{steps:4});await page.mouse.up();assert.deepEqual(await snapshot(),cancelBefore);assert.deepEqual(await page.evaluate(()=>({yaw,pitch})),cancelView);
    const b=await page.locator('#fit').boundingBox();before=await snapshot();await page.keyboard.down('Alt');await page.mouse.move(b.x+b.width*.5,b.y+b.height*.55);await page.mouse.down();await page.mouse.move(b.x+b.width*.55,b.y+b.height*.55,{steps:5});await page.mouse.up();await page.keyboard.up('Alt');assert.deepEqual(await snapshot(),before);assert.notEqual((await page.evaluate(()=>({yaw}))).yaw,view.yaw);
    await page.getByRole('button',{name:'Front',exact:true}).click();
    await page.getByLabel('Mask style',{exact:true}).selectOption('trifold');await page.getByLabel('Perimeter name',{exact:true}).fill('Automated trifold fixture');await page.getByRole('button',{name:'Add perimeter',exact:true}).click();await page.locator('#perimeterGuide').filter({hasText:'neck'}).waitFor();await trace(.61,.59,.66,.65);
    const all=await snapshot();assert.equal(all.length,2);assert.deepEqual(all[0],before[0]);assert.ok(all[1].strokes.flat().length>=2);
    // A deliberate miss creates separate strokes rather than a cross-face bridge.
    const box=await page.locator('#fit').boundingBox();await page.mouse.move(box.x+box.width*.32,box.y+box.height*.6);await page.mouse.down();await page.mouse.move(box.x-30,box.y+box.height*.6);await page.mouse.move(box.x+box.width*.65,box.y+box.height*.6);await page.mouse.up();assert.ok((await snapshot())[1].strokes.length>1);
    const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download direct measurements',exact:true}).click();const draft=JSON.parse(fs.readFileSync(await(await download).path()));assert.equal(draft.perimeters.length,2);assert.equal(draft.measurements.perimeters[1].status,'separate_strokes_partial_length');
    await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles({name:'traces.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(draft))});await page.waitForFunction(()=>directDraft().perimeters.length===2);assert.deepEqual(await snapshot(),draft.perimeters);
    await page.getByLabel('Shape components',{exact:true}).selectOption('300');assert.equal((await snapshot()).length,0);await page.getByLabel('Shape components',{exact:true}).selectOption('100');assert.equal((await snapshot()).length,2);
    // Draw a half from visible model-midline landmarks across one cheek to the
    // chin. Local model targets locate interaction fixtures, not anatomy labels.
    await page.getByLabel('Mask style',{exact:true}).selectOption('bifold');await page.getByLabel('Perimeter name',{exact:true}).fill('Automated mirror half');await page.getByRole('button',{name:'Add perimeter',exact:true}).click();await page.getByLabel('Trace spacing (pixels)',{exact:true}).fill('8');
    await page.getByRole('button',{name:'Front',exact:true}).click();await page.locator('#fit').scrollIntoViewIfNeeded();
    const half=await page.locator('#fit').evaluate(c=>{const row=report.variants.find(r=>fitKey(r)===el('variant').value),t=row.transform,world=directMesh().vertices,f=c.pickFrame;return [[0,.02,.06],[.05,-.025,.035],[.04,-.065,.015],[0,-.08,.02]].map(target=>{let id=0,best=Infinity;world.forEach((p,i)=>{const local=[0,1,2].map(k=>t.R.reduce((s,r,j)=>s+r[k]*(p[j]-t.t[j]),0)/t.scale_reconstruction_units_per_model_unit),d=FlameMeasurements.distance(local,target);if(d<best){best=d;id=i;}});const v=f.vertices[id];return {x:(f.w/2+v[0]*f.scale)*c.clientWidth/c.width,y:(f.h/2-v[1]*f.scale)*c.clientHeight/c.height};});});
    const bounds=await page.locator('#fit').boundingBox();await page.mouse.move(bounds.x+half[0].x,bounds.y+half[0].y);await page.mouse.down();for(const p of half.slice(1))await page.mouse.move(bounds.x+p.x,bounds.y+p.y,{steps:40});await page.mouse.up();
    const sourceHalf=(await snapshot()).at(-1);assert.equal(sourceHalf.strokes.length,1);
    await page.getByRole('button',{name:'Mirror half to opposite side',exact:true}).click();
    await page.waitForFunction(()=>directDraft().perimeters.length===4);const copy=(await snapshot()).at(-1);assert.equal(copy.status,'pending');assert.equal(copy.mirror_provenance.source_perimeter_id,sourceHalf.id);assert.deepEqual((await snapshot())[2],sourceHalf);
    await page.locator('#mirrorFeedback').filter({hasText:'Created and selected'}).waitFor();
    await page.getByLabel('Active perimeter',{exact:true}).selectOption(sourceHalf.id);await page.getByRole('button',{name:'Build mirrored full perimeter',exact:true}).click();
    await page.waitForFunction(()=>directDraft().perimeters.length===5);const full=(await snapshot()).at(-1);assert.equal(full.closed,true);assert.equal(full.status,'pending');assert.equal(full.mirror_provenance.full_perimeter,true);assert.deepEqual((await snapshot())[2],sourceHalf);
    const mirrorDownload=page.waitForEvent('download');await page.getByRole('button',{name:'Download direct measurements',exact:true}).click();const mirroredDraft=JSON.parse(fs.readFileSync(await(await mirrorDownload).path()));assert.equal(mirroredDraft.perimeters.at(-1).mirror_provenance.source_perimeter_id,sourceHalf.id);
    await page.getByLabel('Show all perimeter drafts',{exact:true}).uncheck();
    await page.getByRole('button',{name:'Fit displayed FLAME head',exact:true}).click();await page.locator('#workspace').evaluate(e=>e.scrollIntoView({block:'start'}));await page.screenshot({path:path.join(folder,'perimeter-workspace-test.png')});assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    if(process.argv[3]){
      const regression=JSON.parse(fs.readFileSync(process.argv[3])),source=regression.perimeters[0];
      await page.getByLabel('Reload direct measurements',{exact:true}).setInputFiles(process.argv[3]);await page.waitForFunction(id=>activePerimeter()?.id===id,source.id);
      await page.getByRole('button',{name:'Mirror half to opposite side',exact:true}).click();await page.waitForFunction(count=>directDraft().perimeters.length===count,regression.perimeters.length+1);await page.locator('#mirrorFeedback').filter({hasText:'Created and selected'}).waitFor();
      assert.deepEqual((await snapshot())[0],source);await page.getByLabel('Active perimeter',{exact:true}).selectOption(source.id);await page.getByRole('button',{name:'Build mirrored full perimeter',exact:true}).click();await page.waitForFunction(count=>directDraft().perimeters.length===count,regression.perimeters.length+2);assert.equal((await snapshot()).at(-1).closed,true);
      console.log('Provided half-arc regression: mirrored half and full perimeter created; original unchanged PASS');
    }
    console.log('Perimeters: drag sampling, stable camera, Alt rotation, styles, undo, gaps, export/reload, fit isolation and no network PASS');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
