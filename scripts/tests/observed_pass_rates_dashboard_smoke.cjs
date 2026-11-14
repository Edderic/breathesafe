// Compile the real dashboard with local database aggregates; no network requests.
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const {parse,compileScript,compileTemplate}=require(path.join(root,'node_modules/@vue/compiler-sfc'));
const esbuild=require(path.join(root,'node_modules/esbuild'));
const {chromium}=require(path.join(root,'tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const folder=path.join(root,'tmp/dashboard-pass-rate-review'),stats=JSON.parse(fs.readFileSync(path.join(folder,'dashboard-stats.json'),'utf8'));
 const rates=stats.fit_tests.pass_rates;assert(rates.equal_person_mask,'New aggregates required');const styles=[];
 await esbuild.build({stdin:{contents:"import {createApp,h} from 'vue';import Dashboard from './app/javascript/dashboard.vue';const fixture=JSON.parse(document.getElementById('fixture').textContent);globalThis.fetch=async url=>{if(url!=='/dashboard/stats')throw Error('Unexpected endpoint');return {ok:true,json:async()=>fixture}};createApp({render:()=>h(Dashboard)}).mount('#app');",resolveDir:root,loader:'js'},bundle:true,outfile:path.join(folder,'dashboard.js'),define:{__VUE_OPTIONS_API__:'true',__VUE_PROD_DEVTOOLS__:'false',__VUE_PROD_HYDRATION_MISMATCH_DETAILS__:'false'},plugins:[{name:'vue-review',setup(build){build.onLoad({filter:/\.vue$/},args=>{const {descriptor}=parse(fs.readFileSync(args.path,'utf8'));const script=compileScript(descriptor,{id:'observed-review'});const template=compileTemplate({source:descriptor.template.content,filename:args.path,id:'observed-review',compilerOptions:{bindingMetadata:script.bindings}});if(template.errors.length)throw Error(template.errors.join('\n'));styles.push(...descriptor.styles.map(s=>s.content));return {contents:script.content.replace('export default','const Component =')+'\n'+template.code.replace('export function render','function render')+'\nComponent.render=render;export default Component;',loader:'js',resolveDir:path.dirname(args.path)}})}}]});
 const file=path.join(folder,'dashboard.html');fs.writeFileSync(file,'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Breathesafe dashboard · balanced pass rates</title><style>body{font:16px system-ui;margin:0}'+styles.join('\n')+'</style><div id="app"></div><script id="fixture" type="application/json">'+JSON.stringify(stats).replaceAll('</','<\\/')+'</script><script src="dashboard.js"></script>');
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url())));
  await page.goto('file://'+file);const panel=page.locator('.observed-rate-comparison');await panel.waitFor();
  assert((await page.getByTestId('equal-pair-overall').innerText()).includes(rates.equal_person_mask.overall.pass_rate.toFixed(1)+'%'));
  assert((await page.getByTestId('equal-pair-overall').innerText()).includes(rates.equal_person_mask.overall.pair_count+' pairs'));
  const rows=page.getByTestId('style-rate-comparison').locator('tbody tr');assert.equal(await rows.count(),rates.equal_family_by_style.length);
  for(const family of rates.equal_family_by_style){const row=rows.filter({has:page.locator('th',{hasText:new RegExp('^'+family.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'$')})});assert.equal(await row.count(),1);assert((await row.locator('td').nth(2).innerText()).includes(family.pass_rate.toFixed(1)+'%'));}
  await panel.locator('summary').click();assert.equal(await page.getByTestId('equal-pair-mask-rates').locator('tbody tr').count(),rates.equal_person_mask.by_mask.length);
  await panel.screenshot({path:path.join(folder,'balanced-rates-desktop.png')});
  await panel.locator('summary').click();await page.setViewportSize({width:390,height:844});await page.waitForTimeout(300);const overflow=await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(el=>el.getBoundingClientRect().right>innerWidth+1 && getComputedStyle(el).display!=='none').slice(0,15).map(el=>({tag:el.tagName,cls:el.className,right:el.getBoundingClientRect().right,width:el.getBoundingClientRect().width})));if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))console.log(JSON.stringify(overflow));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile document overflow');
  await panel.screenshot({path:path.join(folder,'balanced-rates-mobile.png')});assert.deepEqual(errors,[]);
  console.log('Actual Dashboard: balanced rates, family comparison, per-mask detail, offline rendering and mobile bounds passed.');console.log(file);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
