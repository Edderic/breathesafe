const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');
const { execFileSync } = require('node:child_process');
const root = path.join(__dirname, '../..');
const context = { TextEncoder, crypto: webcrypto };
for (const file of ['dimension_fixture_geometry.js', 'face_annotation_geometry.js']) {
  const source = fs.readFileSync(path.join(root, 'app/javascript', file), 'utf8')
    .replace(/^import .*;\n/gm, '').replace(/export (async )?function /g, '$1function ');
  vm.runInNewContext(source, context);
}
const { pickSurface, attachmentPoint, makeHead, meshFingerprint, validateAnnotations } = context;
const base = JSON.parse(fs.readFileSync(path.join(root, 'python/dimension_pipeline/assets/makehuman_head.json')));
const controls = JSON.parse(fs.readFileSync(path.join(root, 'python/dimension_pipeline/assets/head_variants.json')));

test('overlapping triangles pick the visible surface independent of face order', () => {
  const record = { mesh: { vertices: [[0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 5], [2, 0, 5], [0, 2, 5]],
    triangles: [[3, 4, 5], [0, 1, 2]] } };
  const points = record.mesh.vertices.map(([x, y, depth]) => ({ x, y, depth }));
  const hit = pickSurface(record, points, .5, .5);
  assert.equal(hit.triangle_index, 0);
  assert.deepEqual(Array.from(attachmentPoint(record, hit)), [.5, .5, 5]);
  assert.equal(pickSurface(record, points, 8, 8), null);
  record.mesh.triangles.reverse();
  assert.equal(pickSurface(record, points, .5, .5).triangle_index, 1);
});

test('surface attachment stays the same 3D point when the view changes', () => {
  const record = { mesh: { vertices: [[0, 0, 0], [5, 0, 0], [0, 5, 0]], triangles: [[0, 1, 2]] } };
  for (const yaw of [-45, 0, 45]) {
    const points = context.projectMesh(record, [0, 0, 0], yaw, 25, 10);
    const target = context.projectPoint([1, 2, 0], [0, 0, 0], yaw, 25, 10);
    const recovered = attachmentPoint(record, pickSurface(record, points, target.x, target.y));
    recovered.forEach((v, i) => assert.ok(Math.abs(v-[1, 2, 0][i]) < 1e-10));
  }
});

test('generation preserves source identity, topology, and independent local controls', () => {
  const records = controls.map(c => makeHead(base, c));
  for (const r of records) {
    assert.equal(r.source.identity_id, base.source.identity_id);
    assert.equal(r.topology_id, base.topology_id);
    assert.equal(r.mesh.triangles.length, base.mesh.triangles.length);
  }
  const local = records[3];
  assert.ok(local.mesh.vertices.some((p, i) => p[2] > base.mesh.vertices[i][2]+4));
  local.mesh.vertices.forEach((p, i) => { assert.equal(p[0], base.mesh.vertices[i][0]); assert.equal(p[1], base.mesh.vertices[i][1]); });
});

test('browser variants match the offline Python generator', () => {
  const output = execFileSync('python3', ['-c',
    'import json; from dimension_pipeline.generate_heads import load, variant_record; print(json.dumps([variant_record(load("makehuman_head.json"), c)["mesh"]["vertices"] for c in load("head_variants.json")]))'],
  { cwd: root, env: { ...process.env, PYTHONPATH: path.join(root, 'python') }, maxBuffer: 4*1024*1024 });
  const expected = JSON.parse(output);
  controls.forEach((control, i) => {
    const actual = makeHead(base, control).mesh.vertices;
    actual.forEach((p, j) => p.forEach((v, axis) => assert.ok(Math.abs(v-expected[i][j][axis]) <= 1e-6)));
  });
});

test('annotation round trip rejects wrong geometry, invalid weights, and unknown labels', async () => {
  const record = makeHead(base, controls[0]), fingerprint = await meshFingerprint(record);
  const bundle = { annotation_version: '1.0.0', record_id: record.record_id, topology_id: record.topology_id,
    mesh_sha256: fingerprint, units: 'mm', review_status: 'draft', landmarks: {
      pronasale: { attachment: { kind: 'barycentric', triangle_index: 1, weights: [.2, .3, .5] }, annotator: 'Reviewer' },
    } };
  assert.equal(validateAnnotations(bundle, record, fingerprint, ['pronasale']).pronasale.annotator, 'Reviewer');
  assert.notEqual(await meshFingerprint(makeHead(base, controls[1])), fingerprint);
  for (const mutate of [b => { b.mesh_sha256 = 'wrong'; }, b => { b.landmarks.pronasale.attachment.weights = [0, 0, 0]; },
    b => { b.landmarks.pronasale.attachment.triangle_index = 999999; }, b => { b.landmarks.unknown = b.landmarks.pronasale; },
    b => { b.landmarks.pronasale.annotator = ''; }, b => { b.units = 'm'; }]) {
    const bad = structuredClone(bundle); mutate(bad);
    assert.throws(() => validateAnnotations(bad, record, fingerprint, ['pronasale']));
  }
});
