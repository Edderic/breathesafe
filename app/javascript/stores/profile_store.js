import { defineStore } from 'pinia'

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useProfileStore = defineStore('profile', {
  state: () => ({
    systemOfMeasurement: "imperial",
    carbonDioxideMonitors: []
  }),
  getters: {
  },
  actions: {
    setSystemOfMeasurement(systemOfMeasurement) {
      this.systemOfMeasurement = systemOfMeasurement;
    }
  }
});
