import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import { deepSnakeToCamel, setupCSRF } from '../misc.js'
import axios from 'axios'
import { useMainStore } from './main_store'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useMeasurementDeviceStore = defineStore('measurementDevices', {
  state: () => ({
    measurement_device: {
      device_type: '',
      manufacturer: '',
      model: '',
      serial: '',
      notes: ''
    },
    measurementDevices: []
  }),
  getters: {
    // ...mapState(useMainStore, ['currentUser']),
    // ...mapWritableState(useMainStore, ['message']),
  },
  actions: {
    async loadMeasurementDevices() {
      this.measurementDevices = [];
      let mainStore = useMainStore()
      let measurementDevices = [];
      let measurementDevice;

      setupCSRF();

      await axios.get(
        `/measurement_devices.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.measurement_devices) {
            measurementDevices = response.data.measurement_devices

            for(let measurementDeviceData of measurementDevices) {
              measurementDevice = measurementDeviceData
              this.measurementDevices.push(
                measurementDevice
              )
            }
          }
        })
        .catch(error => {
          debugger;
          if (error && error.response && error.response.data && error.response.data.messages) {
            mainStore.addMessages(error.response.data.messages)
          } else {
            mainStore.addMessages([error.message])
          }
        // whatever you want
        })
    },
    async loadMeasurementDevice(measurementDeviceId) {
      setupCSRF();

      let mainStore = useMainStore()

      await axios.get(
        `/measurement_devices/${measurementDeviceId}`,
      )
        .then(response => {
          let data = response.data
          this.measurement_device = response.data.measurement_device
        })
        .catch(error => {
          mainStore.addMessages(error.response.data.messages)
        })

    },
    async deleteMeasurementDevice(measurementDeviceId, successCallback, failureCallback) {
      setupCSRF();
      let mainStore = useMainStore()

      let answer = window.confirm("Are you sure you want to delete data?");

      if (answer) {
        await axios.delete(
          `/measurement_devices/${measurementDeviceId}`,
        )
          .then(response => {
            let data = response.data
            this.measurementDevice = {}
            this.measurementDevices = this.measurementDevices.filter((m) => m.measurementDeviceId != measurementDeviceId)

          })
          .catch(error => {
            if (error && error.response && error.response.data && error.response.data.messages) {
              mainStore.addMessages(error.response.data.messages)
            } else {
              mainStore.addMessages(["Something went wrong."])
            }


          })

          successCallback()
      }
      else {
        failureCallback()
        //some code
      }

    },
  }
});
