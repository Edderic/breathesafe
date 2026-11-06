/* Direct FLAME measurements. Edge routes are approximations, not tape simulation. */
const FlameMeasurements=(()=>{
  const VERSION='flame-direct-measurements-v1';
  const distance=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
  function location(mesh,a){
    if(!a||!['vertex','barycentric'].includes(a.kind))throw Error('Place a point on the FLAME surface.');
    if(a.kind==='vertex'){
      if(!Number.isInteger(a.vertex_index)||!mesh.vertices[a.vertex_index])throw Error('Invalid original FLAME vertex.');
      return {point:mesh.vertices[a.vertex_index],seeds:[a.vertex_index],face:null};
    }
    if(!Number.isInteger(a.triangle_index)||!mesh.triangles[a.triangle_index]||!Array.isArray(a.weights)||a.weights.length!==3||a.weights.some(w=>!Number.isFinite(w)||w<0||w>1)||Math.abs(a.weights.reduce((s,x)=>s+x,0)-1)>1e-7)throw Error('Invalid triangle attachment.');
    const face=mesh.triangles[a.triangle_index];
    return {point:[0,1,2].map(j=>face.reduce((s,v,k)=>s+mesh.vertices[v][j]*a.weights[k],0)),seeds:face,face:a.triangle_index};
  }
  function graph(mesh){const result=mesh.vertices.map(()=>new Map());for(const f of mesh.triangles)for(let i=0;i<3;i++){const a=f[i],b=f[(i+1)%3],d=distance(mesh.vertices[a],mesh.vertices[b]);result[a].set(b,d);result[b].set(a,d);}return result;}
  function segment(mesh,edges,start,end){
    const a=location(mesh,start),b=location(mesh,end);
    if((a.face!==null&&a.face===b.face)||(a.face!==null&&b.seeds.every(i=>a.seeds.includes(i)))||(b.face!==null&&a.seeds.every(i=>b.seeds.includes(i))))return {length:distance(a.point,b.point),points:[a.point,b.point]};
    const dist=mesh.vertices.map(()=>Infinity),previous=new Map(),visited=new Set(),goals=new Map(b.seeds.map(i=>[i,distance(mesh.vertices[i],b.point)]));
    for(const i of a.seeds)dist[i]=distance(a.point,mesh.vertices[i]);
    let best=Infinity,finish=null;
    // Bounded 5k-vertex mesh; dense Dijkstra keeps implementation deterministic.
    for(let step=0;step<dist.length;step++){
      let v=-1,min=Infinity;for(let i=0;i<dist.length;i++)if(!visited.has(i)&&dist[i]<min){v=i;min=dist[i];}
      if(v<0||min>best)break;visited.add(v);
      if(goals.has(v)&&min+goals.get(v)<best){best=min+goals.get(v);finish=v;}
      for(const [n,length]of edges[v])if(min+length<dist[n]){dist[n]=min+length;previous.set(n,v);}
    }
    if(finish===null)throw Error('Route crosses disconnected surface components.');
    const ids=[finish];while(previous.has(ids[ids.length-1]))ids.push(previous.get(ids[ids.length-1]));ids.reverse();
    return {length:best,points:[a.point,...ids.map(i=>mesh.vertices[i]),b.point]};
  }
  function route(mesh,edges,points,names){
    if(!Array.isArray(names)||names.length<2||names.length>200)throw Error('Choose at least two route controls (maximum 200).');
    let length=0,path=[];
    for(let i=0;i<names.length-1;i++){
      const a=points.find(p=>p.name===names[i]),b=points.find(p=>p.name===names[i+1]);
      if(!a?.attachment||!b?.attachment||a.status==='unavailable'||b.status==='unavailable')throw Error('Place every available route control: '+names[i]+' → '+names[i+1]);
      const part=segment(mesh,edges,a.attachment,b.attachment);length+=part.length;path.push(...part.points);
    }
    if(!(length>0))throw Error('Route has zero length.');return {length,points:path,method:'piecewise_mesh_edge_dijkstra_with_barycentric_endpoint_links'};
  }
  function readings(values){
    if(!Array.isArray(values)||values.length!==3||values.some(v=>!Number.isFinite(v)||v<=0))throw Error('Enter three positive tape readings in millimeters.');
    const sorted=[...values].sort((a,b)=>a-b);return {readings_mm:values,median_mm:sorted[1],spread_mm:sorted[2]-sorted[0]};
  }
  function calibration(mesh,edges,draft){
    const names=draft.routes.scale;
    if(names[0]!=='left_tragion'||names.at(-1)!=='right_tragion'||names.filter(n=>n==='subnasale').length!==1)throw Error('Scale route must run left_tragion → subnasale → right_tragion, with intermediate controls.');
    if(names.some(n=>draft.points.find(p=>p.name===n)?.status!=='reviewed'))throw Error('Review every control on the scale route before calibration.');
    const arc=route(mesh,edges,draft.points,names),tape=readings(draft.scale_readings_mm),scale=tape.median_mm/arc.length;
    let check={status:'not_measured'};
    if(draft.check_readings_mm.some(v=>v!==null&&v!=='')){
      try{
        const order=draft.routes.check;
        if(order[0]!=='left_tragion'||order.at(-1)!=='right_tragion'||order.filter(n=>n==='menton').length!==1)throw Error('Check route must pass left_tragion → menton → right_tragion.');
        if(order.some(n=>draft.points.find(p=>p.name===n)?.status!=='reviewed'))throw Error('Review every independent-check control.');
        const arcCheck=route(mesh,edges,draft.points,order),tapeCheck=readings(draft.check_readings_mm),mm=arcCheck.length*scale;
        check={status:'ok',...tapeCheck,mesh_length_mm:mm,discrepancy_mm:mm-tapeCheck.median_mm,discrepancy_percent:100*(mm/tapeCheck.median_mm-1)};
      }catch(error){check={status:'incomplete',error:error.message};}
    }
    return {method:'uniform_tape_arc_median_v1',mm_per_reconstruction_unit:scale,scale:{...tape,route_length_reconstruction_units:arc.length},independent_check:check};
  }
  function validate(draft,identity,mesh){
    if(draft?.version!==VERSION||Object.keys(identity).some(k=>draft[k]!==identity[k]))throw Error('Measurements belong to a different fitted mesh, model or session.');
    if(!Array.isArray(draft.points)||draft.points.length>200)throw Error('Invalid direct point list.');
    const seen=new Set();
    for(const p of draft.points){if(typeof p.name!=='string'||! /^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(p.name)||seen.has(p.name)||!['pending','reviewed','uncertain','unavailable'].includes(p.status)||typeof p.notes!=='string'||p.notes.length>4000)throw Error('Invalid or duplicate direct point.');seen.add(p.name);if(p.attachment)location(mesh,p.attachment);else if(p.status==='reviewed')throw Error('Reviewed point needs a placement.');}
    for(const key of ['scale','check','custom'])if(!Array.isArray(draft.routes?.[key])||draft.routes[key].length>200||draft.routes[key].some(n=>typeof n!=='string'||!seen.has(n)))throw Error('Invalid route controls.');
    for(const key of ['scale_readings_mm','check_readings_mm'])if(!Array.isArray(draft[key])||draft[key].length!==3||draft[key].some(x=>x!==null&&(!Number.isFinite(x)||x<=0)))throw Error('Invalid tape readings.');
    if(!Array.isArray(draft.line)||draft.line.length!==2||draft.line.some(n=>!seen.has(n)))throw Error('Invalid straight-line endpoints.');
    return draft;
  }
  return {VERSION,distance,location,graph,route,readings,calibration,validate};
})();
if(typeof module!=='undefined')module.exports=FlameMeasurements;
