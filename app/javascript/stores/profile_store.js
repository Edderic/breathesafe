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
      await mainStore.getCurrentUser();
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser
      let hasProfile = false

      if (!currentUser) {
        prevalenceStore.numPositivesLastSevenDays = 300000
        prevalenceStore.numPopulation = 60000000
        prevalenceStore.uncountedFactor = 10
        prevalenceStore.maskType = "None"

        this.message = "No current user found. Using defaults."
        this.systemOfMeasurement = "imperial"
        this.measurementUnits = getMeasurementUnits(this.systemOfMeasurement)

        return ""
      }

      await axios.get(
        `/users/${currentUser.id}/profile.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.profile) {
            hasProfile = true

            let profile = data.profile
            prevalenceStore.numPositivesLastSevenDays = profile.num_positive_cases_last_seven_days
            prevalenceStore.numPopulation = profile.num_people_population
            prevalenceStore.uncountedFactor = profile.uncounted_cases_multiplier
            prevalenceStore.maskType = profile.mask_type

            this.message = data.message
            this.systemOfMeasurement = profile.measurement_system
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
          'mask_type': prevalenceStore.maskType
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
          prevalenceStore.maskType = profile.mask_type

          this.message = data.message
          this.systemOfMeasurement = profile.systemOfMeasurement
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
          'mask_type': prevalenceStore.maskType
        }
      }

      await axios.put(
        `/users/${currentUser.id}/profile.json`,
        toSave
      )
        .then(response => {
          let data = response.data

          let profile = data.profile
          prevalenceStore.numPositivesLastSevenDays = profile.num_positive_cases_last_seven_days
          prevalenceStore.numPopulation = profile.num_people_population
          prevalenceStore.uncountedFactor = profile.uncounted_cases_multiplier
          prevalenceStore.maskType = profile.mask_type

          this.message = data.message
          this.systemOfMeasurement = profile.systemOfMeasurement
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
