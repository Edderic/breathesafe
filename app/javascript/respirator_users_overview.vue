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

        <table class='facial-measurements-table phone' >
          <thead class='facial-measurements-header'>
            <tr>
              <th v-if='currentUser && currentUser.admin'>Manager Email</th>
              <th></th>
              <th>Demog</th>
              <th>Face</th>
              <th># masks tested</th>
              <th>Rec</th>
              <th>Add FT</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in displayables' text='Edit'>
              <td v-if='currentUser && currentUser.admin'>{{r['managerEmail']}}</td>
              <td class='name' @click="visit(r.managedId, 'Name')">
                {{r.firstName}} {{r.lastName}}
              </td>
              <td @click="visit(r.managedId, 'Demographics')" class='colored-cell' >
                <ColoredCell
                  :colorScheme="evenlySpacedColorScheme"
                  :maxVal=1
                  :value='1 - r.demogPercentComplete / 100'
                  :text='percentage(r.demogPercentComplete)'
                  class='colored-cell'
                />
              </td>
              <td @click="visit(r.managedId, 'Facial Measurements')" class='colored-cell' >
                <ColoredCell
                  :colorScheme="evenlySpacedColorScheme"
                  :maxVal=1
                  :value='1- r.fmPercentComplete / 100'
                  :text='percentage(r.fmPercentComplete)'
                  class='colored-cell'
                />
              </td>
              <td class='colored-cell' @click='v'>
                <router-link :to="{name: 'FitTests', query: {'managedId': r.managedId }}">
                  <ColoredCell
                      :colorScheme="genColorSchemeBounded(0, 1)"
                      :maxVal=1
                      :value='1 - r.numUniqueMasksTested / 40 < 0 ? 0 : 1 - r.numUniqueMasksTested / 40 '
                      :text='r.numUniqueMasksTested'
                      class='colored-cell'
                      />
                </router-link>
              </td>
              <td class='colored-cell' @click='maybeRecommend(r)'>
                  <Button :style='`font-size: 1em; background-color: ${backgroundColorForRecommender(r)}`'>
                    Rec
                  </Button>
              </td>
              <td class='centered-text'>
                <CircularButton text="+" @click="createFitTestForUser(r)"/>
              </td>
            </tr>
          </tbody>
        </table>

        <table class='facial-measurements-table non-phone'>
          <thead class='facial-measurements-header'>
            <tr>
              <th v-if='currentUser && currentUser.admin'>Manager Email</th>
              <th>Name</th>
              <th>Demographics Completion</th>
              <th>Face Measurements Completion</th>
              <th>Unique masks tested</th>
              <th>Recommend</th>
              <th>Add Fit Test</th>
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
                  class='colored-cell'
                />
              </td>
              <td @click="visit(r.managedId, 'Facial Measurements')" class='colored-cell' >
                <ColoredCell
                  :colorScheme="evenlySpacedColorScheme"
                  :maxVal=1
                  :value='1- r.fmPercentComplete / 100'
                  :text='percentage(r.fmPercentComplete)'
                  class='colored-cell'
                />
              </td>
              <td class='colored-cell' @click='v'>
                <router-link :to="{name: 'FitTests', query: {'managedId': r.managedId }}">
                  <ColoredCell
                      :colorScheme="genColorSchemeBounded(0, 1)"
                      :maxVal=1
                      :value='1 - r.numUniqueMasksTested / 40 < 0 ? 0 : 1 - r.numUniqueMasksTested / 40 '
                      :text='r.numUniqueMasksTested'
                      class='colored-cell'
                      />
                </router-link>
              </td>
              <td class='colored-cell' @click='maybeRecommend(r)'>
                  <Button :style='`font-size: 1em; background-color: ${backgroundColorForRecommender(r)}`'>
                    Recommend
                  </Button>
              </td>
              <td class='centered-text'>
                <CircularButton text="+" @click="createFitTestForUser(r)"/>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination-container">
          <nav aria-label="Respirator users pagination">
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button @click="goToPage(1)" class="page-link" :disabled="currentPage === 1">First</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button @click="goToPage(currentPage - 1)" class="page-link" :disabled="currentPage === 1">Previous</button>
              </li>

              <li
                v-for="page in visiblePages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
              >
                <button @click="goToPage(page)" class="page-link">{{ page }}</button>
              </li>

              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button @click="goToPage(currentPage + 1)" class="page-link" :disabled="currentPage === totalPages">Next</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button @click="goToPage(totalPages)" class="page-link" :disabled="currentPage === totalPages">Last</button>
              </li>
            </ul>
            <div class="pagination-info">
              Showing {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, totalCount) }} of {{ totalCount }} users
            </div>
          </nav>
        </div>
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
import CircularButton from './circular_button.vue'
import ExpandableButton from './expandable_button.vue'
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
    CircularButton,
    ClosableMessage,
    ColoredCell,
    ExpandableButton,
    Popup
  },
  props: {
    search: {
      type: String,
      default: ""
    },
    metricToShow: {
      type: String,
      default: "Demographics"
    }
  },
  data() {
    return {
      missingFacialMeasurementsForRecommender: [],
      userId: 0,
      recommenderColumns: [],
      expandedUsers: {} // Track expansion state for each user
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
    ...mapState(
        useManagedUserStore,
        [
          'totalCount',
          'currentPage',
          'perPage'
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
    isAdminView() {
      return this.$route.query.admin === 'true' && this.currentUser?.admin
    },
    totalPages() {
      return Math.ceil(this.totalCount / this.perPage)
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    },
    evenlySpacedColorScheme() {
      return genColorSchemeBounds(0, 1, 5)
    },
    getColoredCellValue() {
      return (user) => {
        switch (this.metricToShow) {
          case 'Demographics':
            return 1 - user.demogPercentComplete / 100
          case 'Facial measurements':
            return 1 - user.fmPercentComplete / 100
          case 'Num masks tested':
            const value = 1 - user.numUniqueMasksTested / 40
            return value < 0 ? 0 : value
          default:
            return 1 - user.demogPercentComplete / 100
        }
      }
    },
    getColoredCellText() {
      return (user) => {
        switch (this.metricToShow) {
          case 'Demographics':
            return this.percentage(user.demogPercentComplete)
          case 'Facial measurements':
            return this.percentage(user.fmPercentComplete)
          case 'Num masks tested':
            return `${user.numUniqueMasksTested || 0}`
          default:
            return this.percentage(user.demogPercentComplete)
        }
      }
    }
  },
  async created() {
    await this.getCurrentUser()
    if (this.currentUser) {
      this.loadData()
    }
    await this.fetchRecommenderColumns()
  },
  watch: {
    '$route'(to, from) {
      // Reload managed users when navigating back to RespiratorUsers page
      // This ensures we have the latest data, especially after saving profile changes
      // Reload if navigating TO RespiratorUsers OR if admin query param changes
      if (this.currentUser && to.name === 'RespiratorUsers') {
        if (from.name !== 'RespiratorUsers' || to.query.admin !== from.query.admin) {
          this.loadData()
        }
      }
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    loadData(page = 1) {
      const admin = this.isAdminView
      this.loadManagedUsers({ admin, page, perPage: 25 })
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.loadData(page)
        // Scroll to top of table
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    genColorSchemeBounded(minimum, maximum) {
      return genColorSchemeBounds(minimum, maximum, 5)
    },
    toggleExpansion(userId) {
      this.expandedUsers[userId] = !this.expandedUsers[userId];
    },
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
    },
    createFitTestForUser(user) {
      this.$router.push({
        name: 'NewFitTest',
        query: {
          userId: user.managedId,
          tabToShow: 'Mask'
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

  .flex-direction-row {
    display: flex;
    flex-direction: row;
  }

  p {
    margin: 1em;
  }

  th, td {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
    padding-left: 0;
    padding-right: 0;
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
    padding-top: 1em;
    padding-bottom: 1em;
    background-color: #eee;
    border-bottom: 2px solid #ddd;
    font-weight: bold;
  }

  .facial-measurements-table tbody tr:hover {
    background-color: rgb(240, 240, 240);
  }

  .facial-measurements-table tbody tr:hover {
    background-color: rgb(240, 240, 240);
  }

  .maxed-width {
    width: 100%;
  }

  .phone {
    display: none;
  }

  td.name {
    padding: 1em;
  }

  .colored-cell {
    padding: 0.5em;
  }

  .centered-text {
    text-align: center;
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

    .header {
      flex-direction: column;

    }

    .first-layer-td {
      padding-left: 0.5em;
      padding-right: 0.5em;
      width: 90vw;
    }
    .phone table {
      width: 90vw;
    }

    .phone tr {
      border-bottom: 1px solid #aaa;
    }


    .non-phone {
      display: none;
    }

    .phone {
      display: block;
    }

    /* Rotated headers for mobile */

    .phone.facial-measurements-table thead tr {
      height: 80px; /* Match the th height */
    }
    .phone th, .phone td {
      width: 1em;
    }
  }

  .pagination-container {
    margin: 2em 0;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .pagination {
    display: flex;
    list-style: none;
    padding: 0;
    gap: 0.5em;
    margin: 0;
    flex-wrap: wrap;
    justify-content: center;
  }

  .page-item {
    display: inline-block;
  }

  .page-link {
    padding: 0.5em 1em;
    border: 1px solid #ddd;
    background-color: white;
    color: #007bff;
    cursor: pointer;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .page-link:hover:not(:disabled) {
    background-color: #e9ecef;
  }

  .page-item.active .page-link {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
  }

  .page-item.disabled .page-link {
    color: #6c757d;
    cursor: not-allowed;
    opacity: 0.5;
  }

  .pagination-info {
    text-align: center;
    margin-top: 1em;
    color: #666;
    font-size: 0.9em;
  }

  @media(max-width: 700px) {
    .pagination {
      font-size: 0.85em;
    }

    .page-link {
      padding: 0.4em 0.7em;
    }
  }

</style>
