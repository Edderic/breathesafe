import { attachmentPoint } from './face_annotation_geometry';

const distance = (a, b) => Math.hypot(...a.map((v, i) => v-b[i]));

// Edges belong to actual triangles. No connection is made across a gap, hole,
// disconnected eye component, or through the interior of the head.
export function buildSurfaceGraph(record) {
  const graph = record.mesh.vertices.map(() => new Map());
  for (const face of record.mesh.triangles) {
    for (let i = 0; i < 3; i++) {
      const a = face[i], b = face[(i+1)%3];
      const length = distance(record.mesh.vertices[a], record.mesh.vertices[b]);
      graph[a].set(b, length); graph[b].set(a, length);
    }
  }
  return graph;
}

function push(heap, item) {
  heap.push(item); let i = heap.length-1;
  while (i > 0) {
    const parent = (i-1)>>1;
    if (heap[parent][0] <= item[0]) break;
    heap[i] = heap[parent]; i = parent;
  }
  heap[i] = item;
}

function pop(heap) {
  const first = heap[0], last = heap.pop();
  if (heap.length) {
    let i = 0;
    while (2*i+1 < heap.length) {
      let child = 2*i+1;
      if (child+1 < heap.length && heap[child+1][0] < heap[child][0]) child++;
      if (heap[child][0] >= last[0]) break;
      heap[i] = heap[child]; i = child;
    }
    heap[i] = last;
  }
  return first;
}

export function surfacePath(record, graph, start, end) {
  for (const attachment of [start, end]) {
    if (attachment?.kind !== 'barycentric' || !Number.isInteger(attachment.triangle_index) ||
      attachment.triangle_index < 0 || attachment.triangle_index >= record.mesh.triangles.length ||
      !Array.isArray(attachment.weights) || attachment.weights.length !== 3 ||
      attachment.weights.some(w => !Number.isFinite(w) || w < 0 || w > 1) ||
      Math.abs(attachment.weights.reduce((a, b) => a+b, 0)-1) > 1e-9) {
      throw new Error('A surface path needs two valid barycentric attachments.');
    }
  }
  const a = attachmentPoint(record, start), b = attachmentPoint(record, end);
  const common = { method: 'mesh_edge_dijkstra_v1', unit: 'mm', chord_mm: distance(a, b) };
  const finish = attachments => {
    const points = attachments.map(p => p.kind === 'vertex' ? record.mesh.vertices[p.vertex_index] : attachmentPoint(record, p));
    return { ...common, status: 'ok', length_mm: points.slice(1).reduce((sum, p, i) => sum+distance(points[i], p), 0),
      path: attachments, points };
  };
  if (start.triangle_index === end.triangle_index) return finish([start, end]);
  // Connect the exact endpoints to the three vertices of their own triangles.
  // This preserves click locations, rather than snapping them to a vertex.
  const distances = new Float64Array(graph.length).fill(Infinity);
  const previous = new Int32Array(graph.length).fill(-1), heap = [];
  for (const i of record.mesh.triangles[start.triangle_index]) {
    distances[i] = distance(a, record.mesh.vertices[i]); push(heap, [distances[i], i]);
  }
  const goals = new Map(record.mesh.triangles[end.triangle_index].map(i => [i, distance(record.mesh.vertices[i], b)]));
  let best = Infinity, last = -1;
  while (heap.length) {
    const [length, vertex] = pop(heap);
    if (length !== distances[vertex]) continue;
    if (length > best) break;
    if (goals.has(vertex) && length+goals.get(vertex) < best) {
      best = length+goals.get(vertex); last = vertex;
    }
    for (const [neighbor, edge] of graph[vertex]) {
      const next = length+edge;
      if (next < distances[neighbor]) {
        distances[neighbor] = next; previous[neighbor] = vertex; push(heap, [next, neighbor]);
      }
    }
  }
  if (last === -1) return { ...common, status: 'disconnected', length_mm: null, path: [], points: [] };
  const route = [];
  for (let vertex = last; vertex !== -1; vertex = previous[vertex]) route.push({ kind: 'vertex', vertex_index: vertex });
  route.reverse();
  return finish([start, ...route, end]);
}

export function zygionGonionPaths(record, graph, landmarks) {
  return ['left', 'right'].map(side => {
    const endpoints = [`zygion_${side}`, `gonion_${side}`];
    const entry = { id: `project_zygion_gonion_surface_${side}`, side, endpoints,
      definition_status: 'project_candidate_published_equivalence_unverified' };
    if (endpoints.some(name => !landmarks[name])) return { ...entry, status: 'missing_landmarks' };
    return { ...entry, ...surfacePath(record, graph, ...endpoints.map(name => landmarks[name].attachment)) };
  });
}
