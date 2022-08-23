<template>
  <div class='col'>
    <div class='row horizontally-center'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">
      <select class='margined' :value='eventDisplayRiskTime' @change='setDisplayRiskTime'>
        <option>At this hour</option>
        <option>At max occupancy</option>
      </select>
      <router-link class='margined' to="/events/new" v-if='signedIn'>Add New Event</router-link>
    </div>

    <div class='scrollable'>
      <table>
        <tr>
          <th>Room</th>
          <th>Address</th>
          <th class='clickable'>
          <span @click='sortByRisk'>
            1-hr Risk ({{this.sortRiskArrow}})
          </span>
          <router-link to='/faqs#one-hr-risk'>
          (?)
          </router-link>
          </th>
          <th
            title="This risk assumes that there is an infector is in the room."
            class='clickable'
          >
          <span @click='sortByInfectorRisk'>
            1-hr Risk w/ 1 Infector ({{this.sortRiskInfectorArrow}})
          </span>

          <router-link to='/faqs#one-hr-risk-with-infector'>
          (?)
          </router-link>
          </th>
          <th>Show Analysis</th>
          <th v-if="adminView">User ID</th>
          <th v-if="adminView">Approve</th>
        </tr>
        <MeasurementsRow v-for="ev in displayables" :key="ev.id" :measurements="ev"/>
      </table>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import MeasurementsRow from './measurements_row.vue';
import { Intervention } from './interventions.js';
import { useProfileStore } from './stores/profile_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { filterEvents, getWeekdayText, sortArrow } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'Events',
  components: {
    Event,
    MeasurementsRow
  },
  computed: {
    ...mapWritableState(
        useProfileStore,
        [
          'eventDisplayRiskTime',
        ]
    ),
    ...mapWritableState(
        useEventStores,
        [
          'events',
          'displayables'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'focusTab',
          'signedIn'
        ]
    ),
    ...mapState(
        useMainStore,
        [
          'isAdmin',
        ]
    ),
    adminView() {
      return this.isAdmin && this.$route.query['admin-view'] == 'true'
    },
    sortRiskArrow() {
      return sortArrow(this.$route.query['sort-how'], this.$route.query.sort == 'risk')
    },
    sortRiskInfectorArrow() {
      return sortArrow(this.$route.query['sort-how'], this.$route.query.sort == 'risk-infector')
    }
  },
  async created() {
    await this.load()
    this.sortByParams()

    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        this.sortByParams()
        // react to route changes...
      }
    )
  },
  mounted() {
  },
  data() {
    return {
      'search': "",
    }
  },
  methods: {
    setDisplayRiskTime(e) {
      this.eventDisplayRiskTime = e.target.value
      this.updateProfile()
      this.computeRiskAll()
    },
    getOpenHours(x) {
      return getWeekdayText(x)
    },
    ...mapActions(
        useMainStore,
        [
          'setFocusTab',
          'focusEvent'
        ]
    ),
    ...mapActions(
        useEventStores,
        [
          'load',
          'computeRiskAll'
        ]
    ),
    ...mapActions(
        useProfileStore,
        [
          'updateProfile'
        ]
    ),
    newEvent() {
      this.setFocusTab('event')
    },
    updateSearch(event) {
      this.search = event.target.value
      this.displayables = filterEvents(this.search, this.events)
    },

    sortByRisk() {
      this.computeRiskAll()
      if (!this.$route.query.sort || this.$route.query.sort != 'risk' || this.$route.query['sort-how'] == "descending" && this.$route.query.sort == 'risk') {
        this.$router.push(
          {
            name: 'MapEvents',
            query: {
              'sort': 'risk',
              'sort-how': 'ascending'
            }
          }
        )
      } else if (this.$route.query.sort == "risk" && this.$route.query['sort-how'] == 'ascending') {
        this.$router.push(
          {
            name: 'MapEvents',
            query: {
              'sort': 'risk',
              'sort-how': 'descending'
            }
          }
        )
      }
    },
    sortByInfectorRisk() {
      if (!this.$route.query.sort ||
          this.$route.query.sort != "risk-infector" ||
          (this.$route.query.sort == "risk-infector"
          && this.$route.query['sort-how'] == "descending")
         ) {
        this.$router.push(
          {
            name: 'MapEvents',
            query: {
              'sort': 'risk-infector',
              'sort-how': 'ascending'
            }
          }
        )
      } else if (this.$route.query.sort == "risk-infector" && this.$route.query['sort-how'] == "ascending") {
        this.$router.push(
          {
            name: 'MapEvents',
            query: {
              'sort': 'risk-infector',
              'sort-how': 'descending'
            }
          }
        )
      }
    },

    sortByParams() {
      if (this.$route.query.sort == 'risk' && this.$route.query['sort-how'] == 'ascending') {
        this.displayables = this.displayables.sort((a, b) => a.risk - b.risk)
      }

      else if (this.$route.query.sort == 'risk' && this.$route.query['sort-how'] == 'descending') {
        this.displayables = this.displayables.sort((a, b) => b.risk - a.risk)
      }
      else if (this.$route.query.sort == 'risk-infector' && this.$route.query['sort-how'] == 'ascending') {
        this.displayables = this.displayables.sort(
          (a, b) => new Intervention(a, []).computeRisk() - new Intervention(b, []).computeRisk()
        )
      }
      else if (this.$route.query.sort == 'risk-infector' && this.$route.query['sort-how'] == 'descending') {
        this.displayables = this.displayables.sort(
          (a, b) => new Intervention(b, []).computeRisk() - new Intervention(a, []).computeRisk()
        )
      }
    }
  },
}
</script>

<style scoped>
  tr:hover.clickable {
    background-color: #efefef;
    cursor: pointer;
  }
  .clicked {
    background-color: #e6e6e6;
  }
  td {
    padding: 1em;
  }

  .col {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .horizontally-center {
    display: flex;
    justify-content: center;
  }

  .margined {
    padding: 1em;
    margin: 1em;
  }
  th {
    padding: 1em;
  }

  .scrollable {
    overflow-y: scroll;
    height: 50vh;
  }

</style>
