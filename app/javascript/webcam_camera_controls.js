export const cameraControlDefinitions=[
  {id:'focus',label:'Focus',mode:'focusMode',value:'focusDistance'},
  {id:'exposure',label:'Exposure',mode:'exposureMode',value:'exposureTime'},
  {id:'white_balance',label:'White balance',mode:'whiteBalanceMode',value:'colorTemperature'},
];

export function inspectCameraControls(track) {
  let capabilities={},settings={},error=null;
  try {settings=track.getSettings();capabilities=track.getCapabilities?.()||{};}catch(e){error=e.message;}
  return cameraControlDefinitions.map(d=>{
    const modes=Array.isArray(capabilities[d.mode]) ? [...capabilities[d.mode]]:[];
    const range=capabilities[d.value];
    const current=settings[d.value],mode=settings[d.mode];
    const supported=modes.includes('manual') && modes.includes(mode) && Number.isFinite(current) && range && Number.isFinite(range.min) && Number.isFinite(range.max) && current>=range.min && current<=range.max;
    return {...d,supported:!!supported,modes,range:range ? {min:range.min,max:range.max,step:range.step}:null,
      current_mode:mode??null,current_value:Number.isFinite(current)?current:null,
      reason:error || (!modes.includes('manual') ? 'Manual control is not exposed by this camera/browser.' : !supported ? 'Current mode/value cannot be read reliably for locking.':null)};
  });
}

function matches(setting,requested,step) {
  return Number.isFinite(setting) && Math.abs(setting-requested)<=Math.max(1e-6,(step||0)/2);
}

export async function applyCameraControl(track, control, target) {
  const before=track.getConstraints?.()||{};
  const advanced=(before.advanced||[]).map(item=>Object.fromEntries(Object.entries(item).filter(([k])=>k!==control.mode && k!==control.value))).filter(item=>Object.keys(item).length);
  const base=Object.fromEntries(Object.entries(before).filter(([k])=>k!=='advanced' && k!==control.mode && k!==control.value));
  const patch={[control.mode]:target.mode};
  if(target.mode==='manual')patch[control.value]=target.value;
  try {
    if(!track.applyConstraints)throw Error('Camera constraints are unavailable.');
    await track.applyConstraints({...base,advanced:[...advanced,patch]});
    const settings=track.getSettings();
    const verified=settings[control.mode]===target.mode && (target.mode!=='manual' || matches(settings[control.value],target.value,control.range?.step));
    return {id:control.id,requested:target,verified,status:verified ? 'verified':'unverified',
      reported_mode:settings[control.mode]??null,reported_value:settings[control.value]??null,
      error:verified ? null:'The camera did not report the requested mode/value.'};
  }catch(error){return {id:control.id,requested:target,verified:false,status:'failed',error:error.message};}
}

export function cameraControlSnapshot(track, attempts=[]) {
  const controls=inspectCameraControls(track),settings=track.getSettings();
  return {version:'webcam_camera_controls_v1',controls,attempts:attempts.map(attempt=>{
    const d=cameraControlDefinitions.find(d=>d.id===attempt.id),target=attempt.requested;
    const verified=attempt.verified && settings[d.mode]===target.mode && (target.mode!=='manual'||matches(settings[d.value],target.value,controls.find(c=>c.id===d.id)?.range?.step));
    return {...attempt,verified:!!verified,status:attempt.verified && !verified ? 'changed_since_verification':attempt.status};
  })};
}
