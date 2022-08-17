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
    displayables: []
  }),
  getters: {
  },
  actions: {
    async load() {
      setupCSRF()

      const profileStore = useProfileStore()

      axios.get('/events')
        .then(response => {
          console.log(response)
          if (response.status == 200) {
            let camelized = deepSnakeToCamel(response.data.events)
            this.events = camelized
            this.displayables = this.events

            let markers = []

            for (let event of this.events) {
              let center = event.placeData.center
              event.clicked = false
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

        await profileStore.loadProfile()
        this.computeRiskAll()
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

    computeRiskAll() {
      const prevalenceStore = usePrevalenceStore()
      const profileStore = useProfileStore()

      const probaRandomSampleOfOneIsInfectious = prevalenceStore.numPositivesLastSevenDays
        * prevalenceStore.uncountedFactor / prevalenceStore.numPopulation

      const susceptibleMaskType = prevalenceStore.maskType

      for (let event of this.events) {
        const flowRate = event.roomUsableVolumeCubicMeters * event.totalAch

        event['risk'] = computeRiskWithVariableOccupancy(
          event,
          probaRandomSampleOfOneIsInfectious,
          flowRate,
          event.roomUsableVolumeCubicMeters,
          susceptibleMaskType,
          profileStore.eventDisplayRiskTime
        )
      }

      for (let event of this.displayables) {
        const flowRate = event.roomUsableVolumeCubicMeters * event.totalAch

        event['risk'] = computeRiskWithVariableOccupancy(
          event,
          probaRandomSampleOfOneIsInfectious,
          flowRate,
          event.roomUsableVolumeCubicMeters,
          susceptibleMaskType,
          profileStore.eventDisplayRiskTime
        )
      }
    }
  }
});
