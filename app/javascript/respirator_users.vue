<template>
  <div>
    <div class='flex align-items-center justify-content-center row'>
      <h2 class='tagline'>Respirator Users</h2>
      <CircularButton text="+" @click="newUser"/>
    </div>

    <div class='row justify-content-center'>
      <input type="text" v-model='search'>
      <SearchIcon height='2em' width='2em'/>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <div class='main'>
      <div class='centered'>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Race &amp; Ethnicity filled out</th>
              <th>Gender filled out</th>
              <th>Has Facial Measurements</th>
              <th>Ready to add Fit Testing Data</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in displayables' @click="edit(r.managedId)" text='Edit'>
              <td>
                {{r.firstName}} {{r.lastName}}
              </td>
              <td>
                {{r.raceEthnicityComplete}}
              </td>
              <td>
                {{r.genderAndSexComplete}}
              </td>
              <td>
                {{r.facialMeasurementsComplete}}
              </td>
              <td>
                {{r.readyToAddFitTestingDataPercentage}}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import CircularButton from './circular_button.vue'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { RespiratorUser } from './respirator_user.js'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import SearchIcon from './search_icon.vue'

export default {
  name: 'RespiratorUsers',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SearchIcon
  },
  data() {
    return {
      managedUsers: [],
      facialMeasurementsLength: 0,
      search: ""
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
          'messages'
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
          'readyToAddFitTestingDataPercentage',
          'nameComplete',
          'genderAndSexComplete',
          'raceEthnicityComplete',
          'facialMeasurementsComplete',
          'loadFacialMeasurements',
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity',
          'genderAndSex',
        ]
    ),
    displayables() {
      if (this.search == "") {
        return this.managedUsers
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.managedUsers.filter(
          function(mu) {
            return mu.firstName.toLowerCase().match(lowerSearch)
              || mu.lastName.toLowerCase().match(lowerSearch)

          }
        )
      }
    },
    facialMeasurementsIncomplete() {
      return this.facialMeasurementsLength == 0
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadStuff()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useProfileStore, ['loadProfile']),
    async loadStuff() {
      let managedUsers = [];
      let managedUser = {};

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
          this.addMessages(error.response.data.messages)
        // whatever you want
        })
    },

    async newUser() {
      setupCSRF();

      let managedUsers;
      let managedUser;
      let respiratorUser;

      await axios.post(
        `/managed_users.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.managed_user) {
            managedUser = deepSnakeToCamel(response.data.managed_user)

            respiratorUser = new RespiratorUser(
              managedUser
            )

            this.managedUsers.push(
              respiratorUser
            )

            this.$router.push(
              {
                'name': 'RespiratorUser',
                params: {
                  id: respiratorUser.managedId
                }
              }
            )
          }
        })
        .catch(error => {
          if (error && error.response && error.response.data && error.response.data.messages) {
            this.addMessages(error.response.data.messages)
          } else {
            this.addMessages['Something went wrong.']
          }

        // whatever you want
        })
    },
    edit(profileId) {
      this.$router.push({
        name: 'RespiratorUser',
        params: {
          id: profileId
        }
      })
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  p {
    margin: 1em;
  }

  th, td {
    padding: 0.5em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  img {
    width: 30em;
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .align-items-center {
    align-items: center;
  }

  .justify-content-center {
    justify-content: center;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  thead th {
    background-color: #eee;
    padding: 1em;
  }
</style>
