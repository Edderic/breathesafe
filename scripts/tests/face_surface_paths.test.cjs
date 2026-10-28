const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '../..');
const geometry = {};
vm.runInNewContext(fs.readFileSync(path.join(root, 'app/javascript/face_annotation_geometry.js'), 'utf8')
  .replace(/^import .*;\n/gm, '').replace(/export (async )?function /g, '$1function '), geometry);
const context = { attachmentPoint: geometry.attachmentPoint };
vm.runInNewContext(fs.readFileSync(path.join(root, 'app/javascript/face_surface_paths.js'), 'utf8')
  .replace(/^import .*;\n/gm, '').replace(/export function /g, 'function '), context);
const { buildSurfaceGraph, surfacePath, zygionGonionPaths } = context;
const attach = (triangle_index, weights) => ({ kind: 'barycentric', triangle_index, weights });
const folded = () => ({ mesh: { vertices: [[0, 0, 0], [2, 0, 0], [0, 0, 2], [0, 2, 0]], triangles: [[0, 1, 2], [0, 2, 3]] } });
const start = attach(0, [0, 1, 0]), end = attach(1, [0, 0, 1]);

test('a folded surface path follows supported edges and exceeds its chord', () => {
  const record = folded(), result = surfacePath(record, buildSurfaceGraph(record), start, end);
  assert.equal(result.status, 'ok');
  assert.equal(result.length_mm, 4);
  assert.ok(Math.abs(result.chord_mm-Math.sqrt(8)) < 1e-12);
  assert.equal(result.method, 'mesh_edge_dijkstra_v1');
  const vertices = result.path.filter(a => a.kind === 'vertex').map(a => a.vertex_index);
  for (let i = 1; i < vertices.length; i++) {
    assert.ok(record.mesh.triangles.some(face => face.includes(vertices[i-1]) && face.includes(vertices[i])));
  }
});

test('same-triangle endpoints use their direct on-surface segment without snapping', () => {
  const record = { mesh: { vertices: [[0, 0, 0], [3, 0, 0], [0, 4, 0]], triangles: [[0, 1, 2]] } };
  const a = attach(0, [.5, .5, 0]), b = attach(0, [0, .5, .5]);
  const result = surfacePath(record, buildSurfaceGraph(record), a, b);
  assert.equal(result.length_mm, 2);
  assert.equal(result.path.length, 2);
  assert.deepEqual(Array.from(result.points[0]), [1.5, 0, 0]);
  assert.deepEqual(Array.from(result.points[1]), [1.5, 2, 0]);
});

test('flat square exposes mesh-edge approximation bias instead of claiming an exact geodesic', () => {
  const record = { mesh: { vertices: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], triangles: [[0, 1, 2], [0, 2, 3]] } };
  const result = surfacePath(record, buildSurfaceGraph(record), start, end);
  assert.equal(result.length_mm, 2);
  assert.ok(Math.abs(result.chord_mm-Math.sqrt(2)) < 1e-12);
});

test('disconnected surfaces are not bridged even when their coordinates coincide', () => {
  const record = { mesh: { vertices: [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0]],
    triangles: [[0, 1, 2], [3, 4, 5]] } };
  const result = surfacePath(record, buildSurfaceGraph(record), attach(0, [1, 0, 0]), attach(1, [1, 0, 0]));
  assert.equal(result.status, 'disconnected');
  assert.equal(result.length_mm, null);
  assert.equal(result.path.length, 0);
});

test('surface distance is pose-invariant, scales with model units, and retains exact endpoints', () => {
  const record = folded();
  const initial = surfacePath(record, buildSurfaceGraph(record), start, end);
  record.mesh.vertices = record.mesh.vertices.map(([x, y, z]) => [-1.5*y+10, 1.5*x-7, 1.5*z+30]);
  const result = surfacePath(record, buildSurfaceGraph(record), start, end);
  assert.ok(Math.abs(result.length_mm-1.5*initial.length_mm) < 1e-12);
  assert.deepEqual(Array.from(result.points[0]), [10, -4, 30]);
  assert.deepEqual(Array.from(result.points.at(-1)), [7, -7, 30]);
});

test('bilateral measurements require the named endpoints and never reuse legacy cheekbone labels', () => {
  const record = folded(), graph = buildSurfaceGraph(record);
  const points = { lateral_zygomatic_edge_left: { attachment: start }, gonion_left: { attachment: end } };
  assert.equal(zygionGonionPaths(record, graph, points)[0].status, 'missing_landmarks');
  points.zygion_left = { attachment: start };
  const results = zygionGonionPaths(record, graph, points);
  assert.equal(results[0].length_mm, 4);
  assert.equal(results[1].status, 'missing_landmarks');
  assert.equal(results[0].definition_status, 'project_candidate_published_equivalence_unverified');
});

test('invalid barycentric attachments are rejected before searching', () => {
  const record = folded(), graph = buildSurfaceGraph(record);
  for (const bad of [attach(-1, [1, 0, 0]), attach(0, [0, 0, 0]), attach(0, [NaN, 0, 1])]) {
    assert.throws(() => surfacePath(record, graph, bad, end));
  }
});
