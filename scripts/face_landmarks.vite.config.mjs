import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';

// Research-only local preview without a running Rails server or database.
export default defineConfig({
  root: fileURLToPath(new URL('../', import.meta.url)),
  plugins: [vue()],
  server: { host: '127.0.0.1', port: 5178, strictPort: true },
  build: {
    outDir: 'tmp/face-preview-build',
    rollupOptions: {
      input: {
        generator: fileURLToPath(new URL('./flame_face_generator.html', import.meta.url)),
        landmarks: fileURLToPath(new URL('./face_landmarks_preview.html', import.meta.url)),
      },
    },
  },
});
