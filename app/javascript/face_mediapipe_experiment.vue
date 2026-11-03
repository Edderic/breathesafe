<template>
  <section class="mp-experiment">
    <div class="actions"><h2>MediaPipe experiment</h2><button @click="close">Back to annotations</button></div>
    <p>Read-only pilot · current shaded geometry · candidate correspondences chosen by you. Image points are projected onto the visible mesh; MediaPipe depth is not used as millimeters.</p>
    <p v-if="error" role="alert" class="error">{{ error }}</p>
    <div class="actions">
      <label>Capture preset<select v-model="preset"><option v-for="view in views" :key="view.id" :value="view.id">{{ view.label }}</option></select></label>
      <button @click="run(false)" :disabled="busy">Run selected view</button><button @click="run(true)" :disabled="busy">Run all seven views</button>
      <button v-if="busy" @click="cancel">Cancel</button>
      <button @click="exportReport" :disabled="busy || !results.length">Download experiment JSON</button>
      <label>Reload experiment<input type="file" accept=".json" @change="importReport" :disabled="busy" /></label>
    </div>
    <p role="status">{{ progress }} {{ results.length }} captured views · {{ results.filter(r => r.status === 'ok').length }} detections · {{ results.filter(r => !['ok', 'pending'].includes(r.status)).length }} failed/cancelled views.</p>
    <p v-if="provenance" class="hint">MediaPipe {{ provenance.sdk_version }} · CPU · IMAGE mode · model SHA-256 <code>{{ provenance.model_sha256 }}</code></p>
    <div class="actions"><label>Observation filter<select v-model="filterMode"><option value="conservative">Conservative view filter</option><option value="raw">Raw baseline (no filtering)</option></select></label>
      <label class="check"><input type="checkbox" v-model="showRejected" /> Show excluded predictions in gray</label></div>
    <p class="hint">Experimental heuristic: frontal yaw ≤15° retains both sides; yaw 15–60° retains the subject's near side and excludes the central band. Tilt over 20° and yaw over 60° are excluded. Regions come from a fixed canonical index map, not your manual labels. Passing this rule does not prove visibility or accuracy.</p>
    <div class="actions"><button v-for="result in results" :key="result.view_id" @click="selectedView = result.view_id">{{ result.view_id }}: {{ result.status }}</button></div>
    <div class="panes">
      <section>
        <h3>Captured image and 2D detections</h3>
        <svg v-if="selected" ref="imageViewport" viewBox="0 0 720 480" role="img" aria-label="Captured image with numbered MediaPipe detections" @click="pickImagePoint">
          <image v-if="imageUrl" :href="imageUrl" width="720" height="480" />
          <g v-for="mark in imageMarks" :key="mark.index" pointer-events="none"><circle :cx="mark.x" :cy="mark.y" :r="mark.index === selectedIndex ? 5 : 1.6" :fill="mark.excluded ? '#7b858d' : mark.index === selectedIndex ? '#e95d21' : '#0072b2'" :opacity="mark.excluded ? .5 : 1" />
            <text v-if="showNumbers || mark.index === selectedIndex" :x="mark.x+4" :y="mark.y-4">{{ mark.index }}</text></g>
        </svg>
        <p v-else>Choose a preset and run detection.</p>
        <div class="actions"><label class="check"><input type="checkbox" v-model="showNumbers" /> Show all numbers</label>
          <button @click="downloadImage" :disabled="!selected">Download captured PNG</button>
          <label v-if="selected">Restore original PNG<input type="file" accept="image/png" @change="restoreImage" /></label></div>
        <p v-if="selected && !imageUrl" class="hint">The original image is unavailable. Restore its exported PNG; the checksum must match this view.</p>
        <p v-if="selected">{{ selected.detections.filter(d => d.status === 'ok').length }} raw surface hits · {{ selected.detections.filter(d => d.observation_status === 'accepted').length }} accepted observations / {{ selected.detections.length }} detections. {{ selected.error || '' }}</p>
        <p v-if="selectedDetection">Selected #{{ selectedIndex }} · canonical {{ selectedDetection.region }} region · {{ selectedDetection.observation_status }}<span v-if="selectedDetection.rejection_reason">: {{ selectedDetection.rejection_reason }}</span>.</p>
        <p class="hint">Click near a detected dot to select its index. Blue points can be inferred or occluded features; a ray hit alone does not establish anatomical correspondence.</p>
      </section>
      <section>
        <h3>Projected points on the 3D face</h3>
        <svg ref="meshViewport" viewBox="0 0 720 480" tabindex="0" role="img" aria-label="Projected detections and manual reference on the mesh; drag or arrow keys rotate, scroll zooms"
          @pointerdown="startDrag" @pointermove="moveDrag" @pointerup="drag = null" @pointercancel="drag = null" @lostpointercapture="drag = null" @keydown="rotateKey" @wheel.prevent="zoom">
          <rect width="720" height="480" fill="#edf2f5" /><polygon v-for="face in meshFaces" :key="face.index" :points="face.points" :fill="face.fill" />
          <g v-for="mark in meshMarks" :key="mark.id" pointer-events="none"><circle :cx="mark.x" :cy="mark.y" :r="mark.selected ? 5 : 1.8" :fill="mark.color" :opacity="mark.excluded ? .4 : 1" stroke="white" :stroke-width="mark.selected ? 1 : .3" />
            <text v-if="mark.selected" :x="mark.x+6" :y="mark.y-5">{{ mark.label }}</text></g>
        </svg>
        <div class="actions"><button @click="useCaptureView" :disabled="!selected">Use capture view</button>
          <label class="check"><input type="checkbox" v-model="through" /> Show points through head</label>
          <label class="check"><input type="checkbox" v-model="allViews" /> Selected index across all views</label></div>
        <p class="hint">Blue: accepted observations. Orange: selected accepted index. Gray: excluded predictions (when enabled). Purple: selected manual reference. Filtering uses the original capture camera, not this inspection rotation.</p>
      </section>
    </div>
    <div class="panes">
      <section>
        <h3>Candidate correspondences</h3>
        <label>MediaPipe index<input v-model.number="selectedIndex" type="number" min="0" max="477" /></label>
        <label>Research landmark<select v-model="namedLandmark"><option v-for="label in labels" :key="label.id" :value="label.id">{{ label.name }}</option></select></label>
        <div class="actions"><button @click="assignMapping" :disabled="!validIndex">Assign candidate match</button><button @click="removeMapping">Unmap this landmark</button>
          <button @click="exportMappings">Download mappings</button><label>Load mappings<input type="file" accept=".json" @change="importMappings" /></label></div>
        <p>Current match: {{ mappings[namedLandmark] === undefined ? 'unmapped' : `MediaPipe #${mappings[namedLandmark]}` }}. No anatomical matches are assumed. Ear and other unsupported landmarks can stay unmapped.</p>
        <ul><li v-for="(index, name) in mappings" :key="name"><button @click="namedLandmark = name; selectedIndex = index">{{ name }} ↔ #{{ index }}</button></li></ul>
        <p v-if="indexSummary">Index #{{ selectedIndex }}: {{ indexSummary.surface_hits }} raw surface hits · {{ indexSummary.valid }} accepted / {{ results.length }} attempted views.<br />
          Accepted-view 3D pairwise median: {{ mm(indexSummary.median_mm) }} · maximum: {{ mm(indexSummary.maximum_mm) }}.<br />
          Raw baseline pairwise median: {{ mm(indexSummary.raw_dispersion.median_mm) }} · maximum: {{ mm(indexSummary.raw_dispersion.maximum_mm) }}.</p>
        <p class="hint">Fewer accepted observations can reduce dispersion without improving accuracy. One accepted view gives no pairwise estimate. Across-view agreement is not anatomical accuracy.</p>
      </section>
      <section>
        <h3>Manual references</h3>
        <label>Load reference annotation exports<input type="file" multiple accept=".json" @change="importReferences" /></label>
        <div v-for="reference in localReferences" :key="reference.id" class="actions"><label class="check"><input type="checkbox" v-model="reference.enabled" /> {{ reference.label }}</label></div>
        <label>Reference displayed in 3D<select v-model="primaryReference"><option v-for="reference in enabledReferences" :key="reference.id" :value="reference.id">{{ reference.label }}</option></select></label>
        <p v-if="!localReferences.length">Load annotations for this exact mesh to compare mapped landmarks.</p>
        <p class="hint">Errors below are straight-line 3D distances in model mm. Each annotation set stays separate; none is averaged or declared ground truth. Occluded reference points and failed detections remain explicit statuses.</p>
        <div class="scroll-table"><table><caption>{{ namedLandmark }} · candidate #{{ mappings[namedLandmark] ?? 'unmapped' }}</caption>
          <thead><tr><th>View</th><th>Reference</th><th>Filtered result</th><th>Raw baseline</th></tr></thead><tbody><tr v-for="row in selectedRows" :key="`${row.view_id}:${row.reference_id}`"><td>{{ row.view_id }}</td><td>{{ row.reference_label }}</td><td>{{ row.status === 'ok' ? mm(row.distance_mm) : row.status === 'filtered_out' ? 'filtered: '+row.reason : row.status }}</td><td>{{ row.raw_status === 'ok' ? mm(row.raw_distance_mm) : row.raw_status }}</td></tr></tbody></table></div>
      </section>
    </div>
  </section>
</template>

<script>
import views from '../../python/dimension_pipeline/assets/head_views.json';
import { projectPoint } from './dimension_fixture_geometry';
import { projectMesh, shadedFaces, pickSurface, attachmentPoint, meshFingerprint, validateAnnotations } from './face_annotation_geometry';
import { captureFace, captureVersion, projectDetection, comparisonRows, distanceSummary, validateMappings, validateExperiment } from './face_mediapipe_geometry';
import { filterResults, viewFilterPolicy, validateViewFilter } from './face_mediapipe_filter';

const clone = value => JSON.parse(JSON.stringify(value));
const download = (blob, name) => { const url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 10000); };
const jsonDownload = (value, name) => download(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }), name);
const sha256 = async bytes => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), x => x.toString(16).padStart(2, '0')).join('');
export default {
  name: 'FaceMediapipeExperiment', props: ['record', 'references', 'labels', 'frame'], emits: ['close'],
  data() { return { views, results: [], provenance: null, preset: 'front', selectedView: '', selectedIndex: 1, namedLandmark: 'pronasale', mappings: {},
    filterMode: 'conservative', showRejected: false,
    localReferences: clone(this.references), primaryReference: this.references[0]?.id || '', busy: false, progress: '', error: '', showNumbers: false,
    through: false, allViews: false, yaw: -45, pitch: 0, scale: this.frame.pixels_per_mm, drag: null,
    worker: null, sequence: 0, waiter: null, revision: 0, images: {}, imageUrl: '', urls: {}, fingerprint: '' }; },
  computed: {
    filteredResults() { return filterResults(this.results, this.filterMode); },
    selected() { return this.filteredResults.find(r => r.view_id === this.selectedView); },
    selectedDetection() { return this.selected?.detections.find(d => d.index === this.selectedIndex); },
    validIndex() { return Number.isInteger(this.selectedIndex) && this.selectedIndex >= 0 && this.selectedIndex < 478; },
    enabledReferences() { return this.localReferences.filter(r => r.enabled); },
    imageMarks() { return (this.selected?.raw_landmarks || []).flatMap((p, index) => {
      const excluded = this.selected.detections[index]?.observation_status !== 'accepted';
      return (this.showRejected || !excluded) && Number.isFinite(p.x) && Number.isFinite(p.y) && p.x >= 0 && p.x <= 1 && p.y >= 0 && p.y <= 1 ? [{ x: p.x*720, y: p.y*480, index, excluded }] : [];
    }); },
    meshPoints() { return projectMesh(this.record, this.frame.center_mm, this.yaw, this.pitch, this.scale); },
    meshFaces() { return shadedFaces(this.record, this.meshPoints); },
    meshMarks() {
      const marks = (this.allViews ? this.filteredResults : this.selected ? [this.selected] : []).flatMap(result => result.detections.filter(d => d.status === 'ok' && (this.showRejected || d.observation_status === 'accepted') && (!this.allViews || d.index === this.selectedIndex)).map(d => ({ id: result.view_id+':'+d.index, point: d.point_mm,
        color: d.observation_status !== 'accepted' ? '#7b858d' : d.index === this.selectedIndex ? '#e95d21' : '#0072b2', excluded: d.observation_status !== 'accepted', selected: d.index === this.selectedIndex, label: '#'+d.index+(this.allViews ? ' '+result.view_id : '') })));
      const reference = this.enabledReferences.find(r => r.id === this.primaryReference), annotation = reference?.landmarks[this.namedLandmark];
      if (annotation) marks.push({ id: 'manual', point: attachmentPoint(this.record, annotation.attachment), color: '#a23a91', selected: true, label: reference.label });
      return marks.flatMap(mark => { const p = projectPoint(mark.point, this.frame.center_mm, this.yaw, this.pitch, this.scale);
        const hit = this.through ? null : pickSurface(this.record, this.meshPoints, p.x, p.y);
        return this.through || (hit && Math.abs(hit.depth-p.depth) < .1) ? [{ ...mark, ...p }] : []; });
    },
    rows() { return comparisonRows(this.record, this.filteredResults, this.mappings, this.enabledReferences); },
    rawRows() { return comparisonRows(this.record, this.results, this.mappings, this.enabledReferences); },
    selectedRows() { return this.rows.flatMap((row, index) => row.landmark === this.namedLandmark ? [{ ...row, raw_status: this.rawRows[index].status, raw_distance_mm: this.rawRows[index].distance_mm }] : []); },
    summaries() { return Array.from({ length: 478 }, (_, index) => {
      const points = [], rawPoints = [], statuses = {};
      for (const result of this.filteredResults) {
        const detection = result.detections[index], status = result.status !== 'ok' ? result.status : !detection || detection.status !== 'ok' ? detection?.status || 'missing_detection' : detection.observation_status === 'accepted' ? 'accepted' : detection.rejection_reason;
        statuses[status] = (statuses[status] || 0)+1;
        if (result.status === 'ok' && detection?.status === 'ok') rawPoints.push(detection.point_mm);
        if (status === 'accepted') points.push(detection.point_mm);
      }
      return { index, attempted_views: this.results.length, surface_hits: rawPoints.length, accepted_views: points.length, rejected_views: rawPoints.length-points.length,
        valid: points.length, statuses, raw_dispersion: distanceSummary(rawPoints), ...distanceSummary(points) };
    }); },
    indexSummary() { return this.summaries[this.selectedIndex]; },
  },
  watch: {
    namedLandmark(value) { if (this.mappings[value] !== undefined) this.selectedIndex = this.mappings[value]; },
    references(value) { this.localReferences = [...clone(value), ...this.localReferences.filter(r => r.id.startsWith('file:'))]; this.primaryReference = this.localReferences.find(r => r.id === this.primaryReference)?.id || this.localReferences[0]?.id || ''; },
    selectedView() { this.updateImage(); },
    record() { this.cancel(); this.clearImages(); this.results = []; this.provenance = null; this.selectedView = ''; this.localReferences = clone(this.references); this.primaryReference = this.localReferences[0]?.id || ''; this.fingerprint = ''; this.error = ''; this.progress = ''; this.scale = this.frame.pixels_per_mm; },
  },
  beforeUnmount() { this.cancel(); this.clearImages(); },
  methods: {
    mm(value) { return Number.isFinite(value) ? value.toFixed(2)+' mm' : '—'; },
    clearImages() { Object.values(this.urls).forEach(URL.revokeObjectURL); this.urls = {}; this.images = {}; this.imageUrl = ''; },
    async hash() { if (this.fingerprint) return this.fingerprint; const record = this.record, fingerprint = await meshFingerprint(record); if (record === this.record) this.fingerprint = fingerprint; return fingerprint; },
    camera(view) { return { ...clone(this.frame), ...view, projection: 'orthographic', width: 720, height: 480, mirrored: false, distortion: 'none', version: '1.0.0' }; },
    callWorker(type, extra = {}, transfer = []) {
      const worker = this.worker;
      if (!worker) return Promise.reject(Error('MediaPipe worker stopped. Run the experiment again.'));
      return new Promise((resolve, reject) => {
        const id = ++this.sequence, timer = setTimeout(() => {
          if (this.waiter?.id !== id) return;
          this.waiter = null; reject(Error('MediaPipe worker timed out. Run the experiment again.')); worker.terminate(); if (this.worker === worker) this.worker = null;
        }, type === 'init' ? 60000 : 20000);
        this.waiter = { id, resolve, reject, timer };
        try { worker.postMessage({ id, type, ...extra }, transfer); }
        catch (error) { clearTimeout(timer); this.waiter = null; reject(error); }
      });
    },
    async initWorker() {
      this.worker = new Worker('/mediapipe/face_experiment_worker.js');
      this.worker.onmessage = event => { const waiter = this.waiter; if (!waiter || waiter.id !== event.data.id) return; clearTimeout(waiter.timer); this.waiter = null; event.data.error ? waiter.reject(Error(event.data.error)) : waiter.resolve(event.data); };
      this.worker.onerror = event => { if (this.waiter) { clearTimeout(this.waiter.timer); this.waiter.reject(Error(event.message || 'Worker failed')); this.waiter = null; } };
      this.provenance = (await this.callWorker('init')).provenance;
    },
    cancel() {
      const wasBusy = this.busy;
      this.revision++; this.worker?.terminate(); this.worker = null;
      if (this.waiter) { clearTimeout(this.waiter.timer); this.waiter.reject(Error('Cancelled')); this.waiter = null; }
      for (const result of this.results) if (result.status === 'pending') result.status = 'cancelled';
      this.busy = false;
      if (wasBusy) this.progress = 'Cancelled. Completed captures are retained; remaining presets were not attempted.';
    },
    close() { this.cancel(); this.$emit('close'); },
    async run(all) {
      if (this.busy) return; this.cancel(); const revision = this.revision, record = this.record;
      const chosen = all ? views : views.filter(view => view.id === this.preset);
      this.busy = true; this.error = ''; this.results = []; this.selectedView = ''; this.clearImages(); this.progress = 'Initializing local MediaPipe…';
      try {
        await this.initWorker(); if (revision !== this.revision) return;
        await this.hash();
        for (const view of chosen) {
          if (revision !== this.revision) return;
          this.progress = 'Processing '+view.label+'…'; const camera = this.camera(view), canvas = document.createElement('canvas');
          const projected = captureFace(record, camera, canvas);
          const png = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
          if (!png) throw Error('Could not capture PNG');
          const checksum = await sha256(await png.arrayBuffer());
          if (revision !== this.revision) return;
          this.images[view.id] = png; this.urls[view.id] = URL.createObjectURL(png);
          const result = { view_id: view.id, camera, capture_version: captureVersion, image_sha256: checksum, status: 'pending', raw_landmarks: [], detections: [] };
          this.results.push(result); this.selectedView = view.id;
          try {
            const image = await createImageBitmap(canvas), response = await this.callWorker('detect', { image }, [image]);
            if (revision !== this.revision) { result.status = 'cancelled'; return; }
            result.raw_landmarks = response.landmarks.map(p => ({ x: Number.isFinite(p.x) ? p.x : null, y: Number.isFinite(p.y) ? p.y : null, z: Number.isFinite(p.z) ? p.z : null })); result.elapsed_ms = response.elapsed_ms;
            for (let start = 0; start < result.raw_landmarks.length; start += 32) {
              if (revision !== this.revision) { result.status = 'cancelled'; return; }
              result.detections.push(...result.raw_landmarks.slice(start, start+32).map((p, i) => projectDetection(record, projected, p, start+i)));
              await new Promise(resolve => setTimeout(resolve, 0));
            }
            result.status = result.raw_landmarks.length ? 'ok' : 'no_detection';
          } catch (error) { result.status = revision === this.revision ? 'error' : 'cancelled'; result.error = error.message; if (revision !== this.revision) return; }
          // Results are plain local objects; replace the array to notify Vue.
          this.results = [...this.results]; this.updateImage();
        }
        this.progress = 'Finished. Failures are retained in coverage counts.';
      } catch (error) { if (revision === this.revision) { this.error = error.message; this.progress = 'Experiment could not start.'; } }
      finally { if (revision === this.revision) { this.busy = false; this.worker?.terminate(); this.worker = null; } }
    },
    updateImage() { this.imageUrl = this.urls[this.selectedView] || ''; },
    pickImagePoint(event) { const p = this.$refs.imageViewport.createSVGPoint(); p.x = event.clientX; p.y = event.clientY; const q = p.matrixTransform(this.$refs.imageViewport.getScreenCTM().inverse());
      const nearest = [...this.imageMarks].sort((a, b) => Math.hypot(a.x-q.x, a.y-q.y)-Math.hypot(b.x-q.x, b.y-q.y))[0]; if (nearest && Math.hypot(nearest.x-q.x, nearest.y-q.y) < 18) this.selectedIndex = nearest.index; },
    assignMapping() { if (this.validIndex) this.mappings = { ...this.mappings, [this.namedLandmark]: this.selectedIndex }; },
    removeMapping() { const next = { ...this.mappings }; delete next[this.namedLandmark]; this.mappings = next; },
    exportMappings() { jsonDownload({ mapping_version: '1.0.0', status: 'candidate', mappings: this.mappings }, 'mediapipe-candidate-mappings.json'); },
    async importMappings(event) { try { const file = event.target.files[0]; if (!file) return; if (file.size > 100000) throw Error('Mapping file too large'); const bundle = JSON.parse(await file.text()); if (bundle.mapping_version !== '1.0.0') throw Error('Unsupported mapping version'); this.mappings = validateMappings(bundle.mappings, this.labels.map(l => l.id)); this.error = ''; } catch (error) { this.error = error.message; } finally { event.target.value = ''; } },
    async importReferences(event) {
      const files = [...event.target.files], record = this.record, revision = this.revision;
      try { if (files.length+this.localReferences.length > 11 || files.reduce((n, f) => n+f.size, 0) > 20*1024*1024) throw Error('Use at most 11 references including the draft, and 20 MB per batch');
        const fingerprint = await meshFingerprint(record), additions = [];
        for (const file of files) { if (file.size > 5*1024*1024) throw Error('Reference exceeds 5 MB'); const bundle = JSON.parse(await file.text()); const landmarks = validateAnnotations(bundle, record, fingerprint, this.labels.map(l => l.id)); additions.push({ id: 'file:'+crypto.randomUUID(), label: file.name, enabled: true, landmarks }); }
        if (this.record !== record || this.revision !== revision) return; this.localReferences.push(...additions); this.primaryReference ||= this.localReferences[0]?.id || ''; this.error = '';
      } catch (error) { this.error = error.message; } finally { event.target.value = ''; }
    },
    async exportReport() {
      const record = this.record;
      try { const fingerprint = await this.hash(); if (record !== this.record) return;
        jsonDownload({ experiment_version: '1.1.0', record_id: record.record_id, topology_id: record.topology_id, mesh_sha256: fingerprint, units: 'mm',
        created_at: new Date().toISOString(), provenance: this.provenance, renderer: captureVersion, mappings: this.mappings,
        view_filter: { ...viewFilterPolicy, mode: this.filterMode },
        references: this.localReferences, results: this.filteredResults, summaries: this.summaries, comparisons: this.rows, raw_comparisons: this.rawRows,
        interpretation: 'Candidate correspondences; acceptance is a view heuristic, not proven visibility. Manual references never determine acceptance. Distances are Euclidean model mm.' }, record.record_id+'-mediapipe-experiment.json'); } catch (error) { this.error = error.message; }
    },
    async importReport(event) {
      if (this.busy) return; const record = this.record, revision = this.revision;
      try { const file = event.target.files[0]; if (!file) return; if (file.size > 10*1024*1024) throw Error('Experiment exceeds 10 MB'); const fingerprint = await meshFingerprint(record);
        const bundle = validateExperiment(JSON.parse(await file.text()), record, fingerprint, this.labels.map(l => l.id));
        const filterMode = validateViewFilter(bundle.view_filter);
        const refs = (bundle.references || []).map(reference => ({ id: reference.id, label: reference.label, enabled: !!reference.enabled,
          landmarks: validateAnnotations({ annotation_version: '1.0.0', record_id: record.record_id, topology_id: record.topology_id, mesh_sha256: fingerprint, units: 'mm', review_status: 'draft', landmarks: reference.landmarks }, record, fingerprint, this.labels.map(l => l.id)) }));
        if (refs.length > 11 || new Set(refs.map(r => r.id)).size !== refs.length || refs.some(r => typeof r.id !== 'string' || typeof r.label !== 'string')) throw Error('Invalid reference identities');
        const results = [], images = {};
        for (const item of bundle.results) {
          const canvas = document.createElement('canvas'), points = captureFace(record, item.camera, canvas);
          results.push({ ...item, detections: item.raw_landmarks.map((p, i) => projectDetection(record, points, p, i)) });
          if (item.capture_version === captureVersion) { const png = await new Promise(resolve => canvas.toBlob(resolve, 'image/png')); if (png && await sha256(await png.arrayBuffer()) === item.image_sha256) images[item.view_id] = png; }
        }
        if (revision !== this.revision || record !== this.record) return;
        this.cancel(); this.clearImages(); this.fingerprint = fingerprint; this.results = results; this.localReferences = refs; this.primaryReference = refs[0]?.id || ''; this.mappings = { ...bundle.mappings }; this.provenance = bundle.provenance; this.filterMode = filterMode;
        this.images = images; this.urls = Object.fromEntries(Object.entries(images).map(([id, image]) => [id, URL.createObjectURL(image)]));
        this.selectedView = results[0]?.view_id || ''; this.updateImage(); this.error = ''; this.progress = 'Reloaded results; projections and comparisons recalculated. '+Object.keys(images).length+' of '+results.length+' PNGs reproduced with matching checksums; unmatched images need their original PNG.';
      } catch (error) { this.error = error.message; } finally { event.target.value = ''; }
    },
    async downloadImage() {
      if (!this.selected) return;
      const result = this.selected;
      try { let png = this.images[result.view_id]; if (!png) { if (result.capture_version !== captureVersion) throw Error('Renderer version differs; use the original exported PNG.'); const canvas = document.createElement('canvas'); captureFace(this.record, result.camera, canvas); png = await new Promise(resolve => canvas.toBlob(resolve, 'image/png')); if (!png || await sha256(await png.arrayBuffer()) !== result.image_sha256) throw Error('Regenerated PNG differs from the original checksum. Use the original PNG.'); }
        download(png, this.record.record_id+'-'+result.view_id+'.png');
      } catch (error) { this.error = error.message; }
    },
    async restoreImage(event) {
      const selected = this.selected, revision = this.revision;
      try { const file = event.target.files[0]; if (!file || !selected) return;
        if (file.size > 10*1024*1024 || await sha256(await file.arrayBuffer()) !== selected.image_sha256) throw Error('PNG does not match the selected capture checksum.');
        const bitmap = await createImageBitmap(file), valid = bitmap.width === 720 && bitmap.height === 480; bitmap.close(); if (!valid) throw Error('Expected a 720 × 480 PNG.');
        if (revision !== this.revision || selected !== this.selected) return;
        if (this.urls[selected.view_id]) URL.revokeObjectURL(this.urls[selected.view_id]); this.images[selected.view_id] = file; this.urls[selected.view_id] = URL.createObjectURL(file); this.updateImage(); this.error = '';
      } catch (error) { this.error = error.message; } finally { event.target.value = ''; }
    },
    useCaptureView() { const camera = this.selected?.camera; if (camera) { this.yaw = camera.yaw; this.pitch = camera.pitch; this.scale = camera.pixels_per_mm; } },
    startDrag(event) { if (event.button !== 0 || event.isPrimary === false) return; event.currentTarget.focus(); event.currentTarget.setPointerCapture(event.pointerId); this.drag = { id: event.pointerId, x: event.clientX, y: event.clientY, yaw: this.yaw, pitch: this.pitch }; },
    moveDrag(event) { if (!this.drag || this.drag.id !== event.pointerId) return; this.yaw = ((this.drag.yaw+(event.clientX-this.drag.x)*.4+540)%360)-180; this.pitch = Math.max(-90, Math.min(90, this.drag.pitch+(event.clientY-this.drag.y)*.4)); },
    zoom(event) { this.scale = Math.max(.5, Math.min(5, this.scale*Math.exp(-Math.sign(event.deltaY)*.1))); },
    rotateKey(event) { if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return; const step = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5] }[event.key]; if (!step) return; event.preventDefault(); this.yaw = ((this.yaw+step[0]+540)%360)-180; this.pitch = Math.max(-90, Math.min(90, this.pitch+step[1])); },
  },
};
</script>

<style scoped>
.mp-experiment { color: #193648; padding: 1rem; border: 1px solid #ccd9e0; border-radius: 8px; }
.actions { display: flex; align-items: center; flex-wrap: wrap; gap: .6rem; margin: .8rem 0; }
.panes { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 1rem; margin: 1rem 0; }
section { min-width: 0; } h2, h3 { font-size: 1.2rem; }
label { display: flex; flex-direction: column; gap: .3rem; min-width: 0; } .check { flex-direction: row; align-items: center; }
button, input, select { font: inherit; max-width: 100%; box-sizing: border-box; padding: .4rem; border: 1px solid #a9bbc5; border-radius: 4px; background: white; color: inherit; }
button { cursor: pointer; } button:disabled { opacity: .5; cursor: default; }
svg { width: 100%; display: block; touch-action: none; background: #edf2f5; } svg text { font: 10px sans-serif; paint-order: stroke; stroke: white; stroke-width: 2px; }
.hint { font-size: .9rem; overflow-wrap: anywhere; } .error { background: #fff0ed; padding: .7rem; color: #8b2418; }
.scroll-table { overflow-x: auto; } table { width: 100%; border-collapse: collapse; font-size: .9rem; } th, td { padding: .4rem; text-align: left; border-bottom: 1px solid #ccd9e0; }
@media(max-width: 850px) { .panes { grid-template-columns: 1fr; } }
</style>
