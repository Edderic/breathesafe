import { defineStore } from 'pinia'
import axios from 'axios'
import { setupCSRF } from  '../misc'


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
      this.events.push(event)
    },
    load() {
      setupCSRF()
      axios.get('/events')
        .then(response => {
          console.log(response)
          if (response.status == 200) {
            this.events = response.data.events
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          // whatever you want
        })
    }
  }
});
