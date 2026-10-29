import { attachmentPoint } from './face_annotation_geometry';

const pointDistance = (a, b) => Math.hypot(...a.map((v, i) => v-b[i]));

export function decodeContinuousPaths(record, baselines, response) {
  if (response?.method !== 'cgal_continuous_v1' || !Array.isArray(response.results)) throw new Error('Unsupported continuous solver response.');
  if (typeof response.cgal_version !== 'string' || response.arithmetic !== 'exact_predicates_double_constructions' ||
    !Number.isFinite(response.elapsed_ms) || response.elapsed_ms < 0) throw new Error('Missing continuous solver provenance.');
  const available = baselines.filter(path => path.status !== 'missing_landmarks');
  if (response.results.length !== available.length || new Set(response.results.map(p => p.id)).size !== available.length) {
    throw new Error('Unexpected continuous result count.');
  }
  return baselines.map(baseline => {
    if (baseline.status === 'missing_landmarks') return baseline;
    const result = response.results.find(path => path.id === baseline.id);
    if (!result) throw new Error('Continuous result is missing an endpoint pair.');
    const metadata = { method: response.method, cgal_version: response.cgal_version, arithmetic: response.arithmetic,
      elapsed_ms: response.elapsed_ms, mesh_edge_length_mm: baseline.length_mm };
    if (result.status === 'disconnected' && baseline.status === 'disconnected') {
      return { ...baseline, ...metadata };
    }
    if (result.status !== 'ok' || !Number.isFinite(result.length_mm) || result.length_mm < 0 ||
      !Array.isArray(result.path) || result.path.length < 2 || result.path.length > 40000) throw new Error('Invalid continuous surface path.');
    const supports = [], points = [], path = [];
    for (const a of result.path) {
      if (a?.kind === 'vertex' && Number.isInteger(a.vertex_index) && a.vertex_index >= 0 && a.vertex_index < record.mesh.vertices.length) {
        path.push({ kind: 'vertex', vertex_index: a.vertex_index }); supports.push([a.vertex_index]); points.push(record.mesh.vertices[a.vertex_index]);
      } else if (a?.kind === 'barycentric' && Number.isInteger(a.triangle_index) && a.triangle_index >= 0 &&
        a.triangle_index < record.mesh.triangles.length && Array.isArray(a.weights) && a.weights.length === 3 &&
        a.weights.every(w => Number.isFinite(w) && w >= -1e-9 && w <= 1+1e-9) && Math.abs(a.weights.reduce((s, w) => s+w, 0)-1) < 1e-8) {
        const bounded = a.weights.map(w => Math.max(0, Math.min(1, w))), sum = bounded.reduce((s, w) => s+w, 0);
        const attachment = { kind: 'barycentric', triangle_index: a.triangle_index, weights: bounded.map(w => w/sum) };
        path.push(attachment); points.push(attachmentPoint(record, attachment));
        supports.push(record.mesh.triangles[a.triangle_index].filter((_, i) => attachment.weights[i] > 1e-12));
      } else throw new Error('Invalid continuous path attachment.');
    }
    for (let i = 1; i < supports.length; i++) {
      const indices = [...new Set([...supports[i-1], ...supports[i]])];
      if (indices.length > 3 || !record.mesh.triangles.some(face => indices.every(index => face.includes(index)))) {
        throw new Error('Continuous path segment leaves the mesh surface.');
      }
    }
    const tolerance = 1e-6*Math.max(1, result.length_mm);
    if (!baseline.points.length || pointDistance(points[0], baseline.points[0]) > tolerance ||
      pointDistance(points.at(-1), baseline.points.at(-1)) > tolerance) throw new Error('Continuous solver moved a landmark.');
    const length = points.slice(1).reduce((sum, point, i) => sum+pointDistance(points[i], point), 0);
    if (Math.abs(length-result.length_mm) > tolerance || length < baseline.chord_mm-tolerance ||
      length > baseline.length_mm+tolerance) throw new Error('Continuous path length failed its geometric bounds.');
    return { ...baseline, ...metadata, length_mm: length, path, points };
  });
}

export async function requestContinuousPaths(record, baselines, landmarks, signal) {
  if (!['127.0.0.1', 'localhost', '::1'].includes(globalThis.location?.hostname)) {
    throw new Error('Use the local research preview for the continuous solver.');
  }
  const queries = baselines.filter(path => path.status !== 'missing_landmarks').map(path => ({
    id: path.id, start: landmarks[path.endpoints[0]].attachment, end: landmarks[path.endpoints[1]].attachment,
  }));
  const response = await fetch('http://127.0.0.1:5180/solve', { method: 'POST', signal,
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ units: record.units, mesh: record.mesh, queries }) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Continuous solve failed.');
  return decodeContinuousPaths(record, baselines, result);
}
