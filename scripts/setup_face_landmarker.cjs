// Cache a versioned model and matching SDK/WASM for the local experiment.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const directory = path.join(root, 'public/mediapipe/experiment');
const url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task';
const expectedModelHash = '64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff';
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
(async () => {
  await fs.mkdir(path.join(directory, 'wasm'), { recursive: true });
  const sdk = path.dirname(require.resolve('@mediapipe/tasks-vision'));
  const version = JSON.parse(await fs.readFile(path.join(sdk, 'package.json'))).version;
  const response = await fetch(url);
  if (!response.ok) throw Error(`Model download failed: ${response.status}`);
  const model = Buffer.from(await response.arrayBuffer());
  if (model.length < 1000000 || model.length > 30000000) throw Error('Unexpected model size');
  if (hash(model) !== expectedModelHash) throw Error('Versioned model checksum changed; review the asset before updating the pinned hash.');
  const assets = {};
  for (const [source, target] of [['vision_bundle.cjs', 'vision_bundle_worker.js'],
    ...['vision_wasm_internal.js', 'vision_wasm_internal.wasm', 'vision_wasm_nosimd_internal.js', 'vision_wasm_nosimd_internal.wasm'].map(file => ['wasm/'+file, 'wasm/'+file])]) {
    const bytes = await fs.readFile(path.join(sdk, source));
    await fs.writeFile(path.join(directory, target), bytes); assets[target] = hash(bytes);
  }
  await fs.writeFile(path.join(directory, 'face_landmarker.task'), model);
  await fs.writeFile(path.join(directory, 'assets.json'), JSON.stringify({ sdk_version: version, model_url: url,
    model_sha256: hash(model), model_file: 'face_landmarker.task', runtime_assets: assets }, null, 2)+'\n');
  console.log(`Cached MediaPipe ${version}; model SHA-256 ${hash(model)}`);
})().catch(error => { console.error(error.message); process.exitCode = 1; });
