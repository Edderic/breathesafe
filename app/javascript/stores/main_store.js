import { defineStore } from 'pinia'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    zoom: 7,
  }),
  actions: {
    setGMapsPlace(place) {
      const loc = place.geometry.location;
      this.center = { lat: loc.lat(), lng: loc.lng() };
      this.zoom = 15;
    }
  }
});
