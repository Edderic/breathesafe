import axios from 'axios';
import { useEventStores } from './event_stores'
import { defineStore } from 'pinia'
import { setupCSRF } from '../misc'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    markers: [],
    zoom: 7,
    focusTab: 'events',
    signedIn: false,
    currentUser: undefined,
    message: ''
  }),
  actions: {
    focusEvent(id) {
      let eventStores = useEventStores()

      let event = eventStores.events.find((ev) => { return ev.id == id })

      for (let ev of eventStores.events) {
        if (ev.id == event.id) {
          event.clicked = true
        } else {
          ev.clicked = false
        }
      }


      this.center = event.placeData.center
    },
    setMarkers(markers) {
      this.markers = markers
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
