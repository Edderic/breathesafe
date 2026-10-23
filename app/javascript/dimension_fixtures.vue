<template>
  <main class="fixture-viewer">
    <header>
      <p class="eyebrow">MasqFit research</p>
      <h1>Dimension fixture viewer</h1>
      <p>Explore the reference geometry, landmarks, and measurement paths. These starter fixtures are analytic shapes, not face scans.</p>
    </header>

    <div class="toolbar">
      <label>Fixture
        <select v-model="chosen" @change="chooseFixture">
          <option v-for="item in examples" :key="item.id" :value="item.id">{{ item.label }}</option>
          <option v-if="custom" value="custom">{{ customName }}</option>
        </select>
      </label>
      <label class="file-label">Open fixture JSON
        <input type="file" accept=".json,application/json" @change="openFile" />
      </label>
      <span class="local-note">Files stay in your browser.</span>
    </div>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div class="viewer-layout">
      <section class="geometry-panel" aria-label="Interactive geometry">
        <div class="view-buttons">
          <button type="button" @click="setView(0, 0)">Front</button>
          <button type="button" @click="setView(90, 0)">Side</button>
          <button type="button" @click="setView(0, 90)">Top</button>
          <button type="button" @click="setView(-30, 22)">3D</button>
          <button type="button" @click="fitView">Fit geometry</button>
        </div>
        <svg viewBox="0 0 720 480" tabindex="0" role="img"
          aria-label="Rotatable fixture. Drag to rotate, use arrow keys or the rotation sliders. Scroll to zoom."
          @pointerdown="startDrag" @pointermove="moveDrag" @pointerup="endDrag" @pointercancel="endDrag"
          @lostpointercapture="endDrag" @keydown="rotateKey" @wheel.prevent="zoomWheel">
          <title>{{ record.record_id }} — reference geometry</title>
          <defs>
            <pattern id="fixture-grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#dce5e9" stroke-width="0.7" />
            </pattern>
          </defs>
          <rect width="720" height="480" fill="#f5f8fa" />
          <rect width="720" height="480" fill="url(#fixture-grid)" />
          <g v-if="overlay" fill="none" stroke="#7c8c96" stroke-width="1.5" stroke-dasharray="5 5">
            <polygon v-for="(face, i) in base.faces" :key="i" :points="polygon(base.vertices, face)" />
          </g>
          <polygon v-for="face in sortedFaces" :key="face.index" :points="face.points"
            fill="#a9cfdd" fill-opacity="0.6" :stroke="wireframe ? '#507d90' : 'none'" stroke-width="1.5" />
          <polyline v-if="selected" :points="selected.points.map(pointString).join(' ')"
            fill="none" stroke="#c74d15" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
          <g v-for="(point, name) in geometry.landmarks" :key="name" @click="focused = name">
            <circle :cx="project(point).x" :cy="project(point).y" :r="focused === name ? 7 : 5"
              fill="#173e56" stroke="white" stroke-width="2"><title>{{ name }}: {{ coordinates(point) }} mm</title></circle>
            <text v-if="labels" :x="project(point).x + 9" :y="project(point).y - 9" class="landmark-label">{{ humanize(name) }}</text>
          </g>
          <g transform="translate(35 430)" class="axis-key">
            <g v-for="axis in axes" :key="axis.name">
              <line x1="0" y1="0" :x2="axis.x" :y2="axis.y" :stroke="axis.color" stroke-width="2" />
              <text :x="axis.x + 4" :y="axis.y - 4" :fill="axis.color">{{ axis.name }}</text>
            </g>
          </g>
          <g transform="translate(480 445)" stroke="#173e56" fill="#173e56">
            <line x1="0" y1="0" :x2="5 * pixelsPerMm" y2="0" stroke-width="2" />
            <text x="0" y="-10" stroke="none">5 mm (view plane)</text>
          </g>
        </svg>
        <p class="hint">Drag to rotate · scroll to zoom · arrow keys rotate. Landmarks and the selected path remain visible through the mesh.</p>
        <div class="controls">
          <label>Rotation {{ Math.round(yaw) }}°<input type="range" min="-180" max="180" step="1" v-model.number="yaw" /></label>
          <label>Tilt {{ Math.round(pitch) }}°<input type="range" min="-90" max="90" step="1" v-model.number="pitch" /></label>
          <label>Zoom<input type="range" min="0.001" max="40" step="0.001" v-model.number="pixelsPerMm" /></label>
        </div>
        <div class="toggles">
          <label><input type="checkbox" v-model="labels" /> Landmark names</label>
          <label><input type="checkbox" v-model="wireframe" /> Triangle edges</label>
          <label><input type="checkbox" v-model="overlay" /> Overlay base fixture</label>
        </div>
        <p v-if="focused && geometry.landmarks[focused]" class="coordinate-readout">
          {{ humanize(focused) }}: {{ coordinates(geometry.landmarks[focused]) }} mm (x, y, z)
        </p>
      </section>

      <aside class="measurements-panel">
        <h2>Measurements</h2>
        <p>Select a measurement to highlight its endpoints and route.</p>
        <button v-for="(item, index) in geometry.measurements" :key="item.id" type="button"
          class="measurement" :class="{ selected: selectedIndex === index }" :aria-pressed="selectedIndex === index"
          @click="selectedIndex = index">
          <span>{{ humanize(item.id) }}</span>
          <strong>{{ item.value.toFixed(3) }} {{ item.unit === 'deg' ? '°' : item.unit }}</strong>
          <small>{{ humanize(item.kind) }} · {{ humanize(item.role || 'target') }}</small>
        </button>
        <div v-if="selected" class="definition">
          <h3>{{ humanize(selected.kind) }}</h3>
          <p>{{ selected.definition }}</p>
          <p><strong>Route:</strong> {{ selected.landmarks.map(humanize).join(' → ') }}</p>
          <p v-if="selected.kind === 'angle'">The highlighted segments meet at the middle landmark; the value is their interior 3D angle.</p>
          <p><strong>Definition status:</strong> {{ humanize(selected.definition_status || 'unspecified') }}</p>
        </div>
      </aside>
    </div>

    <details class="metadata">
      <summary>Source and fixture metadata</summary>
      <dl>
        <dt>Record</dt><dd>{{ record.record_id }}</dd>
        <dt>Schema / topology</dt><dd>{{ record.schema_version }} / {{ record.topology_id }}</dd>
        <dt>Source units</dt><dd>{{ record.units }} — displayed coordinates and lengths are in millimeters</dd>
        <dt>Domain / source identity</dt><dd>{{ record.source?.domain }} / {{ record.source?.identity_id }}</dd>
        <dt>Provenance</dt><dd>{{ record.source?.provenance }}</dd>
        <dt>Review</dt><dd>{{ record.review?.status || 'unspecified' }}</dd>
      </dl>
    </details>
  </main>
</template>

<script>
import baseRecord from '../../python/dimension_pipeline/fixtures/base_mm.json';
import largerRecord from '../../python/dimension_pipeline/fixtures/larger_m.json';
import localRecord from '../../python/dimension_pipeline/fixtures/local_nose_mm.json';
import { readFixture, projectPoint } from './dimension_fixture_geometry';

const examples = [
  { id: 'base', label: 'Base · 4 mm ridge height', record: baseRecord },
  { id: 'larger', label: 'Larger · uniform 1.5× scale', record: largerRecord },
  { id: 'local', label: 'Local change · 6 mm ridge height', record: localRecord },
];

export default {
  name: 'DimensionFixtures',
  data() {
    return { examples, chosen: 'base', custom: null, customName: '', geometry: readFixture(baseRecord),
      base: readFixture(baseRecord), selectedIndex: 2, yaw: -30, pitch: 22, pixelsPerMm: 22,
      center: [0, -2, 2], labels: true, wireframe: true, overlay: false, focused: null, drag: null, error: '' };
  },
  computed: {
    record() { return this.geometry.record; },
    selected() { return this.geometry.measurements[this.selectedIndex]; },
    sortedFaces() {
      return this.geometry.faces.map((face, index) => ({ index,
        points: this.polygon(this.geometry.vertices, face),
        depth: face.reduce((sum, i) => sum + this.project(this.geometry.vertices[i]).depth, 0) / 3,
      })).sort((a, b) => a.depth - b.depth);
    },
    axes() {
      const origin = projectPoint([0, 0, 0], [0, 0, 0], this.yaw, this.pitch, 1);
      return [ ['x', [30, 0, 0], '#b53131'], ['y', [0, 30, 0], '#317136'], ['z', [0, 0, 30], '#285eaa'] ]
        .map(([name, point, color]) => {
          const p = projectPoint(point, [0, 0, 0], this.yaw, this.pitch, 1);
          return { name, color, x: p.x - origin.x, y: p.y - origin.y };
        });
    },
  },
  methods: {
    humanize(value) { return String(value).replace(/_/g, ' '); },
    project(point) { return projectPoint(point, this.center, this.yaw, this.pitch, this.pixelsPerMm); },
    pointString(point) { const p = this.project(point); return `${p.x},${p.y}`; },
    polygon(vertices, face) { return face.map(i => this.pointString(vertices[i])).join(' '); },
    coordinates(point) { return point.map(x => x.toFixed(3)).join(', '); },
    chooseFixture() {
      this.geometry = this.chosen === 'custom' ? this.custom : readFixture(examples.find(e => e.id === this.chosen).record);
      this.selectedIndex = Math.min(this.selectedIndex, this.geometry.measurements.length - 1);
      this.focused = null;
      this.error = '';
      // Preserve center, orientation and zoom so size changes stay visible.
    },
    async openFile(event) {
      const file = event.target.files[0];
      if (!file) return;
      try {
        if (file.size > 5 * 1024 * 1024) throw new Error('Choose a JSON file smaller than 5 MB.');
        const geometry = readFixture(JSON.parse(await file.text()));
        this.custom = geometry;
        this.customName = file.name;
        this.chosen = 'custom';
        this.chooseFixture();
        this.fitView();
      } catch (error) {
        this.error = `Could not open fixture: ${error.message}`;
      } finally {
        event.target.value = '';
      }
    },
    setView(yaw, pitch) { this.yaw = yaw; this.pitch = pitch; },
    fitView() {
      const low = [Infinity, Infinity, Infinity], high = [-Infinity, -Infinity, -Infinity];
      for (const vertex of this.geometry.vertices) vertex.forEach((v, i) => {
        low[i] = Math.min(low[i], v); high[i] = Math.max(high[i], v);
      });
      this.center = low.map((v, i) => (v + high[i]) / 2);
      const diameter = Math.hypot(...low.map((v, i) => high[i] - v));
      this.pixelsPerMm = Math.min(40, 330 / Math.max(diameter, 0.001));
    },
    startDrag(event) {
      if (event.button !== 0) return;
      this.drag = { x: event.clientX, y: event.clientY, yaw: this.yaw, pitch: this.pitch };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    moveDrag(event) {
      if (!this.drag) return;
      this.yaw = ((this.drag.yaw + (event.clientX - this.drag.x)*0.5 + 540) % 360) - 180;
      this.pitch = Math.max(-90, Math.min(90, this.drag.pitch + (event.clientY - this.drag.y)*0.5));
    },
    endDrag() { this.drag = null; },
    rotateKey(event) {
      const steps = { ArrowLeft: [-5, 0], ArrowRight: [5, 0], ArrowUp: [0, 5], ArrowDown: [0, -5] };
      if (!steps[event.key]) return;
      event.preventDefault();
      this.yaw = ((this.yaw + steps[event.key][0] + 540) % 360) - 180;
      this.pitch = Math.max(-90, Math.min(90, this.pitch + steps[event.key][1]));
    },
    zoomWheel(event) { this.pixelsPerMm = Math.max(0.001, Math.min(40, this.pixelsPerMm * Math.exp(-Math.sign(event.deltaY)*0.1))); },
  },
};
</script>

<style scoped>
.fixture-viewer { max-width: 1280px; margin: 2rem auto; padding: 0 1.25rem; color: #193648; }
.eyebrow { color: #536d7c; text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.8rem; }
h1 { margin: 0.3rem 0; font-size: 2rem; }
h2 { font-size: 1.25rem; margin: 0 0 0.5rem; }
h3 { font-size: 1rem; }
.toolbar, .view-buttons, .toggles, .controls { display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }
.toolbar { margin: 1.5rem 0; }
label { padding: 0; }
.toolbar label, .controls label { display: flex; flex-direction: column; gap: 0.4rem; }
select, button, input { font: inherit; }
select, .view-buttons button { padding: 0.5rem 0.7rem; border: 1px solid #a9bbc5; border-radius: 5px; background: white; color: #193648; }
button { cursor: pointer; }
.local-note, .hint { font-size: 0.85rem; color: #536d7c; }
.viewer-layout { display: grid; grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr); gap: 1.5rem; align-items: start; }
.geometry-panel, .measurements-panel { border: 1px solid #ccd9e0; border-radius: 10px; padding: 1rem; min-width: 0; }
.view-buttons { gap: 0.5rem; margin-bottom: 1rem; }
svg { display: block; width: 100%; touch-action: none; cursor: grab; border-radius: 6px; }
svg:active { cursor: grabbing; }
svg:focus-visible, button:focus-visible { outline: 3px solid #2078b0; outline-offset: 3px; }
.landmark-label { font: 12px sans-serif; fill: #173e56; paint-order: stroke; stroke: white; stroke-width: 3px; stroke-linejoin: round; pointer-events: none; }
.axis-key { font: 12px sans-serif; }
.controls { margin: 1rem 0; }
.controls label { flex: 1; min-width: 120px; }
.toggles { font-size: 0.9rem; gap: 0.8rem; }
.measurement { display: grid; grid-template-columns: 1fr auto; gap: 0.35rem; text-align: left; width: 100%; padding: 0.8rem; background: #fff; border: 1px solid #cdd9e0; border-radius: 6px; margin: 0.5rem 0; color: inherit; }
.measurement small { grid-column: 1 / -1; color: #536d7c; }
.measurement.selected { border-color: #b34412; background: #fff4e9; box-shadow: inset 3px 0 #b34412; }
.measurement strong { white-space: nowrap; }
.definition { border-top: 1px solid #ccd9e0; margin-top: 1rem; font-size: 0.9rem; overflow-wrap: anywhere; }
.metadata { margin: 1.5rem 0; padding: 1rem; border: 1px solid #ccd9e0; border-radius: 8px; overflow-wrap: anywhere; }
summary { cursor: pointer; }
dl { display: grid; grid-template-columns: 180px 1fr; gap: 0.6rem; font-size: 0.9rem; }
dt { font-weight: bold; } dd { margin: 0; }
.error { color: #8b2418; background: #fff0ed; padding: 0.75rem; }
.coordinate-readout { font-size: 0.9rem; }
@media (max-width: 850px) { .viewer-layout { grid-template-columns: 1fr; } dl { grid-template-columns: 1fr; } }
</style>
