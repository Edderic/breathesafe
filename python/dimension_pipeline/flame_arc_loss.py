"""Frozen, coverage-gated arc constraints. Saved FLAME lengths are not targets."""
import json
import subprocess
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from .flame_fit import nearest, outside


def length_jacobian(template, basis, edges, beta, scale):
    shaped=template+np.einsum('nck,k->nc',basis[:,:,:len(beta)],beta)
    delta=shaped[edges[:,1]]-shaped[edges[:,0]]
    lengths=np.linalg.norm(delta,axis=1)
    direction=np.divide(delta,lengths[:,None],out=np.zeros_like(delta),where=lengths[:,None]>1e-14)
    derivative=basis[edges[:,1],:,:len(beta)]-basis[edges[:,0],:,:len(beta)]
    return float(scale*lengths.sum()),scale*np.einsum('ec,eck->k',direction,derivative)


def resample(points, spacing):
    points=np.asarray(points,dtype=float)
    points=points[np.r_[True,np.linalg.norm(np.diff(points,axis=0),axis=1)>1e-10]]
    if len(points)<2: raise ValueError('Arc contains no measurable surface path.')
    lengths=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    count=min(1000,max(3,int(np.ceil(lengths[-1]/spacing))+1))
    parameter=np.linspace(0,lengths[-1],count)
    return np.column_stack([np.interp(parameter,lengths,points[:,i]) for i in range(3)])


def supported_edges(source, projected, valid, span):
    """No bridges across misses/exclusions, projection jumps or tiny islands."""
    a=np.linalg.norm(np.diff(source,axis=0),axis=1)
    b=np.linalg.norm(np.diff(projected,axis=0),axis=1)
    keep=valid[:-1]&valid[1:]&(a>span*1e-6)&(b>=a*.5)&(b<=a*1.5)
    starts=np.flatnonzero(keep&~np.r_[False,keep[:-1]])
    ends=np.flatnonzero(keep&~np.r_[keep[1:],False])+1
    output=np.zeros(len(keep),dtype=bool)
    for start,end in zip(starts,ends):
        if end-start>=3 and a[start:end].sum()>=span*.075: output[start:end]=True
    return np.column_stack([np.flatnonzero(output),np.flatnonzero(output)+1])


def annotations_from_node(draft, seed, identity):
    """Run the exact local UI route implementation; reject unrelated annotations."""
    script="""
const fs=require('fs'),M=require(process.argv[1]),d=JSON.parse(fs.readFileSync(0,'utf8'));
M.validate(d.draft,d.identity,d.mesh);const edges=M.graph(d.mesh),rows=[];
for(const p of d.draft.perimeters){if(!p.closed)continue;const arc=M.measurePerimeter(p,d.mesh,edges,d.span*.15);if(arc.status!=='closed_perimeter')throw Error('Use continuous full perimeter definitions.');rows.push({id:p.id,name:p.name,style:p.style,review_status:p.status,mirrored:!!p.mirror_provenance,points:arc.paths[0].points,source_ui_length:arc.length});}
process.stdout.write(JSON.stringify(rows));
"""
    identity=dict(identity);span=identity.pop('_span')
    payload={'draft':draft,'identity':identity,'mesh':{'vertices':seed.vertices.tolist(),'triangles':seed.faces.tolist()},'span':span}
    # Private geometry never leaves the local Node process.
    result=subprocess.run(['node','-e',script,str(Path(__file__).with_name('flame_measurements_ui.js').resolve())],
                          input=json.dumps(payload),capture_output=True,text=True,timeout=60,check=False)
    if result.returncode: raise ValueError('Arc definition validation/routing failed: '+result.stderr[-1500:])
    rows=json.loads(result.stdout)
    if not rows: raise ValueError('Provide at least one complete perimeter; half/mirrored/full duplicates are not counted separately.')
    return rows


def prepare_constraints(rows,seed,target,template,basis,ids,span,exclusions):
    constraints=[];guides=[];reports=[];supported_samples=[]
    for row in rows:
        samples=resample(row['points'],span*.025)
        attached,_,faces=nearest(seed,samples)
        weights=trimesh.triangles.points_to_barycentric(seed.triangles[faces],attached)
        weights=np.clip(weights,0,1);weights/=weights.sum(axis=1)[:,None]
        tri=seed.faces[faces]
        t=np.einsum('ni,nic->nc',weights,template[tri])
        b=np.einsum('ni,nick->nck',weights,basis[tri])
        projected,distance,target_faces=nearest(target,attached)
        normals=np.abs(np.einsum('ij,ij->i',seed.face_normals[faces],target.face_normals[target_faces]))
        valid=(distance<=span*.06)&(normals>=.5)&outside(attached,exclusions)&outside(projected,exclusions)
        edges=supported_edges(attached,projected,valid,span)
        coverage=len(edges)/(len(samples)-1)
        target_length=float(np.linalg.norm(projected[edges[:,1]]-projected[edges[:,0]],axis=1).sum()) if len(edges) else 0.
        status='full_support' if coverage>=.98 else 'partial_support' if coverage>=.2 else 'insufficient_support'
        report={k:row[k] for k in ('id','name','style','review_status','mirrored','source_ui_length')}
        report.update(status=status,sample_count=len(samples),valid_sample_count=int(valid.sum()),supported_edge_fraction=coverage,
                      supported_edges=edges.tolist(),target_supported_length=target_length if target_length else None,
                      target_full_length=target_length if status=='full_support' else None,
                      target_method='frozen_nearest_analysis_triangle_projection; dense_sample_chord_sum_on_contiguous_supported_runs',
                      saved_FLAME_length_used_as_target=False)
        attachments=[{'kind':'barycentric','triangle_index':int(f),'weights':w.tolist()} for f,w in zip(faces,weights)]
        guides.append({'id':row['id'],'name':row['name'],'style':row['style'],'attachments':attachments,'coverage':coverage})
        if valid.any(): supported_samples.extend(attached[valid])
        if status!='insufficient_support' and target_length>0:
            constraints.append({'id':row['id'],'style':row['style'],'template':t,'basis':b,'edges':edges,'target_length':target_length})
        reports.append(report)
    if not supported_samples: raise ValueError('No arc coverage on the fitting target outside exclusions.')
    distance=cKDTree(np.asarray(supported_samples)).query(seed.vertices[ids])[0]
    radius=span*.12;falloff=np.maximum(0,1-(distance/radius)**2)**2
    importance=1+3*falloff
    return constraints,importance,reports,guides


def evaluate_arcs(mesh,guides,coverage,span):
    rows=[]
    for guide,report in zip(guides,coverage):
        faces=np.array([a['triangle_index'] for a in guide['attachments']]);weights=np.array([a['weights'] for a in guide['attachments']])
        points=np.einsum('ni,nic->nc',weights,mesh.vertices[mesh.faces[faces]])
        edges=np.asarray(report['supported_edges'],dtype=int).reshape(-1,2)
        supported=float(np.linalg.norm(points[edges[:,1]]-points[edges[:,0]],axis=1).sum()) if len(edges) else None
        target=report['target_supported_length']
        rows.append({'id':guide['id'],'style':guide['style'],'name':guide['name'],'coverage':guide['coverage'],
                     'target_status':report['status'],'full_FLAME_sampled_length':float(np.linalg.norm(np.diff(points,axis=0),axis=1).sum()),
                     'model_supported_length':supported,'target_supported_length':target,
                     'supported_length_error_percent':100*(supported/target-1) if supported is not None and target else None,
                     'units':'reconstruction_unit','anatomical_accuracy':'not_evaluated'})
    return rows
