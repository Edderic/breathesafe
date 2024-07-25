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
    firstName: "",
    lastName: "",
    facialMeasurementsLength: 0,
    heightMeters: "",
    externalAPIToken: "",
    measurementUnits: {
      'lengthMeasurementType': "feet",
      'airDeliveryRateMeasurementType': 'cubic feet per minute',
      'airDeliveryRateMeasurementTypeShort': 'ft³ / h',
      'cubicLengthShort': 'ft³',
    },
    raceEthnicity: "",
    genderAndSex: "",
    otherGender: "",
    strideLengthMeters: 0.43,
    systemOfMeasurement: "imperial",
    carbonDioxideMonitors: [
      {
        'name': "",
        'serial': "",
        'model': ""
      }
    ],
    status: 'saved',
    socials: {
      'twitter': '',
      'mastodon': '',
    }
  }),
  getters: {
    // ...mapState(useMainStore, ['currentUser']),
    // ...mapWritableState(useMainStore, ['message']),
    nameComplete() {
      return !!this.firstName || !!this.lastName
    },
    raceEthnicityComplete() {
      return !!this.raceEthnicity
    },
    genderAndSexComplete() {
      return !!this.genderAndSex
    },
    facialMeasurementsComplete() {
      return this.facialMeasurementsLength > 0
    },
    readyToAddFitTestingDataPercentage() {
      let numerator = this.nameComplete
        + this.raceEthnicityComplete
        + this.genderAndSexComplete
        + this.facialMeasurementsComplete

      let rounded = Math.round(
        numerator / 4 * 100
      )

      return `${rounded}%`
    },
  },
  actions: {
    async loadFacialMeasurements(userId) {
      await axios.get(
        `/users/${userId}/facial_measurements.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.facial_measurements) {
            this.facialMeasurementsLength = response.data.facial_measurements.length
          } else {
            this.facialMeasurementsLength = 0
          }
        })
        .catch(error => {
          this.messages.push({
            str: "Failed to load facial measurements."
          })
          // whatever you want
        })

    },
    async loadProfile() {
      setupCSRF();

      let mainStore = useMainStore()
      await mainStore.getCurrentUser();
      let prevalenceStore = usePrevalenceStore()
      let currentUser = mainStore.currentUser
      let hasProfile = false

      if (!currentUser) {
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
          'first_name': this.firstName,
          'last_name': this.lastName,
          'height_meters': this.heightMeters,
          'stride_length_meters': this.strideLengthMeters,
          'measurement_system': this.systemOfMeasurement,
          'socials': this.socials
        }
      }

      await axios.post(
        `/users/${currentUser.id}/profile.json`,
        toSave
      )
        .then(response => {
          this.message = data.message
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
          'first_name': this.firstName,
          'last_name': this.lastName,
          'race_ethnicity': this.raceEthnicity,
          'gender_and_sex': this.genderAndSex,
          'other_gender': this.otherGender,
          'stride_length_meters': this.strideLengthMeters,
          'height_meters': this.heightMeters,
          'socials': this.socials
        }
      }

      await axios.put(
        `/users/${currentUser.id}/profile.json`,
        toSave
      )
        .then(response => {
          this.message = response.data.message
          this.status = 'saved'
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
