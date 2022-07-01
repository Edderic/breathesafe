// To see this message, add the following to the `<head>` section in your
// views/layouts/application.html.erb
//
//    <%= vite_client_tag %>
console.log('Vite ⚡️ Rails')

// If using a TypeScript entrypoint file:
//     <%= vite_typescript_tag 'application' %>
//
// If you want to use .jsx or .tsx, add the extension:
//     <%= vite_javascript_tag 'application.jsx' %>

console.log('Visit the guide for more information: ', 'https://vite-ruby.netlify.app/guide/rails')

// Example: Load Rails libraries in Vite.
//
// import * as Turbo from '@hotwired/turbo'
// Turbo.start()
//
// import ActiveStorage from '@rails/activestorage'
// ActiveStorage.start()
//
// // Import all channels.
// const channels = import.meta.globEager('./**/*_channel.js')

// Example: Import a stylesheet in app/frontend/index.css
// import '~/index.css'
//
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import VueGoogleMaps from '@fawmi/vue-google-maps';
import Vue3Geolocation from 'vue3-geolocation';
import App from '../app.vue';
import { useEventStore } from '../stores/event_store.js';
import { useMainStore } from '../stores/main_store.js';

document.addEventListener('DOMContentLoaded', () => {
  const app = createApp(App);
  const pinia = createPinia();
  // A store could be good for Manipulating the Google Maps component via a
  // search component contained in another.

  app.use(VueGoogleMaps, {
      load: {
          key: window.gon.GOOGLE_MAPS_API_KEY,
          libraries: 'places'
      },
  // }).use(pinia).use(Vue3Geolocation).mount('#app')
  }).use(pinia).use(Vue3Geolocation).mount('#app')

  const mainStore = useMainStore();
  const eventsStore = useEventStore();
});
