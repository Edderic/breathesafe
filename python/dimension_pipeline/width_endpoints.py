"""Propose alar and zygomatic width contacts from fixed dense correspondence regions.

Template regions identify candidates only. Coordinates come from source-photo
triangulation and immutable reconstructed surfaces, never fitted FLAME geometry.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

from .all_photo_evaluate import attach_batched, observation_gate, triangulate_bounded
from .flame_open import load_model
from .gaussian_validation import eligible_faces
from .gaussian_volume import source_samples
from .mask_route_review import visible_hits
from .nose_overlays import project_pixels
from .photogrammetry_trial import digest
from .tape_linear_checks import linear_check


DEFINITIONS_URL='https://www.faa.gov/sites/faa.gov/files/data_research/research/med_humanfacs/oamtechreports/AM93-10.pdf'


def regions(vertices):
    """Fixed model-space anatomical search windows; independent of tape readings."""
    x,y,z=np.asarray(vertices).T
    nose=(abs(x)>.012)&(abs(x)<.026)&(y>-.029)&(y<-.014)&(z>.047)
    cheek=(abs(x)>.055)&(abs(x)<.09)&(y>-.025)&(y<.012)&(z>-.025)&(z<.045)
    return {name+('_negative_x' if sign<0 else '_positive_x'):np.flatnonzero(mask & (x*sign>0))
            for name,mask in [('alar',nose),('zygomatic',cheek)] for sign in (-1,1)}


def anatomical_axes(named):
    lateral=np.asarray(named['left_tragion']['surface_point'],dtype=float)-named['right_tragion']['surface_point']
    if not np.isfinite(lateral).all() or np.linalg.norm(lateral)<1e-10:raise ValueError('Degenerate tragion axis')
    lateral/=np.linalg.norm(lateral)
    up=np.asarray(named['sellion']['surface_point'],dtype=float)-named['menton']['surface_point']
    up-=np.dot(up,lateral)*lateral
    if not np.isfinite(up).all() or np.linalg.norm(up)<1e-10:raise ValueError('Degenerate face-height axis')
    up/=np.linalg.norm(up)
    return lateral,up


def select_extremum(indices, records, lateral, sign):
    supported=[int(i) for i in indices if records[int(i)]['status']=='supported']
    if not supported:return None
    return max(supported,key=lambda i:sign*float(np.dot(records[i]['surface_point'],lateral)))


def select_pair(left, right, records, lateral, up, maximum_height_difference):
    pairs=[]
    for a in left:
        for b in right:
            if records[a]['status']!='supported' or records[b]['status']!='supported':continue
            delta=np.asarray(records[a]['surface_point'])-records[b]['surface_point']
            if abs(float(delta@up))<=maximum_height_difference:
                pairs.append((float(delta@lateral),int(a),int(b)))
    if not pairs:return None
    _,a,b=max(pairs)
    return a,b


def run(args):
    session,predictions,neck,coverage,calibration,out=map(Path,(args.session,args.predictions,args.neck,args.coverage,args.calibration,args.out))
    state=json.loads((session/'session.json').read_text());parent=json.loads((coverage/'report.json').read_text())
    scale_report=json.loads((calibration/'report.json').read_text());volume=json.loads((neck/'report.json').read_text())
    neural=json.loads((predictions/'report.json').read_text());template,_,faces,model=load_model(args.model)
    if model['model_sha256']!=parent['model']['model_sha256']:raise ValueError('Correspondence template changed')
    if scale_report['provenance']['coverage_report_sha256']!=digest(coverage/'report.json'):raise ValueError('Calibration parent differs')
    if digest(predictions/'report.json')!=parent['neural_report_sha256']:raise ValueError('Neural report changed')
    if state['id']!=parent['session_id'] or state['id']!=scale_report['session_id']:raise ValueError('Session differs')
    selected_path=neck/(parent['selected_surface']+'.ply');raw_path=session/state['result']['full_mesh']
    if digest(selected_path)!=parent['selected_sha256'] or digest(raw_path)!=parent['source_sha256']:raise ValueError('Surface changed')
    named={d['name']:p for d,p in zip(parent['descriptors'],parent['runs']['all_views']['smoothed_points']) if d['kind']=='guide'}
    for name in ('left_tragion','right_tragion','sellion','menton'):
        if named[name]['status']!='supported':raise ValueError('Unsupported anatomical-axis anchor '+name)
    lateral,up=anatomical_axes(named);patches=regions(template)
    vertices=np.unique(np.concatenate(list(patches.values())))
    local={int(v):i for i,v in enumerate(vertices)}
    cameras=[];obs=[];images=[];masks=[];inputs=[]
    captures={c['slot']:c for c in state['captures']}
    for v in neural['views']:
        slot=v['slot'];capture=captures[slot];reference=next(p for p in parent['input_views'] if p['slot']==slot)
        if digest(session/capture['image'])!=reference['image_sha256'] or digest(session/capture['mask'])!=reference['mask_sha256']:
            raise ValueError('Photo or mask changed')
        array_path=predictions/(slot+'.npz')
        if digest(array_path)!=reference['prediction_sha256']:raise ValueError('Dense prediction changed')
        a=np.load(array_path,allow_pickle=False);xy=a['vertex_coord'][vertices].copy()
        camera=parent['fixed_cameras'][slot]
        mask=np.asarray(Image.open(session/capture['mask']).convert('L'))>=128
        expanded=cv2.dilate(mask.astype(np.uint8),np.ones((7,7),np.uint8))>0
        gates=observation_gate(xy,a['crop'],camera['width'],camera['height'],expanded)
        xy[~(gates[0]&gates[1]&gates[2])]=np.nan
        cameras.append(camera);obs.append(xy);images.append(slot);masks.append(expanded)
        inputs.append({'slot':slot,'prediction_sha256':digest(array_path),'image_sha256':reference['image_sha256'],'mask_sha256':reference['mask_sha256']})
    obs=np.array(obs);span=volume['eye_proxy_span']
    raw=trimesh.load(raw_path,process=False);selected=trimesh.load(selected_path,process=False)
    samples,_,_=source_samples(raw,span);tree=cKDTree(samples)
    if args.reuse:
        previous=json.loads(Path(args.reuse).read_text())
        expected={'selected_mesh_sha256':digest(selected_path),'source_mesh_sha256':digest(raw_path),
            'coverage_report_sha256':digest(coverage/'report.json'),'neural_report_sha256':digest(predictions/'report.json')}
        if previous['inputs']!=inputs or previous['policy']!=parent['policy'] or any(previous['provenance'][k]!=v for k,v in expected.items()):
            raise ValueError('Cached candidate inputs or support policy changed')
        cached={p['template_vertex_id']:p for p in previous['candidates']}
        if not all(int(v) in cached for v in vertices):raise ValueError('Cache does not cover the candidate region')
        records=[cached[int(v)]['raw'] for v in vertices];smoothed=[cached[int(v)]['selected'] for v in vertices]
        print('Reusing',len(vertices),'hash-matched triangulated candidates; selecting narrower regions',flush=True)
    else:
        print('Triangulating',len(vertices),'width-region candidates from',len(cameras),'photos',flush=True)
        records=triangulate_bounded(cameras,obs)
        attach_batched(raw,records,cameras,obs,span,eligible_faces(raw,span,tree))
        smoothed=[{'status':'consistent','point':p['surface_point'],'inlier_views':p['inlier_views']} if p['status']=='supported' else {'status':'raw_candidate_unsupported'} for p in records]
        attach_batched(selected,smoothed,cameras,obs,span,eligible_faces(selected,span,tree))
    endpoints={};pairs={};colors={'nose_width':'#ed9b23','face_width':'#23b5d3'}
    factor=scale_report['comparison']['provisional_mm_per_reconstruction_unit']
    for kind,measurement,readings in [('alar','nose_width',args.nose_width),('zygomatic','face_width',args.face_width)]:
        pair=[]
        left_indices=[local[int(v)] for v in patches[kind+'_positive_x']]
        right_indices=[local[int(v)] for v in patches[kind+'_negative_x']]
        selected_pair=select_pair(left_indices,right_indices,smoothed,lateral,up,.02*span)
        for suffix,sign,side in [('positive_x',1,'left'),('negative_x',-1,'right')]:
            region=patches[kind+'_'+suffix];indices=[local[int(v)] for v in region]
            # Side is inherited from template identity. Direction is checked against the subject's lateral axis.
            chosen=None if selected_pair is None else selected_pair[0 if side=='left' else 1]
            name=side+('_alare_candidate' if kind=='alar' else '_zygion_candidate')
            record=None if chosen is None else smoothed[chosen]
            endpoints[name]={'name':name,'region':kind+'_'+suffix,'template_vertex_id':None if chosen is None else int(vertices[chosen]),
                'candidate_index':chosen,'region_candidate_count':len(indices),'supported_region_candidates':sum(smoothed[i]['status']=='supported' for i in indices),
                'record':record,'anatomical_review':'pending; widest supported height-matched pair within fixed regions, not identified anatomical landmarks'}
            pair.append(name)
        positions=[endpoints[n]['record']['surface_point'] for n in pair] if all(endpoints[n]['record'] for n in pair) else None
        result=linear_check(readings,factor,positions)
        result.update(endpoint_names=pair,color=colors[measurement],selection='maximum horizontal breadth of supported paired candidates within fixed template regions, height difference <=0.02 eye spans; no tape-dependent selection')
        if positions is not None:
            delta=np.diff(np.asarray(positions),axis=0)[0]
            result.update(horizontal_component_mm=abs(float(delta@lateral))*factor,vertical_endpoint_difference_mm=abs(float(delta@up))*factor)
        pairs[measurement]=result
    report={'version':'width_endpoint_proposals_v1','session_id':state['id'],'endpoints':endpoints,'comparisons':pairs,
        'candidates':[{'template_vertex_id':int(v),'raw':r,'selected':s} for v,r,s in zip(vertices,records,smoothed)],
        'template_regions':{k:v.tolist() for k,v in patches.items()},'fixed_mm_per_reconstruction_unit':factor,
        'selection_policy':{'maximum_pair_height_difference_over_eye_span':.02,'objective':'maximum horizontal breadth within fixed regions; tape readings excluded'},
        'anatomical_axes':{'lateral':lateral.tolist(),'up':up.tolist(),'method':'left-right tragion direction and orthogonalized menton-to-sellion direction'},
        'definitions_url':DEFINITIONS_URL,'policy':parent['policy'],
        'interpretation':'proposed soft-tissue caliper-contact candidates; source consistency is not anatomical identification or independent accuracy',
        'provenance':{'selected_mesh_sha256':digest(selected_path),'source_mesh_sha256':digest(raw_path),'coverage_report_sha256':digest(coverage/'report.json'),
            'calibration_report_sha256':digest(calibration/'report.json'),'neural_report_sha256':digest(predictions/'report.json'),'model':model,'algorithm_sha256':digest(__file__),
            'reused_candidates_report_sha256':digest(args.reuse) if args.reuse else None},'inputs':inputs}
    out.mkdir(parents=True,exist_ok=False)
    photos=[]
    for slot in ('front','turn_11','turn_22','turn_35','turn_48','turn_55'):
        if slot not in images:continue
        i=images.index(slot);camera=cameras[i]
        image=Image.open(session/captures[slot]['image']).convert('RGB');original=image.copy();draw=ImageDraw.Draw(image)
        for name,endpoint in endpoints.items():
            if not endpoint['record']:continue
            p=np.array(endpoint['record']['surface_point']);xy=project_pixels(camera,p[None])[0];x,y=xy
            positive=(np.array(camera['R'])@p+camera['t'])[2]>0
            inside=positive and 0<=x<image.width and 0<=y<image.height
            if not inside:continue
            visible=bool(visible_hits(selected,camera,p[None],span*1e-4)[0]) and bool(masks[i][int(y),int(x)])
            color=colors['nose_width' if 'alare' in name else 'face_width']
            if visible:draw.ellipse((x-8,y-8,x+8,y+8),outline=color,width=4)
            else:
                draw.line((x-7,y-7,x+7,y+7),fill='#aaaaaa',width=3);draw.line((x-7,y+7,x+7,y-7),fill='#aaaaaa',width=3)
            draw.text((x+12,y-15),name.replace('_candidate','')+(' (occluded)' if not visible else ''),fill=color,stroke_width=1,stroke_fill='black')
        nose=[e['record']['surface_point'] for n,e in endpoints.items() if 'alare' in n and e['record']]
        crop_files={}
        if len(nose)==2:
            xy=project_pixels(camera,np.array(nose));center=xy.mean(0)
            radius=max(75.,float(np.linalg.norm(xy[1]-xy[0]))*1.1)
            box=(max(0,int(center[0]-radius)),max(0,int(center[1]-radius)),min(image.width,int(center[0]+radius)),min(image.height,int(center[1]+radius)))
            if box[2]>box[0] and box[3]>box[1]:
                for suffix,source in [('overlay',image),('original',original)]:
                    file=slot+'-nose-'+suffix+'.jpg';source.crop(box).resize((600,600)).save(out/file)
                    crop_files['nose_'+suffix]=file
        image.thumbnail((1100,700));original.thumbnail((1100,700))
        image.save(out/(slot+'-overlay.jpg'));original.save(out/(slot+'-original.jpg'))
        photos.append({'slot':slot,'overlay':slot+'-overlay.jpg','original':slot+'-original.jpg',**crop_files})
    report['photos']=photos
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    build_viewer(report,selected,state,parent,out)
    print(json.dumps({k:{n:v[n] for n in ('median_mm','estimated_mm','signed_difference_mm','relative_difference')} for k,v in pairs.items()},indent=2),flush=True)
    print(out/'review.html',flush=True)


def build_viewer(report,mesh,state,parent,out):
    from .gaussian_volume import display_mesh
    camera=state['result']['cameras'][state['result']['frontal_camera_key']];R=np.asarray(camera['R'])
    transform=lambda p:(np.asarray(p)@R.T*np.array([1,-1,-1])).tolist()
    paths=[];dots=[];control_records=[]
    for endpoint in report['endpoints'].values():
        if not endpoint['record']:continue
        dots.append(endpoint['record']['surface_point']);control_records.append({'automatic_correspondence_status':'supported'})
    for pair in report['comparisons'].values():
        if pair['estimated_mm'] is None:continue
        paths.append({'points':pair['endpoint_coordinates'],'color':pair['color']})
    data={'mesh':display_mesh(mesh,camera),'paths':[dict(p,points=transform(p['points'])) for p in paths],
        'controls':transform(dots) if dots else [],'source_guide':[],
        'report':{'paths':paths,'controls':control_records},'proposal':report}
    template=Path(__file__).with_name('width_endpoints.html').read_text()
    # Share the established WebGL surface renderer rather than another picking or geometry implementation.
    source=Path(__file__).with_name('mask_route_review.html').read_text()
    renderer=source[source.index('let min=[Infinity'):source.rindex('</script>')]
    page=template.replace('__DATA__',json.dumps(data).replace('</','<\\/')).replace('__RENDERER__',renderer)
    (out/'review.html').write_text(page)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('session','predictions','neck','coverage','calibration','model','out'):p.add_argument('--'+k,required=True)
    for k in ('nose-width','face-width'):p.add_argument('--'+k,nargs='+',type=float,required=True)
    p.add_argument('--reuse',help='Prior candidate report with identical inputs and support policy covering every requested vertex')
    run(p.parse_args())
