<template>
  <div class='top-container'>
    <div class='flex align-items-center justify-content-center row'>
      <h2 class='tagline'>Respirator Users</h2>
      <CircularButton text="+" @click="newUser"/>
    </div>

    <div class='row justify-content-center'>
      <input id='search' type="text" v-model='search'>
      <SearchIcon height='2em' width='2em'/>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <Popup v-if='missingFacialMeasurementsForRecommender.length > 0' @onclose='missingFacialMeasurementsForRecommender = []'>
      <p>
      User is missing at least one facial measurement needed for mask recommendations:
      <ul>
        <router-link class='missing' :to="linkToUserFacialMeasurement" >
          <li v-for="m in missingFacialMeasurementsForRecommender">{{m}}</li>
        </router-link>
      </ul>

      </p>
    </Popup>

    <div :class='{main: true, scrollable: managedUsers.length == 0}'>
      <div class='centered'>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Demographics</th>
              <th>Face Measurements</th>
              <th>Masks that have data</th>
              <th>Recommend</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in displayables' text='Edit'>
              <td v-if='currentUser.admin'>{{r['managerEmail']}}</td>
              <td @click="visit(r.managedId, 'Name')">
                {{r.firstName}} {{r.lastName}}
              </td>
              <td @click="visit(r.managedId, 'Demographics')" class='colored-cell' >
                <ColoredCell
                  :colorScheme="evenlySpacedColorScheme"
                  :maxVal=1
                  :value='1 - r.demogPercentComplete / 100'
                  :text='percentage(r.demogPercentComplete)'
                  class='color-cell'
                />
              </td>
              <td @click="visit(r.managedId, 'Facial Measurements')" class='colored-cell' >
                <ColoredCell
                  :colorScheme="evenlySpacedColorScheme"
                  :maxVal=1
                  :value='1- r.fmPercentComplete / 100'
                  :text='percentage(r.fmPercentComplete)'
                  class='color-cell'
                />
              </td>
              <td class='colored-cell' @click='v'>
                <router-link :to="{name: 'FitTests', query: {'managedId': r.managedId }}">
                  <ColoredCell
                    :colorScheme="evenlySpacedColorScheme"
                    :maxVal=1
                    :value='1 - (r.fitTestingPercentComplete || 0) / 100'
                    :text='percentage(r.fitTestingPercentComplete || 0)'
                    class='color-cell'
                  />
                </router-link>
              </td>
              <td class='colored-cell' @click='maybeRecommend(r)'>
                  <Button :style='`font-size: 1em; background-color: ${backgroundColorForRecommender(r)}`'>
                    Recommend
                  </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 class='text-align-center' v-show='displayables.length == 0' >
        No managed users to show. Use the (+) button above to add users you can add fit test data for.
      </h3>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { userSealCheckColorMapping, riskColorInterpolationScheme, genColorSchemeBounds } from './colors.js'
import { RespiratorUser } from './respirator_user.js'
import { signIn } from './session.js'
import { facialMeasurementsPresenceColorMapping } from './colors.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import SearchIcon from './search_icon.vue'
import { useManagedUserStore } from './stores/managed_users_store.js'

export default {
  name: 'RespiratorUsers',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    Popup,
    SearchIcon
  },
  data() {
    return {
      facialMeasurementsLength: 0,
      missingFacialMeasurementsForRecommender: [],
      search: "",
      userId: 0
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
    ...mapWritableState(
        useMainStore,
        [
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
        useManagedUserStore,
        [
          'managedUsers'
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
    linkToUserFacialMeasurement() {
      return {
        'name': 'RespiratorUser',
        'params': {'id': this.userId},
        'query': {
          'tabToShow': "Facial Measurements"
        }
      }
    },
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
    },
    evenlySpacedColorScheme() {
      return genColorSchemeBounds(0, 1, 5)
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadManagedUsers()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    maybeRecommend(r) {
      let missing = []

      let measurements = {
        'bitragionSubnasaleArc': {
          'eng': 'Bitragion subnasale arc (mm)',
          'mm': 'bitragionSubnasaleArcMm'
        },
        'noseProtrusion': {
          'eng': 'Nose protrusion (mm)',
          'mm': 'noseProtrusionMm'
        },
        'faceWidth' : {
          'eng': 'Face width (mm)',
          'mm': 'faceWidthMm'
        }
      }

      for(let key in measurements) {
        if (!r[key]) {
          missing.push(measurements[key]['eng'])
        }
      }

      if (missing.length > 0) {
        this.missingFacialMeasurementsForRecommender = missing

        this.userId = r.managedId
      } else {

        let query = {}
        for(let key in measurements) {
            query[measurements[key]['mm']] = r[key]
        }

        this.$router.push(
         {
           name: 'Masks',
           query: query
         }
        )
      }
    },
    backgroundColorForRecommender(r) {
      let color;
      if (r.bitragionSubnasaleArc && r.noseProtrusion && r.faceWidth ) {
        color = facialMeasurementsPresenceColorMapping['Complete'];
      } else {
        color = facialMeasurementsPresenceColorMapping['Completely missing'];
      }
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    recommendQuery(r) {
      return {
        bitragionSubnasaleArcMm: r.bitragionSubnasaleArc,
        noseProtrusionMm: r.noseProtrusion,
        faceWidthMm: r.faceWidth,
      }

    },
    percentage(num) {
      return `${num}%`
    },
    statusColor(fitTestingPercent) {
      let percentage = parseFloat(fitTestingPercent.split("%")[0])
      let status = 'Passed'
      if (percentage == 0) {
        status = "Failed"
      } else if (percentage > 0 && percentage < 100) {
        status = "Skipped"
      }

      let color = userSealCheckColorMapping[status]
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    backgroundColor(boolean) {
      let color;

      if (boolean) {
        color = userSealCheckColorMapping['Passed']

      } else {
        color = userSealCheckColorMapping['Failed']
      }

      return `rgb(${color.r}, ${color.g}, ${color.b}, 0.5)`
    },
    checkmarkOrCross(boolean) {
      if (boolean) {
        return `&#x2714;`
      } else {
        return "&#x2717;"
      }
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
    visit(profileId, tabToShow) {
      this.$router.push({
        name: 'RespiratorUser',
        params: {
          id: profileId
        },
        query: {
          tabToShow: tabToShow
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

  .colored-cell {
    color: white;
    text-shadow: 1px 1px 2px black;

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

  .missing {
    color: black;
  }
  img {
    width: 30em;
  }
  .top-container {
    height: 100vh;
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    #search {
      width: 75vw;
      padding: 1em;
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

  .colored-cell {
    text-align: center;
  }

  .text-align-center {
    text-align: center;
  }

  .empty-sign {
    margin-top: 25em;
  }

  .scrollable {
    overflow-y: auto;
    height: 75vh;
  }

  a {
    color: white;
  }

</style>
