import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import { deepSnakeToCamel } from '../misc.js'
import axios from 'axios'
import { useMainStore } from './main_store'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useManagedUserStore = defineStore('managedUsers', {
  state: () => ({
    managedUser: {},
    managedUsers: []
  }),
  getters: {
    // ...mapState(useMainStore, ['currentUser']),
    // ...mapWritableState(useMainStore, ['message']),
  },
  actions: {
    async loadManagedUser(managedUserId) {
      let mainStore = useMainStore()

      await axios.get(
        `/managed_users/${managedUserId}`,
      )
        .then(response => {
          let data = response.data
          this.managedUser = deepSnakeToCamel(response.data.managed_users[0])
        })
        .catch(error => {
          mainStore.addMessages(error.response.data.messages)
        })

    },
    async loadProfile(id) {
      setupCSRF();

      let mainStore = useMainStore()
      await mainStore.getCurrentUser();
      let currentUser = mainStore.currentUser

      if (!id) {
        id = currentUser.id
      }

      let prevalenceStore = usePrevalenceStore()
      let hasProfile = false

      if (!currentUser) {
        mainStore.addMessages([
          "No current user found. Using defaults."
        ])

        this.systemOfMeasurement = "imperial"
        this.measurementUnits = getMeasurementUnits(this.systemOfMeasurement)

        return ""
      }

      await axios.get(
        `/users/${id}/profile.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.profile) {
            hasProfile = true

            let profile = data.profile

            this.profileId = profile.id
            this.externalAPIToken = profile.external_api_token
            this.heightMeters = profile.height_meters
            this.strideLengthMeters = profile.stride_length_meters
            this.firstName = profile.first_name
            this.lastName = profile.last_name
            this.raceEthnicity = profile.race_ethnicity
            this.genderAndSex = profile.gender_and_sex
            this.otherGender = profile.other_gender
            this.message = data.message
            this.systemOfMeasurement = profile.measurement_system
            this.measurementUnits = getMeasurementUnits(profile.measurement_system)
            this.socials = profile.socials || {}
          }

          // whatever you want
        })
        .catch(error => {
          mainStore.addMessages(error.response.data.messages)
          // whatever you want
        })

      if (!hasProfile) {
        await this.createProfile(id)
      }
    },
    async createProfile(id) {
      setupCSRF();

      let mainStore = useMainStore()
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser
      if (!id) {
        id = currentUser.id
      }

      let toSave = {
        'profile': {
          'first_name': this.firstName,
          'last_name': this.lastName,
          'height_meters': this.heightMeters,
          'stride_length_meters': this.strideLengthMeters,
          'measurement_system': this.systemOfMeasurement,
          'socials': this.socials
        }
      }

      await axios.post(
        `/users/${id}/profile.json`,
        toSave
      )
        .then(response => {
          // whatever you want
        })
        .catch(error => {
          mainStore.addMessages(error.response.data.messages)
          // whatever you want
        })
    },

    async loadCO2Monitors() {
      setupCSRF();

      let mainStore = useMainStore()
      let currentUser = mainStore.currentUser
      if (!currentUser) {
        return
      }

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
          mainStore.addMessages(error.response.data.messages)
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
          mainStore.addMessages(error.response.data.messages)
          // whatever you want
        })
    }
  }
});
