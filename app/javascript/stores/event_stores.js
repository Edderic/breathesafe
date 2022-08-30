import { defineStore } from 'pinia'
import { Mask, MASKS } from '../masks.js'
import { useMainStore } from './main_store'
import { useProfileStore } from './profile_store'
import { usePrevalenceStore } from './prevalence_store'
import axios from 'axios'
import { computeRiskWithVariableOccupancy, deepSnakeToCamel, setupCSRF } from  '../misc'


// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useEventStores = defineStore('events', {
  state: () => ({
    events: [],
    displayables: [],
    masks: [],
    selectedMask: new Mask(MASKS[0], 1),
  }),
  getters: {
  },
  actions: {
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

      // Load masks
      let masks = []
      for (let mask of MASKS) {
        masks.push(new Mask(mask, 1, 1))
        masks.push(new Mask(mask, 1, 2))
      }

      this.masks = masks
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

    computeRiskAll(eventDisplayRiskTime, selectedMask) {
      /*
       * Parameters:
       *   eventDisplayRiskTime: String
       *     e.g. "At max occupancy", "At 75% occupancy", ... "At this hour"
       *
       *   selectedMask: Mask object
       *
       */

      // numWays: Number
      //   Whether or not the mask is applied one way or both ways.
      //   1 is for 1-way masking
      //   2 is for 2-way masking.
      //     i.e. Assumes everyone will be wearing the selectedMask
      const numWays = selectedMask.numWays

      const prevalenceStore = usePrevalenceStore()
      //prevalenceStore.maskType  const susceptibleMaskType = prevalenceStore.maskType
      // TODO: make this a query parameter using router
      const susceptibleMaskType = selectedMask.filtrationType
      const ascertainmentBiasMitigator = 10
      let probaRandomSampleOfOneIsInfectious;

      let riskTime;

      if (eventDisplayRiskTime) {
        riskTime = eventDisplayRiskTime
      } else {
        riskTime = 'At max occupancy'
      }

      for (let event of this.events) {
        const flowRate = event.roomUsableVolumeCubicMeters * event.totalAch

        probaRandomSampleOfOneIsInfectious = event['naivePrevalence'] * ascertainmentBiasMitigator

        event['risk'] = computeRiskWithVariableOccupancy(
          event,
          probaRandomSampleOfOneIsInfectious,
          flowRate,
          event.roomUsableVolumeCubicMeters,
          susceptibleMaskType,
          riskTime,
          numWays
        )
      }
    },
  }
});
