// Lighting uses mesh coordinates, never a mixture of screen pixels and mesh depth.
export function surfaceFraming(mesh) {
  const lo=[Infinity,Infinity,Infinity], hi=[-Infinity,-Infinity,-Infinity];
  for(const p of mesh.vertices) for(let i=0;i<3;i++) { lo[i]=Math.min(lo[i],p[i]); hi[i]=Math.max(hi[i],p[i]); }
  const center=lo.map((v,i)=>(v+hi[i])/2);
  const radius=Math.max(...mesh.vertices.map(p=>Math.hypot(...p.map((v,i)=>v-center[i]))));
  return {center,scale:radius>0 ? 190/radius : 1};
}

export function surfaceVertexNormals(mesh) {
  const normals=mesh.vertices.map(()=>[0,0,0]);
  for(const face of mesh.triangles) {
    const [a,b,c]=face.map(i=>mesh.vertices[i]);
    const u=b.map((v,i)=>v-a[i]),v=c.map((v,i)=>v-a[i]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    for(const i of face) for(let axis=0;axis<3;axis++) normals[i][axis]+=n[axis];
  }
  return normals.map(n=>{const length=Math.hypot(...n)||1;return n.map(v=>v/length);});
}

export function shadedSurfaceFaces(record, points, yaw, pitch, lightAzimuth=-40, vertexNormals=null) {
  const angle=lightAzimuth*Math.PI/180, light=[Math.sin(angle),.7,Math.cos(angle)];
  const lightLength=Math.hypot(...light);
  const a=yaw*Math.PI/180,b=pitch*Math.PI/180;
  const ca=Math.cos(a),sa=Math.sin(a),cb=Math.cos(b),sb=Math.sin(b);
  return record.mesh.triangles.map((face,index)=>{
    const [p,q,r]=face.map(i=>record.mesh.vertices[i]);
    const u=q.map((v,i)=>v-p[i]),v=r.map((v,i)=>v-p[i]);
    let nx=u[1]*v[2]-u[2]*v[1],ny=u[2]*v[0]-u[0]*v[2],nz=u[0]*v[1]-u[1]*v[0];
    if(vertexNormals) {
      const n=[0,1,2].map(axis=>face.reduce((sum,i)=>sum+vertexNormals[i][axis],0));
      if(Math.hypot(...n)>1e-12) [nx,ny,nz]=n;
    }
    const x=ca*nx+sa*nz,z=-sa*nx+ca*nz;
    let normal=[x,cb*ny-sb*z,sb*ny+cb*z];
    // Two-sided display keeps open reconstructed surfaces inspectable from either side.
    if(normal[2]<0) normal=normal.map(v=>-v);
    const length=Math.hypot(...normal)||1;
    const diffuse=Math.max(0,normal.reduce((sum,v,i)=>sum+v*light[i],0)/(length*lightLength));
    const brightness=.14+.78*diffuse+.08*Math.max(0,normal[2]/length);
    const color=[218,210,198].map(v=>Math.round(v*brightness));
    return {index,points:face.map(i=>`${points[i].x.toFixed(3)},${points[i].y.toFixed(3)}`).join(' '),
      depth:face.reduce((sum,i)=>sum+points[i].depth,0)/3,fill:`rgb(${color.join(',')})`};
  }).sort((a,b)=>a.depth-b.depth);
}
