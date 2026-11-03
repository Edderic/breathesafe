import { defineConfig } from 'vite'
import VuePlugin from '@vitejs/plugin-vue'
import RubyPlugin from 'vite-plugin-ruby'
import { privateWebcamGuard, privateWebcamDirectory } from './scripts/private_webcam_vite.mjs'

export default defineConfig({
  plugins: [
    privateWebcamGuard(),
    VuePlugin(),
    RubyPlugin(),
  ],
  server: { fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', `${privateWebcamDirectory}/**`] } },
})
