// Cache the version-1 person-feature model. All pilot inference is local.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const url = 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/1/selfie_multiclass_256x256.tflite';
const expected = 'c6748b1253a99067ef71f7e26ca71096cd449baefa8f101900ea23016507e0e0';
(async () => {
  const response = await fetch(url);
  if (!response.ok) throw Error('Segmenter download failed: '+response.status);
  const bytes = Buffer.from(await response.arrayBuffer());
  if (crypto.createHash('sha256').update(bytes).digest('hex') !== expected) throw Error('Pinned segmentation hash changed.');
  const directory = path.resolve(__dirname, '../public/mediapipe/segmentation');
  await fs.mkdir(directory, { recursive: true });
  await fs.writeFile(path.join(directory, 'selfie_multiclass.tflite'), bytes);
  await fs.writeFile(path.join(directory, 'assets.json'), JSON.stringify({ url, sha256: expected, sdk_version: '0.10.18',
    categories: ['background', 'hair', 'body_skin', 'face_skin', 'clothes', 'other'], selected_categories: [1, 3],
    limitations: 'Face skin can include neck; ears may be missed. Every mask requires manual review and correction.' }, null, 2));
  console.log('Cached pinned local person-feature segmentation model.');
})().catch(error => { console.error(error.message); process.exitCode = 1; });
