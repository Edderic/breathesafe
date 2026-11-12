<template>
  <section class="landmarks" aria-label="Anatomical landmark review">
    <h3>Review anatomical landmarks</h3>
    <p>Place and inspect nose landmarks on the original full surface. Raw and refined placements stay separate. These points do not change detector decisions, tape calibration or ARKit records.</p>
    <div class="tools">
      <label>Landmark source<select aria-label="Landmark source" v-model="variant" @change="load" :disabled="busy || dirty"><option value="raw">Raw full mesh</option><option v-for="v in variants" :key="v.id" :value="v.id">{{ v.label }} full mesh</option></select></label>
      <button @click="load" :disabled="busy || dirty">Reload landmark review</button>
      <label>Landmark<select aria-label="Landmark" v-model="selected" :disabled="busy || dirty" @change="selectPoint"><option v-for="(v,key) in data?.landmarks || {}" :key="key" :value="key">{{ v.label }}</option></select></label>
    </div>
    <p role="status">{{ message }}</p><p v-if="error" role="alert">{{ error }}</p>
    <template v-if="data">
      <p>{{ data.landmarks[selected].guide }}</p>
      <p>Inspect frontal, profile and underside views. If the surface does not resolve the landmark, save it as uncertain or unavailable. A detector suggestion is not an anatomical identification.</p>
      <div class="views">
        <div><h4>Frontal reference</h4><svg :viewBox="`0 0 ${data.camera.width} ${data.camera.height}`" role="img" aria-label="Landmark frontal reference">
          <image :href="frontalUrl" :width="data.camera.width" :height="data.camera.height" />
          <circle v-if="photoMark" :cx="photoMark[0]" :cy="photoMark[1]" r="8" fill="#ffb531" stroke="white" />
        </svg><p>Marker shows the placement projected through the registered frontal camera; inspect alignment manually.</p></div>
        <div><h4>Full source surface · reconstruction units</h4>
          <div class="surface"><canvas ref="canvas" role="img" aria-label="Landmark full surface" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="drag=null" @wheel.prevent="wheel" />
            <svg viewBox="0 0 720 480" class="overlay" aria-hidden="true"><g v-if="mark"><circle :cx="mark[0]" :cy="mark[1]" r="7" fill="#ffb531" stroke="white" /><text :x="mark[0]+10" :y="mark[1]-10" fill="white">{{ selected }}</text></g></svg>
          </div><p>The marker overlay may lie behind the surface after rotation. Inspect from several sides. Enable placement to click a visible triangle; drag rotates in either mode.</p>
        </div>
      </div>
      <div class="tools">
        <label><input type="checkbox" v-model="placing" :disabled="busy" /> Click to place selected landmark</label>
        <button @click="suggest" :disabled="busy || data.suggestions[selected]?.status!=='ok'">Use detector suggestion for review</button>
        <button @click="setView(0,0)">Front</button><button @click="setView(-90,0)">Left profile</button><button @click="setView(90,0)">Right profile</button><button @click="setView(0,-45)">From below</button>
      </div>
      <div class="tools">
        <label>Landmark yaw<input aria-label="Landmark yaw" type="range" v-model.number="yaw" min="-180" max="180" /></label>
        <label>Landmark tilt<input aria-label="Landmark tilt" type="range" v-model.number="pitch" min="-90" max="90" /></label>
        <label>Landmark zoom<input aria-label="Landmark zoom" type="range" v-model.number="zoom" min=".5" max="3" step=".1" /></label>
        <label>Landmark light<input type="range" v-model.number="light" min="-80" max="80" /></label>
        <label><input type="checkbox" v-model="smooth" /> Smooth lighting</label><label><input type="checkbox" v-model="edges" /> Mesh edges</label>
      </div>
      <label>Review status<select aria-label="Landmark review status" v-model="reviewStatus" @change="dirty=true" :disabled="busy"><option value="pending">Pending</option><option value="accepted">Accepted</option><option value="uncertain">Uncertain</option><option value="unavailable">Unavailable / missing surface</option></select></label>
      <label>Review notes<textarea aria-label="Landmark review notes" v-model="note" maxlength="2000" @input="dirty=true" :disabled="busy" /></label>
      <p>{{ point ? 'Point attached to source triangle '+point.attachment.triangle_index : 'No point placed' }} · {{ dirty ? 'Unsaved review' : 'Saved / unchanged' }}. Unavailable clears this landmark’s current attachment while preserving its history.</p>
      <button @click="save" :disabled="busy || !dirty || (reviewStatus==='accepted' && !point)">Save landmark review</button>
      <button @click="selectPoint" :disabled="busy || !dirty">Discard unsaved edits</button>
      <table><thead><tr><th>Landmark</th><th>Saved status</th><th>Reviewed</th></tr></thead><tbody><tr v-for="(v,key) in data.landmarks" :key="key"><td>{{ v.label }}</td><td>{{ data.review.points[key]?.status || 'not reviewed' }}</td><td>{{ data.review.points[key]?.reviewed_at || '—' }}</td></tr></tbody></table>
      <p>Saved with the session and included in its ZIP export. Anatomical protrusion, surface arcs and mask-contact path measurements remain undefined; these three points alone do not define them.</p>
    </template>
  </section>
</template>

<script setup>
import {computed,nextTick,onBeforeUnmount,ref,toRaw,watch} from 'vue';
import {sharedInspectionFrame} from './webcam_mesh_buffers';
import {createMeshRenderer} from './webcam_mesh_gl';
const props=defineProps({apiBase:String,sessionId:String,variants:Array,frontalUrl:String});
const data=ref(null),variant=ref('raw'),selected=ref('pronasale'),canvas=ref(null),point=ref(null),reviewStatus=ref('pending'),note=ref(''),dirty=ref(false),placing=ref(false);
const busy=ref(false),saving=ref(false),message=ref(''),error=ref('');
const yaw=ref(0),pitch=ref(0),zoom=ref(1),light=ref(-40),smooth=ref(true),edges=ref(false),frame=ref(null);
let renderer,worker,controller,generation=0,drag=null,observer,animation,provenance='manual_review';
function rotate(p){const a=yaw.value*Math.PI/180,b=pitch.value*Math.PI/180,q=[Math.cos(a)*p[0]+Math.sin(a)*p[2],p[1],-Math.sin(a)*p[0]+Math.cos(a)*p[2]];return [q[0],Math.cos(b)*q[1]-Math.sin(b)*q[2],Math.sin(b)*q[1]+Math.cos(b)*q[2]];}
function cameraPoint(){return data.value.camera.R.map((r,i)=>r.reduce((sum,v,j)=>sum+v*point.value.point[j],data.value.camera.t[i]));}
const mark=computed(()=>{if(!point.value || !frame.value)return null;const p=cameraPoint().map((v,i)=>v*(i===0?1:-1)-frame.value.center[i]),q=rotate(p);return [360+q[0]*frame.value.scale*zoom.value,240-q[1]*frame.value.scale*zoom.value];});
const photoMark=computed(()=>{if(!point.value)return null;const p=cameraPoint(),c=data.value.camera;return p[2]>0?[c.fx*p[0]/p[2]+c.cx,c.fy*p[1]/p[2]+c.cy]:null;});
function release(){controller?.abort();worker?.cancelWork?.();worker?.terminate();worker=null;renderer?.dispose();renderer=null;observer?.disconnect();cancelAnimationFrame(animation);}
async function request(path,payload,signal){const response=await fetch(props.apiBase+`/sessions/${props.sessionId}/`+path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal}:{signal});const body=await response.json();if(!response.ok)throw Error(body.error || 'Landmark request failed.');return body;}
function prepare(buffer,camera){return new Promise((resolve,reject)=>{worker=new Worker(new URL('./webcam_mesh_worker.js',import.meta.url),{type:'module'});const timer=setTimeout(()=>{worker?.terminate();reject(Error('Full surface preparation exceeded 60 seconds.'));},60000);worker.cancelWork=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};worker.onmessage=({data})=>{clearTimeout(timer);worker?.terminate();worker=null;data.error?reject(Error(data.error)):resolve(data.result);};worker.onerror=()=>{clearTimeout(timer);reject(Error('Full surface worker failed.'));};worker.postMessage({buffer,camera,scale:1},[buffer]);});}
async function load(){const run=++generation;release();data.value=null;frame.value=null;dirty.value=false;busy.value=true;error.value='';message.value='Loading full source surface…';controller=new AbortController();
 try{const result=await request('landmark-review?variant='+encodeURIComponent(variant.value),null,controller.signal);if(run!==generation)return;
  if(result.version!=='webcam-landmark-review-v1' || result.session_id!==props.sessionId || result.variant_id!==variant.value || result.units!=='reconstruction_unit')throw Error('Landmark source provenance mismatch.');
  if(!new RegExp(`^/sessions/${props.sessionId}/(mesh|mesh-variant/[a-z0-9_-]{1,40})$`).test(result.mesh_url))throw Error('Landmark source is outside this session.');
  const response=await fetch(props.apiBase+result.mesh_url,{signal:controller.signal});if(!response.ok)throw Error('Full source download failed.');
  const reader=response.body.getReader(),chunks=[];let length=0;while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>64*1024*1024){await reader.cancel();throw Error('Full source exceeds 64 MiB.');}chunks.push(value);}
  const bytes=new Uint8Array(length);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
  const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(sha!==result.sha256)throw Error('Full source hash mismatch.');
  const mesh=await prepare(bytes.buffer,result.camera);if(run!==generation)return;data.value=result;frame.value=sharedInspectionFrame([mesh]);await nextTick();
  renderer=createMeshRenderer(canvas.value,text=>{error.value=text;});renderer.upload(mesh);selectPoint();setView(0,0);message.value='Ready. Select a landmark, place it and inspect several views before saving.';observer=new ResizeObserver(schedule);observer.observe(canvas.value);
 }catch(e){if(run===generation && e.name!=='AbortError'){error.value=e.message;message.value='Review unavailable. Reload to retry.';release();}}
 finally{if(run===generation){busy.value=false;schedule();}}}
function selectPoint(){const saved=data.value?.review.points[selected.value];point.value=saved?.attachment?{attachment:structuredClone(toRaw(saved.attachment)),point:[...saved.point]}:null;reviewStatus.value=saved?.status || 'pending';note.value=saved?.note || '';dirty.value=false;provenance=saved?.provenance || 'manual_review';}
function suggest(){const p=data.value.suggestions[selected.value];if(p?.status==='ok'){point.value=structuredClone(toRaw(p));reviewStatus.value='pending';dirty.value=true;provenance='detector_suggestion';message.value='Suggestion loaded for review. Inspect it before acceptance.';}}
function setView(a,b){yaw.value=a;pitch.value=b;}
function schedule(){cancelAnimationFrame(animation);animation=requestAnimationFrame(()=>{try{renderer?.draw({frame:frame.value,yaw:yaw.value,pitch:pitch.value,zoom:zoom.value,lightAzimuth:light.value,smoothLighting:smooth.value,surfaceEdges:edges.value});}catch(e){error.value=e.message;}});}
function down(e){drag={x:e.clientX,y:e.clientY,yaw:yaw.value,pitch:pitch.value,moved:false};e.currentTarget.setPointerCapture(e.pointerId);}
function move(e){if(drag && (drag.moved || Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>4)){drag.moved=true;yaw.value=Math.max(-180,Math.min(180,drag.yaw+(e.clientX-drag.x)*.4));pitch.value=Math.max(-90,Math.min(90,drag.pitch+(e.clientY-drag.y)*.4));}}
async function up(e){const moved=drag?.moved;drag=null;if(moved || !placing.value || busy.value || !renderer)return;
 const rect=e.currentTarget.getBoundingClientRect();busy.value=true;error.value='';const run=generation;
 try{const hit=await request('landmark-review',{op:'pick',variant:variant.value,sha256:data.value.sha256,view:{...toRaw(frame.value),x:(e.clientX-rect.left)/rect.width,y:(e.clientY-rect.top)/rect.height,zoom:zoom.value,yaw:yaw.value,pitch:pitch.value}},controller.signal);
  if(run!==generation)return;if(hit.status!=='ok'){message.value='No visible surface hit. Existing placement retained.';return;}point.value=hit;provenance='manual_surface_pick';reviewStatus.value='pending';dirty.value=true;message.value='Placement changed. Inspect from several views, choose a status and save.';
 }catch(e){if(run===generation)error.value=e.message;}finally{if(run===generation)busy.value=false;}}
function wheel(e){zoom.value=Math.max(.5,Math.min(3,zoom.value*(e.deltaY>0?.95:1.05)));}
async function save(){busy.value=true;saving.value=true;error.value='';try{data.value.review=await request('landmark-review',{op:'review',variant:variant.value,sha256:data.value.sha256,revision:data.value.review.revision,landmark:selected.value,status:reviewStatus.value,attachment:point.value?.attachment || null,note:note.value,provenance},controller.signal);selectPoint();message.value='Landmark review saved locally. Export the session to include it.';}catch(e){error.value=e.message;}finally{busy.value=false;saving.value=false;}}
watch(()=>props.sessionId,load,{immediate:true});watch(()=>[yaw.value,pitch.value,zoom.value,light.value,smooth.value,edges.value],schedule);
onBeforeUnmount(()=>{generation++;release();});
</script>

<style scoped>
.landmarks{border:1px solid #bdcdd7;padding:16px;margin-top:20px}.tools{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.views{display:grid;grid-template-columns:1fr 1fr;gap:18px}.views>div{min-width:0}svg,canvas{display:block;width:100%;aspect-ratio:3/2;background:#192b38}.surface{position:relative}canvas{touch-action:none}.overlay{position:absolute;inset:0;pointer-events:none;background:none}button,select,textarea{font:inherit;padding:7px}textarea{display:block;width:95%;min-height:60px}table{border-collapse:collapse;width:100%;margin-top:12px}td,th{padding:7px;text-align:left;border-bottom:1px solid #dbe1e5}p{line-height:1.4}@media(max-width:850px){.views{grid-template-columns:1fr}}
</style>
