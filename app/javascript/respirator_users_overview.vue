<template>
  <div v-if="currentUser">
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
      <div class='centered facial-measurements-table-container'>
        <table class='facial-measurements-table'>
          <thead class='facial-measurements-header'>
            <tr>
              <th v-if='currentUser && currentUser.admin'>Manager Email</th>
              <th>Name</th>
              <th>Demographics</th>
              <th>Face Measurements</th>
              <th>Masks that have data</th>
              <th>Recommend</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in displayables' text='Edit'>
              <td v-if='currentUser && currentUser.admin'>{{r['managerEmail']}}</td>
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
  <div v-else class='text-align-center'>
    <h3>Loading user data...</h3>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import ColoredCell from './colored_cell.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { facialMeasurementsPresenceColorMapping, genColorSchemeBounds } from './colors.js'
import { RespiratorUser } from './respirator_user.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { useManagedUserStore } from './stores/managed_users_store.js'

export default {
  name: 'RespiratorUsersOverview',
  components: {
    Button,
    ClosableMessage,
    ColoredCell,
    Popup
  },
  props: {
    search: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      missingFacialMeasurementsForRecommender: [],
      userId: 0,
      recommenderColumns: []
    }
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
    ...mapWritableState(
        useManagedUserStore,
        [
          'managedUsers'
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
    evenlySpacedColorScheme() {
      return genColorSchemeBounds(0, 1, 5)
    }
  },
  async created() {
    await this.getCurrentUser()
    if (this.currentUser) {
      this.loadManagedUsers()
    }
    await this.fetchRecommenderColumns()
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    async fetchRecommenderColumns() {
      try {
        const resp = await axios.get('/mask_recommender/recommender_columns.json')
        this.recommenderColumns = (resp.data && resp.data.recommender_columns) || []
      } catch (e) {
        this.recommenderColumns = []
      }
    },
    maybeRecommend(r) {
      const missing = []
      const query = {}

      for (const col of this.recommenderColumns) {
        const camel = col.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
        const baseKey = `${camel}`
        const mmKey = `${camel}Mm`
        if (!r[baseKey]) {
          missing.push(baseKey)
        } else {
          query[mmKey] = r[baseKey]
        }
      }

      if (missing.length > 0) {
        this.missingFacialMeasurementsForRecommender = missing
        this.userId = r.managedId
        return
      }

      this.$router.push({ name: 'Masks', query })
    },
    backgroundColorForRecommender(r) {
      const allPresent = this.recommenderColumns.every(col => {
        const camel = col.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
        return !!r[camel]
      })
      const color = facialMeasurementsPresenceColorMapping[allPresent ? 'Complete' : 'Completely missing']
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    percentage(num) {
      return `${num}%`
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

  .tagline {
    text-align: center;
    font-weight: bold;
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

  .row {
    display: flex;
    flex-direction: row;
  }

  .align-items-center {
    align-items: center;
  }

  .justify-content-center {
    display: flex;
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

  .scrollable {
    overflow-y: auto;
    height: 75vh;
  }

  a {
    color: white;
  }

  .facial-measurements-table-container {
    max-height: 70vh;
    overflow-y: auto;
    position: relative;
  }

  .facial-measurements-table {
    width: 100%;
    border-collapse: collapse;
  }

  .facial-measurements-table thead, .facial-measurements-header {
    position: sticky;
    top: 0;
    z-index: 10;
    background-color: #eee;
  }

  .facial-measurements-table th {
    padding: 1em;
    background-color: #eee;
    border-bottom: 2px solid #ddd;
    font-weight: bold;
  }

  .facial-measurements-table td {
    padding: 0.5em;
    border-bottom: 1px solid #ddd;
  }

  .facial-measurements-table tbody tr:hover {
    background-color: rgb(240, 240, 240);
  }
</style>
