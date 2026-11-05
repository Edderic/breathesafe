// Read-only display buffers. No welding, triangulation, smoothing or repair.
export const meshLimits = {bytes:64*1024*1024, vertices:1000000, triangles:2000000};
const types={char:[1,'getInt8'],int8:[1,'getInt8'],uchar:[1,'getUint8'],uint8:[1,'getUint8'],
  short:[2,'getInt16'],int16:[2,'getInt16'],ushort:[2,'getUint16'],uint16:[2,'getUint16'],
  int:[4,'getInt32'],int32:[4,'getInt32'],uint:[4,'getUint32'],uint32:[4,'getUint32'],
  float:[4,'getFloat32'],float32:[4,'getFloat32'],double:[8,'getFloat64'],float64:[8,'getFloat64']};

export function parseInspectionPLY(buffer) {
  if(buffer.byteLength>meshLimits.bytes)throw Error('Mesh exceeds the 64 MiB inspection limit. Download the original for external inspection.');
  const bytes=new Uint8Array(buffer), headerLimit=Math.min(bytes.length,65536);
  let end=-1;
  for(let i=0;i<headerLimit-10;i++) {
    if(bytes[i]===101 && String.fromCharCode(...bytes.subarray(i,i+10))==='end_header') {
      end=i+10;while(end<bytes.length && bytes[end]!==10)end++;end++;break;
    }
  }
  if(end<0 || end>headerLimit)throw Error('Missing or oversized PLY header.');
  const lines=new TextDecoder().decode(bytes.subarray(0,end)).trim().split(/\r?\n/);
  if(lines[0]!=='ply')throw Error('Expected a PLY mesh.');
  const format=lines[1]?.split(/\s+/)[1];
  if(lines[1]?.split(/\s+/)[2]!=='1.0' || !['binary_little_endian','binary_big_endian','ascii'].includes(format))throw Error('Unsupported PLY encoding.');
  if(format==='ascii' && buffer.byteLength>8*1024*1024)throw Error('ASCII PLY exceeds the 8 MiB tokenization limit. Download the original for external inspection.');
  const elements=[];let element;
  for(const line of lines.slice(2)) {
    const p=line.trim().split(/\s+/);
    if(['comment','obj_info','end_header'].includes(p[0]))continue;
    if(p[0]==='element') {
      if(!['vertex','face'].includes(p[1]) || elements.some(e=>e.name===p[1]))throw Error('Inspection supports vertex/face PLY elements only.');
      const count=Number(p[2]),limit=p[1]==='vertex'?meshLimits.vertices:meshLimits.triangles;
      if(!Number.isInteger(count) || count<1 || count>limit)throw Error('Mesh exceeds vertex/triangle inspection limits or is empty.');
      element={name:p[1],count,properties:[]};elements.push(element);
    } else if(p[0]==='property' && element) {
      if(p[1]==='list') {
        if(!types[p[2]] || !types[p[3]])throw Error('Unsupported PLY property type.');
        element.properties.push({name:p[4],count:p[2],type:p[3]});
      } else {
        if(!types[p[1]])throw Error('Unsupported PLY property type.');
        element.properties.push({name:p[2],type:p[1]});
      }
    } else throw Error('Unsupported PLY header.');
  }
  if(elements.length!==2 || elements[0].name!=='vertex' || elements[1].name!=='face')throw Error('Expected vertices followed by triangular faces.');
  const [vertex,face]=elements;
  if(!['x','y','z'].every(axis=>vertex.properties.some(p=>p.name===axis && !p.count)) || vertex.properties.some(p=>p.count))throw Error('Missing scalar PLY coordinates.');
  if(!face.properties.some(p=>['vertex_indices','vertex_index'].includes(p.name) && p.count))throw Error('Missing PLY face indices.');
  let offset=end, token=0;
  const view=new DataView(buffer), little=format!=='binary_big_endian';
  const tokens=format==='ascii' ? new TextDecoder().decode(bytes.subarray(end)).trim().split(/\s+/) : null;
  function read(type) {
    const [size,method]=types[type];let value;
    if(tokens) {if(token>=tokens.length)throw Error('Truncated PLY.');value=Number(tokens[token++]);}
    else {if(offset+size>buffer.byteLength)throw Error('Truncated PLY.');value=view[method](offset,little);offset+=size;}
    if(!Number.isFinite(value))throw Error('Nonfinite PLY data.');return value;
  }
  const positions=new Float32Array(vertex.count*3),indices=new Uint32Array(face.count*3);
  for(let i=0;i<vertex.count;i++)for(const property of vertex.properties) {
    const value=read(property.type),axis=['x','y','z'].indexOf(property.name);
    if(axis>=0)positions[i*3+axis]=value;
  }
  for(let i=0;i<face.count;i++)for(const property of face.properties) {
    if(!property.count) {read(property.type);continue;}
    const count=read(property.count),isFace=['vertex_indices','vertex_index'].includes(property.name);
    if(!Number.isInteger(count) || count<0 || count>1000 || (isFace && count!==3))throw Error('Nontriangular or invalid PLY face; geometry will not be repaired.');
    for(let j=0;j<count;j++) {
      const index=read(property.type);
      if(isFace) {
        if(!Number.isInteger(index) || index<0 || index>=vertex.count)throw Error('Invalid PLY vertex index.');
        indices[i*3+j]=index;
      }
    }
  }
  return {positions,indices};
}

export function analysisBuffers(mesh) {
  if(mesh.vertices.length>meshLimits.vertices || mesh.triangles.length>meshLimits.triangles)throw Error('Analysis mesh exceeds display limits.');
  return {positions:new Float32Array(mesh.vertices.flat()),indices:new Uint32Array(mesh.triangles.flat())};
}

export function prepareInspectionMesh(buffers,camera,scale=1) {
  const {positions,indices}=buffers;
  if(!Number.isFinite(scale) || scale<=0 || !positions.length || indices.length%3 || !indices.length)throw Error('Invalid mesh or display scale.');
  const normals=new Float32Array(positions.length),lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<positions.length;i+=3) {
    const p=Array.from(positions.subarray(i,i+3),v=>v*scale);
    const q=camera.R.map((row,axis)=>row.reduce((sum,v,j)=>sum+v*p[j],camera.t[axis]));
    for(let axis=0;axis<3;axis++) {
      const value=q[axis]*(axis===0?1:-1);
      positions[i+axis]=value;
      if(!Number.isFinite(positions[i+axis]))throw Error('Nonfinite display coordinates.');
      lo[axis]=Math.min(lo[axis],value);hi[axis]=Math.max(hi[axis],value);
    }
  }
  for(let i=0;i<indices.length;i+=3) {
    const ids=Array.from(indices.subarray(i,i+3));
    if(ids.some(v=>v*3>=positions.length) || new Set(ids).size!==3)throw Error('Invalid mesh indices.');
    const [a,b,c]=ids.map(v=>v*3);
    const u=[0,1,2].map(j=>positions[b+j]-positions[a+j]),v=[0,1,2].map(j=>positions[c+j]-positions[a+j]);
    const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    if(!Number.isFinite(Math.hypot(...n)) || Math.hypot(...n)===0)throw Error('Degenerate inspection triangle.');
    for(const id of ids)for(let j=0;j<3;j++)normals[id*3+j]+=n[j];
  }
  for(let i=0;i<normals.length;i+=3) {
    const length=Math.hypot(...normals.subarray(i,i+3))||1;
    if(!Number.isFinite(length))throw Error('Display normals exceed the numeric range. Original geometry is retained.');
    for(let j=0;j<3;j++)normals[i+j]/=length;
  }
  return {positions,indices,normals,bounds:{lo,hi}};
}

export function sharedInspectionFrame(meshes) {
  const lo=[0,1,2].map(i=>Math.min(...meshes.map(m=>m.bounds.lo[i])));
  const hi=[0,1,2].map(i=>Math.max(...meshes.map(m=>m.bounds.hi[i])));
  const center=lo.map((v,i)=>(v+hi[i])/2);let radius=0;
  for(const mesh of meshes)for(let i=0;i<mesh.positions.length;i+=3)
    radius=Math.max(radius,Math.hypot(...center.map((c,j)=>mesh.positions[i+j]-c)));
  return {center,scale:radius>0?190/radius:1};
}
