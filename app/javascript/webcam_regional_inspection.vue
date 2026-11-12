<template>
  <section class="regional" aria-label="Regional inspection and measurement report">
    <h3>Regional inspection and measurement report</h3>
    <p>Fixed regions from raw full-mesh detector-ray hits · unscaled reconstruction units · no geometry, landmarks or calibration changed.</p>
    <p>Nose, top-cheek, mid-cheek and chin regions are provisional detector proxies. Exact ARKit correspondences, actual seal paths and anatomical nose measurements require review.</p>
    <div class="tools">
      <label>Refined variant<select v-model="variant" aria-label="Regional refined variant" @change="load" :disabled="loading"><option value="raw">Raw stages only</option><option v-for="v in variants" :key="v.id" :value="v.id">{{ v.label }}</option></select></label>
      <button @click="load">Reload regional report</button><button v-if="loading" @click="cancel">Cancel regional inspection</button>
      <button v-if="report" @click="download">Download regional report JSON</button>
    </div>
    <p role="status" v-if="status!=='ready'">{{ message }}</p>
    <template v-if="report">
      <p v-if="report.status!=='ready'" role="alert">Report incomplete: {{ report.status }}. Missing raw-surface hits are not repaired or substituted.</p>
      <label>Inspect region<select aria-label="Inspect region" v-model="regionKey" :disabled="loading" @change="drawRegion"><option v-for="(v,key) in report.policy.regions" :value="key" :key="key">{{ v.label }}</option></select></label>
      <p v-if="region?.status!=='ok'" role="alert">Region unavailable: {{ region?.status || 'missing normalizer' }}. Missing detector indices: {{ region?.missing_indices?.join(', ') }}.</p>
      <div class="overview">
        <div><h4>Frontal image and detector cues</h4>
          <svg v-if="frontalUrl" :viewBox="`0 0 ${report.display_camera.width} ${report.display_camera.height}`" role="img" aria-label="Regional frontal detector cues">
            <image :href="frontalUrl" :width="report.display_camera.width" :height="report.display_camera.height" />
            <polyline v-for="(chain,i) in imageChains" :key="i" :points="chain" fill="none" stroke="#ffd24b" :stroke-width="imageRadius*2" stroke-opacity=".20" stroke-linecap="round" />
            <g v-for="index in shownIndices" :key="index"><template v-if="report.image_anchors[index]">
              <circle :cx="report.image_anchors[index].x" :cy="report.image_anchors[index].y" r="5" :fill="report.image_anchors[index].status==='ok'?'#ffd24b':'#ff5050'" />
              <text :x="report.image_anchors[index].x+8" :y="report.image_anchors[index].y-8" fill="white" stroke="#14202b" stroke-width=".4" font-size="19">{{ index }}</text>
            </template></g>
          </svg>
          <p>Yellow: unreviewed detector cues. Red: missed raw-surface ray. The image overlay illustrates the region; metrics use the fixed 3D volume.</p>
        </div>
        <div><h4>Nose section: depth and height</h4>
          <svg viewBox="0 0 600 320" role="img" aria-label="Nose profile comparison">
            <line :x1="plot([0,0])[0]" y1="20" :x2="plot([0,0])[0]" y2="280" stroke="#bbcbd3" />
            <line x1="30" :y1="plot([0,0])[1]" x2="570" :y2="plot([0,0])[1]" stroke="#bbcbd3" />
            <circle v-for="(p,i) in denseProfile" :key="'p'+i" :cx="plot(p)[0]" :cy="plot(p)[1]" r="1.4" fill="#7b8791" opacity=".35" />
            <g v-for="(stage,i) in report.stages" :key="stage.id" :stroke="colors[i]" stroke-width="1.3">
              <line v-for="(s,j) in stage.nose_profile?.segments || []" :key="j" :x1="plot(s[0])[0]" :y1="plot(s[0])[1]" :x2="plot(s[1])[0]" :y2="plot(s[1])[1]" />
            </g>
            <text x="35" y="310" fill="#334b58" font-size="12">Depth toward camera → · height ↑ · axes relative to raw tip proxy / eye-proxy span</text>
          </svg>
          <p><span v-for="(stage,i) in report.stages" :key="stage.id" :style="{color:colors[i]}">{{ stage.label }} · </span>Gray: sampled dense points in a narrow camera-X slab.</p>
          <p>Unjoined plane/mesh intersection segments retain gaps. This is a camera-based section, not an anatomical midline or a surface-arc measurement. Dense cache: {{ report.dense.status }}.</p>
        </div>
      </div>
      <div class="tools"><label>Regional yaw<input aria-label="Regional yaw" v-model.number="yaw" type="range" min="-100" max="100" /></label>
        <label>Regional tilt<input aria-label="Regional tilt" v-model.number="pitch" type="range" min="-75" max="75" /></label>
        <label>Regional zoom<input aria-label="Regional zoom" v-model.number="zoom" type="range" min=".5" max="3" step=".1" /></label>
        <label>Regional light<input aria-label="Regional light" v-model.number="light" type="range" min="-80" max="80" /></label>
        <label><input type="checkbox" v-model="smooth" /> Smooth regional lighting</label><label><input type="checkbox" v-model="edges" /> Regional mesh edges</label>
        <button @click="yaw=0;pitch=0;zoom=1">Reset regional view</button></div>
      <div class="views" v-show="status==='ready' && region?.status==='ok'">
        <section v-for="(stage,index) in report.stages" :key="stage.id"><h4 :style="{color:colors[index]}">{{ stage.label }}</h4>
          <canvas :key="canvasKey+'-'+stage.id" :ref="el=>canvases[index]=el" role="img" :aria-label="stage.label+' regional surface'" tabindex="0"
            @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="drag=null" @pointercancel="drag=null" @wheel.prevent="wheel" />
          <p>{{ stage.regions[regionKey]?.face_indices.length || 0 }} source triangles · {{ stage.regions[regionKey]?.status }} · {{ stage.regions[regionKey]?.display_status }}. Conservative crop of whole triangles; metrics sample the exact volume. Crop edges are not anatomical holes.</p>
        </section>
      </div>
      <h4>{{ region?.label || regionKey }} regional diagnostics</h4>
      <table><thead><tr><th>Stage</th><th>Status</th><th>Assessed plane neighborhoods</th><th>Plane RMS / eye proxy span</th><th>Raw → stage RMS</th><th>Raw proximity</th><th>Original boundary / nonmanifold edges</th></tr></thead><tbody>
        <tr v-for="stage in report.stages" :key="stage.id"><td>{{ stage.label }}</td><td>{{ stage.regions[regionKey]?.status }}</td><td>{{ stage.regions[regionKey]?.roughness?.count ?? '—' }}</td><td>{{ fmt(stage.regions[regionKey]?.roughness_fraction_eye_proxy_span?.rms) }}</td><td>{{ fmt(stage.regions[regionKey]?.raw_to_stage?.rms) }}</td><td>{{ percent(stage.regions[regionKey]?.raw_proximity_fraction) }}</td><td>{{ stage.regions[regionKey]?.original_boundary_edges ?? '—' }} / {{ stage.regions[regionKey]?.original_nonmanifold_edges ?? '—' }}</td></tr>
      </tbody></table>
      <p>Frontal ray support within the fixed volume: <span v-for="stage in report.stages" :key="stage.id">{{ stage.label }} {{ stage.regions[regionKey]?.frontal_support?.nearest_hits_in_fixed_region ?? '—' }}/{{ stage.regions[regionKey]?.frontal_support?.rays ?? '—' }} · </span></p>
      <p>Dense regional points: {{ report.dense.regions?.[regionKey]?.point_count ?? 'unavailable' }}. Region sizes and neighborhood radii are fixed from the original full mesh, so refined regions do not follow moved geometry.</p>
      <h4>Nose measurement proxies</h4>
      <table><thead><tr><th>Stage</th><th>Detector 4→2 chord</th><th>Camera-depth offset 168→4</th><th>Status</th></tr></thead><tbody><tr v-for="stage in report.stages" :key="stage.id"><td>{{ stage.label }}</td><td>{{ fmt(stage.nose_proxies?.chord) }}</td><td>{{ fmt(stage.nose_proxies?.forward_offset) }}</td><td>{{ stage.nose_proxies?.status }}</td></tr></tbody></table>
      <p>Distances above use reconstruction units. Eye-corner surface-proxy span: {{ fmt(report.eye_proxy_span) }}. These proxies are not reviewed pronasale/subnasale/sellion measurements. Anatomical nose protrusion, surface arc and all four exact ARKit path lengths remain unavailable until landmark/correspondence review.</p>
      <details><summary>Selected ARKit paths and missing correspondence</summary><pre>{{ JSON.stringify(report.arkit_paths,null,2) }}</pre></details>
      <p>Lower plane residuals can reflect curvature or lost detail. Nearest-surface disagreement, original boundary counts and successful ray hits do not validate anatomy, mask seal or physical millimeter accuracy. Measurements use unchanged source geometry, not display crops or smooth lighting.</p>
    </template>
  </section>
</template>

<script setup>
import {computed,nextTick,onBeforeUnmount,ref,toRaw,watch} from 'vue';
import {regionalFrame} from './webcam_regional_buffers';
import {createMeshRenderer} from './webcam_mesh_gl';
const props=defineProps({apiBase:String,sessionId:String,sourceKey:String,variants:Array,frontalUrl:String});
const variant=ref('raw'),regionKey=ref('nose'),report=ref(null),status=ref('idle'),message=ref(''),canvasKey=ref(0);
const yaw=ref(0),pitch=ref(0),zoom=ref(1),light=ref(-40),smooth=ref(true),edges=ref(false);
const colors=['#177d91','#b0770e','#b34477','#476fd0'];const canvases=[];
const region=computed(()=>report.value?.regions[regionKey.value]);
const loading=computed(()=>['loading','preparing'].includes(status.value));
const shownIndices=computed(()=>Array.from(new Set([33,263,...(report.value?.policy.regions[regionKey.value].chains.flat() || [])])).map(String));
const imageChains=computed(()=>report.value?.policy.regions[regionKey.value].chains.map(c=>c.filter(i=>report.value.image_anchors[i]).map(i=>`${report.value.image_anchors[i].x},${report.value.image_anchors[i].y}`).join(' ')) || []);
const imageRadius=computed(()=>{const a=report.value?.image_anchors[33],b=report.value?.image_anchors[263];return a&&b?Math.hypot(a.x-b.x,a.y-b.y)*report.value.policy.regions[regionKey.value].radius_fraction:0;});
const denseProfile=computed(()=>report.value?.dense.regions?.nose?.profile_scatter || []);
const profileBounds=computed(()=>{const span=report.value?.eye_proxy_span || 1,points=[...denseProfile.value,...(report.value?.stages.flatMap(s=>s.nose_profile?.segments.flat() || []) || [])];
  if(!points.length)return {lo:[-.5,-.5],hi:[.5,.5],span};const lo=[0,1].map(i=>Math.min(...points.map(p=>p[i]/span))),hi=[0,1].map(i=>Math.max(...points.map(p=>p[i]/span)));for(let i=0;i<2;i++){const pad=Math.max((hi[i]-lo[i])*.08,.01);lo[i]-=pad;hi[i]+=pad;}return {lo,hi,span};});
let revision=0,controller,workers=[],renderers=[],resizeObserver,drag=null,frame,cache=new Map(),animation;
function release(){workers.forEach(w=>{w.cancelWork?.();w.terminate();});workers=[];renderers.forEach(r=>r?.dispose());renderers=[];resizeObserver?.disconnect();cancelAnimationFrame(animation);}
function cancel(){revision++;controller?.abort();release();status.value='cancelled';message.value='Regional inspection cancelled. Source geometry and annotations are unchanged.';}
function fail(error){release();status.value='error';message.value=error.message || String(error);}
function plot(p){const b=profileBounds.value;return [30+(p[0]/b.span-b.lo[0])/(b.hi[0]-b.lo[0])*540,280-(p[1]/b.span-b.lo[1])/(b.hi[1]-b.lo[1])*260];}
function fmt(value){return Number.isFinite(value)?Math.abs(value)<1e-12?'0':value.toPrecision(5):'—';}
function percent(value){return Number.isFinite(value)?(100*value).toFixed(1)+'%':'—';}
function prepare(data,generation){return new Promise((resolve,reject)=>{
  const worker=new Worker(new URL('./webcam_mesh_worker.js',import.meta.url),{type:'module'});workers.push(worker);
  const timeout=setTimeout(()=>{worker.terminate();reject(Error('Regional mesh preparation exceeded 60 seconds.'));},60000);
  worker.cancelWork=()=>{clearTimeout(timeout);reject(new DOMException('Cancelled','AbortError'));};
  worker.onmessage=({data})=>{clearTimeout(timeout);worker.terminate();workers=workers.filter(w=>w!==worker);if(generation!==revision)return reject(new DOMException('Cancelled','AbortError'));data.error?reject(Error(data.error)):resolve(data.result);};
  worker.onerror=()=>{clearTimeout(timeout);worker.terminate();reject(Error('Regional mesh worker failed.'));};
  worker.postMessage(data,data.buffer?[data.buffer]:[]);
});}
async function fetchStage(stage,signal){
  if(cache.has(stage.id))return cache.get(stage.id).slice(0);
  const prefix=`/sessions/${props.sessionId}/`;if(!stage.mesh_url?.startsWith(prefix) || !/^\/sessions\/[a-f0-9]{32}\/(mesh|mesh-variant\/[a-z0-9_-]{1,40})$/.test(stage.mesh_url))throw Error('Regional mesh URL is outside this session.');
  const response=await fetch(props.apiBase+stage.mesh_url,{signal});if(!response.ok)throw Error('Regional source mesh download failed.');
  const chunks=[];let size=0;const reader=response.body.getReader();while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>64*1024*1024){await reader.cancel();throw Error('Regional source exceeds 64 MiB.');}chunks.push(value);}
  const bytes=new Uint8Array(size);let i=0;for(const chunk of chunks){bytes.set(chunk,i);i+=chunk.length;}
  const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(sha!==stage.sha256)throw Error('Regional source geometry hash changed.');
  cache.set(stage.id,bytes.buffer);return bytes.buffer.slice(0);
}
async function load(){cancel();const generation=revision;cache.clear();report.value=null;controller=new AbortController();status.value='loading';message.value='Inspecting fixed regions, geometry stages and saved dense support…';
 try{const response=await fetch(`${props.apiBase}/sessions/${props.sessionId}/regional-report?variant=${encodeURIComponent(variant.value)}`,{signal:controller.signal});const data=await response.json();if(!response.ok)throw Error(data.error || 'Regional report unavailable.');
  if(generation!==revision)return;if(data.version!=='webcam_regional_inspection_v1' || data.session_id!==props.sessionId || data.variant_id!==variant.value || data.units!=='reconstruction_unit' || data.calibration_applied)throw Error('Regional report provenance/units do not match this session.');
  report.value=data;await drawRegion();
 }catch(error){if(generation===revision && error.name!=='AbortError')fail(error);}}
async function drawRegion(){release();const generation=++revision;controller?.abort();controller=new AbortController();
 if(!report.value || region.value?.status!=='ok'){status.value='ready';return;}
 status.value='preparing';message.value='Preparing regional source triangles…';
 try{const meshes=await Promise.all(report.value.stages.map(async stage=>{
   const ids=stage.regions[regionKey.value]?.face_indices;if(!ids?.length)return null;
   return prepare(stage.mesh?{mesh:toRaw(stage.mesh),faceIndices:Array.from(ids),camera:toRaw(report.value.display_camera),scale:1}:{buffer:await fetchStage(stage,controller.signal),faceIndices:Array.from(ids),camera:toRaw(report.value.display_camera),scale:1},generation);
  }));if(generation!==revision)return;frame=regionalFrame(toRaw(region.value),toRaw(report.value.display_camera));canvasKey.value++;await nextTick();if(generation!==revision)return;
  renderers=meshes.map((mesh,i)=>{if(!mesh)return null;const renderer=createMeshRenderer(canvases[i],message=>fail(Error(message)));renderer.upload(mesh);return renderer;});
  status.value='ready';await nextTick();draw();resizeObserver=new ResizeObserver(schedule);canvases.filter(Boolean).forEach(c=>resizeObserver.observe(c));
 }catch(error){if(generation===revision && error.name!=='AbortError')fail(error);}}
function draw(){if(status.value==='ready'&&frame)for(const r of renderers)r?.draw({frame,yaw:yaw.value,pitch:pitch.value,zoom:zoom.value,lightAzimuth:light.value,smoothLighting:smooth.value,surfaceEdges:edges.value});}
function schedule(){cancelAnimationFrame(animation);animation=requestAnimationFrame(()=>{try{draw();}catch(error){fail(error);}});}
function pointerDown(e){if(e.ctrlKey||e.metaKey)return;drag={x:e.clientX,y:e.clientY,yaw:yaw.value,pitch:pitch.value};e.currentTarget.setPointerCapture(e.pointerId);}
function pointerMove(e){if(drag){yaw.value=Math.max(-100,Math.min(100,drag.yaw+(e.clientX-drag.x)*.4));pitch.value=Math.max(-75,Math.min(75,drag.pitch+(e.clientY-drag.y)*.4));}}
function wheel(e){zoom.value=Math.max(.5,Math.min(3,zoom.value*(e.deltaY>0?.95:1.05)));}
function download(){const url=URL.createObjectURL(new Blob([JSON.stringify(toRaw(report.value),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`regional-${props.sessionId}-${variant.value}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
watch(()=>[props.sessionId,props.sourceKey],()=>{variant.value=props.variants?.at(-1)?.id || 'raw';load();},{immediate:true});
watch(()=>[yaw.value,pitch.value,zoom.value,light.value,smooth.value,edges.value],schedule);
onBeforeUnmount(()=>{revision++;controller?.abort();release();cache.clear();});
</script>

<style scoped>
.regional{border:1px solid #bdcdd7;padding:16px;margin-top:20px}.tools{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.overview,.views{display:grid;grid-template-columns:1fr 1fr;gap:18px}.overview>div,.views>section{min-width:0}svg{width:100%;background:#eef3f5}canvas{display:block;width:100%;aspect-ratio:3/2;background:#192b38;touch-action:none}button,select{font:inherit;padding:7px}table{font-size:13px;border-collapse:collapse;width:100%;margin:12px 0}td,th{text-align:left;padding:7px;border-bottom:1px solid #dbe1e5}p{line-height:1.4}pre{white-space:pre-wrap;max-height:220px;overflow:auto;font-size:12px}@media(max-width:850px){.overview,.views{grid-template-columns:1fr}table{display:block;overflow:auto}}
</style>
