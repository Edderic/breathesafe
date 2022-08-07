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
    interventions: []
  }),
  actions: {
    load(event) {
      this.nullIntervention = new Intervention(event, [])

      // TODO: find the number of people that could upgrade to a mask
      this.interventions = [
        this.nullIntervention,
        new Intervention(
          event,
          [
            new AirCleaner(airCleaners[0], event)
          ]
        ),
        new Intervention(
          event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[0], event)
          ]
        ),
        new Intervention(
          event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[1], event)
          ]
        ),
        new Intervention(
          event,
          [
            new UpperRoomGermicidalUV(UPPER_ROOM_GERMICIDAL_UV[2], event)
          ]
        ),
        new Intervention(
          event,
          [
            new Mask(MASKS[0], 3)
          ]
        ),
        new Intervention(
          event,
          [
            new Mask(MASKS[1], 3)
          ]
        ),
        new Intervention(
          event,
          [
            new Mask(MASKS[2], 3)
          ]
        ),
        new Intervention(
          event,
          [
            new Mask(MASKS[2], 3),
            new AirCleaner(airCleaners[0], event)
          ]
        ),
      ]

      this.interventions = this.interventions.sort((a, b) => a.computeRisk() - b.computeRisk())
    }
  }
});
