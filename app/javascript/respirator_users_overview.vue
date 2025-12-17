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
              <th v-if='currentUser && currentUser.admin' @click='toggleSort("manager_email")' class='sortable-header'>
                Manager Email
                <span class='sort-indicator' v-if='currentSort === "manager_email"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("name")' class='sortable-header'>
                Name
                <span class='sort-indicator' v-if='currentSort === "name"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("demog_percent_complete")' class='sortable-header'>
                Demog
                <span class='sort-indicator' v-if='currentSort === "demog_percent_complete"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("fm_percent_complete")' class='sortable-header'>
                Face
                <span class='sort-indicator' v-if='currentSort === "fm_percent_complete"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("num_unique_masks_tested")' class='sortable-header'>
                # masks tested
                <span class='sort-indicator' v-if='currentSort === "num_unique_masks_tested"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
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
              <th v-if='currentUser && currentUser.admin' @click='toggleSort("manager_email")' class='sortable-header'>
                Manager Email
                <span class='sort-indicator' v-if='currentSort === "manager_email"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("name")' class='sortable-header'>
                Name
                <span class='sort-indicator' v-if='currentSort === "name"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("demog_percent_complete")' class='sortable-header'>
                Demographics Completion
                <span class='sort-indicator' v-if='currentSort === "demog_percent_complete"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("fm_percent_complete")' class='sortable-header'>
                Face Measurements Completion
                <span class='sort-indicator' v-if='currentSort === "fm_percent_complete"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click='toggleSort("num_unique_masks_tested")' class='sortable-header'>
                Unique masks tested
                <span class='sort-indicator' v-if='currentSort === "num_unique_masks_tested"'>
                  {{ currentOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
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
  emits: ['pagination-update'],
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
      expandedUsers: {}, // Track expansion state for each user
      currentSort: null,
      currentOrder: null
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
    metricSortField() {
      // Map the current metric display to its sort field
      switch (this.metricToShow) {
        case 'Demographics':
          return 'demog_percent_complete'
        case 'Facial measurements':
          return 'fm_percent_complete'
        case 'Num masks tested':
          return 'num_unique_masks_tested'
        default:
          return 'demog_percent_complete'
      }
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
    // Initialize sort state from route query params
    this.currentSort = this.$route.query.sort || null
    this.currentOrder = this.$route.query.order || null

    await this.getCurrentUser()
    if (this.currentUser) {
      await this.loadData()
    }
    await this.fetchRecommenderColumns()
  },
  mounted() {
    // Emit initial pagination state after component is mounted
    this.$nextTick(() => {
      this.emitPaginationUpdate()
    })
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
    },
    totalCount() {
      this.emitPaginationUpdate()
    },
    currentPage() {
      this.emitPaginationUpdate()
    },
    perPage() {
      this.emitPaginationUpdate()
    },
    managedUsers() {
      // Also emit when managed users change (data loaded)
      this.$nextTick(() => {
        this.emitPaginationUpdate()
      })
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    emitPaginationUpdate() {
      this.$emit('pagination-update', {
        currentPage: this.currentPage,
        perPage: this.perPage,
        totalCount: this.totalCount
      })
    },
    loadData(page = 1) {
      const admin = this.isAdminView
      const sort = this.currentSort
      const order = this.currentOrder
      this.loadManagedUsers({ admin, page, perPage: 25, sort, order })
    },
    toggleSort(field) {
      if (this.currentSort === field) {
        // Same field - cycle through: asc -> desc -> null
        if (this.currentOrder === 'asc') {
          this.currentOrder = 'desc'
        } else if (this.currentOrder === 'desc') {
          // Remove sort
          this.currentSort = null
          this.currentOrder = null
        }
      } else {
        // New field - start with ascending
        this.currentSort = field
        this.currentOrder = 'asc'
      }

      // Update route with new sort params
      this.updateRoute()

      // Reload data with new sort
      this.loadData(1) // Reset to page 1 when sorting changes
    },
    updateRoute() {
      const query = { ...this.$route.query }

      if (this.currentSort && this.currentOrder) {
        query.sort = this.currentSort
        query.order = this.currentOrder
      } else {
        // Remove sort params when clearing sort
        delete query.sort
        delete query.order
      }

      // Reset to page 1 when sort changes
      delete query.page

      this.$router.push({ query })
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

  .sortable-header {
    cursor: pointer;
    user-select: none;
    position: relative;
    transition: background-color 0.2s;
  }

  .sortable-header:hover {
    background-color: #f0f0f0;
  }

  .sort-indicator {
    margin-left: 0.5em;
    font-size: 0.8em;
    color: #007bff;
  }

  @media(max-width: 700px) {
    .sortable-header {
      padding: 0.5em 0.3em;
    }

    .sort-indicator {
      display: inline-block;
      margin-left: 0.2em;
    }
  }

</style>
