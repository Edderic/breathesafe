import canonicalRegions from '../../python/dimension_pipeline/assets/mediapipe_regions.json';

const regionForIndex = new Map(Object.entries(canonicalRegions.regions).flatMap(([region, indices]) => indices.map(index => [index, region])));
export const viewFilterPolicy = {
  version: '1.0.0', method: 'canonical_side_camera_gate', frontal_yaw_degrees: 15,
  maximum_yaw_degrees: 60, maximum_pitch_degrees: 20,
  central_band_half_width_ratio: canonicalRegions.central_band_half_width_ratio,
  canonical_source_url: canonicalRegions.source_url, canonical_source_sha256: canonicalRegions.source_sha256,
};

// This is a conservative region/view heuristic, not an occlusion detector.
// It uses the known capture camera and fixed index regions, never manual labels,
// predicted screen X, or the already-projected (possibly incorrect) mesh point.
export function filterObservation(detection, camera, mode = 'conservative') {
  const region = regionForIndex.get(detection.index) || 'unknown';
  const output = { ...detection, region };
  if (detection.status !== 'ok') return { ...output, observation_status: 'not_projected', rejection_reason: detection.status };
  if (mode === 'raw') return { ...output, observation_status: 'accepted', rejection_reason: null };
  if (mode !== 'conservative') throw Error('Unknown view-filter mode');
  let reason = null;
  if (!Number.isFinite(camera?.yaw) || !Number.isFinite(camera?.pitch)) reason = 'invalid_camera';
  else if (Math.abs(camera.pitch) > viewFilterPolicy.maximum_pitch_degrees) reason = 'tilt_outside_policy';
  else if (Math.abs(camera.yaw) > viewFilterPolicy.maximum_yaw_degrees) reason = 'yaw_outside_policy';
  else if (region === 'unknown') reason = 'unknown_index_region';
  else if (Math.abs(camera.yaw) > viewFilterPolicy.frontal_yaw_degrees) {
    if (region === 'central') reason = 'central_requires_frontal';
    else if (region !== (camera.yaw < 0 ? 'left' : 'right')) reason = 'far_side';
  }
  return { ...output, observation_status: reason ? 'rejected' : 'accepted', rejection_reason: reason };
}

export function filterResults(results, mode) {
  return results.map(result => ({ ...result, detections: result.detections.map(d => filterObservation(d, result.camera, mode)) }));
}
export function validateViewFilter(filter) {
  // Old pilot exports predate filtering: preserve their raw baseline on reload.
  if (filter === undefined) return 'raw';
  if (!filter || !['conservative', 'raw'].includes(filter.mode) || filter.version !== viewFilterPolicy.version ||
    filter.method !== viewFilterPolicy.method || filter.canonical_source_sha256 !== viewFilterPolicy.canonical_source_sha256 ||
    ['frontal_yaw_degrees', 'maximum_yaw_degrees', 'maximum_pitch_degrees', 'central_band_half_width_ratio'].some(key => filter[key] !== viewFilterPolicy[key])) {
    throw Error('Unsupported or modified view-filter policy.');
  }
  return filter.mode;
}
