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
    async loadManagedUsers() {
      this.managedUsers = [];
      let mainStore = useMainStore()
      let managedUsers = [];
      let managedUser;

      setupCSRF();

      await axios.get(
        `/managed_users.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.managed_users) {
            managedUsers = response.data.managed_users

            for(let managedUserData of managedUsers) {
              managedUser = deepSnakeToCamel(managedUserData)
              this.managedUsers.push(
                new RespiratorUser(
                  managedUser
                )
              )
            }
          }
        })
        .catch(error => {
          if (error && error.response && error.response.data && error.response.data.messages) {
            mainStore.addMessages(error.response.data.messages)
          } else {
            mainStore.addMessages([error.message])
          }
        // whatever you want
        })
    },
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
          const msgs = error && error.response && error.response.data && error.response.data.messages
          if (Array.isArray(msgs)) {
            mainStore.addMessages(msgs)
          } else {
            mainStore.addMessages([error && error.message ? error.message : 'Something went wrong while loading managed user.'])
          }
        })

    },
    async deleteManagedUser(managedUserId, successCallback, failureCallback) {
      setupCSRF();
      let mainStore = useMainStore()

      let answer = window.confirm("Are you sure you want to delete data?");

      if (answer) {
        await axios.delete(
          `/managed_users/${managedUserId}`,
        )
          .then(response => {
            let data = response.data
            this.managedUser = {}
            this.managedUsers = this.managedUsers.filter((m) => m.managedUserId != managedUserId)

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
