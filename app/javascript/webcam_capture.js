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
  const frame = index-1, pass = Math.floor(frame/30)+1, position = frame%30;
  const angle = position < 15 ? -70+position*10 : 70-(position-15)*10;
  return `Pass ${pass}, frame ${position+1}/30: ${pass === 2 ? 'slightly lift your chin; ' : ''}slowly turn toward ${angle < 0 ? 'your left' : 'your right'} (${Math.abs(angle)}°). Keep your torso still, expression neutral and mouth closed. Aim for overlapping views; avoid blur.`;
}
