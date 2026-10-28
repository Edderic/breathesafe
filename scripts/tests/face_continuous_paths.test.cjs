const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const context = {};
for (const file of ['face_annotation_geometry.js', 'face_surface_paths.js', 'face_continuous_paths.js']) {
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../../app/javascript', file), 'utf8')
    .replace(/^import .*;\n/gm, '').replace(/export (async )?function /g, '$1function '), context);
}
const record = { mesh: { vertices: [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], triangles: [[0, 1, 2], [0, 2, 3]] } };
const a = { kind: 'barycentric', triangle_index: 0, weights: [0, 1, 0] };
const b = { kind: 'barycentric', triangle_index: 1, weights: [0, 0, 1] };
const middle = { kind: 'barycentric', triangle_index: 1, weights: [.5, .5, 0] };
const baselines = context.zygionGonionPaths(record, context.buildSurfaceGraph(record), {
  zygion_left: { attachment: a }, gonion_left: { attachment: b },
});
const response = () => ({ method: 'cgal_continuous_v1', cgal_version: '6.2', arithmetic: 'exact_predicates_double_constructions', elapsed_ms: 10,
  results: [{ id: baselines[0].id, status: 'ok', length_mm: Math.sqrt(2), path: [a, middle, b] }] });

test('continuous result keeps endpoints and reconstructs the shorter route inside triangles', () => {
  const paths = context.decodeContinuousPaths(record, baselines, response());
  assert.ok(Math.abs(paths[0].length_mm-Math.sqrt(2)) < 1e-12);
  assert.equal(paths[0].mesh_edge_length_mm, 2);
  assert.equal(paths[0].method, 'cgal_continuous_v1');
  assert.equal(paths[0].cgal_version, '6.2');
  assert.equal(paths[1].status, 'missing_landmarks');
});

test('solver paths cannot move landmarks, jump through the mesh, or invent a distance', () => {
  for (const mutate of [
    r => { r.results[0].path = [a, b]; },
    r => { r.results[0].length_mm = 99; },
    r => { r.results[0].path[0] = { kind: 'vertex', vertex_index: 0 }; },
    r => { r.results[0].path[1] = { kind: 'vertex', vertex_index: 999 }; },
    r => { r.results[0].path[1] = { kind: 'barycentric', triangle_index: 1, weights: [0, 0, 0] }; },
    r => { r.results[0].id = 'unrelated'; },
    r => { r.results.push(r.results[0]); },
    r => { delete r.cgal_version; },
  ]) {
    const bad = structuredClone(response()); mutate(bad);
    assert.throws(() => context.decodeContinuousPaths(record, baselines, bad));
  }
});
