import { defineStore } from 'pinia'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    zoom: 7,
    focusTab: 'events'
  }),
  actions: {
    setGMapsPlace(center) {
      this.center = center
      this.zoom = 15;
    },
    setFocusTab(tabToFocus) {
      this.focusTab = 'event'
    }
  }
});
