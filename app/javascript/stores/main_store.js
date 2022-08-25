import axios from 'axios';
import { useEventStores } from './event_stores'
import { useShowMeasurementSetStore } from './show_measurement_set_store'
import { useAnalyticsStore } from './analytics_store'
import { defineStore } from 'pinia'
import { setupCSRF } from '../misc'
import { MASKS, Mask  } from '../masks.js'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    openedMarkerId: null,
    markers: [],
    zoom: 7,
    focusTab: 'maps',
    focusSubTab: "Analytics",
    signedIn: false,
    currentUser: undefined,
    message: ''
  }),
  getters: {
    isAdmin(state) {
      if (!state.currentUser) {
        return false
      }

      return state.currentUser.admin
    }
  },
  actions: {
    centerMapTo(id) {
      let eventStores = useEventStores()
      let event = eventStores.events.find((ev) => { return ev.id == id })

      // indicate that the event was selected
      for (let ev of eventStores.events) {
        if (ev.id == event.id) {
          event.clicked = true
        } else {
          ev.clicked = false
        }
      }

      // update Google Maps to center at the location of the event
      this.center = event.placeData.center

      let element_to_scroll_to = document.getElementById(`measurements-${id}`);
      element_to_scroll_to.scrollIntoView({behavior: 'smooth'});
    },
    async showAnalysis(id) {
      let eventStores = useEventStores()
      const analyticsStore = useAnalyticsStore()
      const showMeasurementSetStore = useShowMeasurementSetStore()
      let event = await eventStores.findOrLoad(id);
      showMeasurementSetStore.setMeasurementSet(event)
      analyticsStore.load(event)
    },
    setMessage(message) {
      this.message = message
    },
    async getCurrentUser() {
      setupCSRF()

      await axios.get('/users/get_current_user.json')
        .then(response => {
          this.currentUser = response.data.currentUser;
          this.signedIn = !!response.data.currentUser;
          console.log('this.signedIn', this.signedIn)
          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Could not get current user.";
          this.currentUser = undefined;
          this.signedIn = false;
          // whatever you want
        })

    },
    setGMapsPlace(center) {
      this.center = center
      this.zoom = 15;
    },
    setFocusTab(tabToFocus) {
      this.focusTab = tabToFocus
    }
  }
});
