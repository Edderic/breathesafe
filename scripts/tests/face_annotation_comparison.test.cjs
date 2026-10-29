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
vm.runInNewContext(fs.readFileSync(path.join(root, 'app/javascript/face_annotation_comparison.js'), 'utf8')
  .replace(/^import .*;\n/gm, '').replace(/export function /g, 'function '), context);
const { landmarkComparison } = context;
const record = { mesh: { vertices: [[0, 0, 0], [6, 0, 0], [0, 8, 0]], triangles: [[0, 1, 2]] } };
const set = (id, weights) => ({ id, number: id, label: `Set ${id}`, color: '#0072b2', visible: true,
  landmarks: weights ? { gonion_left: { attachment: { kind: 'barycentric', triangle_index: 0, weights }, note: 'Preserve this note' } } : {} });

test('comparison measures barycentric 3D placements across every pair without changing sources', () => {
  const sets = [set(1, [.5, .5, 0]), set(2, [0, 0, 1]), set(3, [1, 0, 0])];
  const before = JSON.stringify(sets), result = landmarkComparison(record, sets, 'gonion_left');
  const expected = [Math.sqrt(73), 3, 8];
  result.pairs.forEach((pair, i) => assert.equal(pair.distance_mm, expected[i]));
  assert.equal(result.median_mm, 8);
  assert.equal(result.maximum_mm, Math.sqrt(73));
  assert.equal(JSON.stringify(sets), before);
  // Rigidly transform the mesh; pairwise distances stay the same.
  const transformed = { mesh: { ...record.mesh, vertices: record.mesh.vertices.map(([x, y, z]) => [10-y, -3+x, 7+z]) } };
  const rotated = landmarkComparison(transformed, sets, 'gonion_left');
  assert.equal(rotated.maximum_mm, result.maximum_mm);
  assert.equal(rotated.median_mm, result.median_mm);
});

test('unchecked and missing landmarks do not contribute invented distances', () => {
  const hidden = { ...set(4, [0, 1, 0]), visible: false };
  const sets = [set(1, [1, 0, 0]), set(2, [0, 0, 1]), set(3), hidden];
  const result = landmarkComparison(record, sets, 'gonion_left');
  assert.equal(result.placements.length, 2);
  assert.equal(result.pairs.length, 1);
  assert.equal(result.median_mm, 8);
  assert.equal(result.maximum_mm, 8);
  sets[1].visible = false;
  const single = landmarkComparison(record, sets, 'gonion_left');
  assert.equal(single.placements.length, 1);
  assert.equal(single.maximum_mm, null);
  assert.equal(single.median_mm, null);
  assert.equal(landmarkComparison(record, sets, 'menton').placements.length, 0);
});
