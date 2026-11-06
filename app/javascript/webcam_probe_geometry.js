// The same camera-space signs and orthographic view transform as webcam_mesh_gl.
export function probeFrame(point,camera,radius) {
  if(!Array.isArray(point)||point.length!==3||!point.every(Number.isFinite)||!Number.isFinite(radius)||radius<=0)throw Error('Invalid diagnostic frame.');
  return {center:camera.R.map((row,i)=>row.reduce((sum,v,j)=>sum+v*point[j],camera.t[i])*(i===0?1:-1)),scale:170/radius};
}
export function probeMark(point,camera,frame,yaw,pitch,zoom) {
  const p=camera.R.map((row,i)=>row.reduce((sum,v,j)=>sum+v*point[j],camera.t[i])*(i===0?1:-1)-frame.center[i]);
  const a=yaw*Math.PI/180,b=pitch*Math.PI/180,x=Math.cos(a)*p[0]+Math.sin(a)*p[2],z=-Math.sin(a)*p[0]+Math.cos(a)*p[2];
  return [360+x*frame.scale*zoom,240-(Math.cos(b)*p[1]-Math.sin(b)*z)*frame.scale*zoom];
}
export function probeSectionPlot(point,radius) {
  if(!Number.isFinite(radius)||radius<=0)throw Error('Invalid diagnostic section radius.');
  return [300+point[0]/radius*170,190-point[1]/radius*170];
}
