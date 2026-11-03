import { projectPoint } from './dimension_fixture_geometry';
import { projectMesh, shadedFaces, pickSurface, attachmentPoint } from './face_annotation_geometry';

export const captureVersion = 'orthographic-shaded-v1';
export function captureFace(record, camera, canvas) {
  canvas.width = 720; canvas.height = 480;
  const context = canvas.getContext('2d');
  context.fillStyle = '#edf2f5'; context.fillRect(0, 0, 720, 480);
  const points = projectMesh(record, camera.center_mm, camera.yaw, camera.pitch, camera.pixels_per_mm);
  for (const face of shadedFaces(record, points)) {
    const vertices = record.mesh.triangles[face.index].map(index => points[index]);
    context.fillStyle = face.fill; context.beginPath(); context.moveTo(vertices[0].x, vertices[0].y);
    context.lineTo(vertices[1].x, vertices[1].y); context.lineTo(vertices[2].x, vertices[2].y); context.closePath(); context.fill();
  }
  return points;
}
export function projectDetection(record, points, landmark, index) {
  const raw = { x: landmark.x, y: landmark.y, z: Number.isFinite(landmark.z) ? landmark.z : null };
  const common = { index, raw };
  if (![raw.x, raw.y].every(Number.isFinite)) return { ...common, status: 'invalid_coordinates' };
  if (raw.x < 0 || raw.x > 1 || raw.y < 0 || raw.y > 1) return { ...common, status: 'outside_image' };
  const hit = pickSurface(record, points, raw.x*720, raw.y*480);
  if (!hit) return { ...common, status: 'missed_surface' };
  const { depth, ...attachment } = hit;
  return { ...common, status: 'ok', attachment, point_mm: attachmentPoint(record, attachment) };
}
export function referenceVisible(record, points, camera, annotation) {
  const point = attachmentPoint(record, annotation.attachment);
  const p = projectPoint(point, camera.center_mm, camera.yaw, camera.pitch, camera.pixels_per_mm);
  if (p.x < 0 || p.x > 720 || p.y < 0 || p.y > 480) return false;
  const hit = pickSurface(record, points, p.x, p.y);
  return !!hit && Math.abs(hit.depth-p.depth) < .1;
}
export function distanceSummary(points) {
  const distances = points.flatMap((a, i) => points.slice(i+1).map(b => Math.hypot(...a.map((v, axis) => v-b[axis])))).sort((a, b) => a-b);
  return { pairs: distances.length, median_mm: distances.length ? (distances[Math.floor(distances.length/2)]+distances[Math.floor((distances.length-1)/2)])/2 : null,
    maximum_mm: distances.length ? distances.at(-1) : null };
}
export function comparisonRows(record, results, mappings, references) {
  return results.flatMap(result => {
    const points = result.status === 'ok' ? projectMesh(record, result.camera.center_mm, result.camera.yaw, result.camera.pitch, result.camera.pixels_per_mm) : null;
    return Object.entries(mappings).flatMap(([name, index]) => references.map(reference => {
      const row = { view_id: result.view_id, landmark: name, index, reference_id: reference.id, reference_label: reference.label };
      const annotation = reference.landmarks[name], detection = result.detections.find(item => item.index === index);
      if (!annotation) return { ...row, status: 'missing_reference' };
      if (result.status !== 'ok') return { ...row, status: result.status };
      if (detection?.observation_status === 'rejected') return { ...row, status: 'filtered_out', reason: detection.rejection_reason };
      if (!referenceVisible(record, points, result.camera, annotation)) return { ...row, status: 'reference_occluded' };
      if (!detection || detection.status !== 'ok') return { ...row, status: detection?.status || 'missing_detection' };
      const manual = attachmentPoint(record, annotation.attachment);
      return { ...row, status: 'ok', distance_mm: Math.hypot(...manual.map((v, axis) => v-detection.point_mm[axis])) };
    }));
  });
}
export function validateMappings(mappings, names) {
  if (!mappings || typeof mappings !== 'object' || Array.isArray(mappings)) throw Error('Expected a landmark-to-index mapping.');
  for (const [name, index] of Object.entries(mappings)) {
    if (!names.includes(name) || !Number.isInteger(index) || index < 0 || index > 477) throw Error('Invalid candidate correspondence: '+name);
  }
  return { ...mappings };
}
export function validateExperiment(bundle, record, fingerprint, names) {
  if (!['1.0.0', '1.1.0'].includes(bundle?.experiment_version) || bundle.record_id !== record.record_id || bundle.mesh_sha256 !== fingerprint || bundle.topology_id !== record.topology_id || bundle.units !== 'mm') throw Error('Experiment belongs to a different mesh or unsupported version.');
  if (bundle.experiment_version === '1.1.0' && !bundle.view_filter) throw Error('Missing view-filter policy in this experiment version.');
  validateMappings(bundle.mappings, names);
  if (!Array.isArray(bundle.results) || bundle.results.length > 7 || new Set(bundle.results.map(r => r.view_id)).size !== bundle.results.length) throw Error('Invalid experiment views.');
  const allowed = ['ok', 'no_detection', 'error', 'cancelled'];
  for (const result of bundle.results) {
    const c = result.camera;
    if (!allowed.includes(result.status) || typeof result.view_id !== 'string' || !c || c.projection !== 'orthographic' || c.width !== 720 || c.height !== 480 || c.mirrored !== false || c.distortion !== 'none' ||
      !Array.isArray(c.center_mm) || c.center_mm.length !== 3 || !c.center_mm.every(Number.isFinite) ||
      ![c.yaw, c.pitch, c.pixels_per_mm].every(Number.isFinite) || Math.abs(c.yaw) > 180 || Math.abs(c.pitch) > 90 || c.pixels_per_mm <= 0 || c.pixels_per_mm > 40 ||
      !Array.isArray(result.raw_landmarks) || result.raw_landmarks.length > 478) throw Error('Invalid camera or detection data.');
    if (result.raw_landmarks.some(p => !p || typeof p !== 'object' || [p.x, p.y].some(v => v !== null && !Number.isFinite(v)))) throw Error('Invalid landmark coordinates.');
  }
  return bundle;
}
