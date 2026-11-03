<template>
  <main class="pilot">
    <p>MasqFit · Local research</p><h1>3D webcam pilot</h1>
    <p>Capture a neutral face, reconstruct a surface, calibrate with a tape arc, and inspect projected frontal landmarks.</p>
    <p class="notice">Experimental surface and points. Tape calibration sets scale; it does not validate 3D accuracy or ARKit equivalence. Reconstruction, camera alignment, and landmark agreement require separate review.</p>
    <p v-if="error" role="alert" class="error">{{ error }}</p><p v-if="message" role="status">{{ message }}</p>
    <div class="toolbar">
      <button @click="guard(connect)">Connect processor</button><button @click="guard(createSession)" :disabled="busy">New session</button>
      <select v-model="resumeId" aria-label="Saved session"><option value="">Select a saved session</option><option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.created_at }} · {{ s.status }}</option></select>
      <button @click="guard(resume)" :disabled="!resumeId || busy">Resume</button>
      <label>Reload exported session<input type="file" accept=".zip" @change="restore" :disabled="busy" /></label>
    </div>
    <details v-if="diagnostics"><summary>Setup diagnostics · {{ diagnostics.ready ? 'tools ready' : 'setup required' }}</summary><pre>{{ JSON.stringify(diagnostics, null, 2) }}</pre></details>
    <p v-else>Start the loopback processor and research preview using <code>python/dimension_pipeline/WEBCAM_PILOT.md</code>.</p>
    <template v-if="session">
      <p>Session {{ session.id }} · {{ session.status }} <span v-if="session.stage">· {{ session.stage }}</span> · {{ session.captures.length }}/61 approved images saved locally</p>
      <p v-if="session.error" role="alert" class="error">{{ session.error }}</p>
      <div class="toolbar">
        <button @click="guard(() => download('export', 'webcam-'+session.id+'.zip'))" :disabled="processing || busy">Export session</button>
        <button v-if="session.result" @click="guard(() => download('mesh', 'full-unscaled-surface.ply'))">Download full unscaled mesh</button>
        <button v-if="session.calibrated?.full_mesh" @click="guard(() => download('mesh-mm', 'full-calibrated-mm-surface.ply'))">Download full calibrated mesh (mm)</button>
        <button @click="guard(deleteSession)" :disabled="processing || busy">Delete this local session</button>
        <button v-if="processing" @click="guard(() => action('cancel'))">Cancel processing</button>
        <button v-if="['capturing', 'failed', 'cancelled', 'interrupted'].includes(session.status)" @click="guard(() => action('start'))" :disabled="session.captures.length !== 61 || hasUnapprovedFrames || busy">{{ session.status === 'capturing' ? 'Reconstruct approved images' : 'Restart reconstruction' }}</button>
      </div>
      <section v-if="session.status === 'capturing'">
        <h2>Capture and mask review</h2>
        <p>Use steady diffuse light and a plain background. Keep the camera fixed and turn your head slowly. Include both ears. Review each image for blur and each mask for background, shoulders and neck.</p>
        <div class="toolbar"><button @click="guard(startCamera)" :disabled="!!stream">Enable camera</button><button @click="stopCamera">Stop camera</button>
          <label><input type="checkbox" v-model="consent" /> I consent to storing and processing these captures locally.</label>
        </div>
        <div class="columns">
          <section><video ref="video" autoplay playsinline muted class="preview" /><p>Mirrored preview · stored photos are unmirrored</p>
            <p>{{ guidance }}</p><p aria-live="polite">{{ countdown || '' }}</p>
            <div class="toolbar"><button @click="guard(() => takePhoto(selected))" :disabled="!stream || !consent || busy">{{ selected === 0 ? 'Capture frontal' : 'Capture / retake selected frame' }}</button>
              <button @click="guard(capturePass)" :disabled="!stream || !consent || busy || selected === 0">Capture 30-frame pass</button>
              <button @click="captureCancelled = true" :disabled="!busy">Stop capture sequence</button>
            </div>
          </section>
          <section><label>Capture to review<select v-model.number="selected" @change="guard(reviewSelected)"><option v-for="i in 61" :key="i" :value="i-1">{{ slot(i-1) }} {{ approved(i-1) ? '✓ saved' : frames[i-1] ? '· review needed' : '' }}</option></select></label>
            <p>Paint <strong>include</strong> to restore ears; paint <strong>exclude</strong> to remove neck, shoulders and background. The green overlay shows included pixels. Review every mask.</p>
            <div class="toolbar"><button @click="guard(reviewSelected)" :disabled="busy">Load / generate mask</button><label><input type="checkbox" v-model="includeBrush" /> Include brush</label>
              <label>Brush size<input type="range" v-model.number="brushSize" min="3" max="120" /></label></div>
            <canvas ref="maskCanvas" class="mask-editor" @pointerdown="brushStart" @pointermove="brushMove" @pointerup="brushEnd" @pointercancel="brushEnd" />
            <button @click="guard(approveMask)" :disabled="!reviewFrame || busy">Approve and save this head-only mask</button>
          </section>
        </div>
      </section>
      <section v-if="session.result">
        <h2>Surface, scale and frontal points</h2>
        <p>{{ surface.units === 'mm' ? 'Tape-calibrated millimeters' : 'Unscaled reconstruction coordinates' }} · human webcam surface · anatomical accuracy unvalidated.</p>
        <div class="columns">
          <section><h3>Undistorted frontal image</h3>
            <svg v-if="frontUrl" :viewBox="`0 0 ${frontCamera.width} ${frontCamera.height}`" role="img" aria-label="Frontal detections and camera alignment">
              <image :href="frontUrl" :width="frontCamera.width" :height="frontCamera.height" />
              <path v-if="showWire" :d="wirePath" stroke="#0ff" fill="none" stroke-width="0.6" opacity=".5" />
              <circle v-for="(p,i) in session.result.raw_predictions" :key="i" :cx="p.x*frontCamera.width" :cy="p.y*frontCamera.height" :r="i === pointIndex ? 8 : 3" :fill="i === pointIndex ? '#ff7b00' : '#00ffba'" @click="pointIndex=i" />
            </svg>
            <label><input type="checkbox" v-model="showWire" /> Show camera-aligned surface wireframe</label>
            <p>Inspect silhouette, ears, nose and chin alignment. A correct ray hit cannot distinguish reconstruction error, registration error, and detector disagreement.</p>
            <label>MediaPipe index<input type="number" v-model.number="pointIndex" min="0" :max="detections.length-1" /></label>
            <pre v-if="point">{{ JSON.stringify(point, null, 2) }}</pre>
            <div class="toolbar"><button v-for="decision in ['pending','accepted','rejected']" :key="decision" @click="guard(() => decide(decision))" :disabled="!point">{{ decision }}</button></div>
          </section>
          <section><h3>Rotatable surface</h3>
            <svg ref="viewport" viewBox="0 0 720 480" role="img" aria-label="Rotate surface; Control-click to trace tape route" tabindex="0" @pointerdown="surfaceDown" @pointermove="surfaceMove" @pointerup="surfaceUp" @pointercancel="drag=null" @wheel.prevent="zoom = Math.max(.25, Math.min(5, zoom * ($event.deltaY > 0 ? .9 : 1.1)))">
              <rect width="720" height="480" fill="#edf2f5" /><polygon v-for="f in faces" :key="f.index" :points="f.points" :fill="f.fill" />
              <polyline v-for="(line,i) in routeLines" :key="'route'+i" :points="line" fill="none" stroke="#d75b10" stroke-width="2" stroke-dasharray="5 2" />
              <g v-for="(p,i) in routeMarks" :key="i"><circle :cx="p.x" :cy="p.y" r="5" fill="#ff7b00" /><text :x="p.x+7" :y="p.y-5">{{ i+1 }}</text></g>
              <circle v-if="selectedMark" :cx="selectedMark.x" :cy="selectedMark.y" r="7" fill="#15c8ae" stroke="white" />
            </svg>
            <label>Yaw<input type="range" v-model.number="yaw" min="-180" max="180" /></label><label>Tilt<input type="range" v-model.number="pitch" min="-90" max="90" /></label>
            <p>Drag to rotate, scroll to zoom. Ctrl-click (or enable tap placement) to add tape contact controls on visible surface. Missing ear/chin coverage requires a new capture.</p>
            <label><input type="checkbox" v-model="tapPlacement" /> Tap to place route controls</label>
          </section>
        </div>
        <h3>Tape calibration and independent check</h3>
        <p>Trace left tragion → subnasale → right tragion for scale, including intermediate tape-contact points. Separately trace left tragion → menton → right tragion for the independent check. Routes use mesh edges between controls and may overestimate a smooth tape arc.</p>
        <div class="toolbar"><label>Route<select v-model="routeKind"><option value="scale">Scale via subnasale</option><option value="check">Independent check via menton</option></select></label>
          <label>Next point<select v-model="routeLabel"><option value="left_tragion">Left tragion (start)</option><option value="control">Intermediate control</option><option value="subnasale">Subnasale</option><option value="menton">Menton</option><option value="right_tragion">Right tragion (end)</option></select></label>
          <button @click="routes[routeKind].pop(); coverageReviewed=false">Undo last route point</button><button @click="routes[routeKind]=[]; coverageReviewed=false">Clear route</button>
          <button @click="guard(saveDraft)">Save route draft locally</button></div>
        <p>{{ routes[routeKind].map((p,i) => `${i+1}: ${p.label}`).join(' → ') || 'No controls placed' }}</p>
        <p v-if="routePreview.length">Mesh-edge route: {{ routePreview.some(p => p.status !== 'ok') ? 'Disconnected surface — cannot calibrate' : routePreview.reduce((sum,p) => sum+p.length, 0).toFixed(3)+' '+surface.units }}. Dashed route overlays include hidden segments; rotate to inspect the full contact route.</p>
        <div class="toolbar"><label v-for="i in 3" :key="'s'+i">Scale reading {{ i }} (mm)<input v-model.number="scaleReadings[i-1]" type="number" min="1" step="0.1" /></label></div>
        <div class="toolbar"><label v-for="i in 3" :key="'c'+i">Independent check {{ i }} (mm)<input v-model.number="checkReadings[i-1]" type="number" min="1" step="0.1" /></label></div>
        <label><input type="checkbox" v-model="coverageReviewed" /> I inspected both complete tape routes, including ears, nose and chin, and found no missing coverage or bridged holes.</label>
        <button @click="guard(calibrate)" :disabled="!coverageReviewed || busy">Calibrate and report independent check</button>
        <pre v-if="session.calibrated">{{ JSON.stringify(session.calibrated.report, null, 2) }}</pre>
        <details><summary>Reconstruction and camera diagnostics</summary><pre>{{ JSON.stringify(session.result.diagnostics, null, 2) }}</pre></details>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { captureNativeFrame, nativeCameraConstraints, captureGuidance } from './webcam_capture';
import { attachmentPoint, projectMesh, shadedFaces, pickSurface } from './face_annotation_geometry';
import { projectPoint } from './dimension_fixture_geometry';
import { buildSurfaceGraph, surfacePath } from './face_surface_paths';

const API = 'http://127.0.0.1:5182';
const session = ref(null), sessions = ref([]), diagnostics = ref(null), resumeId = ref('');
const error = ref(''), message = ref(''), busy = ref(false), consent = ref(false);
const video = ref(null), stream = ref(null), countdown = ref(0), selected = ref(0), frames = ref({}), captureCancelled = ref(false);
const maskCanvas = ref(null), reviewFrame = ref(null), includeBrush = ref(false), brushSize = ref(30);
const frontUrl = ref(''), pointIndex = ref(0), showWire = ref(false), yaw = ref(0), pitch = ref(0), zoom = ref(1), viewport = ref(null);
const routes = ref({ scale: [], check: [] }), routeKind = ref('scale'), routeLabel = ref('left_tragion'), tapPlacement = ref(false);
const scaleReadings = ref(['','','']), checkReadings = ref(['','','']), coverageReviewed = ref(false);
let pollTimer, maskWorker, workerCounter = 0, maskPixels, painting = false, drag = null, disposed = false;
const pending = new Map();
const slot = i => i === 0 ? 'front' : 'turn_'+String(i-1).padStart(2, '0');
const guidance = computed(() => captureGuidance(selected.value));
const approved = i => !frames.value[i]?.pending && session.value?.captures.some(c => c.slot === slot(i));
const hasUnapprovedFrames = computed(() => Object.values(frames.value).some(f => f.pending));
const processing = computed(() => session.value?.status === 'processing');
async function guard(fn) { error.value=''; try { await fn(); } catch (e) { error.value=e.message; } }
async function api(path, payload) {
  const response = await fetch(API+path, payload === undefined ? {} : { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
  const result = await response.json(); if (!response.ok) throw Error(result.error || 'Local processor request failed.'); return result;
}
async function connect() { diagnostics.value=await api('/diagnostics'); sessions.value=await api('/sessions'); message.value='Connected to private local processor.'; }
async function adopt(state) {
  stopCamera(); frames.value={}; reviewFrame.value=null; routes.value={scale:[],check:[]}; coverageReviewed.value=false;
  session.value=state; selected.value=0; schedulePoll();
  if (frontUrl.value) URL.revokeObjectURL(frontUrl.value); frontUrl.value='';
  if (state.calibrated) {
    const report=state.calibrated.report;
    routes.value={scale:report.scale.route,check:report.independent_check.route};
    scaleReadings.value=[...report.scale.readings_mm]; checkReadings.value=[...report.independent_check.readings_mm];
  }
  if (state.draft) {
    routes.value={scale:state.draft.scale_route,check:state.draft.check_route};
    scaleReadings.value=state.draft.scale_readings_mm; checkReadings.value=state.draft.check_readings_mm;
  }
  if (state.result) await loadFrontal();
}
async function createSession() { await adopt(await api('/sessions', {})); await connect(); }
async function resume() { await adopt(await api('/sessions/'+resumeId.value)); }
function schedulePoll() { clearTimeout(pollTimer); if (!disposed && processing.value) pollTimer=setTimeout(() => guard(refresh), 1500); }
async function refresh() {
  const id=session.value.id, state=await api('/sessions/'+id);
  if (session.value?.id !== id) return;
  session.value=state; if (state.result && !frontUrl.value) await loadFrontal(); schedulePoll();
}
async function action(name, payload={}) { const state=await api(`/sessions/${session.value.id}/${name}`,payload); if (name !== 'cancel') session.value=state; schedulePoll(); }
async function deleteSession() { await api(`/sessions/${session.value.id}/delete`,{}); session.value=null; stopCamera(); clearTimeout(pollTimer); await connect(); }
async function download(kind, name) {
  const response=await fetch(`${API}/sessions/${session.value.id}/${kind}`); if (!response.ok) throw Error((await response.json()).error);
  const url=URL.createObjectURL(await response.blob()), a=document.createElement('a'); a.href=url; a.download=name; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
}
const base64 = blob => new Promise((resolve,reject) => { const r=new FileReader(); r.onerror=reject; r.onload=() => resolve(r.result.split(',')[1]); r.readAsDataURL(blob); });
const blobOf = canvas => new Promise(resolve => canvas.toBlob(resolve,'image/png'));
const sha = async blob => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await blob.arrayBuffer())),v=>v.toString(16).padStart(2,'0')).join('');
async function restore(event) { await guard(async () => { const file=event.target.files[0]; if (!file) return; busy.value=true; try {
  const response=await fetch(API+'/restore',{method:'POST',headers:{'Content-Type':'application/zip'},body:file});
  const result=await response.json(); if(!response.ok) throw Error(result.error); await adopt(result); await connect();
} finally { busy.value=false; event.target.value=''; } }); }
async function startCamera() {
  if (!navigator.mediaDevices?.getUserMedia) throw Error('Camera access requires a local secure browser context.');
  stream.value=await navigator.mediaDevices.getUserMedia(nativeCameraConstraints); await nextTick(); video.value.srcObject=stream.value; await video.value.play();
}
function stopCamera() { captureCancelled.value=true; stream.value?.getTracks().forEach(t=>t.stop()); stream.value=null; }
const pause = ms => new Promise(resolve=>setTimeout(resolve,ms));
async function countIn() { for (let i=3;i>0;i--) { if (captureCancelled.value || disposed) throw Error('Capture stopped.'); countdown.value=i; await pause(1000); } countdown.value=0; }
function snap(index) {
  const frame=captureNativeFrame(video.value,stream.value.getVideoTracks()[0].getSettings());
  frame.pending=true;
  frames.value[index]=frame;
}
async function takePhoto(index) { busy.value=true; captureCancelled.value=false; try { await countIn(); if (captureCancelled.value) return; snap(index); await reviewSelected(); } finally { busy.value=false; countdown.value=0; } }
async function capturePass() {
  busy.value=true; captureCancelled.value=false;
  const start=selected.value<=30 ? 1 : 31;
  try { await countIn(); for (let i=start;i<start+30;i++) { if (captureCancelled.value || disposed) break; selected.value=i; snap(i); await pause(1400); } await reviewSelected(); }
  finally { busy.value=false; countdown.value=0; }
}
function workerSegment(canvas) {
  if (!maskWorker) {
    maskWorker=new Worker('/mediapipe/webcam_mask_worker.js');
    maskWorker.onmessage=({data})=>{ const request=pending.get(data.id); if (!request) return; pending.delete(data.id); data.error ? request.reject(Error(data.error)) : request.resolve(data); };
    maskWorker.onerror=event=>{ for (const request of pending.values()) request.reject(Error(event.message || 'Mask worker failed.')); pending.clear(); };
  }
  return new Promise(async (resolve,reject)=>{ const id=++workerCounter; pending.set(id,{resolve,reject}); try { const image=await createImageBitmap(canvas); maskWorker.postMessage({id,image},[image]); } catch(e) { pending.delete(id); reject(e); } });
}
async function reviewSelected() {
  const index=selected.value;
  let frame=frames.value[index];
  if (!frame && approved(index)) {
    const c=session.value.captures.find(c=>c.slot===slot(index));
    const [imgResponse,maskResponse]=await Promise.all(['image','mask'].map(kind=>fetch(`${API}/sessions/${session.value.id}/captures/${slot(index)}/${kind}`)));
    if (!imgResponse.ok || !maskResponse.ok) throw Error('Could not reload saved capture.');
    const [image,mask]=await Promise.all([createImageBitmap(await imgResponse.blob()),createImageBitmap(await maskResponse.blob())]);
    const canvas=document.createElement('canvas'); canvas.width=image.width; canvas.height=image.height; canvas.getContext('2d').drawImage(image,0,0); image.close();
    const maskC=document.createElement('canvas'); maskC.width=mask.width; maskC.height=mask.height; maskC.getContext('2d').drawImage(mask,0,0); mask.close();
    frame={...c,canvas,mask:maskC,provenance:c.mask_provenance}; frames.value[index]=frame;
  }
  reviewFrame.value=null;
  if (!frame) { message.value='Capture this frame first.'; return; }
  if (!frame.mask) {
    message.value='Generating a local person-feature mask…';
    const result=await workerSegment(frame.canvas), small=document.createElement('canvas'); small.width=result.width; small.height=result.height;
    const context=small.getContext('2d'), pixels=context.createImageData(result.width,result.height);
    result.values.forEach((v,i)=>{ pixels.data.set([v,v,v,255],i*4); }); context.putImageData(pixels,0,0);
    const mask=document.createElement('canvas'); mask.width=frame.canvas.width; mask.height=frame.canvas.height;
    const ctx=mask.getContext('2d'); ctx.imageSmoothingEnabled=false; ctx.drawImage(small,0,0,mask.width,mask.height);
    frame.mask=mask; frame.provenance=result.provenance;
  }
  if (index!==selected.value || disposed) return;
  reviewFrame.value=frame; maskPixels=frame.mask; await nextTick(); renderMask(); message.value='Review this mask, correct ears and neck, then approve.';
}
function renderMask() {
  const frame=reviewFrame.value, canvas=maskCanvas.value; if (!frame || !canvas) return;
  canvas.width=frame.canvas.width; canvas.height=frame.canvas.height;
  const ctx=canvas.getContext('2d'); ctx.drawImage(frame.canvas,0,0);
  const overlay=maskPixels.getContext('2d').getImageData(0,0,canvas.width,canvas.height);
  for (let i=0;i<overlay.data.length;i+=4) { const included=overlay.data[i]; overlay.data.set([0,220,100,included ? 100 : 0],i); }
  const temp=document.createElement('canvas'); temp.width=canvas.width; temp.height=canvas.height; temp.getContext('2d').putImageData(overlay,0,0); ctx.drawImage(temp,0,0);
}
function brushStart(event) { if (!reviewFrame.value) return; painting=true; maskCanvas.value.setPointerCapture(event.pointerId); brushMove(event); }
function brushMove(event) {
  if (!painting || !maskPixels) return;
  reviewFrame.value.pending=true;
  const rect=maskCanvas.value.getBoundingClientRect(), x=(event.clientX-rect.left)*maskPixels.width/rect.width, y=(event.clientY-rect.top)*maskPixels.height/rect.height;
  const ctx=maskPixels.getContext('2d'); ctx.fillStyle=includeBrush.value ? 'white':'black'; ctx.beginPath(); ctx.arc(x,y,brushSize.value*maskPixels.width/rect.width/2,0,2*Math.PI); ctx.fill();
  // Canvas anti-aliasing is thresholded to a binary mask at approval.
  renderMask();
}
function brushEnd() { painting=false; }
async function approveMask() {
  busy.value=true;
  try {
    const frame=reviewFrame.value, index=selected.value, ctx=frame.mask.getContext('2d'), pixels=ctx.getImageData(0,0,frame.mask.width,frame.mask.height);
    for (let i=0;i<pixels.data.length;i+=4) { const v=pixels.data[i]>=128 ? 255:0; pixels.data.set([v,v,v,255],i); } ctx.putImageData(pixels,0,0);
    const [image,mask]=await Promise.all([blobOf(frame.canvas),blobOf(frame.mask)]);
    await action('capture',{slot:slot(index),image:await base64(image),mask:await base64(mask),sha256:await sha(image),approved:true,mirrored:false,
      timestamp:frame.timestamp,camera_settings:frame.camera_settings,mask_provenance:frame.provenance});
    frame.pending=false;
    message.value='Approved capture saved locally.';
    if (selected.value<60) { selected.value++; await reviewSelected(); }
  } finally { busy.value=false; }
}
const surface=computed(()=>session.value?.calibrated?.surface || session.value?.result?.surface);
const frontCamera=computed(()=>{ const r=session.value?.result; return r ? (session.value.calibrated?.cameras || r.cameras)[r.frontal_camera_key] : null; });
const detections=computed(()=>session.value?.calibrated?.projected_points || session.value?.result?.projected_points || []);
const point=computed(()=>detections.value[pointIndex.value]);
function displayPoint(point) { const c=frontCamera.value; const p=c.R.map((r,i)=>r.reduce((s,v,j)=>s+v*point[j],c.t[i])); return [p[0],-p[1],-p[2]]; }
const displayRecord=computed(()=>surface.value ? {...surface.value,mesh:{...surface.value.mesh,vertices:surface.value.mesh.vertices.map(displayPoint)}} : null);
const framing=computed(()=>{
  if (!displayRecord.value) return {center:[0,0,0],scale:1};
  const v=displayRecord.value.mesh.vertices, lo=[0,1,2].map(i=>Math.min(...v.map(p=>p[i]))),hi=[0,1,2].map(i=>Math.max(...v.map(p=>p[i])));
  return {center:lo.map((v,i)=>(v+hi[i])/2),scale:380/Math.max(...hi.map((v,i)=>v-lo[i]))};
});
const displayProjection=p=>projectPoint(p,framing.value.center,yaw.value,pitch.value,framing.value.scale*zoom.value);
const projected=computed(()=>displayRecord.value ? projectMesh(displayRecord.value,framing.value.center,yaw.value,pitch.value,framing.value.scale*zoom.value) : []);
const faces=computed(()=>displayRecord.value ? shadedFaces(displayRecord.value,projected.value) : []);
const routeMarks=computed(()=>displayRecord.value ? routes.value[routeKind.value].map(a=>displayProjection(attachmentPoint(displayRecord.value,a))) : []);
const graph=computed(()=>displayRecord.value ? buildSurfaceGraph(displayRecord.value) : null);
const routePreview=computed(()=>{
  const controls=routes.value[routeKind.value];
  return displayRecord.value ? controls.slice(1).map((a,i)=>surfacePath(displayRecord.value,graph.value,controls[i],a)) : [];
});
const routeLines=computed(()=>routePreview.value.filter(p=>p.status==='ok').map(path=>path.points.map(p=>{const q=displayProjection(p);return `${q.x},${q.y}`;}).join(' ')));
const selectedMark=computed(()=>{
  if (!point.value?.attachment || !displayRecord.value) return null;
  const p=displayProjection(attachmentPoint(displayRecord.value,point.value.attachment));
  const hit=pickSurface(displayRecord.value,projected.value,p.x,p.y);
  return hit && Math.abs(hit.depth-p.depth)<.001/Math.max(framing.value.scale,1e-9) ? p : null;
});
const wirePath=computed(()=>{
  if (!showWire.value || !surface.value) return '';
  const c=frontCamera.value, vertices=surface.value.mesh.vertices.map(p=>{
    const q=c.R.map((row,i)=>row.reduce((s,v,j)=>s+v*p[j],c.t[i]));
    return q[2]>0 ? [c.fx*q[0]/q[2]+c.cx,c.fy*q[1]/q[2]+c.cy] : null;
  });
  return surface.value.mesh.triangles.filter((_,i)=>i%Math.max(1,Math.ceil(surface.value.mesh.triangles.length/2000))===0).map(f=>{
    const p=f.map(i=>vertices[i]); return p.every(Boolean) ? `M${p[0]}L${p[1]}L${p[2]}Z` : '';
  }).join(' ');
});
async function loadFrontal() { const response=await fetch(`${API}/sessions/${session.value.id}/frontal`); if (!response.ok) throw Error('Could not load undistorted frontal image.'); frontUrl.value=URL.createObjectURL(await response.blob()); }
function surfaceDown(event) {
  if (event.ctrlKey || tapPlacement.value) {
    const rect=viewport.value.getBoundingClientRect(), x=(event.clientX-rect.left)*720/rect.width, y=(event.clientY-rect.top)*480/rect.height;
    const hit=pickSurface(displayRecord.value,projected.value,x,y);
    if (!hit) { error.value='No surface at that point. Missing coverage cannot be traced.'; return; }
    const {depth,...a}=hit; routes.value[routeKind.value].push({...a,label:routeLabel.value}); routeLabel.value='control'; coverageReviewed.value=false;
  } else { drag={x:event.clientX,y:event.clientY,yaw:yaw.value,pitch:pitch.value}; viewport.value.setPointerCapture(event.pointerId); }
}
function surfaceMove(event) { if (drag) { yaw.value=Math.max(-180,Math.min(180,drag.yaw+(event.clientX-drag.x)*.4)); pitch.value=Math.max(-90,Math.min(90,drag.pitch+(event.clientY-drag.y)*.4)); } }
function surfaceUp() { drag=null; }
async function calibrate() { await action('calibrate',{scale_readings_mm:scaleReadings.value,check_readings_mm:checkReadings.value,scale_route:routes.value.scale,check_route:routes.value.check,coverage_reviewed:coverageReviewed.value}); }
async function saveDraft() { await action('draft',{scale_readings_mm:scaleReadings.value,check_readings_mm:checkReadings.value,scale_route:routes.value.scale,check_route:routes.value.check}); message.value='Route draft saved locally.'; }
async function decide(decision) { await action('decisions',{index:pointIndex.value,decision}); }
onBeforeUnmount(()=>{ disposed=true; clearTimeout(pollTimer); stopCamera(); maskWorker?.terminate(); for(const p of pending.values()) p.reject(Error('Workspace closed.')); pending.clear(); if(frontUrl.value) URL.revokeObjectURL(frontUrl.value); });
</script>

<style scoped>
.pilot{max-width:1400px;margin:auto;padding:24px;color:#203944}.notice{padding:14px;background:#fff4d9;border-left:4px solid #bc7700}.error{color:#a41c12}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:16px 0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}.columns>section{min-width:0}button,input,select{font:inherit;padding:8px}button{cursor:pointer}button:disabled{cursor:default}label{display:inline-flex;gap:8px;align-items:center;flex-wrap:wrap;margin:6px}input[type=number]{width:90px}video,svg,.mask-editor{width:100%;display:block;background:#edf2f5}video{min-height:180px}.preview{transform:scaleX(-1)}.mask-editor,svg{touch-action:none;aspect-ratio:3/2}.mask-editor{height:auto;aspect-ratio:auto}svg text{font-size:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:400px;overflow:auto;font-size:12px}h2{margin-top:32px}@media(max-width:850px){.columns{grid-template-columns:1fr}}
</style>
