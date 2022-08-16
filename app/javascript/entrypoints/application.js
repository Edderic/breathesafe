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
import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router';
import Vue3Geolocation from 'vue3-geolocation';

import App from '../app.vue';
import { useEventStore } from '../stores/event_store.js';
import { useMainStore } from '../stores/main_store.js';
import MapEvents from '../map_events.vue'
import Analytics from '../analytics.vue'
import Home from '../home.vue'
import About from '../about.vue'

document.addEventListener('DOMContentLoaded', () => {
  const pinia = createPinia();
  // 1. Define route components.
  // These can be imported from other files

  // 2. Define some routes
  // Each route should map to a component.
  // We'll talk about nested routes later.
  const routes = [
    { path: '/', component: Home },
    { path: '/about', component: About },
  ]

  // 3. Create the router instance and pass the `routes` option
  // You can pass in additional options here, but let's
  // keep it simple for now.
  const router = createRouter({
    // 4. Provide the history implementation to use. We are using the hash history for simplicity here.
    history: createWebHashHistory(),
    routes, // short for `routes: routes`
  })

  // 5. Create and mount the root instance.
  const app = createApp(App)
  // Make sure to _use_ the router instance to make the
  // whole app router-aware.
  app.use(router).use(pinia)

  app.mount('#app')


});
