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
test('half-arc reflection creates surface attachments and joins a full loop without changing the source',()=>{
  const head={vertices:[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],triangles:[[2,0,4],[2,4,1],[2,1,5],[2,5,0],[3,4,0],[3,1,4],[3,5,1],[3,0,5]]};
  const p=draft();p.strokes=[[a(2),a(0),a(3)]];const before=JSON.stringify(p),edges=M.graph(head),plane={origin:[0,0,0],normal:[1,0,0]};
  const mirrored=M.mirrorPerimeter(p,head,edges,plane,10,false);
  assert.ok(M.distance(M.location(head,mirrored.strokes[0][1]).point,[-1,0,0])<1e-12);assert.equal(mirrored.status,'pending');assert.equal(mirrored.closed,false);
  const full=M.mirrorPerimeter(p,head,edges,plane,10,true);assert.equal(full.closed,true);assert.equal(full.strokes[0].length,4);assert.ok(Math.abs(M.measurePerimeter(full,head,edges,2).length-4*Math.sqrt(2))<1e-12);assert.equal(JSON.stringify(p),before);
  assert.equal(full.mirror_provenance.source_perimeter_id,p.id);
  const offset={...plane,origin:[5,4,3],normal:[0,1,0]},rotated={vertices:head.vertices.map(([x,y,z])=>[5-y,4+x,3+z]),triangles:head.triangles};
  const transformed=M.mirrorPerimeter(p,rotated,M.graph(rotated),offset,10,false);assert.ok(M.distance(M.location(rotated,transformed.strokes[0][1]).point,[5,3,3])<1e-12);
});
test('mirroring fails explicitly for non-half arcs, off-midline closure and excessive surface discrepancy',()=>{
  const head={vertices:[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],triangles:[[2,0,4],[2,4,1],[2,1,5],[2,5,0],[3,4,0],[3,1,4],[3,5,1],[3,0,5]]},plane={origin:[0,0,0],normal:[1,0,0]},edges=M.graph(head);
  const both=draft();both.strokes=[[a(0),a(1)]];assert.throws(()=>M.mirrorPerimeter(both,head,edges,plane,1),/one side/);
  const off=draft();off.strokes=[[a(0),a(2),a(4)]];assert.throws(()=>M.mirrorPerimeter(off,head,edges,plane,1,true),/endpoints/);
  const unequal={...head,vertices:head.vertices.map((p,i)=>i===1?[-3,0,0]:p)},p=draft();p.strokes=[[a(2),a(0),a(3)]];assert.throws(()=>M.mirrorPerimeter(p,unequal,M.graph(unequal),plane,1),/too far/);
});
test('near-midline endpoint overshoot does not invalidate an otherwise one-sided half arc',()=>{
  const head={vertices:[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],triangles:[[2,0,4],[2,4,1],[2,1,5],[2,5,0],[3,4,0],[3,1,4],[3,5,1],[3,0,5]]},plane={origin:[0,0,0],normal:[1,0,0]},edges=M.graph(head);
  const p=draft();p.strokes=[[a(2),a(1),{kind:'barycentric',triangle_index:4,weights:[.945,0,.055]}]];
  const full=M.mirrorPerimeter(p,head,edges,plane,1,true);assert.equal(full.closed,true);assert.equal(full.status,'pending');assert.equal(full.mirror_provenance.half_classification_midline_band_fraction_eye_span,.08);
  const center=draft();center.strokes=[[a(2),a(3)]];assert.throws(()=>M.mirrorPerimeter(center,head,edges,plane,1),/overlap/);
});
