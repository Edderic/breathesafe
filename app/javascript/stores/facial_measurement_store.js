import { defineStore } from 'pinia'
import { getFacialMeasurements } from '../facial_measurements.js'

export const useFacialMeasurementStore = defineStore('facialMeasurement', {
  state: () => ({
    faceWidthMm: 137,
    bitragionSubnasaleArcMm: 230,
    faceLengthMm: 112,
    noseProtrusionMm: 27,

  }),
  actions: {
    updateFacialMeasurement(key, value) {
      this[key] = parseFloat(value)
    },
    updateFacialMeasurements(toQuery) {
      let facialMeasurements = getFacialMeasurements()

      for (let facialMeasurement in facialMeasurements) {
        if (toQuery[facialMeasurement]) {
          this[facialMeasurement] = parseFloat(toQuery[facialMeasurement])
        }
      }
    },
    getFacialMeasurement(key) {
      return this[key]
    }
  },
  getters: {
  }
})
