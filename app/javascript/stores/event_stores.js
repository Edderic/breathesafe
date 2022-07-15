import { defineStore } from 'pinia'
import { useMainStore } from './main_store'
import axios from 'axios'
import { deepSnakeToCamel, setupCSRF } from  '../misc'


// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    events: [],
    displayables: []
  }),
  getters: {
  },
  actions: {
    addEvent(event) {
      let camelized = deepSnakeToCamel(event)
      this.events.push(camelized)
    },
    load() {
      setupCSRF()
      axios.get('/events')
        .then(response => {
          console.log(response)
          if (response.status == 200) {
            let camelized = deepSnakeToCamel(response.data.events)
            this.events = camelized
            this.displayables = camelized
            let markers = []

            for (let event of this.events) {
              let center = event.placeData.center
              markers.push({'center': center})
            }

            const mainStore = useMainStore()
            mainStore.setMarkers(markers)
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
