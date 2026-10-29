<template>
  <main class="flame-generator">
    <p class="eyebrow">MasqFit research</p>
    <h1>FLAME face generator</h1>
    <p>Explore shape combinations, save a face, then open it for landmark annotation.</p>
    <p><a href="/scripts/face_landmarks_preview.html" target="_blank" rel="noopener">Open landmark viewer</a></p>
    <p class="notice">Synthetic faces · neutral expression and pose. Parameters are combined shape directions, not named anatomical controls or age settings.</p>
    <p v-if="error" class="error" role="alert">{{ error }} <button v-if="!model" @click="connect">Reconnect</button>
      <a v-if="!model" href="/python/dimension_pipeline/FLAME_OPEN.md" target="_blank" rel="noopener">Generator setup</a></p>
    <p v-if="!model && !error" role="status">Connecting to the local generator…</p>
    <div v-if="model" class="layout">
      <section class="preview">
        <div class="row"><button v-for="view in views" :key="view.id" @click="yaw = view.yaw; pitch = view.pitch">{{ view.label }}</button></div>
        <svg v-if="record" ref="viewport" viewBox="0 0 720 480" tabindex="0" role="img" aria-label="Generated face. Drag or use arrow keys to rotate; scroll to zoom."
          @pointerdown="startDrag" @pointermove="moveDrag" @pointerup="drag = null" @pointercancel="drag = null" @lostpointercapture="drag = null"
          @keydown="rotateKey" @wheel.prevent="zoom">
          <title>FLAME shape preview</title><rect width="720" height="480" fill="#edf2f5" />
          <polygon v-for="face in faces" :key="face.index" :points="face.points" :fill="face.fill" />
        </svg>
        <p role="status">{{ pending ? 'Updating preview…' : record ? 'Drag to rotate · scroll to zoom · arrow keys rotate' : 'Preparing preview…' }}</p>
        <p v-if="record && previewKey !== parametersKey" class="notice">Showing the last successful preview. Save becomes available after the current parameters render successfully.</p>
        <div class="row"><label>Yaw {{ Math.round(yaw) }}°<input v-model.number="yaw" type="range" min="-180" max="180" /></label>
          <label>Tilt {{ Math.round(pitch) }}°<input v-model.number="pitch" type="range" min="-90" max="90" /></label><button @click="resetView">Reset view</button></div>
        <p v-if="report">Change from neutral: {{ report.rms_vertex_change_mm.toFixed(2) }} mm RMS · {{ report.vertices }} vertices</p>
        <p v-if="report?.flipped_triangles_vs_neutral" class="notice">{{ report.flipped_triangles_vs_neutral }} triangle normal reversal flags relative to neutral. These are review flags, not proof of intersections. You can save this face for review; the flags are retained with it.</p>
        <p class="hint">Shape coefficients range from −2 to +2. Start with small changes; large combinations may distort the mesh. Self-intersections, anatomical placement, physical scale, and population coverage remain unreviewed.</p>
      </section>
      <section>
        <h2>Shape parameters</h2>
        <p>All 300 identity components are available. Expression, jaw, neck, and eye pose remain zero.</p>
        <fieldset :disabled="saving">
          <div class="row"><label>Components<select v-model.number="page"><option v-for="n in 15" :key="n" :value="n-1">{{ (n-1)*20+1 }}–{{ n*20 }}</option></select></label>
            <button @click="resetParameters">Reset all to neutral</button></div>
          <div v-if="activeParameters.length" class="active-parameters"><span>Active: </span>
            <button v-for="item in activeParameters" :key="item.index" @click="page = Math.floor(item.index/20)">PC{{ item.index+1 }}: {{ item.value }}</button></div>
          <div v-for="index in shownIndices" :key="index" class="parameter">
            <label :for="`pc-${index}`">PC {{ index+1 }}</label>
            <input :id="`pc-${index}`" v-model.number="beta[index]" type="range" min="-2" max="2" step="0.05" />
            <input v-model.number="beta[index]" type="number" min="-2" max="2" step="0.05" :aria-label="`PC ${index+1} coefficient`" />
            <button @click="beta[index] = 0" :aria-label="`Reset PC ${index+1}`">↺</button>
          </div>
        </fieldset>
        <h2>Save this face</h2>
        <label>Face name<input v-model="name" maxlength="80" :disabled="saving" placeholder="e.g. Nose and jaw study 01" /></label>
        <div class="row"><button @click="saveFace" :disabled="!canSave">{{ saving ? 'Saving…' : report?.flipped_triangles_vs_neutral ? 'Save face for review' : 'Save face to library' }}</button></div>
        <p class="hint">Saved faces include the full parameter vector and mesh. Saving the same parameters again reuses the existing face and its original name.</p>
        <p v-if="saved" role="status">{{ saved.already_saved ? 'Already in library' : 'Saved' }}: <strong>{{ saved.face.name }}</strong> ·
          <a :href="saved.face.preview_url" target="_blank" rel="noopener">Open for annotation</a> · <a :href="saved.face.mesh_path" download>Download face JSON</a></p>
        <label>Restore parameters from a face JSON<input type="file" accept=".json,application/json" :disabled="saving" @change="restoreFile" /></label>
      </section>
    </div>
    <section v-if="model" class="library">
      <h2>Saved face library</h2>
      <p>Faces stay on this computer in <code>{{ model.library_directory }}</code>. Reloading this page keeps the saved library.</p>
      <button @click="refreshLibrary">Refresh library</button>
      <p v-if="!library.length">No faces saved yet.</p>
      <ul><li v-for="face in library" :key="face.id"><strong>{{ face.name }}</strong>
        <span>{{ new Date(face.created_at).toLocaleString() }}</span>
        <button @click="restoreFace(face)" :disabled="saving">Edit parameters</button>
        <a :href="face.preview_url" target="_blank" rel="noopener">Open for annotation</a>
        <a :href="face.mesh_path" download>Download face JSON</a></li></ul>
    </section>
  </main>
</template>

<script>
import views from '../../python/dimension_pipeline/assets/head_views.json';
import { projectMesh, shadedFaces, readSurfaceRecord } from './face_annotation_geometry';

const API = 'http://127.0.0.1:5181';
const validBeta = values => Array.isArray(values) && values.length === 300 && values.every(v => typeof v === 'number' && Number.isFinite(v) && Math.abs(v) <= 2);

// A development hot update replaces this component. Capture the mounted recipe
// before Vue reloads it so an unsaved face survives changes to generator code.
const previous = import.meta.hot && typeof document !== 'undefined' ? document.querySelector('.flame-generator')?.__vueParentComponent?.proxy : null;
const hotRecipe = previous ? { beta: [...previous.beta], name: previous.name, page: previous.page,
  yaw: previous.yaw, pitch: previous.pitch, scale: previous.scale, savedSignature: previous.savedSignature } : {};

export default {
  name: 'FlameFaceGenerator',
  data() { return { views, model: null, beta: Array(300).fill(0), page: 0, name: '', record: null, report: null,
    yaw: -45, pitch: 0, scale: 1, drag: null, pending: false, saving: false, error: '', saved: null, library: [],
    previewKey: '', timer: null, revision: 0, controller: null, savedSignature: JSON.stringify({ beta: Array(300).fill(0), name: '' }), ...hotRecipe }; },
  computed: {
    parametersKey() { return JSON.stringify(this.beta); },
    signature() { return JSON.stringify({ beta: this.beta, name: this.name }); },
    dirty() { return this.signature !== this.savedSignature; },
    shownIndices() { return Array.from({ length: 20 }, (_, i) => this.page*20+i); },
    activeParameters() { return this.beta.flatMap((value, index) => value !== 0 ? [{ value, index }] : []); },
    points() { return this.record ? projectMesh(this.record, this.record.preview_camera.center_mm, this.yaw, this.pitch, this.scale) : []; },
    faces() { return this.record ? shadedFaces(this.record, this.points) : []; },
    canSave() { return this.record && this.previewKey === this.parametersKey && !this.pending && !this.saving &&
      validBeta(this.beta) && this.name.trim().length > 0; },
  },
  watch: { parametersKey() { this.schedulePreview(); } },
  mounted() { window.addEventListener('beforeunload', this.beforeUnload); this.connect(); },
  beforeUnmount() { clearTimeout(this.timer); this.controller?.abort(); this.revision++; window.removeEventListener('beforeunload', this.beforeUnload); },
  methods: {
    async api(path, payload, signal) {
      const response = await fetch(API+path, { method: payload ? 'POST' : 'GET',
        ...(payload ? { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) } : {}), signal });
      const body = await response.json(); if (!response.ok) throw new Error(body.error || `Generator error ${response.status}`); return body;
    },
    async connect() {
      this.error = '';
      try { this.model = await this.api('/model'); await this.refreshLibrary(); this.schedulePreview(); }
      catch (error) { this.error = `Could not connect to the local FLAME generator. Start the generator service, then reconnect. ${error.message}`; }
    },
    schedulePreview() {
      clearTimeout(this.timer); this.controller?.abort(); const revision = ++this.revision; this.saved = null;
      if (!this.model) return;
      if (!validBeta(this.beta)) { this.pending = false; this.error = 'Every coefficient must be a number between -2 and 2.'; return; }
      this.pending = true; this.error = '';
      this.timer = setTimeout(() => this.updatePreview(revision), 250);
    },
    async updatePreview(revision) {
      const key = this.parametersKey, controller = new AbortController(); this.controller = controller;
      const timeout = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await this.api('/preview', { shape_coefficients: [...this.beta] }, controller.signal);
        if (revision !== this.revision) return;
        const record = readSurfaceRecord(response.record);
        if (!this.record) this.scale = record.preview_camera.pixels_per_mm;
        this.record = record; this.report = response.geometry_report; this.previewKey = key;
      } catch (error) { if (revision === this.revision) this.error = `Preview unavailable: ${error.message}`; }
      finally { clearTimeout(timeout); if (revision === this.revision) this.pending = false; }
    },
    async saveFace() {
      if (!this.canSave) return;
      this.saving = true; this.error = ''; const signature = this.signature;
      try {
        this.saved = await this.api('/save', { shape_coefficients: [...this.beta], name: this.name.trim() });
        this.savedSignature = signature; await this.refreshLibrary();
      } catch (error) { this.error = `Could not save face: ${error.message}`; }
      finally { this.saving = false; }
    },
    async refreshLibrary() {
      try { this.library = (await this.api('/faces')).faces; }
      catch (error) { this.error = `Could not read the library: ${error.message}`; }
    },
    resetParameters() { this.beta = Array(300).fill(0); },
    restoreFace(face) {
      if (this.dirty && !window.confirm('Replace the current unsaved parameters with this saved face?')) return;
      this.beta = [...face.shape_coefficients]; this.name = face.name; this.savedSignature = this.signature;
    },
    async restoreFile(event) {
      const file = event.target.files[0]; if (!file) return;
      this.error = '';
      try {
        if (file.size > 5*1024*1024) throw new Error('Choose a face JSON smaller than 5 MB.');
        const record = JSON.parse(await file.text()), generation = record.generation;
        if (record.source?.model_sha256 !== this.model.model_sha256 || generation?.method !== 'neutral_linear_shape_basis' ||
          generation.source_units !== this.model.source_units || generation.source_axes?.x !== this.model.source_x ||
          generation.pose !== 'zero' || generation.expression !== 'zero' || !validBeta(generation.shape_coefficients)) {
          throw new Error('Choose a neutral face from the same FLAME model, source units and axes.');
        }
        if (this.dirty && !window.confirm('Replace the current unsaved parameters with this face?')) return;
        this.beta = [...generation.shape_coefficients]; this.name = typeof generation.display_name === 'string' ? generation.display_name.slice(0, 80) : file.name.replace(/\.json$/i, '').slice(0, 80);
        // Recompute from the local model; imported mesh coordinates are never trusted.
      } catch (error) { this.error = `Could not restore parameters: ${error.message}`; }
      finally { event.target.value = ''; }
    },
    beforeUnload(event) { if (this.dirty) { event.preventDefault(); event.returnValue = ''; } },
    resetView() { this.yaw = -45; this.pitch = 0; this.scale = this.record?.preview_camera.pixels_per_mm || 1; },
    startDrag(event) {
      if (event.button !== 0 || event.isPrimary === false) return;
      event.currentTarget.focus({ preventScroll: true }); event.currentTarget.setPointerCapture(event.pointerId);
      this.drag = { id: event.pointerId, x: event.clientX, y: event.clientY, yaw: this.yaw, pitch: this.pitch };
    },
    moveDrag(event) {
      if (!this.drag || this.drag.id !== event.pointerId) return;
      this.yaw = ((this.drag.yaw+(event.clientX-this.drag.x)*.4+540)%360)-180;
      this.pitch = Math.max(-90, Math.min(90, this.drag.pitch+(event.clientY-this.drag.y)*.4));
    },
    zoom(event) { this.scale = Math.max(.5, Math.min(5, this.scale*Math.exp(-Math.sign(event.deltaY)*.1))); },
    rotateKey(event) {
      if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return;
      const steps = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5] };
      if (!steps[event.key]) return;
      event.preventDefault(); this.yaw = ((this.yaw+steps[event.key][0]+540)%360)-180;
      this.pitch = Math.max(-90, Math.min(90, this.pitch+steps[event.key][1]));
    },
  },
};
</script>

<style scoped>
.flame-generator { max-width: 1400px; margin: 2rem auto; padding: 0 1.25rem; color: #193648; }
.eyebrow { text-transform: uppercase; letter-spacing: .1em; font-size: .8rem; }
.notice { background: #fff4df; padding: .8rem; border-radius: 6px; }
.error { color: #8b2418; background: #fff0ed; padding: .8rem; overflow-wrap: anywhere; }
.hint { font-size: .9rem; }
.layout { display: grid; grid-template-columns: minmax(0, 3fr) minmax(340px, 2fr); gap: 1.5rem; }
section { min-width: 0; border: 1px solid #ccd9e0; padding: 1rem; border-radius: 8px; }
.preview { position: sticky; top: 1rem; align-self: start; max-height: calc(100vh - 2rem); overflow-y: auto; }
.row { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0; align-items: center; }
label { display: flex; flex-direction: column; gap: .4rem; min-width: 0; }
input, select, button { font: inherit; max-width: 100%; box-sizing: border-box; }
input, select, button { border: 1px solid #a9bbc5; border-radius: 5px; padding: .45rem; background: white; color: inherit; }
button { cursor: pointer; } button:disabled { opacity: .5; cursor: default; }
fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
.parameter { display: grid; grid-template-columns: 3.2rem minmax(50px, 1fr) 5rem 2.3rem; gap: .5rem; align-items: center; margin: .65rem 0; }
.parameter input[type=range] { width: 100%; padding: 0; }
.parameter input[type=number] { width: 100%; }
.active-parameters { display: flex; flex-wrap: wrap; gap: .3rem; max-height: 8rem; overflow-y: auto; }
.active-parameters button { font-size: .85rem; }
svg { width: 100%; display: block; touch-action: none; border-radius: 6px; }
svg:focus-visible, button:focus-visible { outline: 3px solid #2078b0; }
.library { margin-top: 1.5rem; }
.library ul { padding: 0; list-style: none; }
.library li { display: flex; flex-wrap: wrap; gap: .75rem; align-items: center; padding: .75rem 0; border-bottom: 1px solid #ccd9e0; }
.library strong, code { overflow-wrap: anywhere; }
h2 { font-size: 1.2rem; }
@media(max-width: 850px) { .layout { grid-template-columns: 1fr; } .preview { position: static; max-height: none; overflow: visible; } }
</style>
