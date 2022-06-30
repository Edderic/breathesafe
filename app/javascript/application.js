import { createApp } from 'vue';
import { createPinia } from 'pinia';
import VueGoogleMaps from 'vue-google-maps';
import Vue3Geolocation from 'vue3-geolocation';
import App from './app';
import { useEventStore } from './stores/event_store.js';
import { useEventsStore } from './stores/events_store.js';
import { useMainStore } from './stores/main_store.js';

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
  const eventStore = useEventStore();
  const eventsStore = useEventsStore();
});
