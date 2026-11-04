let segmenter;
const modelHash = 'c6748b1253a99067ef71f7e26ca71096cd449baefa8f101900ea23016507e0e0';
const hash = async bytes => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), v => v.toString(16).padStart(2, '0')).join('');
self.onmessage = async ({ data: { id, image } }) => {
  try {
    if (!segmenter) {
      const base = '/mediapipe/experiment/';
      const manifest = await (await fetch(base+'assets.json')).json();
      if (manifest.sdk_version !== '0.10.18') throw Error('Expected MediaPipe JS 0.10.18.');
      for (const [file, expected] of Object.entries(manifest.runtime_assets)) {
        const r = await fetch(base+file);
        if (!r.ok || await hash(await r.arrayBuffer()) !== expected) throw Error('MediaPipe runtime hash mismatch.');
      }
      const response = await fetch('/mediapipe/segmentation/selfie_multiclass.tflite');
      if (!response.ok) throw Error('Run node scripts/setup_webcam_segmenter.cjs and node scripts/setup_face_landmarker.cjs.');
      const bytes = await response.arrayBuffer();
      if (await hash(bytes) !== modelHash) throw Error('Segmenter hash mismatch.');
      self.exports = {}; importScripts(base+'vision_bundle_worker.js');
      segmenter = await self.exports.ImageSegmenter.createFromOptions(await self.exports.FilesetResolver.forVisionTasks(base+'wasm'), {
        baseOptions: { modelAssetBuffer: new Uint8Array(bytes), delegate: 'CPU' },
        runningMode: 'IMAGE', outputCategoryMask: true, outputConfidenceMasks: false,
      });
    }
    segmenter.segment(image, result => {
      const mask = result.categoryMask, categories = mask.getAsUint8Array();
      const values = Uint8ClampedArray.from(categories, v => v === 1 || v === 3 ? 255 : 0);
      self.postMessage({ id, width: mask.width, height: mask.height, values, provenance: {
        sdk_version: '0.10.18', model_sha256: modelHash, selected_categories: [1, 3], delegate: 'CPU', correction: 'none', review_status: 'unreviewed_generated_mask',
      } }, [values.buffer]);
    });
  } catch (error) { self.postMessage({ id, error: error.message }); }
  finally { image?.close(); }
};
