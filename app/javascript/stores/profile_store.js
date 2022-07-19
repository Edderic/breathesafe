import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import axios from 'axios'
import { useMainStore } from './main_store'
import { usePrevalenceStore } from './prevalence_store'
import { useShowMeasurementSetStore } from './show_measurement_set_store'
import { useEventStore } from './event_store'
import { generateUUID, getMeasurementUnits, setupCSRF } from '../misc';

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useProfileStore = defineStore('profile', {
  state: () => ({
    currentUser: undefined,
    measurementUnits: {
      'lengthMeasurementType': "feet",
      'airDeliveryRateMeasurementType': 'cubic feet per minute',
    },
    systemOfMeasurement: "imperial",
    carbonDioxideMonitors: [
      {
        'name': "",
        'serial': "",
        'model': ""
      }
    ]
  }),
  getters: {
    // ...mapState(useMainStore, ['currentUser']),
    // ...mapWritableState(useMainStore, ['message']),
  },
  actions: {
    async loadProfile() {
      setupCSRF();

      let mainStore = useMainStore()
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser

      let hasProfile = false

      await axios.get(
        `/users/${currentUser.id}/profile.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.profile) {
            hasProfile = true

            prevalenceStore.numPositivesLastSevenDays = data.num_positive_cases_last_seven_days
            prevalenceStore.numPopulation = data.num_people_population
            prevalenceStore.uncountedFactor = data.uncounted_cases_multiplier

            this.message = data.message
            let profile = data.profile
            this.systemOfMeasurement = profile.measurement_system
            debugger
            this.measurementUnits = getMeasurementUnits(profile.measurement_system)
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load profile."
          // whatever you want
        })

      if (!hasProfile) {
        await this.createProfile()
      }
    },
    async createProfile() {
      setupCSRF();

      let mainStore = useMainStore()
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser

      let toSave = {
        'profile': {
          'measurement_system': this.systemOfMeasurement,
          'uncounted_cases_multiplier': prevalenceStore.uncountedFactor,
          'num_people_population': prevalenceStore.numPopulation,
          'num_positive_cases_last_seven_days': prevalenceStore.numPositivesLastSevenDays,
        }
      }

      await axios.post(
        `/users/${currentUser.id}/profile.json`,
        toSave
      )
        .then(response => {
          let data = response.data
          let profile = data.profile

          prevalenceStore.numPositivesLastSevenDays = profile.num_positive_cases_last_seven_days
          prevalenceStore.numPopulation = profile.num_people_population
          prevalenceStore.uncountedFactor = profile.uncounted_cases_multiplier

          this.message = data.message
          this.systemOfMeasurement = profile.systemOfMeasurement
          debugger
          this.measurementUnits = getMeasurementUnits(this.systemOfMeasurement)

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load profile."
          // whatever you want
        })
    },
    async updateProfile() {
      setupCSRF();

      let mainStore = useMainStore()
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser

      let toSave = {
        'profile': {
          'measurement_system': this.systemOfMeasurement,
          'uncounted_cases_multiplier': prevalenceStore.uncountedFactor,
          'num_people_population': prevalenceStore.numPopulation,
          'num_positive_cases_last_seven_days': prevalenceStore.numPositivesLastSevenDays,
        }
      }

      await axios.put(
        `/users/${currentUser.id}/profile.json`,
        toSave
      )
        .then(response => {
          let data = response.data

          prevalenceStore.numPositivesLastSevenDays = data.num_positive_cases_last_seven_days
          prevalenceStore.numPopulation = data.num_people_population
          prevalenceStore.uncountedFactor = data.uncounted_cases_multiplier

          this.message = data.message
          this.systemOfMeasurement = data.profile.systemOfMeasurement
          debugger
          this.measurementUnits = getMeasurementUnits(this.systemOfMeasurement)

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load profile."
          // whatever you want
        })
    },

    async loadCO2Monitors() {
      setupCSRF();

      let mainStore = useMainStore()
      let currentUser = mainStore.currentUser

      await axios.get(`/users/${currentUser.id}/carbon_dioxide_monitors.json`)
        .then(response => {
          const monitors = response.data.carbonDioxideMonitors;
          for (let monitor of monitors) {
            monitor['status'] = 'display'
          }
          this.carbonDioxideMonitors = monitors

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Failed to load carbon dioxide monitors."
          // whatever you want
        })
    },
    async setSystemOfMeasurement(event) {
      let mainStore = useMainStore()
      let currentUser = mainStore.currentUser

      const showMeasurementSetStore = useShowMeasurementSetStore()

      let toSave = {
        'measurement_system': event.target.value
      }

      const eventStore = useEventStore()

      await axios.put(`/users/${currentUser.id}/profile.json`, toSave)
        .then(response => {
          console.log(response)

          if (response.status == 200) {
            mainStore.setMessage(response.data.message)
            this.systemOfMeasurement = event.target.value;
            this.measurementUnits = getMeasurementUnits(this.systemOfMeasurement)
            showMeasurementSetStore.displayMeasurementsTailoredToUser()

            eventStore.updateRoomDimensionsMeters(this.measurementUnits)
            eventStore.setCubicMetersPerHour()
          }
        })
        .catch(error => {
          mainStore.setMessage(error)
          // whatever you want
        })
    }
  }
});
