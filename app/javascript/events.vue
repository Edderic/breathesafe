<template>
  <div class='col'>
    <div class='row horizontally-center'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">
      <select class='margined' :value='eventDisplayRiskTime' @change='setDisplayRiskTime'>
        <option>At this hour</option>
        <option>At max occupancy</option>
      </select>
      <router-link class='margined button' to="/events/new">Add New Event</router-link>
    </div>

    <div class='scrollable'>
      <table>
        <tr>
          <th>Room</th>
          <th>Address</th>
          <th class='clickable' @click='sortByRisk'
          >1-hr Risk ({{this.sortRiskArrow}})
          <router-link to='/faqs#one-hr-risk'>
          (?)
          </router-link>
          </th>
          <th
            title="This risk assumes that there is an infector is in the room."
            @click='sortByInfectorRisk'
          >1-hr Risk w/ 1 Infector ({{this.sortRiskInfectorArrow}})

          <router-link to='/faqs#one-hr-risk-with-infector'>
          (?)
          </router-link>
          </th>
          <th>Show Analysis</th>
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
        ]
    ),
    sortRiskArrow() {
      return sortArrow(this.$route.query['sort-how'], this.$route.query.sort == 'risk')
    },
    sortRiskInfectorArrow() {
      return sortArrow(this.$route.query['sort-how'], this.$route.query.sort == 'risk-infector')
    }
  },
  created() {
  },
  mounted() {
    this.load()
  },
  data() {
    return {
      'search': "",
      'sortRisk': "None",
      'sortRiskInfector': "None",
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
        this.displayables = this.displayables.sort((a, b) => a.risk - b.risk)
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
        this.displayables = this.displayables.sort((a, b) => b.risk - a.risk)
        this.sortRisk = "Descending"

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
      this.computeRiskAll()
      if (!this.$route.query.sort ||
          this.$route.query.sort != "risk-infector" ||

          (this.$route.query.sort == "risk-infector"
          && this.$route.query['sort-how'] == "descending")
         ) {
        this.displayables = this.displayables.sort(
(a, b) => new Intervention(a, []).computeRisk() - new Intervention(b, []).computeRisk())
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
        this.displayables = this.displayables.sort(
(a, b) => new Intervention(b, []).computeRisk() - new Intervention(a, []).computeRisk())

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
  .button {
    padding: 1em 3em;
  }

  .tag {
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
