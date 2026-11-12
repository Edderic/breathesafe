// Read-only live inspection of a completed local development experiment run.
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.WEBCAM_PLAYWRIGHT || path.resolve(__dirname,'../../tmp/webcam-browser/node_modules/playwright'));
const root=path.resolve(__dirname,'../..'),privateRoot=path.join(root,'.private-webcam-runs');
const active=JSON.parse(fs.readFileSync(path.join(privateRoot,'capture-comparisons/bre17-active-run.json')));
(async()=>{
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--enable-unsafe-swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1100}});page.setDefaultTimeout(60000);const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const before=fs.readFileSync(path.join(privateRoot,active.session_id,'session.json'),'utf8');const state=JSON.parse(before);
  const run=state.depth_experiments.runs.find(r=>r.id===active.run_id);assert.equal(run.status,'completed');
  await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
  await page.getByRole('button',{name:'Connect processor',exact:true}).click();await page.getByLabel('Saved session').selectOption(active.session_id);await page.getByRole('button',{name:'Resume',exact:true}).click();
  await page.getByRole('button',{name:'Compare full and analysis meshes',exact:true}).click();
  const comparison=page.getByRole('region',{name:'Full and analysis mesh comparison',exact:true});
  await page.getByRole('img',{name:'Full reconstruction inspection',exact:true}).waitFor({state:'visible'});
  for(const row of run.variants){
   await comparison.getByLabel('Comparison variant',{exact:true}).selectOption(row.id);
   const candidate=page.getByRole('img',{name:row.label+' inspection',exact:true});await candidate.waitFor({state:'visible'});
   assert.equal(await comparison.getByLabel('Reference mesh',{exact:true}).inputValue(),'raw');
   const reference=page.getByRole('img',{name:'Full reconstruction inspection',exact:true});await reference.waitFor({state:'visible'});
   await page.getByRole('button',{name:'Reset view / fit surface',exact:true}).click();
   for(const [angle,name] of [[0,'front'],[-35,'left'],[35,'right']]){
    await page.getByLabel('Yaw',{exact:true}).evaluate((input,value)=>{input.value=String(value);input.dispatchEvent(new Event('input',{bubbles:true}));},angle);
    await comparison.screenshot({path:path.join(privateRoot,'capture-comparisons',`bre17-${row.profile_id}-${name}.png`)});
   }
   console.log(row.profile_id+' raw/variant full-resolution comparison + shared orientation: PASS');
  }
  await page.getByRole('checkbox',{name:'Tap to place route controls',exact:true}).check();
  await page.getByRole('img',{name:run.variants.at(-1).label+' inspection',exact:true}).click({modifiers:['Control']});
  await page.getByText('No controls placed',{exact:true}).waitFor();
  assert.equal(fs.readFileSync(path.join(privateRoot,active.session_id,'session.json'),'utf8'),before);assert.deepEqual(errors,[]);
  console.log('live experiment inspection is read-only; original annotation state unchanged: PASS');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
