/* Classic worker: Tasks Vision 0.10.18 loads its WASM glue with importScripts. */
let detector, provenance;
const base = '/mediapipe/experiment/';
async function digest(bytes) {
  const result = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(result), value => value.toString(16).padStart(2, '0')).join('');
}
async function checked(file, expected) {
  const response = await fetch(base+file, { cache: 'no-cache' });
  if (!response.ok) throw Error('Missing local MediaPipe assets. Run node scripts/setup_face_landmarker.cjs.');
  const bytes = await response.arrayBuffer();
  if (await digest(bytes) !== expected) throw Error('MediaPipe asset hash mismatch: '+file+'. Run setup again.');
  return bytes;
}
self.onmessage = async event => {
  const { id, type, image } = event.data;
  try {
    if (type === 'init') {
      const response = await fetch(base+'assets.json', { cache: 'no-cache' });
      if (!response.ok) throw Error('Run node scripts/setup_face_landmarker.cjs to install local experiment assets.');
      provenance = await response.json();
      const model = await checked(provenance.model_file, provenance.model_sha256);
      for (const [file, hash] of Object.entries(provenance.runtime_assets)) await checked(file, hash);
      self.exports = {};
      importScripts(base+'vision_bundle_worker.js');
      const { FaceLandmarker, FilesetResolver } = self.exports;
      const canvas = new OffscreenCanvas(720, 480);
      if (!canvas.getContext('webgl2')) throw Error('MediaPipe image preprocessing requires WebGL 2 in this browser. Enable hardware acceleration and retry. Inference still uses the CPU delegate.');
      detector = await FaceLandmarker.createFromOptions(await FilesetResolver.forVisionTasks(base+'wasm'), {
        canvas,
        baseOptions: { modelAssetBuffer: new Uint8Array(model), delegate: 'CPU' }, runningMode: 'IMAGE', numFaces: 1,
        minFaceDetectionConfidence: .5, minFacePresenceConfidence: .5,
        outputFaceBlendshapes: false, outputFacialTransformationMatrixes: false,
      });
      self.postMessage({ id, provenance: { ...provenance, delegate: 'CPU', running_mode: 'IMAGE', num_faces: 1,
        min_face_detection_confidence: .5, min_face_presence_confidence: .5, browser: navigator.userAgent } });
    } else if (type === 'detect' && detector) {
      const start = performance.now();
      const pixels = new OffscreenCanvas(image.width, image.height);
      const context = pixels.getContext('2d'); context.drawImage(image, 0, 0);
      const result = detector.detect(context.getImageData(0, 0, image.width, image.height));
      self.postMessage({ id, landmarks: result.faceLandmarks[0] || [], elapsed_ms: performance.now()-start });
    } else throw Error('Detector is not initialized.');
  } catch (error) { self.postMessage({ id, error: error.message }); }
  finally { image?.close(); }
};
