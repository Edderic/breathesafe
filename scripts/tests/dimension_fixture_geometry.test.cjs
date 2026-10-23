const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '../..');
const fixtureDir = path.join(root, 'python/dimension_pipeline/fixtures');
const source = fs.readFileSync(path.join(root, 'app/javascript/dimension_fixture_geometry.js'), 'utf8')
  .replace(/export function /g, 'function ');
const context = {};
vm.runInNewContext(source, context);
const { readFixture, projectPoint } = context;
const load = name => JSON.parse(fs.readFileSync(path.join(fixtureDir, name), 'utf8'));

test('browser measurements match analytical millimeter oracles for every fixture', () => {
  for (const variant of load('manifest.json').variants) {
    const result = readFixture(load(variant.path));
    for (const [id, expected] of Object.entries(variant.expected_mm)) {
      const measurement = result.measurements.find(m => m.id === id);
      assert.ok(Math.abs(measurement.value - expected) < 1e-9, `${variant.path}: ${id}`);
      assert.equal(measurement.unit, 'mm');
    }
    assert.equal(result.measurements.find(m => m.kind === 'angle').unit, 'deg');
  }
});

test('local shape change preserves independent span while global scale preserves angle', () => {
  const measurements = name => Object.fromEntries(readFixture(load(name)).measurements.map(m => [m.id, m.value]));
  const base = measurements('base_mm.json'), local = measurements('local_nose_mm.json'), large = measurements('larger_m.json');
  assert.equal(base.pilot_lower_span, local.pilot_lower_span);
  assert.notEqual(base.analytic_tip_angle, local.analytic_tip_angle);
  assert.ok(Math.abs(base.analytic_tip_angle - large.analytic_tip_angle) < 1e-9);
});

test('invalid uploaded geometry fails before projection', () => {
  for (const mutate of [
    r => { r.units = 'pixels'; },
    r => { r.mesh.vertices[0][0] = Infinity; },
    r => { r.mesh.triangles[0] = [0, 1, 999]; },
    r => { r.landmarks.ridge_base_midpoint.weights = [1, 1, 0]; },
    r => { r.measurements[2].landmarks = ['span_left', 'tip', 'span_right']; },
    r => { r.measurements[0].landmarks = ['missing', 'tip']; },
    r => { r.measurements[0].kind = 'guessed_slope'; },
  ]) {
    const record = load('base_mm.json');
    mutate(record);
    assert.throws(() => readFixture(record));
  }
});

test('projection reveals depth in side view without changing viewing scale', () => {
  const front = projectPoint([0, 0, 4], [0, 0, 0], 0, 0, 20);
  const side = projectPoint([0, 0, 4], [0, 0, 0], 90, 0, 20);
  assert.equal(front.x, 360);
  assert.equal(side.x, 440);
  const larger = projectPoint([0, 0, 6], [0, 0, 0], 90, 0, 20);
  assert.equal(larger.x - 360, (side.x - 360) * 1.5);
});
