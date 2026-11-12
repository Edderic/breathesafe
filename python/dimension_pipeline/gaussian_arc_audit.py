"""Matched supported arc sensitivity using the existing triangle-strip shortcuts."""
import argparse
import copy
import json
import os
import subprocess
from pathlib import Path

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from .gaussian_validation import COLORS, eligible_faces, qualified_attachments, recipe
from .gaussian_volume import source_samples
from .photogrammetry_trial import digest


NODE = r'''
const fs=require('fs'),M=require(process.argv[1]),data=JSON.parse(fs.readFileSync(0,'utf8')),mesh=data.mesh,graph=M.graph(mesh),rows=[];
for(const route of data.routes){let length=0,surface=0,fallbacks=0,steps=0,error=null;
 for(let j=0;j<route.pairs.length;j++){
  if(!route.common[j])continue;
  const [a,b]=route.pairs[j],start=data.attachments[a],end=data.attachments[b];
  try{
   if(M.distance(M.location(mesh,start).point,M.location(mesh,end).point)<1e-10){steps++;continue}
   const r=M.route(mesh,graph,[{name:'a',attachment:start},{name:'b',attachment:end}],['a','b'],'surface');
   length+=r.length;surface+=r.surface_segments;fallbacks+=r.edge_fallback_segments;steps++;
  }catch(e){error=e.message;break}
 }
 rows.push({name:route.name,common_supported_edges:route.common.filter(Boolean).length,total_control_edges:route.pairs.length,
            partial_surface_length:steps&&!error?length:null,complete_surface_length:steps===route.pairs.length&&!error?length:null,
            unfolded_shortcut_segments:surface,edge_fallback_segments:fallbacks,error});
}
process.stdout.write(JSON.stringify(rows));
'''


def run(args):
    root,folder,sweep=map(Path,(args.validation,args.session,args.sweep))
    report=json.loads((root/'report.json').read_text())
    state=json.loads((folder/'session.json').read_text())
    draft=json.loads(Path(args.measurements).read_text())
    if digest(args.measurements)!=report['guide_sha256']:
        raise ValueError('Guide changed')
    _,_,routes=recipe(draft)
    raw_path=folder/state['result']['full_mesh']
    if digest(raw_path)!=report['input_mesh_hashes']['raw']:
        raise ValueError('Source mesh changed')
    raw=trimesh.load(raw_path,process=False);span=report['eye_proxy_span']
    samples,_,_=source_samples(raw,span);tree=cKDTree(samples)
    meshes={};attachments={};labels={}
    for name,record in report['variants'].items():
        path=raw_path if name=='raw' else sweep/(name+'.ply')
        if digest(path)!=report['input_mesh_hashes'][name]:
            raise ValueError('Candidate changed')
        mesh=raw if name=='raw' else trimesh.load(path,process=False)
        mask=eligible_faces(mesh,span,tree)
        mesh,a=qualified_attachments(mesh,mask,copy.deepcopy(record['points']))
        for attachment in a.values():
            w=np.array(attachment['weights'])
            if w.min() < -1e-6 or w.max()>1+1e-6:
                raise ValueError('Invalid source attachment')
            w=np.clip(w,0,1);attachment['weights']=(w/w.sum()).tolist()
            attachment['kind']='barycentric'
        edges=mesh.edges_unique
        adjacency=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(mesh.vertices),)*2)
        _,components=connected_components(adjacency,directed=False)
        meshes[name]=mesh;attachments[name]=a;labels[name]=components
    for route,reference in zip(routes,report['matched_routes']):
        route['common']=[]
        for a,b in route['pairs']:
            good=all(a in attachments[n] and b in attachments[n] and
                labels[n][m.faces[attachments[n][a]['triangle_index']][0]]==labels[n][m.faces[attachments[n][b]['triangle_index']][0]]
                for n,m in meshes.items())
            route['common'].append(bool(good))
        if sum(route['common'])!=reference['common_supported_edges']:
            raise ValueError('Matched support differs from validation')
    module=Path(__file__).with_name('flame_measurements_ui.js').resolve()
    result={'version':'gaussian_surface_arc_audit_v1','validation_report_sha256':digest(root/'report.json'),
            'routing_code_sha256':digest(module),'method':'anchored local unfolded triangle-strip shortcuts with explicit edge fallback',
            'interpretation':'partial route sensitivity on identical support; not exact global geodesics or tape lengths',
            'variants':{}}
    for name,mesh in meshes.items():
        print('Triangle-interior routing',name,flush=True)
        payload={'mesh':{'vertices':mesh.vertices.tolist(),'triangles':mesh.faces.tolist()},'attachments':attachments[name],'routes':routes}
        process=subprocess.run(['node','-e',NODE,str(module)],input=json.dumps(payload),capture_output=True,text=True,timeout=240,check=True)
        result['variants'][name]=json.loads(process.stdout)
        (root/'surface-arcs.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    result['algorithm_sha256']=digest(__file__)
    (root/'surface-arcs.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    data={'report':report,'colors':COLORS,'arcs':result,'viewer':os.path.relpath(sweep/'comparison.html',root)}
    if (root/'point-audit.json').is_file():
        audit=json.loads((root/'point-audit.json').read_text())
        if audit['validation_report_sha256']!=digest(root/'report.json'):
            raise ValueError('Point audit stale')
        data['audit']=audit
    (root/'review.html').write_text(Path(__file__).with_name('gaussian_validation.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(json.dumps(result['variants'],indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('validation','session','sweep','measurements'):
        p.add_argument('--'+key,required=True)
    run(p.parse_args())
