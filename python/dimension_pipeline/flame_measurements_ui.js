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
  function queue(){const heap=[];return {push(value){heap.push(value);let i=heap.length-1;while(i){const p=(i-1)>>1;if(heap[p][0]<=value[0])break;heap[i]=heap[p];i=p;}heap[i]=value;},pop(){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1][0]<heap[c][0])c++;if(heap[c][0]>=last[0])break;heap[i]=heap[c];i=c;}heap[i]=last;}return first;},get length(){return heap.length;}};}
  function segment(mesh,edges,start,end){
    const a=location(mesh,start),b=location(mesh,end);
    if((a.face!==null&&a.face===b.face)||(a.face!==null&&b.seeds.every(i=>a.seeds.includes(i)))||(b.face!==null&&a.seeds.every(i=>b.seeds.includes(i))))return {length:distance(a.point,b.point),points:[a.point,b.point]};
    const dist=mesh.vertices.map(()=>Infinity),previous=new Map(),pending=queue(),goals=new Map(b.seeds.map(i=>[i,distance(mesh.vertices[i],b.point)]));
    for(const i of a.seeds){dist[i]=distance(a.point,mesh.vertices[i]);pending.push([dist[i],i]);}
    let best=Infinity,finish=null;
    while(pending.length){
      const [min,v]=pending.pop();if(min!==dist[v])continue;if(min>best)break;
      if(goals.has(v)&&min+goals.get(v)<best){best=min+goals.get(v);finish=v;}
      for(const [n,length]of edges[v])if(min+length<dist[n]){dist[n]=min+length;previous.set(n,v);pending.push([dist[n],n]);}
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
  const stripIndexes=new WeakMap();
  function surfaceIndex(mesh,edges){
    if(stripIndexes.has(edges))return stripIndexes.get(edges);
    const vertexFaces=mesh.vertices.map(()=>[]),adj=mesh.triangles.map(()=>[]),byEdge=new Map();
    mesh.triangles.forEach((f,i)=>{for(const v of f)vertexFaces[v].push(i);for(let j=0;j<3;j++){const a=f[j],b=f[(j+1)%3],key=a<b?a+','+b:b+','+a;const list=byEdge.get(key)??[];list.push(i);byEdge.set(key,list);}});
    for(const list of byEdge.values())if(list.length===2){adj[list[0]].push(list[1]);adj[list[1]].push(list[0]);}
    const index={vertexFaces,adj};stripIndexes.set(edges,index);return index;
  }
  const cross2=(a,b)=>a[0]*b[1]-a[1]*b[0];
  const subtract=(a,b)=>a.map((x,i)=>x-b[i]);
  function stripSegment(mesh,edges,start,end){
    const a=location(mesh,start),b=location(mesh,end),index=surfaceIndex(mesh,edges);
    const starts=a.face===null?index.vertexFaces[a.seeds[0]]:[a.face],ends=new Set(b.face===null?index.vertexFaces[b.seeds[0]]:[b.face]);
    const pending=[...starts],previous=new Map(starts.map(i=>[i,null]));let finish=null;
    for(let j=0;j<pending.length&&j<512;j++){const face=pending[j];if(ends.has(face)){finish=face;break;}for(const n of index.adj[face])if(!previous.has(n)){previous.set(n,face);pending.push(n);}}
    if(finish===null)return null;
    const corridor=[finish];while(previous.get(corridor.at(-1))!==null)corridor.push(previous.get(corridor.at(-1)));corridor.reverse();
    const first=mesh.triangles[corridor[0]],v0=mesh.vertices[first[0]],v1=mesh.vertices[first[1]],v2=mesh.vertices[first[2]],base=distance(v0,v1);if(base<1e-12)return null;
    const x= subtract(v2,v0).reduce((s,v,i)=>s+v*(v1[i]-v0[i]),0)/base,h=Math.sqrt(Math.max(0,distance(v2,v0)**2-x*x));
    let coords=new Map([[first[0],[0,0]],[first[1],[base,0]],[first[2],[x,h]]]);const maps=[coords],gates=[];
    for(let i=1;i<corridor.length;i++){
      const old=mesh.triangles[corridor[i-1]],next=mesh.triangles[corridor[i]],shared=old.filter(v=>next.includes(v));if(shared.length!==2)return null;
      const [u,v]=shared,U=coords.get(u),V=coords.get(v),W=coords.get(old.find(w=>!shared.includes(w))),n=next.find(w=>!shared.includes(w)),delta=subtract(V,U),length=distance(U,V);if(length<1e-12)return null;
      const du=distance(mesh.vertices[u],mesh.vertices[n]),dv=distance(mesh.vertices[v],mesh.vertices[n]),along=(du*du-dv*dv+length*length)/(2*length),height=Math.sqrt(Math.max(0,du*du-along*along)),side=cross2(delta,subtract(W,U))>=0?-1:1;
      const N=[U[0]+along*delta[0]/length-side*height*delta[1]/length,U[1]+along*delta[1]/length+side*height*delta[0]/length];
      gates.push({u,v,U,V});coords=new Map([[u,U],[v,V],[n,N]]);maps.push(coords);
    }
    const flat=(attachment,map)=>attachment.kind==='vertex'?map.get(attachment.vertex_index):[0,1].map(j=>mesh.triangles[attachment.triangle_index].reduce((s,v,i)=>s+map.get(v)[j]*attachment.weights[i],0));
    const origin=flat(start,maps[0]),goal=flat(end,maps.at(-1));if(!origin||!goal)return null;const direction=subtract(goal,origin),points=[a.point];let lastT=-1e-8;
    for(const gate of gates){
      const edge=subtract(gate.V,gate.U),offset=subtract(gate.U,origin),denom=cross2(direction,edge);let t,q;
      if(Math.abs(denom)<1e-12){return null;}
      t=cross2(offset,edge)/denom;q=cross2(offset,direction)/denom;
      if(t<lastT-1e-7||t< -1e-7||t>1+1e-7||q< -1e-7||q>1+1e-7)return null;
      q=Math.max(0,Math.min(1,q));points.push(mesh.vertices[gate.u].map((x,j)=>x+(mesh.vertices[gate.v][j]-x)*q));lastT=t;
    }
    points.push(b.point);const length=points.slice(1).reduce((s,p,i)=>s+distance(points[i],p),0);
    return {length,points,method:'unfolded_triangle_strip',fallback:false};
  }
  function surfaceSegment(mesh,edges,start,end){
    const direct=stripSegment(mesh,edges,start,end);if(direct)return direct;
    return {...segment(mesh,edges,start,end),method:'mesh_edges_fallback',fallback:true};
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
    validatePerimeters(draft.perimeters??[],mesh);
    return draft;
  }
  const perimeterStyles={bifold:'Mid-nose → maxilla/cheeks → jaw → menton',bifold_gasket:'Mid-nose → maxilla/cheeks → jaw → menton; trace the gasket contact',cup:'Mid-nose → maxilla/cheeks → jaw → menton',trifold:'Nose → maxilla/cheeks → zygomatic region → under jaw; include neck contact if applicable',duckbill:'Nose → maxilla/cheeks → zygomatic region → under jaw; include neck contact if applicable',custom:'Trace the contact route you want to study'};
  function validatePerimeters(perimeters,mesh){
    if(!Array.isArray(perimeters)||perimeters.length>20)throw Error('Keep at most 20 perimeter drafts per fitted mesh.');
    const ids=new Set();for(const p of perimeters){
      if(typeof p.id!=='string'||!/^[a-zA-Z0-9_-]{1,64}$/.test(p.id)||ids.has(p.id)||typeof p.name!=='string'||!p.name.trim()||p.name.length>80||!Object.hasOwn(perimeterStyles,p.style)||!['pending','reviewed','uncertain'].includes(p.status)||typeof p.closed!=='boolean'||typeof p.notes!=='string'||p.notes.length>4000||!Array.isArray(p.strokes)||p.strokes.length>20)throw Error('Invalid perimeter draft.');
      ids.add(p.id);let count=0;for(const stroke of p.strokes){if(!Array.isArray(stroke)||!stroke.length||stroke.length>200)throw Error('Invalid perimeter stroke (maximum 200 controls).');for(const a of stroke)location(mesh,a);count+=stroke.length;}if(count>500)throw Error('Keep at most 500 controls per perimeter.');
      if(p.smoothing!==undefined&&!['surface','edges'].includes(p.smoothing))throw Error('Unknown perimeter route smoothing.');
      if(p.closed&&(p.strokes.length!==1||p.strokes[0].length<3))throw Error('A closed perimeter needs one continuous stroke with at least three controls.');
    }return perimeters;
  }
  function addPerimeterStroke(perimeter,stroke,mesh,joinDistance){
    if(!stroke.length)return false;
    const copy=structuredClone(perimeter),last=copy.strokes.at(-1),start=location(mesh,stroke[0]).point;
    if(last&&distance(location(mesh,last.at(-1)).point,start)<=joinDistance){
      if(last.length+stroke.length>200)throw Error('This stroke reached 200 controls. Start a new perimeter or reduce trace sampling.');
      last.push(...structuredClone(stroke));
    }else copy.strokes.push(structuredClone(stroke));
    copy.closed=false;copy.status='pending';validatePerimeters([copy],mesh);Object.assign(perimeter,copy);return true;
  }
  function measurePerimeter(perimeter,mesh,edges,maxGap){
    const smooth=perimeter.smoothing==='surface',paths=[];let total=0,fallbacks=0,surfaceSegments=0;for(const stroke of perimeter.strokes){
      if(stroke.length<2)continue;let length=0,points=[];
      const controls=perimeter.closed?[...stroke,stroke[0]]:stroke;
      for(let i=0;i<controls.length-1;i++){
        if(distance(location(mesh,controls[i]).point,location(mesh,controls[i+1]).point)>maxGap)throw Error('Trace has a surface gap; add nearby controls instead of bridging it.');
        const part=smooth?surfaceSegment(mesh,edges,controls[i],controls[i+1]):segment(mesh,edges,controls[i],controls[i+1]);if(smooth){if(part.fallback)fallbacks++;else surfaceSegments++;}length+=part.length;points.push(...part.points);
      }total+=length;paths.push({length,points});
    }
    return {length:total,paths,control_count:perimeter.strokes.reduce((s,c)=>s+c.length,0),stroke_count:perimeter.strokes.length,closed:perimeter.closed,surface_segments:surfaceSegments,edge_fallback_segments:fallbacks,
            status:perimeter.strokes.length>1?'separate_strokes_partial_length':perimeter.closed?'closed_perimeter':paths.length?'open_arc':'insufficient_controls',method:smooth?'sampled_surface_drag_with_unfolded_triangle_strips_and_explicit_edge_fallback':'sampled_surface_drag_with_piecewise_mesh_edge_paths'};
  }
  function closestTriangle(p,a,b,c){
    const dot=(u,v)=>u.reduce((s,x,i)=>s+x*v[i],0),ab=subtract(b,a),ac=subtract(c,a),ap=subtract(p,a),d1=dot(ab,ap),d2=dot(ac,ap);
    if(d1<=0&&d2<=0)return [1,0,0];const bp=subtract(p,b),d3=dot(ab,bp),d4=dot(ac,bp);if(d3>=0&&d4<=d3)return [0,1,0];
    const vc=d1*d4-d3*d2;if(vc<=0&&d1>=0&&d3<=0){const v=d1/(d1-d3);return [1-v,v,0];}
    const cp=subtract(p,c),d5=dot(ab,cp),d6=dot(ac,cp);if(d6>=0&&d5<=d6)return [0,0,1];
    const vb=d5*d2-d1*d6;if(vb<=0&&d2>=0&&d6<=0){const w=d2/(d2-d6);return [1-w,0,w];}
    const va=d3*d6-d5*d4;if(va<=0&&d4-d3>=0&&d5-d6>=0){const w=(d4-d3)/(d4-d3+d5-d6);return [0,1-w,w];}
    const denominator=va+vb+vc;if(Math.abs(denominator)<1e-20)throw Error('Degenerate triangle during mirror projection.');const v=vb/denominator,w=vc/denominator;return [1-v-w,v,w];
  }
  function mirrorPerimeter(source,mesh,edges,plane,span,full=false){
    validatePerimeters([source],mesh);
    if(!Number.isFinite(span)||span<=0||!Array.isArray(plane?.origin)||!Array.isArray(plane?.normal)||plane.origin.length!==3||plane.normal.length!==3||[...plane.origin,...plane.normal].some(v=>!Number.isFinite(v)))throw Error('Invalid FLAME mirror plane.');
    const norm=Math.hypot(...plane.normal);if(norm<1e-12)throw Error('Invalid FLAME mirror plane.');const normal=plane.normal.map(x=>x/norm),side=p=>subtract(p,plane.origin).reduce((s,x,i)=>s+x*normal[i],0);
    const controls=source.strokes.flat();if(source.closed||controls.length<2)throw Error('Draw an open half arc before mirroring.');
    const sides=controls.map(a=>side(location(mesh,a).point));if(sides.some(x=>x>span*.03)&&sides.some(x=>x< -span*.03))throw Error('Use a half arc on one side of the FLAME midline.');
    if(full&&(source.strokes.length!==1||controls.length<3||Math.abs(sides[0])>span*.05||Math.abs(sides.at(-1))>span*.05))throw Error('For a full perimeter, use one continuous half arc with both endpoints near the FLAME midline (within 0.05 eye spans).');
    const labels=new Int32Array(mesh.vertices.length);labels.fill(-1);let component=0;for(let i=0;i<labels.length;i++){if(labels[i]>=0)continue;const pending=[i];labels[i]=component;while(pending.length){const v=pending.pop();for(const n of edges[v].keys())if(labels[n]<0){labels[n]=component;pending.push(n);}}component++;}
    const distances=[];
    const mirrored=source.strokes.map(stroke=>stroke.map(a=>{const info=location(mesh,a),d=side(info.point),target=info.point.map((x,i)=>x-2*d*normal[i]),component=labels[info.seeds[0]];let best=null;
      mesh.triangles.forEach((face,i)=>{if(labels[face[0]]!==component)return;const weights=closestTriangle(target,...face.map(v=>mesh.vertices[v])),point=[0,1,2].map(j=>face.reduce((s,v,k)=>s+mesh.vertices[v][j]*weights[k],0));if(Math.abs(d)>span*.005&&Math.sign(d)*side(point)>span*.005)return;const residual=distance(target,point);if(!best||residual<best.residual)best={residual,attachment:{kind:'barycentric',triangle_index:i,weights:weights.map(w=>Math.max(0,Math.min(1,w)))}};});
      if(!best||best.residual>span*.08)throw Error('Opposite-side surface is too far from the reflected arc; place that section manually.');distances.push(best.residual);return best.attachment;
    }));
    const result=structuredClone(source);result.status='pending';result.closed=full;result.strokes=mirrored;
    if(full){const combined=[...source.strokes[0]],back=[...mirrored[0]].reverse();for(const a of back)if(distance(location(mesh,combined.at(-1)).point,location(mesh,a).point)>span*1e-7)combined.push(a);if(combined.length>2&&distance(location(mesh,combined[0]).point,location(mesh,combined.at(-1)).point)<span*1e-7)combined.pop();result.strokes=[combined];}
    result.mirror_provenance={method:'FLAME_model_X_plane_reflection_then_same_component_opposite_surface_projection_v1',source_perimeter_id:source.id,source_name:source.name,full_perimeter:full,plane:{origin:[...plane.origin],normal},projection_max_reconstruction_units:Math.max(...distances),projection_mean_reconstruction_units:distances.reduce((s,x)=>s+x,0)/distances.length,endpoint_midline_tolerance_fraction_eye_span:.05,projection_limit_fraction_eye_span:.08,anatomical_symmetry:'assumed_for_draft_not_validated'};
    validatePerimeters([result],mesh);return result;
  }
  return {VERSION,distance,location,graph,route,readings,calibration,validate,perimeterStyles,validatePerimeters,addPerimeterStroke,measurePerimeter,surfaceSegment,mirrorPerimeter};
})();
if(typeof module!=='undefined')module.exports=FlameMeasurements;
