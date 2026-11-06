<template>
  <section class="probe" aria-label="Selected nose point inspection">
    <h4>Select the suspected dent on the full surface</h4>
    <p>This is an unsaved diagnostic point, separate from anatomical landmark acceptance. Click the shaded mesh to replace it; drag to rotate. The same selected world point is projected into every source photo, with visibility status.</p>
    <div class="tools">
      <label>Diagnostic mesh<select aria-label="Diagnostic mesh" v-model="sourceId" @change="load" :disabled="busy"><option v-for="s in meta?.sources || []" :key="s.id" :value="s.id">{{ s.label }}</option></select></label>
      <label>Local radius<select aria-label="Diagnostic radius" v-model.number="radiusFraction" @change="updateSection(true)" :disabled="busy"><option :value=".06">Small</option><option :value=".12">Medium</option><option :value=".20">Large</option></select></label>
      <label>Section plane<select aria-label="Diagnostic section plane" v-model="axis" @change="updateSection(false)" :disabled="busy"><option value="vertical">Vertical camera plane</option><option value="horizontal">Horizontal camera plane</option></select></label>
      <button @click="load" :disabled="busy">Reload diagnostic surface</button><button @click="clearPoint" :disabled="busy">Clear diagnostic point</button>
    </div>
    <p role="status">{{ message }}</p><p v-if="error" role="alert">{{ error }}</p>
    <div class="pair" v-if="meta">
      <div><div class="surface"><canvas ref="canvas" role="img" aria-label="Diagnostic shaded nose surface" @pointerdown="down" @pointermove="move" @pointerup="up" @pointercancel="drag=null" @wheel.prevent="wheel" />
        <svg viewBox="0 0 720 480" class="marker" aria-hidden="true"><g v-if="mark"><circle :cx="mark[0]" :cy="mark[1]" r="7" fill="#ffca28" stroke="#152d38" stroke-width="2" /></g></svg>
      </div><p>Original full geometry with magnified framing; no smoothing or hole filling. The marker overlay may be occluded after rotation.</p></div>
      <div><svg viewBox="0 0 600 400" role="img" aria-label="Diagnostic local cross-section">
        <defs><clipPath :id="clipId"><rect x="130" y="20" width="340" height="340" /></clipPath></defs>
        <line x1="300" y1="20" x2="300" y2="360" stroke="#adbfc8"/><line x1="130" y1="190" x2="470" y2="190" stroke="#adbfc8"/>
        <g :clip-path="`url(#${clipId})`"><g v-for="s in report?.sections || []" :key="s.id" :stroke="s.id==='raw_full'?'#007e99':'#c02088'" stroke-width="1.4"><line v-for="(line,i) in s.segments" :key="i" :x1="plot(line[0])[0]" :y1="plot(line[0])[1]" :x2="plot(line[1])[0]" :y2="plot(line[1])[1]" /></g></g>
        <circle v-if="report" cx="300" cy="190" r="5" fill="#ffca28" stroke="#152d38"/>
        <text x="30" y="385" font-size="12">Depth toward camera → · {{ axis==='vertical'?'height up':'camera right' }} ↑ · reconstruction units</text>
      </svg><p v-if="report">Center: exact selected source point. Axes span ±{{ report.radius.toPrecision(4) }} reconstruction units. Raw: cyan; refined: pink.</p>
      <p v-for="s in report?.sections || []" :key="s.id">{{ s.label }}: {{ s.status }} · {{ s.segments.length }} unjoined segments</p>
      <p>Plane uses the original frontal-camera axes, not an anatomical midline. Both sections pass through the same world location; no point correspondence is inferred.</p></div>
    </div>
    <div class="tools" v-if="meta">
      <label>Probe yaw<input aria-label="Probe yaw" v-model.number="yaw" type="range" min="-180" max="180" /></label><label>Probe tilt<input aria-label="Probe tilt" v-model.number="pitch" type="range" min="-90" max="90" /></label>
      <label>Probe zoom<input aria-label="Probe zoom" v-model.number="zoom" type="range" min=".5" max="3" step=".1" /></label><label>Probe light<input aria-label="Probe light" v-model.number="light" type="range" min="-80" max="80" /></label>
      <label><input v-model="smooth" type="checkbox" /> Smooth diagnostic lighting</label><label><input v-model="edges" type="checkbox" /> Diagnostic mesh edges</label>
      <button @click="yaw=0;pitch=0">Front</button><button @click="yaw=-65;pitch=0">Profile left</button><button @click="yaw=65;pitch=0">Profile right</button><button @click="yaw=0;pitch=-40">From below</button>
      <button @click="center" :disabled="!report||busy">Center selected point</button><button @click="download" :disabled="!report">Download point inspection</button>
    </div>
    <p v-if="report">{{ originLabel }} · {{ report.source_id }} · source triangle {{ report.attachment.triangle_index }}. Selection is not saved into the session; download a report to retain it.</p>
  </section>
</template>

<script setup>
import {computed,nextTick,onBeforeUnmount,ref,toRaw,watch} from 'vue';
import {createMeshRenderer} from './webcam_mesh_gl';
import {probeFrame,probeMark,probeSectionPlot} from './webcam_probe_geometry';
const props=defineProps({apiBase:String,sessionId:String,variant:String,slots:Array});const emit=defineEmits(['probe']);
const meta=ref(null),report=ref(null),sourceId=ref('raw_full'),radiusFraction=ref(.12),axis=ref('vertical'),canvas=ref(null),frame=ref(null),busy=ref(false),error=ref(''),message=ref(''),originLabel=ref('');
const yaw=ref(0),pitch=ref(0),zoom=ref(1),light=ref(-40),smooth=ref(true),edges=ref(false);
const clipId='probe-'+crypto.randomUUID();let renderer,worker,controller,revision=0,drag=null,observer,animation,pendingSlots=false;
const source=computed(()=>meta.value?.sources.find(s=>s.id===sourceId.value));
const mark=computed(()=>report.value&&frame.value?probeMark(report.value.point,meta.value.camera,frame.value,yaw.value,pitch.value,zoom.value):null);
function clearPoint(){report.value=null;emit('probe',null);message.value='Point cleared. Click the full surface to select a diagnostic point.';}
function release(){controller?.abort();worker?.cancelWork?.();worker?.terminate();worker=null;renderer?.dispose();renderer=null;observer?.disconnect();cancelAnimationFrame(animation);}
async function request(payload){const path=`${props.apiBase}/sessions/${props.sessionId}/nose-probe`;const r=await fetch(payload?path:path+'?variant='+encodeURIComponent(props.variant),payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal}:{signal:controller.signal});const d=await r.json();if(!r.ok)throw Error(d.error||'Diagnostic point unavailable.');if(d.version!=='webcam-nose-probe-v1'||d.session_id!==props.sessionId||d.variant_id!==props.variant)throw Error('Diagnostic provenance mismatch.');return d;}
function prepare(buffer,camera){return new Promise((resolve,reject)=>{const active=new Worker(new URL('./webcam_mesh_worker.js',import.meta.url),{type:'module'});worker=active;const timer=setTimeout(()=>{active.terminate();reject(Error('Diagnostic mesh preparation exceeded 60 seconds.'));},60000);active.cancelWork=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};active.onmessage=({data})=>{clearTimeout(timer);active.terminate();if(worker===active)worker=null;data.error?reject(Error(data.error)):resolve(data.result);};active.onerror=()=>{clearTimeout(timer);reject(Error('Diagnostic mesh worker failed.'));};active.postMessage({buffer,camera,scale:1},[buffer]);});}
async function load(){const run=++revision;release();clearPoint();meta.value=null;frame.value=null;busy.value=true;error.value='';controller=new AbortController();message.value='Loading full diagnostic surface…';
 try{const data=await request();if(run!==revision)return;meta.value=data;if(!data.sources.some(s=>s.id===sourceId.value))sourceId.value='raw_full';await nextTick();
 const s=source.value;if(!new RegExp(`^/sessions/${props.sessionId}/(mesh|mesh-variant/[a-z0-9_-]{1,40})$`).test(s.mesh_url))throw Error('Diagnostic mesh is outside this session.');
 const response=await fetch(props.apiBase+s.mesh_url,{signal:controller.signal});if(!response.ok)throw Error('Diagnostic source download failed.');const reader=response.body.getReader(),chunks=[];let size=0;
 while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>64*1024*1024){await reader.cancel();throw Error('Diagnostic source exceeds 64 MiB.');}chunks.push(value);}
 const bytes=new Uint8Array(size);let i=0;for(const c of chunks){bytes.set(c,i);i+=c.length;}const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==s.sha256)throw Error('Diagnostic mesh hash changed.');
 const mesh=await prepare(bytes.buffer,toRaw(data.camera));if(run!==revision)return;frame.value=probeFrame(s.seed.point||data.initial_center,data.camera,data.eye_proxy_span*radiusFraction.value);await nextTick();if(run!==revision)return;
 renderer=createMeshRenderer(canvas.value,text=>{error.value=text;renderer?.dispose();renderer=null;});renderer.upload(mesh);observer=new ResizeObserver(schedule);observer.observe(canvas.value);yaw.value=0;pitch.value=0;zoom.value=1;
 if(s.seed.status==='ok'){originLabel.value='Detector seed—not a manually selected dent';await inspect({op:'inspect',attachment:s.seed.attachment},run);}else message.value='Ready. Click the suspected dent on the surface.';
 }catch(e){if(run===revision&&e.name!=='AbortError'){error.value=e.message;message.value='Diagnostic inspection unavailable; reload to retry.';release();}}
 finally{if(run===revision){busy.value=false;schedule();}}}
async function inspect(extra,run=revision){const d=await request({variant:props.variant,source_id:sourceId.value,sha256:source.value.sha256,radius_fraction:radiusFraction.value,axis:axis.value,slots:[...props.slots],...extra});if(run!==revision)return;
 if(d.status==='missed_surface'){message.value='No visible surface hit. Previous diagnostic selection retained.';return false;}
 if(d.units!=='reconstruction_unit'||d.calibration_applied||d.source_sha256!==source.value.sha256||d.source_id!==sourceId.value)throw Error('Diagnostic source or units changed.');report.value=d;emit('probe',toRaw(d));message.value='Diagnostic point ready. Inspect the exact projected point in the photos below.';return true;}
async function updateSection(focus=false){if(!report.value||busy.value)return;busy.value=true;error.value='';const run=revision;try{await inspect({op:'inspect',attachment:toRaw(report.value.attachment)},run);if(run===revision&&focus)center();}catch(e){if(run===revision&&e.name!=='AbortError')error.value=e.message;}finally{if(run===revision)busy.value=false;}}
function center(){if(report.value){frame.value=probeFrame(report.value.point,meta.value.camera,report.value.radius);zoom.value=1;schedule();}}
function plot(p){return probeSectionPlot(p,report.value?.radius||1);}
function schedule(){cancelAnimationFrame(animation);animation=requestAnimationFrame(()=>{try{if(renderer&&frame.value)renderer.draw({frame:frame.value,yaw:yaw.value,pitch:pitch.value,zoom:zoom.value,lightAzimuth:light.value,smoothLighting:smooth.value,surfaceEdges:edges.value});}catch(e){error.value=e.message;}});}
function down(e){drag={x:e.clientX,y:e.clientY,yaw:yaw.value,pitch:pitch.value,moved:false};e.currentTarget.setPointerCapture(e.pointerId);}
function move(e){if(drag&&(drag.moved||Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>4)){drag.moved=true;yaw.value=Math.max(-180,Math.min(180,drag.yaw+(e.clientX-drag.x)*.4));pitch.value=Math.max(-90,Math.min(90,drag.pitch+(e.clientY-drag.y)*.4));}}
async function up(e){const moved=drag?.moved;drag=null;if(moved||busy.value||!renderer)return;busy.value=true;error.value='';const run=revision,rect=e.currentTarget.getBoundingClientRect();try{const picked=await inspect({op:'pick',view:{...toRaw(frame.value),x:(e.clientX-rect.left)/rect.width,y:(e.clientY-rect.top)/rect.height,yaw:yaw.value,pitch:pitch.value,zoom:zoom.value}},run);if(run===revision&&picked)originLabel.value='Manual diagnostic surface pick';}catch(e){if(run===revision&&e.name!=='AbortError')error.value=e.message;}finally{if(run===revision)busy.value=false;}}
function wheel(e){zoom.value=Math.max(.5,Math.min(3,zoom.value*(e.deltaY>0?.95:1.05)));}
function download(){const url=URL.createObjectURL(new Blob([JSON.stringify(toRaw(report.value),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`nose-point-${props.sessionId}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
watch(()=>[props.sessionId,props.variant],load,{immediate:true});watch(()=>props.slots.join('|'),()=>{if(busy.value)pendingSlots=true;else updateSection(false);});watch(busy,value=>{if(!value&&pendingSlots){pendingSlots=false;updateSection(false);}});watch(()=>[yaw.value,pitch.value,zoom.value,light.value,smooth.value,edges.value],schedule);
onBeforeUnmount(()=>{revision++;release();emit('probe',null);});
</script>

<style scoped>
.probe{padding:14px;border:1px solid #b9cbd5;margin:18px 0}.tools{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}.pair>div{min-width:0}.surface{position:relative}canvas,svg{display:block;width:100%;aspect-ratio:3/2}canvas{background:#192b38;touch-action:none}svg{background:#edf3f5}.marker{position:absolute;inset:0;pointer-events:none;background:none}button,select{font:inherit;padding:6px}p{line-height:1.4}@media(max-width:850px){.pair{grid-template-columns:1fr}}
</style>
