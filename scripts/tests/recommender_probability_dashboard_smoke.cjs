// Compile and inspect the real Vue dashboard panel using a local model artifact.
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),workspace=process.env.BREATHESAFE_DEPENDENCY_ROOT||path.resolve(root,'../..');
const {parse,compileScript,compileTemplate}=require(path.join(workspace,'node_modules/@vue/compiler-sfc'));
const esbuild=require(path.join(workspace,'node_modules/esbuild'));
const {chromium}=require(path.join(workspace,'tmp/webcam-browser/node_modules/playwright'));
(async()=>{
 const folder=path.join(root,'tmp/recommender-metrics-review');fs.mkdirSync(folder,{recursive:true});
 const models=path.join(folder,'models');const latest=fs.readdirSync(models).filter(p=>fs.existsSync(path.join(models,p,'custom_metrics.json'))).sort().at(-1);
 assert(latest,'A completed local training artifact is required');const metrics=JSON.parse(fs.readFileSync(path.join(models,latest,'custom_metrics.json'),'utf8'));
 const evaluation=metrics.cross_validation.probability_evaluation;
 assert(evaluation?.available,'Missing actual held-out evaluation');
 const source=fs.readFileSync(path.join(root,'app/javascript/recommender_probability_metrics.vue'),'utf8'),{descriptor}=parse(source);
 const compiled=compileScript(descriptor,{id:'probability-metrics'});const template=compileTemplate({source:descriptor.template.content,filename:'recommender_probability_metrics.vue',id:'probability-metrics',compilerOptions:{bindingMetadata:compiled.bindings}});assert.equal(template.errors.length,0);const script=compiled.content.replace('export default','const ProbabilityPanel =')+'\n'+template.code.replace('export function render','function render')+'\nProbabilityPanel.render=render;';
 const entry="import {createApp,h} from 'vue';\n"+script+"\nconst data=JSON.parse(document.getElementById('fixture').textContent);window.probabilityApp=createApp({render:()=>h(ProbabilityPanel,data)});window.probabilityApp.mount('#app');";
 await esbuild.build({stdin:{contents:entry,resolveDir:root,loader:'js'},bundle:true,outfile:path.join(folder,'dashboard-panel.js'),nodePaths:[path.join(workspace,'node_modules')],define:{__VUE_OPTIONS_API__:'true',__VUE_PROD_DEVTOOLS__:'false',__VUE_PROD_HYDRATION_MISMATCH_DETAILS__:'false'}});
 const fixture=JSON.stringify({evaluation,timestamp:metrics.timestamp}).replaceAll('</','<\\/');
 const html='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Breathesafe · Held-out probability dashboard review</title><style>body{font:16px system-ui;max-width:1300px;margin:25px auto;padding:0 15px}'+descriptor.styles.map(s=>s.content).join('\n')+'</style><h1>Breathesafe dashboard · probability metrics</h1><p>Local training review; the live model and dashboard have not been changed.</p><div id="app"></div><script id="fixture" type="application/json">'+fixture+'</script><script src="dashboard-panel.js"></script>';
 const file=path.join(folder,'dashboard-review.html');fs.writeFileSync(file,html);
 const publicSnapshot=process.env.BREATHESAFE_DASHBOARD_SNAPSHOT||'/private/tmp/breathesafe-dashboard-20261112.json';
 let fullFile=null;
 if(fs.existsSync(publicSnapshot)){
  const stats=JSON.parse(fs.readFileSync(publicSnapshot,'utf8'));
  stats.recommender_performance={...stats.recommender_performance,timestamp:metrics.timestamp,probability_evaluation:evaluation,
   cross_validation_top_1_hit_rate_mean:metrics.cross_validation.top_1_hit_rate_mean,
   cross_validation_top_3_hit_rate_mean:metrics.cross_validation.top_3_hit_rate_mean,
   cross_validation_top_5_hit_rate_mean:metrics.cross_validation.top_5_hit_rate_mean,validation_roc_auc:metrics.roc_auc};
  const styles=[];
  await esbuild.build({stdin:{contents:"import {createApp,h} from 'vue';import Dashboard from './app/javascript/dashboard.vue';const fixture=JSON.parse(document.getElementById('fixture').textContent);globalThis.fetch=async url=>{if(url!=='/dashboard/stats')throw Error('Unexpected endpoint');return {ok:true,json:async()=>fixture}};createApp({render:()=>h(Dashboard)}).mount('#app');",resolveDir:root,loader:'js'},bundle:true,outfile:path.join(folder,'dashboard-full.js'),nodePaths:[path.join(workspace,'node_modules')],define:{__VUE_OPTIONS_API__:'true',__VUE_PROD_DEVTOOLS__:'false',__VUE_PROD_HYDRATION_MISMATCH_DETAILS__:'false'},plugins:[{name:'vue-review',setup(build){build.onLoad({filter:/\.vue$/},args=>{const {descriptor}=parse(fs.readFileSync(args.path,'utf8'));const script=compileScript(descriptor,{id:'review'});const template=compileTemplate({source:descriptor.template.content,filename:args.path,id:'review',compilerOptions:{bindingMetadata:script.bindings}});if(template.errors.length)throw Error(template.errors.join('\n'));styles.push(...descriptor.styles.map(s=>s.content));return {contents:script.content.replace('export default','const Component =')+'\n'+template.code.replace('export function render','function render')+'\nComponent.render=render;export default Component;',loader:'js',resolveDir:path.dirname(args.path)}})}}]});
  fullFile=path.join(folder,'dashboard-full.html');
  fs.writeFileSync(fullFile,'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Breathesafe dashboard · local training review</title><style>body{font:16px system-ui;margin:0}'+styles.join('\n')+'</style><div id="app"></div><script id="fixture" type="application/json">'+JSON.stringify(stats).replaceAll('</','<\\/')+'</script><script src="dashboard-full.js"></script>');
 }
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,args:['--allow-file-access-from-files']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>assert(!/^https?:/.test(r.url())));
  await page.goto('file://'+file);await page.waitForSelector('#fit-score-threshold');
  assert((await page.locator('body').innerText()).includes(String(evaluation.sample_count)));
  assert.equal(await page.locator('.metric-cards article').count(),4);assert.equal(await page.locator('svg').count(),2);
  const input=page.locator('#fit-score-threshold');await input.fill('0.8');await input.dispatchEvent('input');
  assert((await page.locator('.metric-cards').innerText()).includes('80.0%'));
  await page.getByRole('button',{name:/Explore maximum-F1/}).click();assert.equal(Number(await input.inputValue()),evaluation.exploratory_f1.threshold);
  await page.screenshot({path:path.join(folder,'dashboard-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:path.join(folder,'dashboard-mobile.png'),fullPage:true});
  // The older training artifacts must remain usable without rendering bogus new values.
  await page.evaluate(()=>{window.probabilityApp.unmount();document.getElementById('fixture').textContent='{}';});
  if(fullFile){await page.setViewportSize({width:1440,height:1100});await page.goto('file://'+fullFile);await page.waitForSelector('#fit-score-threshold');await page.locator('.probability-metrics').screenshot({path:path.join(folder,'dashboard-integrated.png')});console.log('Full Dashboard component loaded with the new metrics.');}
  assert.deepEqual(errors,[]);console.log('Actual held-out metrics: cards, curves, cutoff interaction, offline rendering and mobile bounds passed.');console.log(file);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
