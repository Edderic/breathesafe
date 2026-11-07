// Automated interaction fixture only: no participant anatomical review is inferred.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
  const folder=path.resolve(process.argv[2]||'.private-webcam-runs/flame-fits/c79e26de-analog-review');
  const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try{
    const page=await browser.newPage({viewport:{width:1500,height:1200},acceptDownloads:true});
    const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
    await page.goto(pathToFileURL(path.join(folder,'comparison.html')).href);
    await page.getByRole('status').filter({hasText:'Completed'}).waitFor();
    await page.getByText('Optional legacy ARKit counterpart mapping',{exact:true}).click();
    await page.getByLabel('Path',{exact:true}).selectOption('nose');
    await page.getByLabel('ARKit point',{exact:true}).selectOption('14');
    await page.getByLabel('Click to place selected counterpart',{exact:true}).check();
    const canvas=page.locator('#fit');await canvas.scrollIntoViewIfNeeded();
    const click=await canvas.evaluate(c=>{
      const f=c.pickFrame,p=[0,0];
      const a=FlameMapping.pick(f.mesh,f.vertices,p,'vertex');
      return {x:(f.w/2)*c.clientWidth/c.width,y:(f.h/2)*c.clientHeight/c.height,expected:a};
    });
    assert.ok(click.expected);await canvas.click({position:{x:click.x,y:click.y}});
    await page.locator('#mappingStatus').filter({hasText:`Original FLAME vertex ${click.expected.vertex_index}`}).waitFor();
    await page.getByLabel('Review notes',{exact:true}).fill('AUTOMATED TEST ONLY; not participant review.');
    await page.getByLabel('Review status',{exact:true}).selectOption('reviewed');
    await page.locator('#mappingStatus').filter({hasText:'1 reviewed weighted counterparts'}).waitFor();
    const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Download mapping draft',exact:true}).click();
    const exported=JSON.parse(fs.readFileSync(await(await downloadPromise).path()));
    assert.equal(exported.version,'flame-arkit-analogs-v1');assert.deepEqual(exported.points[0].attachment,click.expected);
    assert.equal(exported.points[0].status,'reviewed');
    await page.getByRole('button',{name:'Next point',exact:true}).click();assert.notEqual(await page.getByLabel('ARKit point',{exact:true}).inputValue(),'14');
    await page.getByRole('button',{name:'Previous point',exact:true}).click();assert.equal(await page.getByLabel('ARKit point',{exact:true}).inputValue(),'14');
    await page.getByRole('button',{name:'Clear selected placement',exact:true}).click();
    await page.getByLabel('Reload mapping',{exact:true}).setInputFiles({name:'mapping.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(exported))});
    await page.locator('#mappingStatus').filter({hasText:'1 reviewed weighted counterparts'}).waitFor();
    await page.getByLabel('Shape components',{exact:true}).selectOption('300');
    await page.getByRole('heading',{name:'FLAME · 300 shape components',exact:true}).waitFor();
    assert.equal(await page.getByLabel('FLAME vertex index',{exact:true}).inputValue(),String(click.expected.vertex_index));
    const bad={...exported,topology_id:'wrong'};
    await page.getByLabel('Reload mapping',{exact:true}).setInputFiles({name:'wrong.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(bad))});
    await page.getByRole('alert').filter({hasText:'different model'}).waitFor();
    await page.getByLabel('Reload mapping',{exact:true}).setInputFiles({name:'mapping.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(exported))});
    await page.getByLabel('Placement',{exact:true}).selectOption('barycentric');
    await canvas.click({position:{x:click.x,y:click.y}});
    await page.locator('#mappingStatus').filter({hasText:'Original FLAME triangle'}).waitFor();
    assert.equal(await page.getByLabel('Review status',{exact:true}).inputValue(),'pending');
    await page.getByLabel('Show analysis / comparison mesh',{exact:true}).check();
    await page.getByLabel('Left comparison',{exact:true}).selectOption('100');
    await page.getByRole('heading',{name:'FLAME · 100 components · ordinary',exact:true}).waitFor();
    await page.getByRole('button',{name:'Left profile',exact:true}).click();
    await canvas.screenshot({path:path.join(folder,'mapping-interaction-test.png')});
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('FLAME analog review: original IDs, visible picking, review reset, navigation, export/reload, identity rejection, variant transfer, comparison and no network PASS');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
