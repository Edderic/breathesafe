import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import axios from 'axios'
import { useMainStore } from './main_store'
import { useEventStore } from './event_store'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useProfileStore = defineStore('profile', {
  state: () => ({
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
    ...mapWritableState(useMainStore, ['message'])
  },
  actions: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    async setSystemOfMeasurement(event) {
      this.getCurrentUser()

      let toSave = {
        'measurement_system': event.target.value
      }

      const mainStore = useMainStore()

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
              this.airDeliveryRateMeasurementType = 'cubic meters per minute';
            }

            this.updateRoomDimensionsMeters()
          }
        })
        .catch(error => {
          console.log(error)
            mainStore.setMessage(error)
          // whatever you want
        })

    }
  }
});
