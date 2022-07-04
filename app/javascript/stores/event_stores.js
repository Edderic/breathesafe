import { defineStore } from 'pinia'
import axios from 'axios'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    events: []
  }),
  getters: {
  },
  actions: {
  }
});
