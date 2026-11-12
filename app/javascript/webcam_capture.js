// Preview mirroring belongs in CSS. Pixels written here always use native dimensions.
export function captureNativeFrame(video, settings) {
  if (!video.videoWidth || !video.videoHeight) throw Error('Wait for the camera to provide a frame.');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  return { canvas, timestamp: new Date().toISOString(), camera_settings: { ...settings }, mirrored: false,
    width: canvas.width, height: canvas.height };
}

export const nativeCameraConstraints = { video: { facingMode: 'user', width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false };

export function sweepCues(mode, remaining, duration) {
  if (mode === 'moving_camera_two_pass') return remaining === 0 ? 'Pass complete. Keep head still.' : remaining === duration/2 ? 'Camera in front. Keep head still.' : String(remaining);
  if (mode === 'moving_camera') return remaining === 0 ? 'Camera at subject’s right. Done. Keep head still.' : remaining === duration/2 ? 'Camera in front. Keep head still.' : String(remaining);
  return remaining === 0 ? 'Left profile. Done.' : remaining === duration/2 ? 'Face camera.' : String(remaining);
}

export function captureGuidance(index, mode = 'head_turn') {
  if (index === 0) return 'Designated frontal: look straight ahead with a neutral expression and closed mouth.';
  const twoPass = mode === 'moving_camera_two_pass', pass = index <= 30 ? 1 : 2, local = (index-1)%30;
  const angle = twoPass ? (pass === 1 ? 1 : -1)*(90-180*local/29) : 90-180*(index-1)/59;
  if (mode === 'moving_camera' || twoPass) {
    const position = Math.abs(angle) < 2 ? 'directly in front of the subject' : `on the subject’s ${angle > 0 ? 'left' : 'right'} (about ${Math.round(Math.abs(angle))}° from frontal)`;
    const route = twoPass ? `Pass ${pass}, frame ${local+1}/30: ${pass === 1 ? 'eye-level arc, subject’s left to right' : 'slightly lower arc, subject’s right to left, aiming gently upward toward the nose'}` : 'eye-level arc';
    return `Frame ${index}/60: camera ${position}. ${route}. Keep distance approximately constant and the face centered. Subject: keep head and torso still, look at a fixed point ahead, expression neutral and mouth closed. Do not follow the camera.`;
  }
  const pose = Math.abs(angle) < 2 ? 'face directly toward the camera' : `turn toward your ${angle > 0 ? 'right' : 'left'} (about ${Math.round(Math.abs(angle))}°)`;
  return `Frame ${index}/60: ${pose}. Sweep smoothly from right profile through frontal to left profile. Keep your torso still, expression neutral and mouth closed.`;
}

export function sweepSchedule(durationSeconds, frameCount = 60) {
  if (!(frameCount === 60 && [10,20,30].includes(durationSeconds)) && !(frameCount === 30 && [5,10,15].includes(durationSeconds))) throw Error('Unsupported sweep duration or frame count.');
  const events = Array.from({length: durationSeconds+1}, (_, second) => ({ at_ms: second*1000, remaining: durationSeconds-second }));
  if (!Number.isInteger(durationSeconds/2)) events.push({at_ms:durationSeconds*500,remaining:durationSeconds/2});
  for (let index=1; index<=frameCount; index++) events.push({ at_ms: (index-1)*durationSeconds*1000/(frameCount-1), index });
  return events.sort((a,b)=>a.at_ms-b.at_ms || (a.remaining===0 ? 1 : b.remaining===0 ? -1 : 0));
}

// Absolute deadlines keep frame processing time from lengthening the sweep.
export async function runCaptureSweep({ durationSeconds, frameCount = 60, capture, countdown, cancelled,
  now = () => performance.now(), wait = ms => new Promise(resolve=>setTimeout(resolve,ms)) }) {
  const started = now(), maximumDelay = durationSeconds*1000/(frameCount-1)*1.5;
  for (const event of sweepSchedule(durationSeconds,frameCount)) {
    if (cancelled()) return false;
    const delay = started+event.at_ms-now();
    if (delay > 0) await wait(delay);
    if (cancelled()) return false;
    if (now()-started-event.at_ms > maximumDelay) throw Error('Capture fell behind the sweep timer. Keep this tab visible and try a longer sweep.');
    if (event.index === undefined) countdown(event.remaining);
    else capture(event.index, { intended_elapsed_ms: event.at_ms, elapsed_ms: now()-started });
  }
  return true;
}
