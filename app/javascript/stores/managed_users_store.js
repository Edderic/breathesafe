import { mapActions, mapState, mapWritableState, defineStore } from 'pinia'
import { deepSnakeToCamel, setupCSRF } from '../misc.js'
import axios from 'axios'
import { useMainStore } from './main_store'
import { RespiratorUser } from '../respirator_user.js'

function shouldForceReauth(error) {
  const status = error && error.response && error.response.status
  if (status === 401 || status === 403) {
    return true
  }

  const messages = (error && error.response && error.response.data && error.response.data.messages) || []
  const messageText = Array.isArray(messages) ? messages.join(' ').toLowerCase() : ''
  if (status === 422 && messageText.includes('validation error')) {
    return true
  }

  if (messageText.includes('please log in') || messageText.includes('unauthorized')) {
    return true
  }

  return false
}

function emitAuthExpired() {
  try {
    window.dispatchEvent(new CustomEvent('breathesafe-auth-expired'))
  } catch (_error) {
    // Ignore environments without window/event support.
  }
}

// useStore could be anything like useUser, useCart
// the first argument is a unique id of the store across your application
export const useManagedUserStore = defineStore('managedUsers', {
  state: () => ({
    managedUser: {},
    managedUsers: [],
    totalCount: 0,
    currentPage: 1,
    perPage: 25
  }),
  getters: {
    // ...mapState(useMainStore, ['currentUser']),
    // ...mapWritableState(useMainStore, ['message']),
  },
  actions: {
    async loadManagedUsers({ admin = false, page = 1, perPage = 25, sort = null, order = null } = {}) {
      this.managedUsers = [];
      let mainStore = useMainStore()
      let managedUsers = [];
      let managedUser;

      setupCSRF();

      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString()
      });

      if (admin) {
        params.append('admin', 'true');
      }

      if (sort && order) {
        params.append('sort', sort);
        params.append('order', order);
      }

      await axios.get(
        `/managed_users.json?${params.toString()}`,
      )
        .then(response => {
          let data = response.data

          // Update pagination state
          this.totalCount = data.total_count || 0
          this.currentPage = data.page || 1
          this.perPage = data.per_page || 25

          if (response.data.managed_users) {
            managedUsers = response.data.managed_users

            // Deduplicate by managedId to prevent duplicates
            // Use both snake_case and camelCase field names for compatibility
            const seenManagedIds = new Set()
            for(let managedUserData of managedUsers) {
              managedUser = deepSnakeToCamel(managedUserData)
              const managedId = managedUser.managedId || managedUser.managed_id

              // Skip if we've already seen this managedId
              if (managedId && !seenManagedIds.has(managedId)) {
                seenManagedIds.add(managedId)
                this.managedUsers.push(
                  new RespiratorUser(
                    managedUser
                  )
                )
              } else if (!managedId) {
                // If managedId is missing, use id as fallback for deduplication
                const id = managedUser.id
                if (id && !seenManagedIds.has(`id_${id}`)) {
                  seenManagedIds.add(`id_${id}`)
                  this.managedUsers.push(
                    new RespiratorUser(
                      managedUser
                    )
                  )
                }
              }
            }
          }
        })
        .catch(error => {
          if (shouldForceReauth(error)) {
            mainStore.currentUser = undefined
            mainStore.signedIn = false
            mainStore.addMessages(['Session expired. Please sign in again.'])
            emitAuthExpired()
            return
          }

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
          if (shouldForceReauth(error)) {
            mainStore.currentUser = undefined
            mainStore.signedIn = false
            mainStore.addMessages(['Session expired. Please sign in again.'])
            emitAuthExpired()
            return
          }

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
            if (shouldForceReauth(error)) {
              mainStore.currentUser = undefined
              mainStore.signedIn = false
              mainStore.addMessages(['Session expired. Please sign in again.'])
              emitAuthExpired()
              return
            }

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
