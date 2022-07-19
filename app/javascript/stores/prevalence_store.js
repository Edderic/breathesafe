import axios from 'axios';
import { useEventStores } from './event_stores'
import { useShowMeasurementSetStore } from './show_measurement_set_store'
import { defineStore } from 'pinia'
import { setupCSRF } from '../misc'

// TODO: use the last location that the user was in, as the default
// the first argument is a unique id of the store across your application
export const usePrevalenceStore = defineStore('prevalence', {
  state: () => ({
    numPositivesLastSevenDays: 100,
    numPopulation: 1000,
    uncountedFactor: 10,
  }),
  actions: {

  }
});
