import qualityPolicy from '../../python/dimension_pipeline/capture_quality_policy.json';

export function captureQuality(image, mask, policy=qualityPolicy) {
  const {width,height,data}=image;
  if(width!==mask.width || height!==mask.height || data.length!==width*height*4 || mask.data.length!==data.length) throw Error('Quality checks require matching native image and mask dimensions.');
  let left=width,top=height,right=-1,bottom=-1,foreground=0;
  for(let y=0;y<height;y++) for(let x=0;x<width;x++) if(mask.data[(y*width+x)*4]>=128) {
    left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);foreground++;
  }
  const round=v=>Math.round(v*1e6)/1e6;
  const result={policy:{...policy},image_size:[width,height],head_bbox:null,head_size_px:null,
    sharpness:null,sample_size:null,interior_samples:0,status:'unavailable',flags:[]};
  if(!foreground) {result.flags=['empty_head_mask'];return result;}
  const w=right-left+1,h=bottom-top+1;
  result.head_bbox=[left,top,right+1,bottom+1];result.head_size_px=[w,h];
  result.head_height_fraction=round(h/height);result.mask_area_fraction=round(foreground/(width*height));
  result.border_fraction=round(Math.min(left/width,top/height,(width-right-1)/width,(height-bottom-1)/height));
  if(result.head_height_fraction<policy.head_height_warning_below)result.flags.push('head_small_in_frame');
  if(result.border_fraction<policy.border_warning_below)result.flags.push('head_near_image_edge');
  const scale=Math.min(1,policy.max_sample_side/Math.max(w,h));
  const sw=Math.max(1,Math.round(w*scale)),sh=Math.max(1,Math.round(h*scale));
  result.sample_size=[sw,sh];
  const gray=new Float64Array(sw*sh),inside=new Uint8Array(sw*sh);
  const luma=(x,y)=>{const i=(y*width+x)*4;return .2126*data[i]+.7152*data[i+1]+.0722*data[i+2];};
  for(let y=0;y<sh;y++) for(let x=0;x<sw;x++) {
    const sx=Math.max(0,Math.min(width-1,left+(x+.5)*w/sw-.5)),sy=Math.max(0,Math.min(height-1,top+(y+.5)*h/sh-.5));
    const x0=Math.floor(sx),y0=Math.floor(sy),x1=Math.min(width-1,x0+1),y1=Math.min(height-1,y0+1),dx=sx-x0,dy=sy-y0;
    gray[y*sw+x]=(1-dy)*((1-dx)*luma(x0,y0)+dx*luma(x1,y0))+dy*((1-dx)*luma(x0,y1)+dx*luma(x1,y1));
    inside[y*sw+x]=mask.data[(Math.floor(sy+.5)*width+Math.floor(sx+.5))*4]>=128 ? 1:0;
  }
  let count=0,sum=0,squared=0;
  for(let y=1;y<sh-1;y++) for(let x=1;x<sw-1;x++) {
    const i=y*sw+x;
    if(![i,i-1,i+1,i-sw,i+sw].every(j=>inside[j]))continue;
    const lap=gray[i-1]+gray[i+1]+gray[i-sw]+gray[i+sw]-4*gray[i];
    count++;sum+=lap;squared+=lap*lap;
  }
  result.interior_samples=count;
  if(count<policy.minimum_interior_samples) {result.flags.push('insufficient_head_pixels');return result;}
  result.sharpness=round(Math.max(0,squared/count-(sum/count)**2));
  if(result.sharpness<policy.sharpness_warning_below)result.flags.push('low_sharpness_or_low_texture');
  result.status=result.flags.length ? 'review_recommended':'no_flags';
  return result;
}

export function qualityMessages(report) {
  const messages={empty_head_mask:'No head pixels: correct the mask before assessing the image.',
    head_small_in_frame:'Head is small in the image. Move closer while keeping both profiles, ears and chin in frame.',
    head_near_image_edge:'Mask reaches the image edge. Check for cropped ears/chin or unwanted mask pixels.',
    insufficient_head_pixels:'Too few head pixels to assess sharpness. Check the mask and framing.',
    low_sharpness_or_low_texture:'Low sharpness or little visible texture. Check focus, add diffuse light, and try a slower sweep or retake.'};
  return (report?.flags||[]).map(flag=>messages[flag]||flag);
}
