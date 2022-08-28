import { defineStore } from 'pinia'
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

    computeRiskAll(eventDisplayRiskTime) {
      const prevalenceStore = usePrevalenceStore()
      //prevalenceStore.maskType  const susceptibleMaskType = prevalenceStore.maskType
      // TODO: make this a query parameter using router
      const susceptibleMaskType = "None"
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
          riskTime
        )
      }
    }
  }
});
