import { fileURLToPath } from 'node:url';

export const privateWebcamDirectory = fileURLToPath(new URL('../.private-webcam-runs', import.meta.url));

// Reject both ordinary URLs and Vite's /@fs/ route, including encoded spellings.
export function privateWebcamGuard() {
  return {
    name: 'private-webcam-runs',
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        let url;
        try { url = decodeURIComponent(request.url || '').replaceAll('\\', '/'); }
        catch { response.statusCode = 400; response.end(); return; }
        if (url.toLowerCase().includes('.private-webcam-runs')) {
          response.statusCode = 403; response.end('Private research captures are available only through the local processor.');
        } else next();
      });
    },
  };
}
