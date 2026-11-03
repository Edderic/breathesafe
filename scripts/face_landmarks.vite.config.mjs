import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';
import { privateWebcamGuard, privateWebcamDirectory } from './private_webcam_vite.mjs';

// Research-only local preview without a running Rails server or database.
export default defineConfig({
  root: fileURLToPath(new URL('../', import.meta.url)),
  plugins: [privateWebcamGuard(), vue()],
  server: { host: '127.0.0.1', port: 5178, strictPort: true,
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', `${privateWebcamDirectory}/**`] } },
  build: {
    outDir: 'tmp/face-preview-build',
    rollupOptions: {
      input: {
        generator: fileURLToPath(new URL('./flame_face_generator.html', import.meta.url)),
        landmarks: fileURLToPath(new URL('./face_landmarks_preview.html', import.meta.url)),
        webcam: fileURLToPath(new URL('./webcam_pilot.html', import.meta.url)),
      },
    },
  },
});
