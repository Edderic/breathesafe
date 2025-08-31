/* Copy @mediapipe/tasks-vision wasm assets to public/mediapipe/wasm */
const fs = require('fs');
const path = require('path');

function copyRecursiveSync(src, dest) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      const s = path.join(src, entry);
      const d = path.join(dest, entry);
      copyRecursiveSync(s, d);
    }
  } else {
    fs.copyFileSync(src, dest);
  }
}

function resolveTasksVisionDir() {
  const candidates = [
    '@mediapipe/tasks-vision/vision_bundle.mjs',
    '@mediapipe/tasks-vision/vision_bundle.js',
    '@mediapipe/tasks-vision'
  ];
  for (const id of candidates) {
    try {
      const resolved = require.resolve(id);
      return path.dirname(resolved);
    } catch (_) {
      // continue
    }
  }
  throw new Error('Unable to resolve @mediapipe/tasks-vision entry file');
}

try {
  const pkgDir = resolveTasksVisionDir();
  const wasmDir = path.join(pkgDir, 'wasm');
  const publicDir = path.join(process.cwd(), 'public', 'mediapipe', 'wasm');
  copyRecursiveSync(wasmDir, publicDir);
  console.log('Copied MediaPipe wasm assets to', publicDir);
} catch (e) {
  console.warn('Could not copy MediaPipe wasm assets:', e.message);
}
