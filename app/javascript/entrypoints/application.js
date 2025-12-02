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

// Global styles
import '../index.css'
//
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import VueGoogleMaps from '@fawmi/vue-google-maps';
import Vue3Progress from "vue3-progress";
import VueMathjax from 'vue-mathjax-next';

import Datepicker from "@vuepic/vue-datepicker";
import '@vuepic/vue-datepicker/dist/main.css'

import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router';
import Vue3Geolocation from 'vue3-geolocation';

import Analytics from '../analytics.vue'
import App from '../app.vue';
import AddMeasurements from '../add_measurements.vue';
import ConsentForm from '../consent_form.vue'
import FAQs from '../faqs.vue';
import Disclaimer from '../disclaimer.vue';
import Venues from '../map_events.vue'
import Landing from '../landing.vue'
import Mask from '../add_mask.vue'
import FitTest from '../fit_test.vue'
import FitTests from '../fit_tests.vue'
import FitTestsImport from '../fit_tests_import.vue'
import BulkFitTestsImportsList from '../bulk_fit_tests_imports_list.vue'
import MaskRecommenderOnboarding from '../mask_recommender_onboarding.vue'
import MeasurementDevices from '../measurement_devices.vue'
import MeasurementDevice from '../measurement_device.vue'
import Masks from '../masks.vue'
import Profile from '../profile.vue'
import PrivacyPolicy from '../privacy_policy.vue'
import RespiratorUsers from '../respirator_users.vue'
import RespiratorUser from '../respirator_user.vue'
import Registration from '../registration.vue'
import SignIn from '../sign_in.vue'
import TermsOfService from '../terms_of_service.vue'
import AdminStudyParticipants from '../admin_study_participants.vue'
import { useEventStore } from '../stores/event_store.js';
import { useMainStore } from '../stores/main_store.js';

document.addEventListener('DOMContentLoaded', () => {
  const mountEl = document.getElementById('app');
  if (!mountEl) {
    console.error('Breathesafe: #app mount element not found; aborting Vue mount.');
    return;
  }

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
    { path: '/respirator_users', component: RespiratorUsers, name: 'RespiratorUsers' },
    { path: '/masks', component: Masks, name: 'Masks' },
    { path: '/masks/new', component: Mask, name: 'NewMask' },
    { path: '/masks/:id', component: Mask, name: 'ShowMask' },
    { path: '/masks/:id/edit', component: Mask, name: 'EditMask' },
    { path: '/respirator_user/:id', component: RespiratorUser, name: 'RespiratorUser' },
    { path: '/fit_tests/new', component: FitTest, name: 'NewFitTest' },
    { path: '/fit_tests/bulk_imports', component: BulkFitTestsImportsList, name: 'BulkFitTestsImportsList' },
    { path: '/fit_tests/bulk_imports/new', component: FitTestsImport, name: 'NewBulkFitTestsImport' },
    { path: '/fit_tests/bulk_imports/:id', component: FitTestsImport, name: 'BulkFitTestsImport' },
    { path: '/fit_tests/:id/edit', component: FitTest, name: 'EditFitTest' },
    { path: '/fit_tests/:id', component: FitTest, name: 'ViewFitTest' },
    { path: '/fit_tests', component: FitTests, name: 'FitTests' },
    { path: '/onboarding', component: MaskRecommenderOnboarding, name: 'MaskRecommenderOnboarding' },
    { path: '/measurement_devices', component: MeasurementDevices, name: 'MeasurementDevices' },
    { path: '/measurement_devices/new', component: MeasurementDevice, name: 'NewMeasurementDevice' },
    { path: '/measurement_devices/:id', component: MeasurementDevice, name: 'ShowMeasurementDevice' },
    { path: '/measurement_device', component: MeasurementDevice, name: 'MeasurementDevice' },
    { path: '/venues', component: Venues, name: 'Venues' },
    { path: '/analytics/:id', component: Analytics, name: 'Analytics' },
    { path: '/signin', component: SignIn, name: 'SignIn' },
    { path: '/events/new', component: AddMeasurements, name: 'AddMeasurements' },
    { path: '/events/:id/:action', component: AddMeasurements, name: 'UpdateOrCopyMeasurements' },
    { path: '/profile', component: Profile, name: 'Profile' },
    { path: '/register', component: Registration, name: 'Registration' },
    { path: '/faqs', component: FAQs, name: 'FAQs' },
    { path: '/disclaimer', component: Disclaimer, name: 'Disclaimer' },
    { path: '/terms_of_service', component: TermsOfService, name: 'TermsOfService' },
    { path: '/consent_form', component: ConsentForm, name: 'ConsentForm' },
    { path: '/privacy', component: PrivacyPolicy, name: 'PrivacyPolicy' },
    { path: '/admin/study_participants', component: AdminStudyParticipants, name: 'AdminStudyParticipants' },
  ]

  // 3. Create the router instance and pass the `routes` option
  // You can pass in additional options here, but let's
  // keep it simple for now.
  const router = createRouter({
    // 4. Provide the history implementation to use. We are using the hash history for simplicity here.
    history: createWebHashHistory(),
    routes, // short for `routes: routes`
    scrollBehavior(to, from, savedPosition) {
      if (to.hash && to.hash.startsWith('#') && to.hash.length > 1) {
        const elementToScrollTo = document.getElementById(to.hash.slice(1));
        if (elementToScrollTo && typeof elementToScrollTo.scrollIntoView === 'function') {
          elementToScrollTo.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }
  })

  // Router guard: show consent form after login if needed
  router.beforeEach(async (to, from, next) => {
    const main = useMainStore();
    // Ensure current user info is loaded once per session
    if (main.currentUser === undefined) {
      await main.getCurrentUser();
    }

    const user = main.currentUser;
    // Ensure consentFormVersion is a string, not an object
    const latest = typeof main.consentFormVersion === 'string'
      ? main.consentFormVersion
      : (main.consentFormVersion ? String(main.consentFormVersion) : '');

    const needsConsent = !!user && !!latest && user.consent_form_version_accepted !== latest && !main.consentDismissedForSession;
    const navigatingToConsent = to.name === 'ConsentForm';

    // Only intercept normal navigation; do not loop
    if (needsConsent && !navigatingToConsent) {
      next({
        name: 'ConsentForm',
        query: {
          return_to_name: to.name || 'Landing',
          return_to_query: JSON.stringify(to.query || {}),
          return_to_params: JSON.stringify(to.params || {}),
          latest_version: latest
        }
      });
      return;
    }

    next();
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
  }).use(VueMathjax)
    .use(pinia).use(Datepicker).use(Vue3Progress, options).use(Vue3Geolocation).use(router).mount(mountEl)


  const mainStore = useMainStore();
  const eventsStore = useEventStore();
});
