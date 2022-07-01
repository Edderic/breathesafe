import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useProfileStore = defineStore('profile', {
  state: () => ({
    lengthMeasurementType: "feet",
    airDeliveryRateMeasurementType: 'cubic feet per minute',
    systemOfMeasurement: "imperial",
    carbonDioxideMonitors: []
  }),
  getters: {
  },
  actions: {
    setSystemOfMeasurement(event) {
      this.systemOfMeasurement = event.target.value;

      if (this.systemOfMeasurement == 'imperial') {
        this.lengthMeasurementType = 'feet';
        this.airDeliveryRateMeasurementType = 'cubic feet per minute';
      } else {
        this.lengthMeasurementType = 'meters';
        this.airDeliveryRateMeasurementType = 'cubic meters per minute';
      }
    }
  }
});
