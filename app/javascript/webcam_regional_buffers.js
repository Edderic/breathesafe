// Display-only extraction. Source indices and coordinates are never changed.
export function selectInspectionFaces(buffers,faceIds) {
  if(!Array.isArray(faceIds) || !faceIds.length || faceIds.length>200000 || new Set(faceIds).size!==faceIds.length)throw Error('Invalid or oversized regional face selection.');
  const indices=new Uint32Array(faceIds.length*3),vertices=[],mapping=new Map();
  faceIds.forEach((face,i)=>{
    if(!Number.isInteger(face) || face<0 || face*3+2>=buffers.indices.length)throw Error('Regional face index is outside its source topology.');
    for(let j=0;j<3;j++){
      const source=buffers.indices[face*3+j];
      if(!mapping.has(source)){
        mapping.set(source,vertices.length/3);vertices.push(...buffers.positions.subarray(source*3,source*3+3));
      }
      indices[i*3+j]=mapping.get(source);
    }
  });
  return {positions:new Float32Array(vertices),indices};
}

export function regionalFrame(region,camera) {
  const points=region.chains.flat();if(!points.length || !(region.radius>0))throw Error('No supported regional frame.');
  const center=[0,1,2].map(i=>(Math.min(...points.map(p=>p[i]))+Math.max(...points.map(p=>p[i])))/2);
  const radius=Math.max(...points.map(p=>Math.hypot(...p.map((v,i)=>v-center[i]))))+region.radius;
  return {center:camera.R.map((row,i)=>(row.reduce((s,v,j)=>s+v*center[j],camera.t[i]))*(i===0?1:-1)),scale:170/radius};
}
