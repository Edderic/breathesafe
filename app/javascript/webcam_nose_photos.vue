<template>
  <section class="nose-photos" aria-label="Nose source-photo overlays">
    <h3>Nose close-ups on registered source photos</h3>
    <p>Compare full surfaces against original unmirrored capture pixels. Original camera registration stays fixed; lens distortion is included. These turn photos helped build the surface, so agreement is not independent accuracy validation.</p>
    <div class="tools">
      <label>Photo-overlay refinement<select aria-label="Photo-overlay refinement" v-model="variant" @change="load" :disabled="loading"><option value="raw">Raw only</option><option v-for="v in variants" :key="v.id" :value="v.id">{{ v.label }}</option></select></label>
      <label>Show overlay<select aria-label="Show nose overlay" v-model="overlay"><option value="both">Raw + refined</option><option value="raw_full">Raw full</option><option value="refined_full" :disabled="variant==='raw'">Refined full</option><option value="photo">Photo only</option></select></label>
      <label>Overlay opacity<input aria-label="Nose overlay opacity" type="range" v-model.number="opacity" min=".1" max="1" step=".05" /></label>
      <label><input type="checkbox" v-model="wire" /> Include fine wireframe</label>
      <label>Close-up zoom<input aria-label="Nose photo zoom" type="range" v-model.number="zoom" min="1" max="3" step=".1" /></label>
      <button @click="load" :disabled="loading">Reload nose photos</button><button v-if="loading" @click="cancel">Cancel nose photo loading</button>
      <button @click="download" :disabled="!cards.some(c=>c.report)">Download nose overlay report</button>
    </div>
    <p role="status">{{ message }}</p><p v-if="error" role="alert">{{ error }}</p>
    <div class="tools" v-if="catalog">
      <label>Registered source view<select aria-label="Registered source view" v-model="addSlot" :disabled="loading"><option v-for="v in catalog.views" :key="v.slot" :value="v.slot">{{ viewLabel(v) }}</option></select></label>
      <button @click="addView" :disabled="loading || cards.length>=6 || cards.some(c=>c.slot===addSlot)">Add view (up to 6)</button>
      <label><input type="checkbox" v-model="probeOpen" /> Select suspected dent on 3D surface</label>
    </div>
    <WebcamNoseProbe v-if="catalog&&probeOpen" :key="sessionId+'|'+variant" :api-base="apiBase" :session-id="sessionId" :variant="variant" :slots="cards.map(c=>c.slot)" @probe="probe=$event" />
    <p v-if="probe">Gold marker: selected diagnostic point on {{ probe.source_id }}. Dashed marker: occluded from that photo. The point is not snapped to photo features or transferred to the other mesh.</p>
    <label v-if="probe"><input type="checkbox" v-model="focusProbe" /> Center photos on selected diagnostic point</label>
    <p><span class="raw">Cyan: raw full mesh.</span> <span class="refined">Pink: refined full mesh.</span> Contours mark mesh-facing transitions and original boundaries; enable fine wireframe for surface context. Switch to Photo only to inspect the original image. Missing lines do not imply a hole: edges are sampled and visibility is tested at segment midpoints.</p>
    <div class="grid">
      <article v-for="card in cards" :key="card.slot">
        <h4>{{ card.view ? viewLabel(card.view) : card.slot }} <button @click="remove(card.slot)" :disabled="loading" :aria-label="'Remove '+card.slot">Remove</button></h4>
        <p v-if="card.error" role="alert">{{ card.error }}</p><p v-else-if="!card.report">Loading source view…</p>
        <template v-if="card.report && card.url">
          <svg :viewBox="box(card.report.crop,card.slot).join(' ')" role="img" :aria-label="card.slot+' nose source overlay'" :style="{aspectRatio:card.report.crop[2]/card.report.crop[3]}">
            <image :href="card.url" :width="card.view.camera.width" :height="card.view.camera.height" />
            <g v-for="stage in card.report.stages" :key="stage.id" :opacity="opacity" :stroke="stage.id==='raw_full'?'#00e5ff':'#ff4cbb'" fill="none" stroke-width=".75">
              <template v-if="overlay==='both'||overlay===stage.id"><polyline v-for="(line,i) in stage.lines.filter(l=>wire||l.kind==='contour')" :key="i" :stroke-width="line.kind==='contour'?1.2:.6" :points="line.pixels.map(p=>p.join(',')).join(' ')" /></template>
            </g>
            <g v-if="probe?.projections[card.slot]?.pixel" :data-probe-status="probe.projections[card.slot].status">
              <circle :cx="probe.projections[card.slot].pixel[0]" :cy="probe.projections[card.slot].pixel[1]" r="3.5" :fill="probe.projections[card.slot].status==='visible'?'#ffca28':'none'" stroke="#192b38" stroke-width="1.1" :stroke-dasharray="probe.projections[card.slot].status==='visible'?null:'2 2'" />
            </g>
          </svg>
          <p v-for="stage in card.report.stages" :key="stage.id">{{ stage.label }}: {{ stage.visible_contour_subsegments || 0 }} contour segments / {{ stage.visible_subsegments }} total sampled segments · {{ stage.status }}</p>
          <p v-if="card.view.quality_flags.length">Capture flags: {{ card.view.quality_flags.join(', ') }}</p>
          <p v-if="probe?.projections[card.slot]">Diagnostic point: {{ probe.projections[card.slot].status }} · {{ probe.source_id }}</p>
        </template>
      </article>
    </div>
    <p>Yaw and elevation describe camera position in the registered frontal-camera frame, not anatomical orientation. Height labels come from the capture protocol. Check nose silhouette, tip, columella and nearby skin across several views; alignment error, shape error, motion, highlights and shadows can each affect agreement. No annotations, scale, geometry or acceptance decisions change here.</p>
  </section>
</template>

<script setup>
import {onBeforeUnmount,ref,toRaw,watch} from 'vue';
import WebcamNoseProbe from './webcam_nose_probe.vue';
const props=defineProps({apiBase:String,sessionId:String,sourceKey:String,variants:Array});
const variant=ref('raw'),catalog=ref(null),cards=ref([]),overlay=ref('both'),wire=ref(false),opacity=ref(.65),zoom=ref(1),addSlot=ref(''),loading=ref(false),message=ref(''),error=ref('');
const probeOpen=ref(false),probe=ref(null),focusProbe=ref(true);
let revision=0,controller;
function viewLabel(v){return `${v.slot} · ${v.declared_height} · yaw ${v.yaw.toFixed(0)}° · elevation ${v.elevation.toFixed(0)}°`;}
function box(crop,slot){const [x,y,w,h]=crop,p=focusProbe.value&&probe.value?.projections[slot],center=p?.pixel&&['visible','occluded'].includes(p.status)?p.pixel:[x+w/2,y+h/2];return [center[0]-w/(2*zoom.value),center[1]-h/(2*zoom.value),w/zoom.value,h/zoom.value];}
function clear(){for(const c of cards.value)if(c.url)URL.revokeObjectURL(c.url);cards.value=[];}
function cancel(){revision++;controller?.abort();loading.value=false;message.value='Nose photo loading cancelled. Completed views retained.';}
async function json(endpoint,signal){const r=await fetch(`${props.apiBase}/sessions/${props.sessionId}/${endpoint}?variant=${encodeURIComponent(variant.value)}`,{signal});const d=await r.json();if(!r.ok)throw Error(d.error || 'Nose source view unavailable.');if(d.version!=='webcam-nose-photo-overlays-v1'||d.session_id!==props.sessionId||d.variant_id!==variant.value||d.units!=='reconstruction_unit')throw Error('Nose overlay provenance mismatch.');return d;}
async function fill(card,run){try{
 const report=await json('nose-overlay/'+card.slot,controller.signal);if(run!==revision)return;
 if(report.calibration_applied || JSON.stringify(report.view)!==JSON.stringify(toRaw(card.view)) || report.stages.some(s=>!catalog.value.stages.some(c=>c.id===s.id&&c.sha256===s.sha256)))throw Error('Source camera or mesh provenance changed. Reload nose photos.');
 const url=card.view.photo_url;if(url!==`/sessions/${props.sessionId}/captures/${card.slot}/image`)throw Error('Source photo is outside this session.');
 const response=await fetch(props.apiBase+url,{signal:controller.signal});if(!response.ok)throw Error('Original photo download failed.');const reader=response.body.getReader(),parts=[];let size=0;
 while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>16000000){await reader.cancel();throw Error('Source photo exceeds 16 MB.');}parts.push(value);}
 const bytes=new Uint8Array(size);let at=0;for(const p of parts){bytes.set(p,at);at+=p.length;}
 const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==card.view.photo_sha256)throw Error('Original photo hash changed.');
 if(run!==revision)return;card.url=URL.createObjectURL(new Blob([bytes],{type:'image/png'}));card.report=report;
 }catch(e){if(run===revision&&e.name!=='AbortError')card.error=e.message;}}
async function load(){cancel();const run=revision;clear();probe.value=null;catalog.value=null;error.value='';controller=new AbortController();loading.value=true;message.value='Selecting registered views and projecting full source geometry…';
 try{const data=await json('nose-views',controller.signal);if(run!==revision)return;catalog.value=data;addSlot.value=data.views[0]?.slot || '';
  cards.value=data.default_slots.map(slot=>({slot,view:data.views.find(v=>v.slot===slot),report:null,url:null,error:null}));
  for(const [i,card] of cards.value.entries()){if(run!==revision)return;await fill(card,run);if(run===revision)message.value=`Prepared ${i+1}/${cards.value.length} close-ups. Completed views can be inspected while the rest load.`;}
  if(run===revision)message.value=`Loaded ${cards.value.filter(c=>c.report).length}/${cards.value.length} registered source views. Toggle overlays to inspect alignment.`;
 }catch(e){if(run===revision&&e.name!=='AbortError'){error.value=e.message;message.value='Nose photo inspection unavailable.';}}
 finally{if(run===revision)loading.value=false;}}
async function addView(){if(loading.value||cards.value.length>=6||cards.value.some(c=>c.slot===addSlot.value))return;const view=catalog.value.views.find(v=>v.slot===addSlot.value);if(!view)return;if(controller?.signal.aborted)controller=new AbortController();cards.value.push({slot:view.slot,view,report:null,url:null,error:null});loading.value=true;const run=revision;await fill(cards.value.at(-1),run);if(run===revision)loading.value=false;}
function remove(slot){const card=cards.value.find(c=>c.slot===slot);if(card?.url)URL.revokeObjectURL(card.url);cards.value=cards.value.filter(c=>c.slot!==slot);}
function download(){const payload={...toRaw(catalog.value),overlays:cards.value.filter(c=>c.report).map(c=>toRaw(c.report)),diagnostic_probe:toRaw(probe.value)};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=`nose-source-overlays-${props.sessionId}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
watch(()=>[props.sessionId,props.sourceKey],()=>{variant.value=props.variants?.at(-1)?.id || 'raw';load();},{immediate:true});
onBeforeUnmount(()=>{revision++;controller?.abort();clear();});
</script>

<style scoped>
.nose-photos{padding:16px;border:1px solid #bdcdd7;margin-top:20px}.tools{display:flex;flex-wrap:wrap;gap:12px;margin:12px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid article{min-width:0}svg{width:100%;display:block;background:#192b38;max-height:550px}button,select{font:inherit;padding:6px}.raw{color:#006c80}.refined{color:#a20a64}p{line-height:1.4}h4 button{font-size:12px}@media(max-width:850px){.grid{grid-template-columns:1fr}}
</style>
