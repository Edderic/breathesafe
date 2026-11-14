const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
function component(rates=null){
 const script=fs.readFileSync(path.join(__dirname,'../../app/javascript/observed_pass_rate_comparison.vue'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1].replace('export default','module.exports =');
 const context={module:{exports:{}}};vm.runInNewContext(script,context);const options=context.module.exports,state={rates};
 for(const [name,fn]of Object.entries(options.methods))state[name]=fn.bind(state);
 for(const [name,fn]of Object.entries(options.computed))Object.defineProperty(state,name,{get:()=>fn.call(state)});
 return state;
}
test('older dashboard payloads do not imply zero-valued balanced rates',()=>{
 const panel=component({overall:{pass_rate:50}});assert.equal(panel.available,false);assert.equal(panel.percent(undefined),'N/A');assert.equal(panel.percent(null),'N/A');assert.equal(panel.percent(0),'0.0%');
});
test('style comparison aligns by style name rather than sorted backend row position',()=>{
 const panel=component({by_style:[{name:'Cup',pass_rate:80},{name:'Boat',pass_rate:20}],equal_person_mask:{by_style:[{name:'Boat',pass_rate:30},{name:'Cup',pass_rate:60}],by_mask:[]},equal_family_by_style:[{name:'Cup',pass_rate:45},{name:'Boat',pass_rate:50}]});
 assert.equal(panel.available,true);assert.equal(panel.styleRows[0].name,'Boat');assert.equal(panel.styleRows[0].test.pass_rate,20);assert.equal(panel.styleRows[0].pair.pass_rate,30);assert.equal(panel.styleRows[0].family.pass_rate,50);
});
test('missing family results remain unavailable and mask ordering is stable',()=>{
 const panel=component({by_style:[{name:'Cup',pass_rate:80}],equal_person_mask:{by_mask:[{name:'Z mask'},{name:'A mask'}]}});
 assert.equal(panel.percent(panel.styleRows[0].family?.pass_rate),'N/A');assert.equal(panel.maskRows[0].name,'A mask');
});
