import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    events: []
  }),
  getters: {
  },
  actions: {
    addEvent(event) {
      this.events.unshift(event)
    }
  }
});
