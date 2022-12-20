import { defineStore } from 'pinia'
import { Intervention } from '../interventions.js';
import { Mask, MASKS } from '../masks.js'
import { useMainStore } from './main_store'
import { useProfileStore } from './profile_store'
import { usePrevalenceStore } from './prevalence_store'
import axios from 'axios'
import { computeRiskWithVariableOccupancy, deepSnakeToCamel, setupCSRF, round } from  '../misc'


// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    location: { lat: 0, lng: 0},
    durationHours: 1,
    events: [],
    displayables: [],
    masks: [],
    selectedMask: new Mask(MASKS[0], 1, 1),
  }),
  getters: {
  },
  actions: {
    addEvent(event) {
      let camelized = deepSnakeToCamel([event])
      const mainStore = useMainStore()

      this.setDistance(mainStore, camelized)
      this.events.push(camelized[0])
      this.displayables = this.events
    },
    setDistance(mainStore, events) {
      let milesPerEuclidean = 0.8 / 0.012414

      for (let event of events) {
        let x = (mainStore.whereabouts.lat - event.placeData.center.lat)**2
        let y = (mainStore.whereabouts.lng - event.placeData.center.lng)**2

        event.distance = round(Math.sqrt(x + y) * milesPerEuclidean, 1)
      }
    },
    loadMasks() {
      // Load masks
      let masks = []
      for (let mask of MASKS) {
        masks.push(new Mask(mask, 1, 1))
        masks.push(new Mask(mask, 1, 2))
      }

      this.masks = masks
    },
    async load() {
      setupCSRF()

      const mainStore = useMainStore()
      const profileStore = useProfileStore()

      await mainStore.getCurrentUser();
      await profileStore.loadProfile()
      let success = true
      await axios.get('/events')
        .then(response => {
          console.log(response)
          if (response.status == 200) {
            let camelized = deepSnakeToCamel(response.data.events)
            this.setDistance(mainStore, camelized)
            this.events = camelized
            this.displayables = this.events
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          success = false
          // whatever you want
        })

      this.loadMasks()
    },

    async findOrLoad(id) {
      // TODO: maybe create a Rails route to find a specific analytics to load?
      let event = this.events.find((ev) => { return ev.id == parseInt(id) })

      if (!event) {
        await this.load()
        event = this.events.find((ev) => { return ev.id == parseInt(id) })
      }

      return event
    },

    computeRiskAll(selectedMask) {
      /*
       * Parameters:
       *
       *   selectedMask: Mask object
       *
       */

      // numWays: Number
      //   Whether or not the mask is applied one way or both ways.
      //   1 is for 1-way masking
      //   2 is for 2-way masking.
      //     i.e. Assumes everyone will be wearing the selectedMask
      let numWays = 1;
      if (selectedMask) {
        numWays = selectedMask.numWays
      }
      else {
        numWays = 1
      }

      // TODO: make this a query parameter using router

      for (let event of this.events) {
        let intervention = new Intervention(
          event,
          [
          ],
          this.selectedMask,
        )

        if (numWays == 2) {
          let intervention = new Intervention(
            event,
            [
            ],
            this.selectedMask,
            this.selectedMask
          )
        }

        event['risk'] = intervention.computeRisk(this.durationHours)
      }
    },
  }
});
