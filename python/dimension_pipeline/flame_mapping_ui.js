/* Pure screen-space picking and original-index attachments; also tested in Node. */
const FlameMapping = (() => {
  function barycentric2D(p,a,b,c) {
    const det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);
    if(Math.abs(det)<1e-12)return null;
    const u=((b[1]-c[1])*(p[0]-c[0])+(c[0]-b[0])*(p[1]-c[1]))/det;
    const v=((c[1]-a[1])*(p[0]-c[0])+(a[0]-c[0])*(p[1]-c[1]))/det;
    const w=1-u-v;
    if(Math.min(u,v,w)<-1e-8)return null;
    const weights=[u,v,w].map(x=>Math.max(0,Math.min(1,x))),sum=weights.reduce((s,x)=>s+x,0);
    return weights.map(x=>x/sum);
  }
  function pick(mesh,rotated,point,mode) {
    if(!mesh.original_vertex_ids||!mesh.original_triangle_ids)return null;
    let hit=null;
    mesh.triangles.forEach((triangle,i)=>{
      const vertices=triangle.map(v=>rotated[v]),weights=barycentric2D(point,...vertices);
      if(!weights)return;
      const depth=weights.reduce((sum,w,j)=>sum+w*vertices[j][2],0);
      if(hit&&depth<=hit.depth)return;
      let attachment;
      if(mode==='vertex'){
        const nearest=vertices.map(v=>Math.hypot(v[0]-point[0],v[1]-point[1]));
        const corner=nearest.indexOf(Math.min(...nearest));
        attachment={kind:'vertex',vertex_index:mesh.original_vertex_ids[triangle[corner]]};
      }else attachment={kind:'barycentric',triangle_index:mesh.original_triangle_ids[i],weights};
      hit={depth,attachment};
    });
    return hit?.attachment??null;
  }
  function point(mesh,attachment){
    if(!attachment)return null;
    if(attachment.kind==='vertex')return mesh.vertices[mesh.original_vertex_ids.indexOf(attachment.vertex_index)]??null;
    const index=mesh.original_triangle_ids.indexOf(attachment.triangle_index);
    if(index<0)return null;
    return [0,1,2].map(axis=>mesh.triangles[index].reduce((sum,v,j)=>sum+mesh.vertices[v][axis]*attachment.weights[j],0));
  }
  function validate(mapping,report,mesh){
    if(mapping?.version!=='flame-arkit-analogs-v1'||mapping.model_sha256!==report.model.model_sha256||mapping.topology_id!==report.flame_topology_id||mapping.session_id!==report.session_id||mapping.source_mesh_id!==report.source_mesh_id)throw Error('Mapping belongs to a different model, topology, session or analysis mesh.');
    const allowed=new Set(report.arkit_analog_catalog.map(r=>r.arkit_index)),seen=new Set();
    if(!Array.isArray(mapping.points)||mapping.points.length>allowed.size)throw Error('Invalid mapping points.');
    for(const row of mapping.points){
      if(!Number.isInteger(row.arkit_index)||!allowed.has(row.arkit_index)||seen.has(row.arkit_index))throw Error('Unknown or duplicate ARKit index.');seen.add(row.arkit_index);
      if(!['pending','reviewed','uncertain','unavailable'].includes(row.status)||typeof(row.notes===undefined?'':row.notes)!=='string'||(row.notes??'').length>4000)throw Error('Invalid review status or notes.');
      if(!Number.isFinite(row.radius_fraction_eye_span)||row.radius_fraction_eye_span<.03||row.radius_fraction_eye_span>.5||!Number.isFinite(row.multiplier)||row.multiplier<1||row.multiplier>10)throw Error('Radius must be 0.03–0.5 and weight 1–10.');
      const a=row.attachment;
      if(!a){if(row.status==='reviewed')throw Error('Reviewed analog needs a placement.');continue;}
      if(a.kind==='vertex'){
        if(!Number.isInteger(a.vertex_index)||a.vertex_index<0||a.vertex_index>=report.flame_vertex_count)throw Error('Invalid original FLAME vertex index.');
      }else if(a.kind==='barycentric'){
        if(!Number.isInteger(a.triangle_index)||a.triangle_index<0||a.triangle_index>=report.flame_triangle_count||!Array.isArray(a.weights)||a.weights.length!==3||a.weights.some(w=>!Number.isFinite(w)||w<0||w>1)||Math.abs(a.weights.reduce((s,x)=>s+x,0)-1)>1e-7)throw Error('Invalid original FLAME triangle attachment.');
      }else throw Error('Unknown attachment type.');
    }
    return mapping;
  }
  return {barycentric2D,pick,point,validate};
})();
if(typeof module!=='undefined')module.exports=FlameMapping;
