<template>
  <section class="comparison" aria-label="Full and analysis mesh comparison">
    <h3>{{ selectedVariants[1]?.label || 'Full surface' }} versus analysis mesh</h3>
    <p>Read-only inspection · {{ unitsLabel }} · shared orientation, framing, zoom and lighting. Drag either view to rotate; Shift + scroll to zoom. Use the controls above for lighting and mesh edges.</p>
    <p>Landmarks and tape controls remain attached to the original analysis topology. Clicking these inspection views never places or transfers annotations.</p>
    <div class="tools"><button @click="load">{{ status === 'ready' ? 'Reload comparison' : 'Retry comparison' }}</button>
      <button v-if="loading" @click="cancel">Cancel comparison loading</button>
      <button v-if="report" @click="exportReport">Download comparison report</button></div>
    <p v-if="status !== 'ready'" :role="status === 'error' ? 'alert' : 'status'">{{ statusText }}</p>
    <progress v-if="loading" :value="downloadTotal ? downloaded : undefined" :max="downloadTotal || 1" aria-label="Full mesh loading progress" />
    <div class="views" v-show="status === 'ready'">
      <section v-for="(variant,index) in selectedVariants" :key="variant.id">
        <h4>{{ variant.label }} · read-only</h4>
        <p>{{ variant.vertices.toLocaleString() }} vertices · {{ variant.triangles.toLocaleString() }} triangles · {{ unitsLabel }}</p>
        <canvas :key="canvasKey+'-'+index" :ref="element=>canvases[index]=element" :aria-label="variant.label+' inspection'" role="img" tabindex="0"
          @pointerdown="pointerDown" @pointermove="pointerMove" @pointerup="drag=null" @pointercancel="drag=null" @wheel="wheel" />
        <details><summary>Mesh identity and provenance</summary><pre>{{ JSON.stringify(variant,null,2) }}</pre></details>
      </section>
    </div>
    <template v-if="report">
      <label v-if="candidates.length>1">Comparison variant<select aria-label="Comparison variant" v-model="variantId" :disabled="loading" @change="load"><option v-for="v in candidates" :key="v.id" :value="v.id">{{ v.label }} · {{ v.kind }}</option></select></label>
      <h4>Sampled surface disagreement</h4>
      <p>Area-weighted triangle-surface samples to nearest triangle surfaces, in shared original coordinates. No alignment fit. Values describe mesh disagreement; they do not measure anatomical accuracy or provide an exact Hausdorff bound.</p>
      <table><thead><tr><th>Direction</th><th>Samples / seed</th><th>RMS</th><th>95th percentile</th><th>Sampled maximum</th></tr></thead>
        <tbody><tr v-for="direction in ['full_to_analysis','analysis_to_full']" :key="direction"><td>{{ direction==='full_to_analysis' ? selectedVariants[1].label+' → analysis' : 'Analysis → '+selectedVariants[1].label }}</td><td>{{ report.deviation[direction].sample_count }} / {{ report.deviation[direction].seed }}</td>
          <td>{{ statistic(report.deviation[direction].rms) }}</td><td>{{ statistic(report.deviation[direction].p95) }}</td><td>{{ statistic(report.deviation[direction].sampled_max) }}</td></tr></tbody></table>
      <p>Sampling can miss localized defects. Full-mesh bytes and all annotation attachments remain unchanged. Complete ear/chin coverage still requires inspection.</p>
    </template>
  </section>
</template>

<script setup>
import {computed,nextTick,onBeforeUnmount,ref,toRaw,watch} from 'vue';
import {meshLimits,sharedInspectionFrame} from './webcam_mesh_buffers';
import {createMeshRenderer} from './webcam_mesh_gl';

const props=defineProps({apiBase:String,sessionId:String,sourceKey:String,analysisMesh:Object,camera:Object,scaleFactor:Number,
  units:String,yaw:Number,pitch:Number,zoom:Number,lightAzimuth:Number,smoothLighting:Boolean,surfaceEdges:Boolean});
const emit=defineEmits(['rotate','zoom','frame']);
const status=ref('idle'),statusText=ref(''),report=ref(null),variantId=ref('raw'),canvasKey=ref(0);
const canvases=[];
const downloaded=ref(0),downloadTotal=ref(0),frame=ref(null);
const loading=computed(()=>['metadata','downloading','preparing'].includes(status.value));
const candidates=computed(()=>report.value?.variants.filter(v=>v.id!=='analysis') || []);
const selectedVariants=computed(()=>report.value ? [report.value.variants.find(v=>v.id==='analysis'),report.value.variants.find(v=>v.id===variantId.value)].filter(Boolean) : []);
const unitsLabel=computed(()=>props.units==='mm'?'tape-calibrated mm':'unscaled reconstruction units');
let generation=0,controller,workers=[],renderers=[],resizeObserver,animation,drag=null,closed=false;

function release(){controller?.abort();workers.forEach(w=>{w.cancelWork?.();w.terminate();});workers=[];renderers.forEach(r=>r.dispose());renderers=[];resizeObserver?.disconnect();cancelAnimationFrame(animation);}
function cancel(){generation++;release();status.value='cancelled';statusText.value='Comparison loading cancelled. Existing analysis annotations are available.';}
function fail(error){release();status.value='error';statusText.value=error.message || String(error);}
function prepare(data,revision){
  return new Promise((resolve,reject)=>{
    const worker=new Worker(new URL('./webcam_mesh_worker.js',import.meta.url),{type:'module'});workers.push(worker);
    const timer=setTimeout(()=>{worker.terminate();workers=workers.filter(w=>w!==worker);reject(Error('Mesh preparation exceeded 60 seconds. Download the original for external inspection.'));},60000);
    worker.cancelWork=()=>{clearTimeout(timer);reject(new DOMException('Cancelled','AbortError'));};
    worker.onmessage=({data})=>{clearTimeout(timer);worker.terminate();workers=workers.filter(w=>w!==worker);if(revision!==generation){reject(new DOMException('Cancelled','AbortError'));return;}
      data.error?reject(Error(data.error)):resolve(data.result);};
    worker.onerror=()=>{clearTimeout(timer);worker.terminate();workers=workers.filter(w=>w!==worker);reject(Error('Mesh worker failed or ran out of memory. The original remains available for download.'));};
    worker.postMessage(data,data.buffer?[data.buffer]:[]);
  });
}
async function fetchMesh(variant,signal){
  const expected=variant.byte_length;
  if(expected>meshLimits.bytes)throw Error('Mesh exceeds the 64 MiB inspection limit. Download the original for external inspection.');
  const response=await fetch(props.apiBase+variant.mesh_url,{signal});if(!response.ok)throw Error('Could not download inspection mesh. Reconnect the local processor and retry.');
  downloadTotal.value=expected;const chunks=[];let size=0;const reader=response.body.getReader();
  try {while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;
    if(size>meshLimits.bytes)throw Error('Mesh download exceeds inspection memory limits.');chunks.push(value);downloaded.value=size;}}
  catch(error){await reader.cancel().catch(()=>{});throw error;}
  if(size!==expected)throw Error('Mesh byte count changed during loading. Retry comparison.');
  const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
  if(digest!==variant.sha256)throw Error('Mesh hash does not match its comparison report. Retry without changing the session.');
  return bytes.buffer;
}
async function load(){
  const revision=++generation;release();report.value=null;frame.value=null;emit('frame',null);downloaded.value=0;downloadTotal.value=0;
  status.value='metadata';statusText.value='Sampling mesh disagreement and reading provenance…';controller=new AbortController();const signal=controller.signal;
  try {
    const response=await fetch(`${props.apiBase}/sessions/${props.sessionId}/mesh-comparison?variant=${encodeURIComponent(variantId.value)}`,{signal});
    const metadata=await response.json();if(!response.ok)throw Error(metadata.error || 'Comparison metadata unavailable.');
    if(revision!==generation)return;
    if(metadata.units!==props.units || metadata.display_scale!==props.scaleFactor)throw Error('Session scale changed during comparison loading. Retry.');
    report.value=metadata;if(!candidates.value.some(v=>v.id===variantId.value))variantId.value=candidates.value[0]?.id;
    const variant=candidates.value.find(v=>v.id===variantId.value);if(!variant)throw Error('No inspection variant is available.');
    if(metadata.comparison_source_id!==variant.id)throw Error('Deviation report does not identify the selected comparison variant.');
    status.value='downloading';statusText.value='Downloading and verifying the original full mesh…';
    const buffer=await fetchMesh(variant,signal);if(revision!==generation)return;
    status.value='preparing';statusText.value='Preparing full and analysis GPU buffers in local workers…';
    const [analysis,full]=await Promise.all([
      prepare({mesh:toRaw(props.analysisMesh),camera:toRaw(props.camera),scale:props.scaleFactor},revision),
      prepare({buffer,camera:toRaw(props.camera),scale:props.scaleFactor},revision)]);
    if(revision!==generation)return;
    for(const [mesh,variant] of [[analysis,selectedVariants.value[0]],[full,selectedVariants.value[1]]]) {
      if(mesh.positions.length/3!==variant.vertices || mesh.indices.length/3!==variant.triangles)throw Error('Mesh counts do not match the comparison provenance.');
    }
    frame.value=sharedInspectionFrame([analysis,full]);canvasKey.value++;await nextTick();
    if(revision!==generation || closed)return;
    for(const canvas of canvases)renderers.push(createMeshRenderer(canvas,message=>{if(revision===generation)fail(Error(message));}));
    renderers[0].upload(analysis);renderers[1].upload(full);
    status.value='ready';emit('frame',frame.value);await nextTick();draw();
    resizeObserver=new ResizeObserver(scheduleDraw);canvases.forEach(canvas=>resizeObserver.observe(canvas));
  }catch(error){if(revision===generation && !closed && error.name!=='AbortError')fail(error);}
}
function draw(){if(status.value!=='ready' || !frame.value)return;try{for(const renderer of renderers)renderer.draw({...props,frame:frame.value});}catch(error){fail(error);}}
function scheduleDraw(){cancelAnimationFrame(animation);animation=requestAnimationFrame(draw);}
function pointerDown(event){if(event.ctrlKey || event.metaKey)return;drag={x:event.clientX,y:event.clientY,yaw:props.yaw,pitch:props.pitch};event.currentTarget.setPointerCapture(event.pointerId);}
function pointerMove(event){if(drag)emit('rotate',{yaw:Math.max(-180,Math.min(180,drag.yaw+(event.clientX-drag.x)*.4)),pitch:Math.max(-90,Math.min(90,drag.pitch+(event.clientY-drag.y)*.4))});}
function wheel(event){if(!event.shiftKey)return;event.preventDefault();emit('zoom',Math.max(.5,Math.min(3,props.zoom*(event.deltaY>0?.95:1.05))));}
function statistic(value){return `${value.toPrecision(4)} ${props.units==='mm'?'mm':'reconstruction units'}`;}
function exportReport(){const url=URL.createObjectURL(new Blob([JSON.stringify(report.value,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`mesh-comparison-${props.sessionId}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
watch(()=>JSON.stringify([props.sessionId,props.sourceKey,props.scaleFactor,props.camera]),load,{immediate:true});
watch(()=>[props.yaw,props.pitch,props.zoom,props.lightAzimuth,props.smoothLighting,props.surfaceEdges],scheduleDraw);
onBeforeUnmount(()=>{closed=true;generation++;release();emit('frame',null);});
</script>

<style scoped>
.comparison{border:1px solid #bdcdd7;padding:16px;margin-top:24px}.views{display:grid;grid-template-columns:1fr 1fr;gap:20px}.views>section{min-width:0}canvas{display:block;width:100%;aspect-ratio:3/2;background:#192b38;touch-action:none}progress{width:100%}.tools{display:flex;gap:12px;flex-wrap:wrap}button,select{font:inherit;padding:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:240px;overflow:auto;font-size:12px}table{font-size:13px;border-collapse:collapse}td,th{padding:7px;text-align:left;border-bottom:1px solid #ddd}@media(max-width:850px){.views{grid-template-columns:1fr}}
</style>
