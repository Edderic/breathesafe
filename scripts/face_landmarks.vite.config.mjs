import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath } from 'node:url';

// Research-only local preview without a running Rails server or database.
export default defineConfig({
  root: fileURLToPath(new URL('../', import.meta.url)),
  plugins: [vue()],
  server: { host: '127.0.0.1', port: 5178, strictPort: true },
});
