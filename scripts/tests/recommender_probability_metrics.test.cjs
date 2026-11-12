const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
function component(evaluation=null){
 const source=fs.readFileSync(path.join(__dirname,'../../app/javascript/recommender_probability_metrics.vue'),'utf8');
 const script=source.match(/<script>([\s\S]*?)<\/script>/)[1].replace('export default','module.exports =');
 const context={module:{exports:{}}};vm.runInNewContext(script,context);const options=context.module.exports;
 const state={...options.data(),evaluation};
 for(const [name,fn]of Object.entries(options.methods))state[name]=fn.bind(state);
 for(const [name,fn]of Object.entries(options.computed))Object.defineProperty(state,name,{get:()=>fn.call(state)});
 return state;
}
test('legacy artifacts show unavailable instead of zero-valued metrics',()=>{
 const panel=component();assert.equal(Boolean(panel.available),false);assert.equal(panel.percent(null),'N/A');assert.equal(panel.number(undefined),'N/A');assert.equal(panel.selectedMetrics,null);
});
test('zero is a valid metric and changing a cutoff selects its own confusion row',()=>{
 const panel=component({version:'held_out_probability_evaluation_v1',available:true,threshold_curve:[{threshold:.5,precision:0,recall:0},{threshold:.3,precision:.6,recall:.8}],exploratory_f1:{threshold:.3}});
 assert.equal(panel.available,true);assert.equal(panel.percent(0),'0.0%');assert.equal(panel.selectedMetrics.precision,0);
 panel.useExploratoryThreshold();assert.equal(panel.threshold,.3);assert.equal(panel.selectedMetrics.recall,.8);
});
test('curves omit undefined precision rather than plotting a fabricated zero',()=>{
 const panel=component({threshold_curve:[{threshold:0,precision:.2},{threshold:1,precision:null}]});
 assert.equal(panel.metricPoints('precision'),'40,156');
});
