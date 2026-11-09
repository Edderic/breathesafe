"""Add visible route samples to original neck photographs without changing the audit."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image,ImageDraw

from .mask_route_review import visible_hits
from .nose_overlays import project_pixels
from .photogrammetry_trial import digest


def run(args):
    root,folder,coverage,neck=map(Path,(args.review,args.session,args.coverage,args.neck))
    report=json.loads((root/'report.json').read_text());state=json.loads((folder/'session.json').read_text())
    sources=json.loads((coverage/'report.json').read_text());volume=json.loads((neck/'report.json').read_text())
    if digest(coverage/'report.json')!=report['coverage_report_sha256']:raise ValueError('Coverage input changed')
    selected=next(v for v in volume['variants'] if v['sigma_over_eye_span']==.03);path=neck/(selected['id']+'.ply')
    if digest(path)!=report['selected_mesh_sha256']:raise ValueError('Selected mesh changed')
    mesh=trimesh.load(path,process=False);points=np.array(report['sample_points']);span=volume['eye_proxy_span']
    records={v['slot']:v for v in sources['input_views']};captures={c['slot']:c for c in state['captures']}
    photos=[]
    for slot in ('front','turn_11','turn_22','turn_35','turn_48','turn_55'):
        capture=captures[slot];record=records[slot];image_path=folder/capture['image'];mask_path=folder/capture['mask']
        camera=state['result']['cameras']['registered:'+slot+'.png']
        if digest(image_path)!=record['image_sha256'] or digest(mask_path)!=record['mask_sha256'] or camera!=sources['fixed_cameras'][slot]:
            raise ValueError('Photo, mask or camera changed')
        image=Image.open(image_path).convert('RGB');image.thumbnail((1000,600));original=slot+'-original.jpg';overlay=slot+'-route.jpg';image.save(root/original,quality=94)
        mask=np.asarray(Image.open(mask_path).convert('L'))>=128;mask=cv2.dilate(mask.astype(np.uint8),np.ones((7,7),np.uint8))>0
        xy=project_pixels(camera,points);width,height=camera['width'],camera['height']
        inside=(xy[:,0]>=0)&(xy[:,0]<width)&(xy[:,1]>=0)&(xy[:,1]<height)
        pixel=xy.clip([0,0],[width-1,height-1]).astype(int)
        inside &= mask[pixel[:,1],pixel[:,0]]
        indices=np.flatnonzero(inside)
        indices=indices[visible_hits(mesh,camera,points[indices],span*1e-4)] if len(indices) else indices
        draw=ImageDraw.Draw(image);scale=image.width/width
        for i in indices:
            x,y=xy[i]*scale;color='#00bb82' if report['sample_evidence'][i]['supported'] else '#ee9725'
            draw.ellipse((x-1.7,y-1.7,x+1.7,y+1.7),fill=color)
        image.save(root/overlay,quality=94)
        photos.append({'slot':slot,'original':original,'overlay':overlay,'visible_route_samples':len(indices),
                       'image_sha256':record['image_sha256'],'mask_sha256':record['mask_sha256']})
        print(slot,len(indices),'visible route samples',flush=True)
    output={'version':'mask_route_photo_overlays_v1','route_report_sha256':digest(root/'report.json'),
            'interpretation':'visible candidate route samples on reconstruction source photos; no independent accuracy validation',
            'photos':photos,'algorithm_sha256':digest(__file__)}
    (root/'photos.json').write_text(json.dumps(output,indent=2))
    page=root/'review.html';text=page.read_text();payload=text.split('<script id="data" type="application/json">',1)[1].split('</script>',1)[0]
    data=json.loads(payload);data['photo_overlays']=output
    page.write_text(Path(__file__).with_name('mask_route_review.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/')))
    print(page,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('review','session','coverage','neck'):p.add_argument('--'+key,required=True)
    run(p.parse_args())
