import { defineStore } from 'pinia'
import { getFacialMeasurements } from '../facial_measurements.js'

export const useFacialMeasurementStore = defineStore('facialMeasurement', {
  state: () => ({
    bitragionSubnasaleArcMm: getFacialMeasurements().bitragionSubnasaleArcMm || 230,
    faceWidthMm: getFacialMeasurements().faceWidthMm || 137,
    noseProtrusionMm: getFacialMeasurements().noseProtrusionMm || 27,
    facialHairBeardLengthMm: getFacialMeasurements().facialHairBeardLengthMm || 0
  }),
  actions: {
    updateFacialMeasurements(measurements) {
      if (measurements.bitragionSubnasaleArcMm) {
        this.bitragionSubnasaleArcMm = measurements.bitragionSubnasaleArcMm
      }
      if (measurements.faceWidthMm) {
        this.faceWidthMm = measurements.faceWidthMm
      }
      if (measurements.noseProtrusionMm) {
        this.noseProtrusionMm = measurements.noseProtrusionMm
      }
      if (measurements.facialHairBeardLengthMm) {
        this.facialHairBeardLengthMm = measurements.facialHairBeardLengthMm
      }
    },
    updateFromRouteQuery(query) {
      const measurements = {}
      if (query.bitragionSubnasaleArcMm) {
        measurements.bitragionSubnasaleArcMm = parseFloat(query.bitragionSubnasaleArcMm)
      }
      if (query.faceWidthMm) {
        measurements.faceWidthMm = parseFloat(query.faceWidthMm)
      }
      if (query.noseProtrusionMm) {
        measurements.noseProtrusionMm = parseFloat(query.noseProtrusionMm)
      }
      if (query.facialHairBeardLengthMm) {
        measurements.facialHairBeardLengthMm = parseFloat(query.facialHairBeardLengthMm)
      }
      this.updateFacialMeasurements(measurements)
    }
  }
}) 