import axios from 'axios';
import { defineStore } from 'pinia'
import { MASKS, Mask  } from '../masks.js'
import { airCleaners, AirCleaner } from '../air_cleaners.js'
import { UpperRoomGermicidalUV, UPPER_ROOM_GERMICIDAL_UV } from '../upper_room_germicidal_uv.js'
import { Intervention } from '../interventions.js'
import { useShowMeasurementSetStore } from './show_measurement_set_store';


// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    nullIntervention: "",
    interventions: [],
    numPeopleToInvestIn: 5,
    event: "",
  }),
  actions: {
    load(event) {
      this.event = event
      this.reload()
    },
    setNumPeopleToInvestIn(num) {
      this.numPeopleToInvestIn = num
    },
    reload() {
      this.nullIntervention = new Intervention(this.event, [])

      // TODO: find the number of people that could upgrade to a mask
      this.interventions = [
        this.nullIntervention,
        new Intervention(
          this.event,
          [
            new AirCleaner(airCleaners[0], this.event)
          ]
        ),
        new Intervention(
          this.event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[0], this.event)
          ]
        ),
        new Intervention(
          this.event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[1], this.event)
          ]
        ),
        new Intervention(
          this.event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[2], this.event)
          ]
        ),
        new Intervention(
          this.event,
          [
            new Mask(MASKS[0], this.numPeopleToInvestIn)
          ]
        ),
        new Intervention(
          this.event,
          [
            new Mask(MASKS[1], this.numPeopleToInvestIn)
          ]
        ),
        new Intervention(
          this.event,
          [
            new Mask(MASKS[2], this.numPeopleToInvestIn)
          ]
        ),
        new Intervention(
          this.event,
          [
            new Mask(MASKS[2], this.numPeopleToInvestIn),
            new AirCleaner(airCleaners[0], this.event)
          ]
        ),
      ]

      this.interventions = this.interventions.sort((a, b) => a.computeRisk() - b.computeRisk())
    }
  }
});
