const {test}=require('node:test'),assert=require('node:assert/strict');
const M=require('../../python/dimension_pipeline/flame_measurements_ui.js');
const mesh={vertices:[[0,0,0],[1,0,0],[1,1,0],[0,1,0]],triangles:[[0,1,2],[0,2,3]]};
const a=i=>({kind:'vertex',vertex_index:i});
const draft=()=>({id:'p1',name:'Candidate perimeter',style:'bifold',status:'pending',closed:false,notes:'',strokes:[]});
test('drag controls append locally, split distant strokes and reset review without changing other drafts',()=>{
  const p=draft(),other={...draft(),id:'p2',style:'trifold'};
  M.addPerimeterStroke(p,[a(0),a(1)],mesh,.1);p.status='reviewed';
  M.addPerimeterStroke(p,[a(1),a(2)],mesh,.1);
  assert.equal(p.strokes.length,1);assert.equal(p.status,'pending');assert.equal(other.strokes.length,0);
  M.addPerimeterStroke(p,[a(0),a(3)],mesh,.1);assert.equal(p.strokes.length,2);
  const report=M.measurePerimeter(p,mesh,M.graph(mesh),2);assert.equal(report.status,'separate_strokes_partial_length');assert.equal(report.length,3);assert.equal(report.closed,false);
});
test('explicit closure includes the closing surface path, and gaps do not become valid perimeters',()=>{
  const p=draft();p.strokes=[[a(0),a(1),a(2),a(3)]];
  assert.equal(M.measurePerimeter(p,mesh,M.graph(mesh),1.1).length,3);
  p.closed=true;assert.equal(M.measurePerimeter(p,mesh,M.graph(mesh),1.1).length,4);
  p.strokes=[[a(0),a(2),a(3)]];assert.throws(()=>M.measurePerimeter(p,mesh,M.graph(mesh),1.1),/gap/);
});
test('perimeter persistence validates style, original attachments, resources and closed continuity',()=>{
  const p=draft();p.strokes=[[a(0),a(1)]];assert.equal(M.validatePerimeters([p],mesh)[0],p);
  for(const style of ['bifold','bifold_gasket','cup','trifold','duckbill','custom'])assert.ok(M.perimeterStyles[style]);
  assert.throws(()=>M.validatePerimeters([{...p,style:'unknown'}],mesh));
  assert.throws(()=>M.validatePerimeters([p,p],mesh));
  assert.throws(()=>M.validatePerimeters([{...p,strokes:[[a(99)]]}],mesh));
  assert.throws(()=>M.validatePerimeters([{...p,closed:true,strokes:[[a(0)],[a(1)]]}],mesh));
  const snapshot=JSON.stringify(p);assert.throws(()=>M.addPerimeterStroke(p,Array(201).fill(a(1)),mesh,.1));assert.equal(JSON.stringify(p),snapshot);
});
test('heap edge routing preserves disconnected failures and surface detours',()=>{
  const p=draft(),two={vertices:[...mesh.vertices,[0,0,2],[1,0,2],[0,1,2]],triangles:[...mesh.triangles,[4,5,6]]};p.strokes=[[a(0),a(4)]];
  assert.throws(()=>M.measurePerimeter(p,two,M.graph(two),3),/disconnected/);
});
test('surface smoothing crosses planar triangle interiors instead of zigzagging over edges',()=>{
  const p=draft();p.strokes=[[a(1),a(3)]];
  const edges=M.graph(mesh),raw=M.measurePerimeter(p,mesh,edges,2);assert.equal(raw.length,2);
  p.smoothing='surface';const smooth=M.measurePerimeter(p,mesh,edges,2);
  assert.ok(Math.abs(smooth.length-Math.sqrt(2))<1e-12);assert.equal(smooth.edge_fallback_segments,0);
  assert.deepEqual(smooth.paths[0].points[0],mesh.vertices[1]);assert.deepEqual(smooth.paths[0].points.at(-1),mesh.vertices[3]);
  for(const q of smooth.paths[0].points)assert.equal(q[2],0);
  assert.ok(smooth.method.includes('unfolded_triangle'));
});
test('folded-face smoothing measures the surface crossing, not a chord through the mesh',()=>{
  const folded={vertices:[[0,0,0],[1,0,0],[1,1,0],[.5,.5,Math.sqrt(.5)]],triangles:mesh.triangles};
  const path=M.surfaceSegment(folded,M.graph(folded),a(1),a(3));
  assert.ok(Math.abs(path.length-Math.sqrt(2))<1e-12);assert.ok(path.length>M.distance(folded.vertices[1],folded.vertices[3]));
  assert.deepEqual(path.points[1],[.5,.5,0]);
  assert.throws(()=>M.validatePerimeters([{...draft(),smoothing:'unknown'}],mesh));
});
