// Intercept every processor request: no real session is modified or submitted.
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(path.resolve('tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const folder=path.resolve(process.argv[2]),state=JSON.parse(fs.readFileSync(path.join(folder,'session.json'))),id=state.id;
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 try{const page=await browser.newPage({viewport:{width:1400,height:1100}}),errors=[],saves=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://127.0.0.1:5182/**',async route=>{
  const request=route.request(),url=new URL(request.url()),headers={'Access-Control-Allow-Origin':'http://127.0.0.1:5178','Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'GET, POST, OPTIONS'};
  const json=body=>route.fulfill({headers,contentType:'application/json',body:JSON.stringify(body)});
  if(request.method()==='OPTIONS')return route.fulfill({headers,status:204});
  if(url.pathname==='/diagnostics')return json({ready:true,tools:{}});
  if(url.pathname==='/sessions')return json([{id,created_at:state.created_at,status:state.status,capture_context:state.capture_context,capture_count:61}]);
  if(url.pathname===`/sessions/${id}`)return json(state);
  const capture=url.pathname.match(/\/captures\/(front|turn_\d\d)\/(image|mask)$/);
  if(capture){const row=state.captures.find(c=>c.slot===capture[1]);return route.fulfill({headers,contentType:'image/png',body:fs.readFileSync(path.join(folder,row[capture[2]]))});}
  if(url.pathname.endsWith('/capture')){const p=request.postDataJSON();saves.push(p);const c=state.captures.find(c=>c.slot===p.slot);c.mask_approved=true;c.mask_provenance=p.mask_provenance;return json(state);}
  throw Error('Unexpected request '+url.pathname);
 });
 await page.goto('http://127.0.0.1:5178/scripts/webcam_pilot.html');
 await page.getByRole('button',{name:'Connect processor',exact:true}).click();
 await page.getByLabel('Saved session',{exact:true}).selectOption(id);
 await page.getByRole('button',{name:'Resume',exact:true}).click();
 await page.getByText('0/61 approved images saved locally',{exact:false}).waitFor();
 assert.equal(await page.getByRole('button',{name:'Reconstruct approved images',exact:true}).isDisabled(),true);
 assert.equal(await page.getByRole('button',{name:'Accept all frames',exact:true}).isDisabled(),true);
 await page.getByRole('button',{name:'Load / generate mask',exact:true}).click();
 const approve=page.getByRole('button',{name:'Approve and save this mask',exact:true});await approve.waitFor();
 await page.waitForFunction(()=>[...document.querySelectorAll('button')].some(b=>b.textContent==='Approve and save this mask'&&!b.disabled));
 await approve.click();await page.getByText('1/61 approved images saved locally',{exact:false}).waitFor();
 await page.waitForFunction(()=>[...document.querySelectorAll('select')].some(s=>s.value==='1'));
 assert.equal(saves.length,1);assert.equal(saves[0].slot,'front');assert.equal(saves[0].mask_provenance.acceptance_method,'individual');
 assert.equal(saves[0].mask_provenance.source_mask_sha256,state.captures.find(c=>c.slot==='front').mask_provenance.source_mask_sha256);
 await page.screenshot({path:path.join(folder,'review-browser.png'),fullPage:true});
 assert.deepEqual(errors,[]);console.log('Upper-neck proposals: resume, pending count, stored mask loading, gated reconstruction, individual save and advance PASS');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
