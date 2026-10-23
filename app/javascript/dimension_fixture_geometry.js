// Reference-label calculations for the research viewer, independent of rendering.
const units = { mm: 1, m: 1000 };
const finiteVector = (v, n) => Array.isArray(v) && v.length === n && v.every(Number.isFinite);
const distance = (a, b) => Math.hypot(...a.map((v, i) => v - b[i]));

export function readFixture(record) {
  const require = (condition, message) => { if (!condition) throw new Error(message); };
  require(record && record.schema_version === '1.0.0', 'Expected a reference fixture with schema_version 1.0.0.');
  require(Object.hasOwn(units, record.units), 'Fixture units must be mm or m.');
  const frame = record.coordinate_frame;
  require(frame?.handedness === 'right' && frame.x === 'subject_left' && frame.y === 'superior' && frame.z === 'anterior',
    'Expected right-handed coordinates: subject left, superior, anterior.');
  const mesh = record.mesh;
  require(Array.isArray(mesh?.vertices) && mesh.vertices.length >= 3 && mesh.vertices.length <= 20000 &&
    mesh.vertices.every(v => finiteVector(v, 3)), 'Expected 3–20,000 finite 3D vertices.');
  const vertices = mesh.vertices.map(v => v.map(x => x * units[record.units]));
  require(vertices.every(v => v.every(Number.isFinite)), 'Coordinates overflow after millimeter conversion.');
  require(Array.isArray(mesh.triangles) && mesh.triangles.length > 0 && mesh.triangles.length <= 40000,
    'Expected 1–40,000 triangles.');
  for (const face of mesh.triangles) {
    require(Array.isArray(face) && face.length === 3 && new Set(face).size === 3 &&
      face.every(i => Number.isInteger(i) && i >= 0 && i < vertices.length), 'Invalid triangle indices.');
    const [a, b, c] = face.map(i => vertices[i]);
    const u = b.map((v, i) => v - a[i]), v = c.map((v, i) => v - a[i]);
    require(Math.hypot(u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]) > 0,
      'Degenerate mesh triangle.');
  }
  require(record.landmarks && typeof record.landmarks === 'object' && !Array.isArray(record.landmarks) &&
    Object.keys(record.landmarks).length > 0, 'Missing landmark attachments.');
  const landmarks = {}, supports = {};
  for (const [name, attachment] of Object.entries(record.landmarks)) {
    require(attachment && typeof attachment === 'object', `Invalid attachment: ${name}`);
    if (attachment.kind === 'vertex') {
      require(Number.isInteger(attachment.vertex_index) && attachment.vertex_index >= 0 &&
        attachment.vertex_index < vertices.length, `Invalid vertex attachment: ${name}`);
      landmarks[name] = vertices[attachment.vertex_index];
      supports[name] = [attachment.vertex_index];
    } else {
      require(attachment.kind === 'barycentric' && Number.isInteger(attachment.triangle_index) &&
        attachment.triangle_index >= 0 && attachment.triangle_index < mesh.triangles.length,
        `Invalid surface attachment: ${name}`);
      const weights = attachment.weights;
      require(finiteVector(weights, 3) && weights.every(w => w >= 0 && w <= 1) &&
        Math.abs(weights.reduce((a, b) => a + b, 0) - 1) <= 1e-9, `Invalid barycentric weights: ${name}`);
      const face = mesh.triangles[attachment.triangle_index];
      landmarks[name] = [0, 1, 2].map(axis => face.reduce((sum, index, i) => sum + weights[i]*vertices[index][axis], 0));
      supports[name] = face.filter((_, i) => weights[i] > 0);
    }
  }
  require(Array.isArray(record.measurements) && record.measurements.length > 0, 'Missing measurements.');
  const ids = new Set();
  const measurements = record.measurements.map(target => {
    require(target && typeof target.id === 'string' && target.id.length > 0 && !ids.has(target.id), 'Missing or duplicate measurement ID.');
    ids.add(target.id);
    require(['straight_distance', 'surface_polyline', 'angle'].includes(target.kind), 'Unsupported measurement kind.');
    const names = target.landmarks;
    require(Array.isArray(names) && names.every(n => typeof n === 'string' && Object.hasOwn(landmarks, n)) &&
      new Set(names).size === names.length, `Invalid landmarks: ${target.id}`);
    require(target.kind === 'surface_polyline' ? names.length >= 2 : names.length === (target.kind === 'angle' ? 3 : 2),
      `Wrong landmark count: ${target.id}`);
    const points = names.map(n => landmarks[n]);
    let value;
    if (target.kind === 'angle') {
      const u = points[0].map((v, i) => v - points[1][i]);
      const v = points[2].map((v, i) => v - points[1][i]);
      const norm = Math.hypot(...u) * Math.hypot(...v);
      require(norm > 0, `Undefined angle: ${target.id}`);
      value = Math.acos(Math.max(-1, Math.min(1, u.reduce((sum, x, i) => sum + x*v[i], 0) / norm))) * 180 / Math.PI;
    } else {
      value = points.slice(1).reduce((sum, p, i) => sum + distance(points[i], p), 0);
    }
    if (target.kind === 'surface_polyline') {
      for (let i = 1; i < names.length; i++) {
        const needed = [...supports[names[i-1]], ...supports[names[i]]];
        require(mesh.triangles.some(face => needed.every(index => face.includes(index))),
          `Polyline leaves mesh surface: ${target.id}`);
      }
    }
    require(Number.isFinite(value) && value > 0, `Invalid measurement: ${target.id}`);
    return { ...target, points, value, unit: target.kind === 'angle' ? 'deg' : 'mm' };
  });
  return { record, vertices, faces: mesh.triangles, landmarks, measurements };
}

// Orthographic projection preserves a shared scale when changing fixtures.
export function projectPoint(point, center, yaw, pitch, pixelsPerMm) {
  const [x, y, z] = point.map((v, i) => v - center[i]);
  const a = yaw * Math.PI / 180, b = pitch * Math.PI / 180;
  const rx = Math.cos(a)*x + Math.sin(a)*z;
  const rz = -Math.sin(a)*x + Math.cos(a)*z;
  const ry = Math.cos(b)*y - Math.sin(b)*rz;
  return { x: 360 + rx*pixelsPerMm, y: 240 - ry*pixelsPerMm,
    depth: Math.sin(b)*y + Math.cos(b)*rz };
}
