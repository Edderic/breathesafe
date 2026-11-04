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

export function captureGuidance(index) {
  if (index === 0) return 'Designated frontal: look straight ahead with a neutral expression and closed mouth.';
  const angle = 90-180*(index-1)/59;
  const pose = Math.abs(angle) < 2 ? 'face directly toward the camera' : `turn toward your ${angle > 0 ? 'right' : 'left'} (about ${Math.round(Math.abs(angle))}°)`;
  return `Frame ${index}/60: ${pose}. Sweep smoothly from right profile through frontal to left profile. Keep your torso still, expression neutral and mouth closed.`;
}

export function sweepSchedule(durationSeconds) {
  if (![10, 20, 30].includes(durationSeconds)) throw Error('Choose a 10, 20 or 30 second sweep.');
  const events = Array.from({length: durationSeconds+1}, (_, second) => ({ at_ms: second*1000, remaining: durationSeconds-second }));
  for (let index=1; index<=60; index++) events.push({ at_ms: (index-1)*durationSeconds*1000/59, index });
  return events.sort((a,b)=>a.at_ms-b.at_ms || (a.remaining===0 ? 1 : b.remaining===0 ? -1 : 0));
}

// Absolute deadlines keep frame processing time from lengthening the sweep.
export async function runCaptureSweep({ durationSeconds, capture, countdown, cancelled,
  now = () => performance.now(), wait = ms => new Promise(resolve=>setTimeout(resolve,ms)) }) {
  const started = now(), maximumDelay = durationSeconds*1000/59*1.5;
  for (const event of sweepSchedule(durationSeconds)) {
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
