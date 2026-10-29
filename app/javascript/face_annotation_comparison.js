import { attachmentPoint } from './face_annotation_geometry';

// Compare placements in model space; camera position and zoom never enter the
// calculation. Missing landmarks are omitted rather than treated as zero.
export function landmarkComparison(record, sets, name) {
  const placements = sets.filter(set => set.visible && set.landmarks[name]).map(set => ({
    id: set.id, number: set.number, label: set.label, color: set.color,
    annotation: set.landmarks[name], point: attachmentPoint(record, set.landmarks[name].attachment),
  }));
  const pairs = placements.flatMap((a, i) => placements.slice(i+1).map(b => ({
    a, b, distance_mm: Math.hypot(...a.point.map((v, axis) => v-b.point[axis])),
  })));
  const distances = pairs.map(pair => pair.distance_mm).sort((a, b) => a-b), middle = Math.floor(distances.length/2);
  return { placements, pairs, maximum_mm: distances.length ? distances.at(-1) : null,
    median_mm: distances.length ? (distances[middle]+distances[Math.floor((distances.length-1)/2)])/2 : null };
}
