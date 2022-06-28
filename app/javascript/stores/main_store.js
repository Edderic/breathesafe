import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useMainStore = defineStore('main', {
  state: () => ({
    center: {lat: 51.093048, lng: 6.842120},
    zoom: 7,
  }),
  actions: {
    setPlace(place) {
      const loc = place.geometry.location;
      this.center = { lat: loc.lat(), lng: loc.lng() };
      this.zoom = 15;
    }
  }
});
