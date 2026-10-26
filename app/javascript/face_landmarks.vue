<template>
  <main class="face-review">
    <p class="eyebrow">MasqFit research</p>
    <h1>Face landmark labeling</h1>
    <p>Explore five synthetic head variants, capture consistent views, and mark points on the surface.</p>
    <p class="notice">Draft annotations · one template identity · nominal model millimeters. Anatomical placement and realism await review.</p>
    <div class="toolbar">
      <label>Head variant<select v-model="variantId" @change="changeHead">
        <option v-for="v in variants" :key="v.id" :value="v.id">{{ v.label }}</option>
      </select></label>
      <label>Your name<input v-model="annotator" maxlength="100" placeholder="Required to place a point" /></label>
      <label>Interaction<select v-model="mode"><option value="rotate">Rotate</option><option value="label">Place landmark</option></select></label>
    </div>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <p v-if="message" role="status">{{ message }}</p>
    <div class="layout">
      <section>
        <div class="views">
          <button v-for="view in views" :key="view.id" @click="setView(view)">{{ view.label }}</button>
        </div>
        <svg ref="viewport" viewBox="0 0 720 480" tabindex="0" role="img"
          :aria-label="`${record.record_id}: ${mode === 'label' ? 'click to place ' + selectedLabel.name : 'drag to rotate'}`"
          @pointerdown="startPointer" @pointermove="movePointer" @pointerup="finishPointer"
          @pointercancel="drag = null" @lostpointercapture="drag = null" @keydown="rotateKey" @wheel.prevent="zoom">
          <title>{{ record.record_id }} — draft landmark placement</title>
          <rect width="720" height="480" fill="#edf2f5" />
          <polygon v-for="face in faces" :key="face.index" :points="face.points" :fill="face.fill" />
          <g v-for="mark in visibleMarks" :key="mark.name" pointer-events="none">
            <circle :cx="mark.x" :cy="mark.y" r="5" :fill="mark.name === landmark ? '#e95d21' : '#126477'" stroke="white" stroke-width="1.5" />
            <text v-if="showNames" :x="mark.x + 8" :y="mark.y - 7">{{ mark.name.replaceAll('_', ' ') }}</text>
          </g>
        </svg>
        <p>{{ mode === 'label' ? 'Click the visible surface to place or replace the selected landmark.' : 'Drag or use arrow keys to rotate. Scroll to zoom.' }} Hidden points disappear behind the surface.</p>
        <div class="toolbar">
          <label>Yaw {{ Math.round(yaw) }}°<input v-model.number="yaw" type="range" min="-180" max="180" /></label>
          <label>Tilt {{ Math.round(pitch) }}°<input v-model.number="pitch" type="range" min="-90" max="90" /></label>
          <label><input type="checkbox" v-model="showNames" /> Show names</label>
          <button @click="resetView">Reset view</button>
        </div>
        <h2>Automatic views</h2>
        <p>Download a seven-view PNG sheet of the current head, with a shared scale and framing. Captures contain geometry without annotation overlays.</p>
        <div class="views"><button @click="downloadViews">Download view sheet</button><button @click="downloadCameras">Download camera metadata</button></div>
      </section>
      <aside>
        <h2>Landmarks</h2>
        <p>{{ Object.keys(current).length }} / {{ labelOptions.length }} marked on this head</p>
        <label>Point to place<select v-model="landmark">
          <option v-for="label in labelOptions" :key="label.id" :value="label.id">{{ current[label.id] ? '✓ ' : '' }}{{ label.name }}</option>
        </select></label>
        <p>{{ selectedLabel.description }}</p>
        <p v-if="selectedLabel.provisional" class="notice">Provisional placement definition. Mark your interpretation and explain it in the note.</p>
        <label>Placement note<textarea v-model="note" rows="3" maxlength="2000" placeholder="How you identified this point" /></label>
        <p>Notes are saved when placing a point, or with Save note.</p>
        <button @click="saveNote" :disabled="!current[landmark]">Save note</button>
        <p v-if="current[landmark]">Placed by {{ current[landmark].annotator }}. Coordinates: {{ pointReadout }} mm.</p>
        <div class="views"><button @click="removePoint" :disabled="!current[landmark]">Remove point</button><button @click="undo" :disabled="!history.length">Undo last edit</button></div>
        <h2>Save and resume</h2>
        <p>Edits stay in memory until downloaded. Export each head before leaving. Files are processed locally in your browser.</p>
        <label>Review status<select v-model="reviewStatus"><option value="draft">Draft</option><option value="ready_for_review">Ready for review</option></select></label>
        <div class="views"><button @click="exportAnnotations">Download annotations</button></div>
        <label>Resume annotations<input type="file" accept=".json,application/json" @change="importAnnotations" /></label>
        <p>Import requires the same variant and exact mesh fingerprint. Each point retains its annotator, surface attachment, view, and note.</p>
        <router-link :to="{ name: 'DimensionFixtures' }">Open analytic fixture viewer</router-link>
      </aside>
    </div>
  </main>
</template>

<script>
import base from '../../python/dimension_pipeline/assets/makehuman_head.json';
import variants from '../../python/dimension_pipeline/assets/head_variants.json';
import views from '../../python/dimension_pipeline/assets/head_views.json';
import { projectPoint } from './dimension_fixture_geometry';
import { makeHead, headCenter, projectMesh, shadedFaces, pickSurface, attachmentPoint,
  meshFingerprint, validateAnnotations } from './face_annotation_geometry';

const labelOptions = [
  ['pronasale', 'Pronasale', 'Anterior nasal tip on the midline.'],
  ['subnasale', 'Subnasale', 'Midline junction of the underside of the nose and upper lip.'],
  ['sellion', 'Sellion', 'Deepest nasal-root depression on the midline.'],
  ['menton', 'Menton', 'Inferior chin point on the midline of the external surface.'],
  ['midpoint_of_nose', 'Nasal midpoint', 'Proposed: halfway along the midline surface route from the chosen nasal root to pronasale. Record your root and route interpretation.', true],
  ...['left', 'right'].flatMap(side => [
    [`mid_nose_root_${side}`, `Mid-nose root · ${side}`, 'Proposed lateral transition between the nose and cheek near the nasal midpoint. Exact placement remains unresolved.', true],
    [`lateral_zygomatic_edge_${side}`, `Lateral zygomatic edge · ${side}`, 'Lateral cheekbone boundary; exact external-surface placement needs review.', true],
    [`gonion_${side}`, `Gonion · ${side}`, 'Jaw-angle landmark: lateral, inferior, posterior region of the mandibular angle. Review the external-surface placement.'],
    [`tragion_${side}`, `Tragion · ${side}`, 'Upper junction of the tragus (cartilaginous ear flap) with the head.'],
    [`ear_top_edge_${side}`, `Upper ear · ${side}`, 'Uppermost ear point in the agreed anatomical head orientation.', true],
  ]),
].map(([id, name, description, provisional]) => ({ id, name, description, provisional }));

function download(blob, name) {
  const url = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 10000);
}

export default {
  name: 'FaceLandmarks',
  data() {
    return { variants, views, labelOptions, variantId: 'base', record: makeHead(base, variants[0]), center: headCenter(base),
      drafts: {}, histories: {}, landmark: 'pronasale', annotator: '', note: '', reviewStatus: 'draft', mode: 'rotate',
      yaw: -45, pitch: 0, scale: 1.45, showNames: true, error: '', message: '', drag: null, savedDrafts: {} };
  },
  computed: {
    dirty() { return Object.entries(this.drafts).some(([id, draft]) => JSON.stringify(draft) !== this.savedDrafts[id]); },
    current() { return this.drafts[this.variantId]?.landmarks || {}; },
    history() { return this.histories[this.variantId] || []; },
    selectedLabel() { return labelOptions.find(l => l.id === this.landmark); },
    points() { return projectMesh(this.record, this.center, this.yaw, this.pitch, this.scale); },
    faces() { return shadedFaces(this.record, this.points); },
    visibleMarks() {
      return Object.entries(this.current).flatMap(([name, a]) => {
        const p = projectPoint(attachmentPoint(this.record, a.attachment), this.center, this.yaw, this.pitch, this.scale);
        const hit = pickSurface(this.record, this.points, p.x, p.y);
        return hit && Math.abs(hit.depth-p.depth) < .1 ? [{ name, ...p }] : [];
      });
    },
    pointReadout() { return attachmentPoint(this.record, this.current[this.landmark].attachment).map(v => v.toFixed(2)).join(', '); },
  },
  watch: {
    landmark() { this.note = this.current[this.landmark]?.note || ''; },
    reviewStatus(value) {
      if (this.drafts[this.variantId] && this.drafts[this.variantId].review_status !== value) {
        this.drafts[this.variantId].review_status = value;
      }
    },
  },
  mounted() { window.addEventListener('beforeunload', this.beforeUnload); },
  beforeUnmount() { window.removeEventListener('beforeunload', this.beforeUnload); },
  beforeRouteLeave() {
    if (this.dirty) return window.confirm('Some head annotations have not been exported. Leave this page and discard those edits?');
  },
  methods: {
    beforeUnload(event) { if (this.dirty) { event.preventDefault(); event.returnValue = ''; } },
    changeHead() {
      this.record = makeHead(base, variants.find(v => v.id === this.variantId));
      this.reviewStatus = this.drafts[this.variantId]?.review_status || 'draft';
      this.note = this.current[this.landmark]?.note || ''; this.error = ''; this.message = '';
    },
    setView(view) { this.yaw = view.yaw; this.pitch = view.pitch; },
    resetView() { this.yaw = -45; this.pitch = 0; this.scale = 1.45; },
    startPointer(event) {
      if (event.button !== 0) return;
      this.drag = { x: event.clientX, y: event.clientY, yaw: this.yaw, pitch: this.pitch };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    movePointer(event) {
      if (!this.drag || this.mode !== 'rotate') return;
      this.yaw = ((this.drag.yaw + (event.clientX-this.drag.x)*.4+540)%360)-180;
      this.pitch = Math.max(-90, Math.min(90, this.drag.pitch+(event.clientY-this.drag.y)*.4));
    },
    finishPointer(event) {
      const drag = this.drag; this.drag = null;
      if (this.mode !== 'label' || !drag || Math.hypot(event.clientX-drag.x, event.clientY-drag.y) > 5) return;
      this.error = ''; this.message = '';
      if (!this.annotator.trim()) { this.error = 'Enter your name before placing a point.'; return; }
      const point = this.$refs.viewport.createSVGPoint(); point.x = event.clientX; point.y = event.clientY;
      const local = point.matrixTransform(this.$refs.viewport.getScreenCTM().inverse());
      const hit = pickSurface(this.record, this.points, local.x, local.y);
      if (!hit) { this.error = 'Click a visible part of the head surface.'; return; }
      this.remember();
      const { depth, ...attachment } = hit;
      this.drafts[this.variantId].landmarks[this.landmark] = { attachment, annotator: this.annotator.trim(),
        note: this.note, placed_at: new Date().toISOString(), camera: this.camera() };
      this.drafts[this.variantId].review_status = 'draft'; this.reviewStatus = 'draft';
      this.message = `${this.selectedLabel.name} placed. Switch views to inspect its position.`;
    },
    remember() {
      if (!this.drafts[this.variantId]) this.drafts[this.variantId] = { landmarks: {}, review_status: 'draft' };
      if (!this.histories[this.variantId]) this.histories[this.variantId] = [];
      this.histories[this.variantId].push(JSON.parse(JSON.stringify(this.drafts[this.variantId])));
      if (this.histories[this.variantId].length > 100) this.histories[this.variantId].shift();
    },
    removePoint() { this.remember(); delete this.drafts[this.variantId].landmarks[this.landmark]; this.reviewStatus = 'draft'; this.note = ''; },
    saveNote() {
      if (!this.annotator.trim()) { this.error = 'Enter your name before editing a note.'; return; }
      this.remember(); Object.assign(this.current[this.landmark], { note: this.note,
        note_edited_by: this.annotator.trim(), note_edited_at: new Date().toISOString() });
      this.reviewStatus = 'draft'; this.message = 'Placement note saved to this draft.';
    },
    undo() {
      if (!this.history.length) return;
      this.drafts[this.variantId] = this.histories[this.variantId].pop();
      this.reviewStatus = this.drafts[this.variantId].review_status;
      this.note = this.current[this.landmark]?.note || '';
    },
    zoom(event) { this.scale = Math.max(.5, Math.min(5, this.scale*Math.exp(-Math.sign(event.deltaY)*.1))); },
    rotateKey(event) {
      const steps = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5] };
      if (!steps[event.key]) return;
      event.preventDefault(); this.yaw = ((this.yaw+steps[event.key][0]+540)%360)-180;
      this.pitch = Math.max(-90, Math.min(90, this.pitch+steps[event.key][1]));
    },
    camera(view = null) { return { projection: 'orthographic', width: 720, height: 480, center_mm: this.center,
      pixels_per_mm: view ? 1.45 : this.scale, yaw: view ? view.yaw : this.yaw, pitch: view ? view.pitch : this.pitch,
      mirrored: false, distortion: 'none', version: '1.0.0' }; },
    async exportAnnotations() {
      const record = this.record, variantId = this.variantId, landmarks = JSON.parse(JSON.stringify(this.current)), reviewStatus = this.reviewStatus;
      try {
        const bundle = { annotation_version: '1.0.0', record_id: record.record_id, topology_id: record.topology_id,
          mesh_sha256: await meshFingerprint(record), units: 'mm', source: record.source,
          definition_version: 'pilot-placement-2026-10-25', review_status: reviewStatus, landmarks };
        download(new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' }), `${record.record_id}-annotations.json`);
        this.savedDrafts[variantId] = JSON.stringify({ landmarks, review_status: reviewStatus });
        this.message = 'Annotation download requested. Keep exports for all edited heads before leaving.';
      } catch (error) { this.error = error.message; }
    },
    async importAnnotations(event) {
      const file = event.target.files[0]; if (!file) return;
      const record = this.record, variantId = this.variantId;
      try {
        if (file.size > 5*1024*1024) throw new Error('Choose an annotation file smaller than 5 MB.');
        const bundle = JSON.parse(await file.text());
        const landmarks = validateAnnotations(bundle, record, await meshFingerprint(record), labelOptions.map(l => l.id));
        if (this.variantId !== variantId) throw new Error('Head changed during import. Select it and import again.');
        this.remember(); this.drafts[variantId] = { landmarks, review_status: bundle.review_status };
        this.reviewStatus = bundle.review_status; this.note = this.current[this.landmark]?.note || '';
        this.savedDrafts[variantId] = JSON.stringify(this.drafts[variantId]);
        this.error = ''; this.message = 'Annotations imported. Undo restores the previous draft.';
      } catch (error) { this.error = `Could not import: ${error.message}`; }
      finally { event.target.value = ''; }
    },
    downloadCameras() {
      download(new Blob([JSON.stringify({ record_id: this.record.record_id, views: views.map(view =>
        ({ id: view.id, camera: this.camera(view) })) }, null, 2)], { type: 'application/json' }), `${this.record.record_id}-cameras.json`);
    },
    downloadViews() {
      const canvas = document.createElement('canvas'); canvas.width = 2160; canvas.height = 1530;
      const ctx = canvas.getContext('2d'); ctx.fillStyle = '#edf2f5'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      views.forEach((view, i) => {
        const x = (i%3)*720, y = Math.floor(i/3)*510;
        const points = projectMesh(this.record, this.center, view.yaw, view.pitch, 1.45);
        ctx.save(); ctx.translate(x, y); ctx.beginPath(); ctx.rect(0, 0, 720, 480); ctx.clip();
        for (const face of shadedFaces(this.record, points)) {
          const vertices = this.record.mesh.triangles[face.index].map(i => points[i]);
          ctx.fillStyle = face.fill; ctx.beginPath(); ctx.moveTo(vertices[0].x, vertices[0].y);
          ctx.lineTo(vertices[1].x, vertices[1].y); ctx.lineTo(vertices[2].x, vertices[2].y); ctx.closePath(); ctx.fill();
        }
        ctx.restore(); ctx.fillStyle = '#193648'; ctx.font = '18px sans-serif'; ctx.fillText(view.label, x+20, y+500);
      });
      canvas.toBlob(blob => { if (blob) download(blob, `${this.record.record_id}-views.png`); }, 'image/png');
    },
  },
};
</script>

<style scoped>
.face-review { max-width: 1400px; margin: 2rem auto; padding: 0 1.25rem; color: #193648; }
.eyebrow { text-transform: uppercase; letter-spacing: .1em; font-size: .8rem; }
.notice { background: #fff4df; padding: .8rem; border-radius: 6px; }
.toolbar, .views { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0; align-items: center; }
.layout { display: grid; grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr); gap: 1.5rem; }
section, aside { min-width: 0; border: 1px solid #ccd9e0; padding: 1rem; border-radius: 8px; }
label { display: flex; flex-direction: column; gap: .4rem; padding: 0; }
input, select, button, textarea { font: inherit; max-width: 100%; box-sizing: border-box; }
button, select, input, textarea { border: 1px solid #a9bbc5; border-radius: 5px; padding: .5rem; background: white; color: inherit; }
button { cursor: pointer; } button:disabled { opacity: .5; cursor: default; }
svg { width: 100%; display: block; touch-action: none; border-radius: 6px; }
svg text { font: 11px sans-serif; fill: #173e56; paint-order: stroke; stroke: white; stroke-width: 3px; }
svg:focus-visible, button:focus-visible { outline: 3px solid #2078b0; }
aside label { margin: 1rem 0; } .error { color: #8b2418; background: #fff0ed; padding: .75rem; }
h2 { font-size: 1.2rem; margin-top: 1.5rem; }
@media(max-width: 850px) { .layout { grid-template-columns: 1fr; } }
</style>
