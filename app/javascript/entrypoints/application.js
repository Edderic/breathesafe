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
import Vue3Progress from "vue3-progress";
import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router';
import Vue3Geolocation from 'vue3-geolocation';

import Analytics from '../analytics.vue'
import App from '../app.vue';
import AddMeasurements from '../add_measurements.vue';
import FAQs from '../faqs.vue';
import Venues from '../map_events.vue'
import Landing from '../landing.vue'
import Profile from '../profile.vue'
import Registration from '../registration.vue'
import SignIn from '../sign_in.vue'
import { useEventStore } from '../stores/event_store.js';
import { useMainStore } from '../stores/main_store.js';

document.addEventListener('DOMContentLoaded', () => {
  const app = createApp(App);
  const pinia = createPinia();
  // 1. Define route components.
  // These can be imported from other files
  const About = { template: '<div>About</div>' }

  // 2. Define some routes
  // Each route should map to a component.
  // We'll talk about nested routes later.
  const routes = [
    { path: '/', component: Landing, name: 'Landing' },
    { path: '/venues', component: Venues, name: 'Venues' },
    { path: '/analytics/:id', component: Analytics, name: 'Analytics' },
    { path: '/signin', component: SignIn, name: 'SignIn' },
    { path: '/events/new', component: AddMeasurements, name: 'AddMeasurements' },
    { path: '/profile', component: Profile, name: 'Profile' },
    { path: '/register', component: Registration, name: 'Registration' },
    { path: '/faqs', component: FAQs, name: 'FAQs' },
  ]

  // 3. Create the router instance and pass the `routes` option
  // You can pass in additional options here, but let's
  // keep it simple for now.
  const router = createRouter({
    // 4. Provide the history implementation to use. We are using the hash history for simplicity here.
    history: createWebHashHistory(),
    routes, // short for `routes: routes`
    scrollBehavior(to, from, savedPosition) {
      if (to.hash) {

        let element_to_scroll_to = document.getElementById(to.hash.slice(1));
        element_to_scroll_to.scrollIntoView(
          {
            behavior: 'smooth',
          }
        );
      }
    }
  })

  const options = {
    position: "fixed",
    height: "3px",
    display: 'block',
    opacity: 1

   // color: "<Your Color>",
  };

  // Make sure to _use_ the router instance to make the
  // whole app router-aware.

  // A store could be good for Manipulating the Google Maps component via a
  // search component contained in another.

  app.use(VueGoogleMaps, {
      load: {
          key: window.gon.GOOGLE_MAPS_API_KEY,
          libraries: 'places'
      },
  // }).use(pinia).use(Vue3Geolocation).mount('#app')
  })
    .use(pinia).use(Vue3Progress, options).use(Vue3Geolocation).use(router).mount('#app')


  const mainStore = useMainStore();
  const eventsStore = useEventStore();
});
