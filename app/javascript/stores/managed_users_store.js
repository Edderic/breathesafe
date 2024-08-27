import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import { deepSnakeToCamel, setupCSRF } from '../misc.js'
import axios from 'axios'
import { useMainStore } from './main_store'
import { RespiratorUser } from '../respirator_user.js'

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
      setupCSRF();

      let mainStore = useMainStore()

      await axios.get(
        `/managed_users/${managedUserId}`,
      )
        .then(response => {
          let data = response.data
          this.managedUser = new RespiratorUser(
            deepSnakeToCamel(response.data.managed_users[0])
          )
        })
        .catch(error => {
          mainStore.addMessages(error.response.data.messages)
        })

    },
  }
});
