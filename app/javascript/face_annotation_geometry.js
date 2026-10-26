import { projectPoint } from './dimension_fixture_geometry';

export function makeHead(base, control) {
  const record = JSON.parse(JSON.stringify(base));
  record.record_id = `makehuman-head-${control.id}`;
  record.source.parent_record_ids = control.id === 'base' ? [] : [base.record_id];
  record.generation = { version: '1.0.0', seed: 0, controls: control };
  record.mesh.vertices = base.mesh.vertices.map(([x, y, z]) => {
    const nasal = Math.exp(-((x/15)**2 + ((y+20)/22)**2 + ((z-150)/35)**2));
    const jaw = Math.exp(-(((y+65)/30)**2));
    return [x*control.width*(1+(control.jaw-1)*jaw)*control.scale,
      y*control.scale, (z+control.nose_mm*nasal)*control.scale].map(v => Number(v.toFixed(6)));
  });
  return record;
}

export function headCenter(base) {
  return [0, 1, 2].map(i => {
    const values = base.mesh.vertices.map(p => p[i]);
    return (Math.min(...values) + Math.max(...values))/2;
  });
}

export function projectMesh(record, center, yaw, pitch, scale) {
  return record.mesh.vertices.map(point => projectPoint(point, center, yaw, pitch, scale));
}

export function shadedFaces(record, points) {
  return record.mesh.triangles.map((face, index) => {
    const [a, b, c] = face.map(i => points[i]);
    const u = [b.x-a.x, b.y-a.y, b.depth-a.depth], v = [c.x-a.x, c.y-a.y, c.depth-a.depth];
    const n = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
    const norm = Math.hypot(...n);
    const brightness = norm ? .4 + .6*Math.abs((-.3*n[0]-.5*n[1]+n[2])/(norm*Math.sqrt(1.34))) : .4;
    const color = [180, 202, 212].map(c => Math.round(c*brightness));
    return { index, points: face.map(i => `${points[i].x.toFixed(3)},${points[i].y.toFixed(3)}`).join(' '),
      depth: (a.depth+b.depth+c.depth)/3, fill: `rgb(${color.join(',')})` };
  }).sort((a, b) => a.depth-b.depth);
}

// Orthographic ray intersection in projected coordinates. Select the nearest
// actual surface, not the nearest vertex or last polygon's average depth.
export function pickSurface(record, points, x, y) {
  let nearest = null;
  record.mesh.triangles.forEach((face, triangle_index) => {
    const [a, b, c] = face.map(i => points[i]);
    const determinant = (b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);
    if (Math.abs(determinant) < 1e-10) return;
    const wa = ((b.y-c.y)*(x-c.x)+(c.x-b.x)*(y-c.y))/determinant;
    const wb = ((c.y-a.y)*(x-c.x)+(a.x-c.x)*(y-c.y))/determinant;
    const weights = [wa, wb, 1-wa-wb];
    if (weights.some(w => w < -1e-8 || w > 1+1e-8)) return;
    const depth = weights.reduce((sum, w, i) => sum+w*points[face[i]].depth, 0);
    if (!nearest || depth > nearest.depth) {
      const bounded = weights.map(w => Math.max(0, Math.min(1, w)));
      const total = bounded.reduce((a, b) => a+b, 0);
      nearest = { kind: 'barycentric', triangle_index, weights: bounded.map(w => w/total), depth };
    }
  });
  return nearest;
}

export function attachmentPoint(record, attachment) {
  const face = record.mesh.triangles[attachment.triangle_index];
  return [0, 1, 2].map(axis => face.reduce((sum, vertex, i) =>
    sum + attachment.weights[i]*record.mesh.vertices[vertex][axis], 0));
}

export async function meshFingerprint(record) {
  const bytes = new TextEncoder().encode(JSON.stringify({ topology: record.topology_id, units: record.units,
    frame: record.coordinate_frame, mesh: record.mesh }));
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
}

export function validateAnnotations(bundle, record, fingerprint, allowedNames) {
  const require = (ok, message) => { if (!ok) throw new Error(message); };
  require(bundle?.annotation_version === '1.0.0', 'Unsupported annotation version.');
  require(bundle.record_id === record.record_id && bundle.topology_id === record.topology_id &&
    bundle.mesh_sha256 === fingerprint && bundle.units === 'mm', 'Annotations belong to a different mesh or scale.');
  require(['draft', 'ready_for_review'].includes(bundle.review_status), 'Unsupported review status.');
  require(bundle.landmarks && typeof bundle.landmarks === 'object' && !Array.isArray(bundle.landmarks), 'Missing landmarks.');
  require(Object.keys(bundle.landmarks).length <= allowedNames.length, 'Too many landmarks.');
  for (const [name, annotation] of Object.entries(bundle.landmarks)) {
    require(allowedNames.includes(name), `Unknown landmark: ${name}`);
    const a = annotation?.attachment;
    require(a?.kind === 'barycentric' && Number.isInteger(a.triangle_index) && a.triangle_index >= 0 &&
      a.triangle_index < record.mesh.triangles.length, `Invalid triangle for ${name}.`);
    require(Array.isArray(a.weights) && a.weights.length === 3 && a.weights.every(w =>
      Number.isFinite(w) && w >= 0 && w <= 1) && Math.abs(a.weights.reduce((s, w) => s+w, 0)-1) < 1e-9,
    `Invalid surface weights for ${name}.`);
    require(typeof annotation.annotator === 'string' && annotation.annotator.trim().length > 0,
      `Missing annotator for ${name}.`);
  }
  return JSON.parse(JSON.stringify(bundle.landmarks));
}
