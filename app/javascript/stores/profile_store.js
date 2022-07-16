import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import axios from 'axios'
import { useMainStore } from './main_store'
import { useShowMeasurementSetStore } from './show_measurement_set_store'
import { useEventStore } from './event_store'
import { generateUUID, setupCSRF } from '../misc';

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useProfileStore = defineStore('profile', {
  state: () => ({
    currentUser: undefined,
    profileLoaded: false,
    lengthMeasurementType: "feet",
    airDeliveryRateMeasurementType: 'cubic feet per minute',
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
    ...mapState(useMainStore, ['currentUser']),
    ...mapWritableState(useMainStore, ['message']),
  },
  actions: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    async loadProfile() {
      setupCSRF();
      await this.getCurrentUser()

      let toSave = {
        'profile': {
          'measurement_system': this.systemOfMeasurement
        }
      }

      await axios.post(
        `/users/${this.currentUser.id}/profiles.json`,
        toSave
      )
        .then(response => {
          let data = response.data

          this.message = data.message
          this.systemOfMeasurement = data.systemOfMeasurement

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Failed to load profile."
          // whatever you want
        })
    },
    async loadCO2Monitors() {
      setupCSRF();

      await axios.get(`/users/${this.currentUser.id}/carbon_dioxide_monitors.json`)
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
      this.getCurrentUser()

      let toSave = {
        'measurement_system': event.target.value
      }

      const mainStore = useMainStore()
      const eventStore = useEventStore()

      await axios.post(`/users/${this.currentUser.id}/profiles.json`, toSave)
        .then(response => {
          console.log(response)

          if (response.status == 200) {
            mainStore.setMessage(response.data.message)
            this.systemOfMeasurement = event.target.value;

            if (this.systemOfMeasurement == 'imperial') {
              this.lengthMeasurementType = 'feet';
              this.airDeliveryRateMeasurementType = 'cubic feet per minute';
            } else {
              this.lengthMeasurementType = 'meters';
              this.airDeliveryRateMeasurementType = 'cubic meters per hour';
            }

            eventStore.updateRoomDimensionsMeters()
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
