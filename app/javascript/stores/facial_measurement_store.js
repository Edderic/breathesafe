import { defineStore } from 'pinia'
import { getFacialMeasurements } from '../facial_measurements.js'

export const useFacialMeasurementStore = defineStore('facialMeasurement', {
  state: () => ({
    faceWidthMm: 155,
    bitragionSubnasaleArcMm: 255,
    faceLengthMm: 127,
    noseProtrusionMm: 28,

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
