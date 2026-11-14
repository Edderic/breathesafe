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
 if(process.argv.includes('--capture-bifold')){
  await page.goto('file://'+path.join(workspace,'.private-webcam-runs/mask-route-review/bifold-neck-003-v1/review.html'));
  await page.waitForFunction(()=>document.querySelector('canvas[data-ready="true"]'));
  await page.addStyleTag({content:'.controls{display:none!important}'});
  await page.evaluate(()=>{yaw=.4;tilt=0;for(const p of paths)p.color='#ff9f1c';draw()});
  await page.locator('#view').screenshot({path:path.join(assets,'bifold-cup-route.jpg'),type:'jpeg',quality:95});
  assert.deepEqual(errors,[]);console.log('Captured proposed bifold/cup route on the reconstructed surface.');return;
 }
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
 const goal=page.locator('.slide').nth(1);assert((await goal.innerText()).includes('general public'));assert.equal(await goal.locator('img.goal-illustration').count(),1);
 const paired=JSON.parse(fs.readFileSync(path.join(deck,'paired-measurement-evidence.json'),'utf8'));
 for(const [index,weighting] of [[9,'test_weighted']]){
  const rows=await page.locator('.slide').nth(index).locator('tbody tr').allTextContents();
  const expected=paired.metrics.filter(r=>r.weighting===weighting);assert.equal(rows.length,3);
  for(let i=0;i<3;i++){for(const value of [(100*expected[i].precision).toFixed(1)+'%',(100*expected[i].recall).toFixed(1)+'%',(100*expected[i].negative_predictive_value).toFixed(1)+'%',expected[i].f1.toFixed(3),expected[i].log_loss.toFixed(3)])assert(rows[i].includes(value),'Paired metric mismatch: '+value)}
 }
 assert.equal(await page.locator('.slide').nth(9).locator('h1').innerText(),'ARKit vs. Traditional (Tape/Caliper)');
 const pairedDimensions=await page.locator('.paired-slide .paired-dimensions').innerText();for(const label of ['face width','face length','bitragion–subnasale arc','nose protrusion','nasal root breadth','nose bridge height','PCA-3'])assert(pairedDimensions.includes(label));
 const predictorSlide=page.locator('.slide').filter({hasText:'Which predictors enter the traditional models?'});assert.equal(await predictorSlide.count(),1);
 assert.deepEqual(await predictorSlide.locator('[data-predictor]').evaluateAll(nodes=>nodes.map(n=>n.dataset.predictor)),paired.traditional_predictors_mm);
 const experiment=JSON.parse(fs.readFileSync(path.join(deck,'recommender-evidence.json'),'utf8'));
 const npvRow=page.locator('.slide').nth(8).locator('tbody tr').filter({hasText:'Negative predictive value'});
 for(const name of ['none','latent_nose_v1'])assert((await npvRow.innerText()).includes((experiment.variants[name].negative_predictive_value*100).toFixed(1)+'%'));
 assert.equal(await page.locator('.slide').filter({hasText:'Give every participant equal influence, too.'}).count(),0);
 const community=page.locator('.sample-slide');assert.equal(await community.count(),1);for(const text of ['Convenience sample','Immunocompromised or disabled people','Disability justice advocates','Family members'])assert((await community.innerText()).includes(text));
 const logit=page.locator('.defined-logit');assert.equal(await logit.count(),1);assert((await logit.innerText()).includes('aΔP² + bΔP + c'));
 const coefficients=page.locator('.coefficient-slide');assert.equal(await coefficients.count(),1);for(const text of ['a = −exp(α','b = b','c = c','ΔP* = −b / (2a)','learned jointly'])assert((await coefficients.innerText()).includes(text));
 const terms=page.locator('.traditional-terms-slide');assert.equal(await terms.count(),1);for(const text of ['x₁²','PC₁²','Each linear or squared facial term','No explicit pairwise facial cross-products','unconstrained coefficient signs'])assert((await terms.innerText()).includes(text));
 const definition=page.locator('.fit-definition-slide');assert.equal(await definition.count(),1);for(const text of ['≥100','harmonic mean ×2','User seal-check reports','no positive fit label'])assert((await definition.innerText()).includes(text));
 const sourceCounts=JSON.parse(fs.readFileSync(path.join(deck,'fit-evidence-source-counts.json'),'utf8'));assert.equal(Object.values(sourceCounts.by_type).reduce((a,b)=>a+b,0),sourceCounts.total_analyzed_records);
 for(const [key,value] of Object.entries(sourceCounts.by_type)){const row=definition.locator('[data-fit-source="'+key+'"]');assert((await row.innerText()).includes(value.toLocaleString('en-US')));assert((await row.innerText()).includes((100*value/sourceCounts.total_analyzed_records).toFixed(1)+'%'));}assert((await definition.innerText()).includes('Access varies'));
 const equations=page.locator('.conversion-equations-slide');assert.equal(await equations.count(),1);for(const text of ['1/Fᵢ = Lᵢ','F̂ᵢ = 1/Lᵢ','2 × n / Σᵢ(1/F̂ᵢ)','Aaron Collins','normal breathing rates'])assert((await equations.innerText()).includes(text));assert.equal(await equations.locator('a').filter({hasText:'MaskNerd spreadsheet'}).count(),1);
 assert((await equations.locator('.conversion-example').innerText()).includes('198'));assert(Math.abs(1/(1-(1-1/50)/.99)*2-198)<1e-9);
 assert.equal(await equations.locator('a[href="https://github.com/Edderic/breathesafe/blob/main/python/mask_recommender/notebooks/inferring-n95-mode-fit-factors.ipynb"]').count(),1);
 assert((await community.innerText()).includes('55 unique users'));assert((await definition.locator('.fit-data-summary').innerText()).includes(sourceCounts.total_analyzed_records.toLocaleString('en-US')+' fit tests'));assert((await definition.locator('.fit-data-summary').innerText()).includes(sourceCounts.unique_user_mask_pairs.toLocaleString('en-US')+' unique user–mask pairs'));
 const conversion=JSON.parse(fs.readFileSync(path.join(deck,'n95-conversion-evidence.json'),'utf8'));assert.equal(conversion.mask_aggregates,24);assert.equal(conversion.people,1);assert.equal(conversion.excluded_assigned_or_mixed_mask_aggregates,12);assert(conversion.diagnostics.split_rhat.every(v=>v<1.01));
 const conversionSlide=page.locator('.conversion-slide');assert.equal(await conversionSlide.count(),1);assert.equal(await conversionSlide.locator('img.conversion-chart').count(),1);assert((await conversionSlide.innerText()).includes('1 wearer · 24 mask aggregates'));
 const sealRules=page.locator('.seal-rule-slide');assert.equal(await sealRules.count(),1);for(const text of ['Too big','Too small','A lot of air movement','Somewhere in-between too small and too big','Some air movement','No air movement','unknown (NULL)','“A lot” with missing sizing is incomplete','Negative-pressure answers do not enter'])assert((await sealRules.innerText()).includes(text));
 const reorderedTitles=await page.locator('.slide h1').allTextContents();assert.deepEqual(reorderedTitles.slice(4,8),['A convenience sample seeking protection.','Demographic breakdown','What does “fit” mean in this dataset?','Which masks are most represented? · Top 30']);
 assert.deepEqual(reorderedTitles.slice(10,17),['Photos now produce a physically scaled digital headform.','Automated landmark placements support chords and surface routes.','Three linear checks agree within 2.3 mm in one pilot.','Acknowledgements.','The tradeoff: metric scale, speed, and reach.','ARKit vs. caliper: an exploratory self-check.','A mesh vertex is not an anatomical definition.']);
 const demographicEvidence=JSON.parse(fs.readFileSync(path.join(deck,'data/dashboard-2026-10-29.json'),'utf8')).fit_tests.demographics;
 const demographicSlide=page.locator('.slide').nth(5);assert((await demographicSlide.innerText()).includes('55 unique participants'));
 for(const [index,key] of ['gender_and_sex','race_ethnicity','age'].entries()){const rows=demographicSlide.locator('.demographic-grid article').nth(index).locator('.demographic-row');assert.equal(await rows.count(),demographicEvidence[key].length);for(const [i,row] of demographicEvidence[key].entries())assert.equal(await rows.nth(i).locator('strong').innerText(),row.unique_users+' ('+(100*row.unique_users/55).toFixed(1)+'%)');}
 const testingPhotos=JSON.parse(fs.readFileSync(path.join(deck,'fit-testing-photo-sources.json'),'utf8'));assert.equal(await definition.locator('.fit-testing-gallery img').count(),4);for(const photo of testingPhotos.images)assert((await definition.locator('.fit-testing-gallery').innerText()).includes(photo.caption));
 const observed=JSON.parse(fs.readFileSync(path.join(deck,'observed-pass-rate-evidence.json'),'utf8')).pass_rates;
 const balanced=page.locator('.balanced-pass-slide');assert.equal(await balanced.count(),1);for(const rate of [observed.overall.pass_rate,observed.equal_person_mask.overall.pass_rate])assert((await balanced.innerText()).includes(rate.toFixed(1)+'%'));
 for(const family of observed.equal_family_by_style){const test=observed.by_style.find(s=>s.name===family.name);if(!test||test.total<10)continue;const row=balanced.locator('tr').filter({has:page.locator('td',{hasText:new RegExp('^'+family.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'$')})});assert.equal(await row.count(),1);assert((await row.locator('td').nth(3).innerText()).includes(family.pass_rate.toFixed(1)+'%'));}
 const coverage=JSON.parse(fs.readFileSync(path.join(deck,'mask-coverage-evidence.json'),'utf8'));const coverageSlide=page.locator('.mask-coverage-slide');assert.equal(await coverageSlide.count(),1);assert.equal(coverage.top_n,30);assert.equal(await coverageSlide.locator('.coverage-columns table').count(),3);assert.equal(await coverageSlide.locator('tbody tr').count(),coverage.top_n);assert.equal(coverage.masks.reduce((sum,row)=>sum+row.test_count,0),coverage.total_tests);
 for(const [index,mask] of coverage.masks.slice(0,coverage.top_n).entries()){const row=coverageSlide.locator('tbody tr').nth(index);assert.equal(await row.locator('td').nth(1).getAttribute('data-mask-name'),mask.name);assert.equal(await row.locator('td').nth(2).innerText(),String(mask.test_count));assert.equal(await row.locator('td').nth(3).innerText(),(100*mask.test_count/coverage.total_tests).toFixed(1)+'%');}assert((await page.locator('.slide').nth(27).innerText()).includes('Pass rates depend on how observations are weighted.'));
 const routesSlide=page.locator('.landmark-routes');assert.equal(await routesSlide.locator('.prototype-figures figure').count(),3);assert((await routesSlide.innerText()).includes('Proposed bifold / cup arc'));
 const captureSlide=page.locator('.capture-prototype');assert.equal(await captureSlide.locator('.capture-photo-row img').count(),4);assert((await captureSlide.innerText()).includes('MacBook Pro camera'));
 const walkthrough=page.locator('.projection-walkthrough-slide');assert.equal(await walkthrough.count(),1);assert.equal(await walkthrough.locator('img').count(),2);for(const text of ['RealDenseFace','Triangulate','Previously drawn FLAME','unsupported gaps','mm scale'])assert((await walkthrough.innerText()).includes(text));
 const bootstrap=JSON.parse(fs.readFileSync(path.join(deck,'recommender-bootstrap-evidence.json'),'utf8'));assert.equal(bootstrap.replicates,10000);const bootstrapSlide=page.locator('.bootstrap-slide');assert.equal(await bootstrapSlide.count(),1);assert.equal(await bootstrapSlide.locator('tbody tr').count(),5);assert.equal(await page.locator('.metrics-slide .metric-ci').count(),10);
 for(const [metric,result] of Object.entries(bootstrap.superiority)){const cell=bootstrapSlide.locator('[data-bootstrap-metric="'+metric+'"] .bootstrap-frequency');assert((await cell.innerText()).includes((100*result.better_frequency).toFixed(2)+'%'));assert.equal(result.better_replicates+result.worse_replicates+result.tied_replicates,result.valid_replicates);assert.equal(result.valid_replicates,10000);}
 const rankedMetrics=Object.entries(bootstrap.superiority).sort((a,b)=>b[1].better_frequency-a[1].better_frequency);const metricRows=page.locator('.metrics-slide tbody tr');assert.deepEqual(await metricRows.evaluateAll(rows=>rows.map(row=>row.dataset.metric)),rankedMetrics.map(([metric])=>metric));for(const [index,[metric,result]] of rankedMetrics.entries())assert.equal(await metricRows.nth(index).locator('.nose-win-frequency').innerText(),(100*result.better_frequency).toFixed(2)+'%');
 const count=await page.locator('.slide').count();assert.equal(count,31);assert(!(await page.locator('main').innerText()).includes('Unresolved difference'));
 const overflow=[];
 for(let i=0;i<count;i++){
  await page.goto('file://'+file+'#slide-'+(i+1));
  const info=await page.locator('.slide.active').evaluate(s=>({title:s.querySelector('h1').textContent,height:s.getBoundingClientRect().height,bottom:s.querySelector('footer').getBoundingClientRect().bottom,width:s.scrollWidth,client:s.clientWidth}));
  if(info.bottom>769||info.width>info.client+1)overflow.push({slide:i+1,...info});
  if([1,4,5,6,7,8,9,10,11,13,14,15,20,21,22,23,24,25,26,27,28,29].includes(i))await page.screenshot({path:path.join(root,'tmp/nasem-preview/slide-'+(i+1)+'.png')});
 }
 if(overflow.length)console.log(JSON.stringify(overflow,null,2));assert.deepEqual(overflow,[],'Screen overflow');
 await page.setViewportSize({width:1448,height:1140});await page.goto('file://'+file+'#slide-8');
 const tallCoverage=await page.locator('.mask-coverage-slide').evaluate(s=>({font:parseFloat(getComputedStyle(s.querySelector('tbody td:nth-child(2)')).fontSize),bottom:s.querySelector('footer').getBoundingClientRect().bottom,width:s.scrollWidth,client:s.clientWidth}));
 assert(tallCoverage.font>=19,'Tall-screen table text should use the available space');assert(tallCoverage.bottom<=1141,'Tall-screen coverage overflow');assert(tallCoverage.width<=tallCoverage.client+1);
 await page.screenshot({path:path.join(root,'tmp/nasem-preview/slide-8-tall.png')});await page.setViewportSize({width:1366,height:768});
 await page.goto('file://'+file+'#slide-1');await page.locator('#next').click();assert.equal(await page.locator('.slide.active').count(),1);assert.equal(await page.locator('#counter').textContent(),'2 / '+count);
 await page.locator('body').click({position:{x:5,y:100}});await page.keyboard.press('End');assert.equal(await page.locator('#counter').textContent(),count+' / '+count);await page.keyboard.press('Home');assert.equal(await page.locator('#counter').textContent(),'1 / '+count);
 await page.click('#overview');assert.equal(await page.locator('.slide:visible').count(),count);await page.click('#overview');
 await page.emulateMedia({media:'print'});
 const printOverflow=await page.locator('.slide').evaluateAll(slides=>slides.flatMap((s,i)=>s.scrollHeight>s.clientHeight+2?[{slide:i+1,height:s.clientHeight,scroll:s.scrollHeight}]:[]));if(printOverflow.length)console.log(JSON.stringify(printOverflow,null,2));assert.deepEqual(printOverflow,[],'Print overflow');
 await page.pdf({path:path.join(deck,'presentation.pdf'),preferCSSPageSize:true,printBackground:true,displayHeaderFooter:false});
 await page.emulateMedia({media:'screen'});await page.setViewportSize({width:390,height:844});
 for(const i of [1,4,5,6,7,8,9,10,11,13,14,15,20,21,22,23,24,25,26,27,28,29]){await page.goto('file://'+file+'#slide-'+(i+1));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),'Mobile horizontal overflow on '+(i+1))}
 assert.deepEqual(errors,[]);console.log(count+' slides: offline assets, desktop/mobile layout, navigation, print bounds and PDF export passed.');
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
