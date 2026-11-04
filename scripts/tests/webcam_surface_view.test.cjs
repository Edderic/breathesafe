const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const context={};
vm.runInNewContext(fs.readFileSync(path.resolve(__dirname,'../../app/javascript/webcam_surface_view.js'),'utf8').replaceAll('export ',''),context);
const mesh={vertices:[[0,0,0],[1,0,0],[0,1,0],[0,0,0],[.5,0,.866],[0,1,0],[0,0,0],[.5,0,-.866],[0,1,0]],triangles:[[0,1,2],[3,4,5],[6,7,8]]};
const points=mesh.vertices.map(([x,y,depth])=>({x,y,depth}));
const fills=(record,points,light=-40)=>Array.from(context.shadedSurfaceFaces(record,points,0,0,light)).sort((a,b)=>a.index-b.index).map(f=>f.fill);
test('lighting reveals slopes and is independent of pixel magnification and model units',()=>{
 const record={mesh};const colors=fills(record,points);
 assert.equal(new Set(colors).size,3);
 const red=fill=>Number(fill.match(/\d+/)[0]);
 assert.ok(Math.max(...colors.map(red))-Math.min(...colors.map(red))>80);
 assert.deepEqual(fills(record,points.map(p=>({...p,x:p.x*300,y:p.y*300}))),colors);
 assert.deepEqual(fills({mesh:{...mesh,vertices:mesh.vertices.map(p=>p.map(v=>v*1000))}},points),colors);
 assert.notDeepEqual(fills(record,points,40),colors);
});
test('fit framing leaves margins at every rotation without changing geometry',()=>{
 const original=JSON.stringify(mesh),frame=context.surfaceFraming(mesh);
 for(const p of mesh.vertices)assert.ok(Math.hypot(...p.map((v,i)=>(v-frame.center[i])*frame.scale))<=190.000001);
 assert.equal(JSON.stringify(mesh),original);
 const translated={...mesh,vertices:mesh.vertices.map(p=>p.map(v=>v*10+123))};
 const second=context.surfaceFraming(translated);
 assert.ok(Math.abs(second.scale-frame.scale/10)<1e-10);
});
test('smooth lighting averages normals without moving vertices or changing topology',()=>{
 const folded={vertices:[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],triangles:[[0,1,2],[0,3,1]]};
 const original=JSON.stringify(folded),normals=context.surfaceVertexNormals(folded);
 assert.ok(normals[0][1]>0 && normals[0][2]>0);
 const points=folded.vertices.map(([x,y,depth])=>({x,y,depth}));
 const flat=context.shadedSurfaceFaces({mesh:folded},points,0,0);
 const smooth=context.shadedSurfaceFaces({mesh:folded},points,0,0,-40,normals);
 assert.notDeepEqual(Array.from(flat,f=>f.fill),Array.from(smooth,f=>f.fill));
 assert.deepEqual(Array.from(flat,f=>f.points),Array.from(smooth,f=>f.points));
 assert.equal(JSON.stringify(folded),original);
});
