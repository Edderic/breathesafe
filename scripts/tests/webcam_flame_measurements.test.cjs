const {test}=require('node:test'),assert=require('node:assert/strict');
const M=require('../../python/dimension_pipeline/flame_measurements_ui.js');
const mesh={vertices:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],triangles:[[0,1,2],[0,2,3]]};
const point=(name,i)=>({name,status:'reviewed',notes:'',attachment:{kind:'vertex',vertex_index:i}});
const identity={session_id:'s',fit_id:'100',model_sha256:'m',topology_id:'t',mesh_sha256:'sha'};
const draft=()=>({version:M.VERSION,...identity,points:[point('left_tragion',1),point('subnasale',0),point('right_tragion',3),point('menton',2)],routes:{scale:['left_tragion','subnasale','right_tragion'],check:['left_tragion','menton','right_tragion'],custom:[]},line:['left_tragion','right_tragion'],scale_readings_mm:[198,202,200],check_readings_mm:[210,211,209]});
test('surface routes follow edges and controls while chords use Euclidean distance',()=>{
  const d=draft(),arc=M.route(mesh,M.graph(mesh),d.points,d.routes.scale);
  assert.equal(arc.length,2);assert.equal(M.distance(mesh.vertices[1],mesh.vertices[3]),Math.sqrt(2));
  assert.ok(arc.points.length>=3);
  const bary=[{name:'a',status:'pending',attachment:{kind:'barycentric',triangle_index:0,weights:[.5,.5,0]}},{name:'b',status:'pending',attachment:{kind:'barycentric',triangle_index:0,weights:[.5,0,.5]}}];
  assert.equal(M.route(mesh,M.graph(mesh),bary,['a','b']).length,.5);
});
test('median calibration, reading spread, independent discrepancy and scale invariance',()=>{
  const d=draft(),c=M.calibration(mesh,M.graph(mesh),d);
  assert.equal(c.mm_per_reconstruction_unit,100);assert.equal(c.scale.spread_mm,4);
  assert.equal(c.independent_check.mesh_length_mm,200);assert.equal(c.independent_check.discrepancy_mm,-10);assert.equal(c.independent_check.spread_mm,2);
  d.check_readings_mm=[999,1000,1001];assert.equal(M.calibration(mesh,M.graph(mesh),d).mm_per_reconstruction_unit,100);
  const scaled={...mesh,vertices:mesh.vertices.map(p=>p.map(x=>x*5))};assert.equal(M.calibration(scaled,M.graph(scaled),d).mm_per_reconstruction_unit,20);
  d.points[1].status='pending';assert.throws(()=>M.calibration(mesh,M.graph(mesh),d),/Review/);
});
test('missing, unavailable and disconnected coverage fails explicitly',()=>{
  const d=draft();d.points[0].attachment=null;assert.throws(()=>M.route(mesh,M.graph(mesh),d.points,d.routes.scale),/Place/);
  d.points[0]=point('left_tragion',1);d.points[0].status='unavailable';assert.throws(()=>M.route(mesh,M.graph(mesh),d.points,d.routes.scale),/available/);
  const separate={vertices:[[0,0,0],[1,0,0],[0,1,0],[0,0,2],[1,0,2],[0,1,2]],triangles:[[0,1,2],[3,4,5]]};
  assert.throws(()=>M.route(separate,M.graph(separate),[point('a',0),point('b',3)],['a','b']),/disconnected/);
  assert.throws(()=>M.readings([1,NaN,2]));
});
test('reload binds points and calibration readings to the exact fitted mesh',()=>{
  const d=draft();assert.equal(M.validate(d,identity,mesh),d);
  for(const key of Object.keys(identity))assert.throws(()=>M.validate({...d,[key]:'changed'},identity,mesh),/different/);
  const invalid=structuredClone(d);invalid.points.push(point('menton',0));assert.throws(()=>M.validate(invalid,identity,mesh),/duplicate/);
  const bad=structuredClone(d);bad.points[0].attachment={kind:'vertex',vertex_index:999};assert.throws(()=>M.validate(bad,identity,mesh),/Invalid/);
});
test('named arc smoothing preserves controls and recalibrates using the displayed route length',()=>{
  const d=draft();d.points.find(p=>p.name==='subnasale').attachment={kind:'vertex',vertex_index:3};d.points.find(p=>p.name==='right_tragion').attachment={kind:'vertex',vertex_index:2};
  const original=JSON.stringify(d.points),edges=M.graph(mesh),raw=M.route(mesh,edges,d.points,d.routes.scale),smooth=M.route(mesh,edges,d.points,d.routes.scale,'surface');
  assert.equal(raw.length,3);assert.ok(Math.abs(smooth.length-(Math.sqrt(2)+1))<1e-12);assert.ok(smooth.points.some(p=>M.distance(p,mesh.vertices[3])<1e-12));assert.equal(JSON.stringify(d.points),original);
  d.route_methods={scale:'surface',check:'edges'};const calibrated=M.calibration(mesh,edges,d);
  assert.equal(calibrated.scale.route_length_reconstruction_units,smooth.length);assert.equal(calibrated.mm_per_reconstruction_unit,200/smooth.length);assert.equal(calibrated.scale.route_method,smooth.method);
  d.route_methods.scale='invalid';assert.throws(()=>M.validate(d,identity,mesh),/smoothing/);
});
