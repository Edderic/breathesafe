<template>
<div class='col'>
    <div class='middle-controls horizontally-center controls'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">
      <select class='margined' :value='eventDisplayRiskTime' @change='setDisplayRiskTime'>
        <option>At this hour</option>
        <option>At 25% occupancy</option>
        <option>At 50% occupancy</option>
        <option>At 75% occupancy</option>
        <option>At max occupancy</option>
      </select>

      <select class='margined' :value='`${selectedMask.numWays}-way ${selectedMask.maskName}`' @change='setMaskType'>
        <option v-for='m in masks'>{{ m.numWays }}-way {{ m.maskName }}</option>
      </select>
      <router-link class='margined button' to="/events/new" v-if='signedIn'>Create</router-link>
    </div>

    <div class='scrollable'>
      <table>
        <tr>
          <th></th>
          <th>Room</th>
          <th>Address</th>
          <th class='clickable col justify-space-between'>
            1-hr Risk
          </th>
          <th class='desktop'>
            1-hr Risk w/ 1 Infector
          </th>
          <th class='desktop'>Show Analysis</th>
          <th v-if="adminView">User ID</th>
          <th v-if="adminView">Approve</th>
        </tr>
        <tr>
          <td></td>
          <td></td>
          <td></td>
          <td class='desktop'>
            <div class='row horizontally-center' >
              <span :style="circleCSS" @click='sortByRisk'>
                {{this.sortRiskArrow}}
              </span>
              <router-link :style="circleCSS" to='/faqs#one-hr-risk'>
                ?
              </router-link>
            </div>
          </td>
          <td>
            <div class='row horizontally-center'>
              <span :style="circleCSS" @click='sortByInfectorRisk'>{{this.sortRiskInfectorArrow}}</span>

              <router-link :style="circleCSS" to='/faqs#one-hr-risk-with-infector'
              title="This risk assumes that there is an infector is in the room."
              >
              ?
              </router-link>
            </div>
          </td>
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
import { Mask, MASKS } from './masks.js'
import { toggleCSS } from './colors.js'
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
        useEventStores,
        [
          'events',
          'displayables',
          'masks',
          'numWays',
          'selectedMask'
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
    circleCSS() {
      let css = JSON.parse(JSON.stringify(toggleCSS))
      css['cursor'] = 'pointer'
      return css
    },
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
    this.eventDisplayRiskTime = this.$route.query['eventDisplayRiskTime'] || 'At max occupancy'
    await this.load();

    if (this.$route.query['mask']) {
      this.selectedMask = this.findMask(
          this.$route.query['mask'],
          this.$route.query['numWays']
      )
    }

    this.computeRiskAll(this.eventDisplayRiskTime, this.selectedMask)
    this.sortByParams()

    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        if (toQuery['eventDisplayRiskTime'] != previousQuery['eventDisplayRiskTime']) {
          this.eventDisplayRiskTime = toQuery['eventDisplayRiskTime']
        }
        if (toQuery['mask'] != previousQuery['mask'] || toQuery['numWays'] != previousQuery['numWays']) {
          this.selectedMask = this.findMask(
            toQuery['mask'],
            toQuery['numWays'],
          )
        }
        this.computeRiskAll(this.eventDisplayRiskTime, this.selectedMask)
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
      'eventDisplayRiskTime': 'At max occupancy'
    }
  },
  methods: {
    setDisplayRiskTime(e) {
      this.eventDisplayRiskTime = e.target.value
      let oldQuery = JSON.parse(JSON.stringify(this.$route.query))

      let newQuery = {
        eventDisplayRiskTime: this.eventDisplayRiskTime
      }

      Object.assign(oldQuery, newQuery)

      this.$router.push({
        name: 'MapEvents',
        query: oldQuery
      })
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
    newEvent() {
      this.setFocusTab('event')
    },
    updateSearch(event) {
      this.search = event.target.value
      this.displayables = filterEvents(this.search, this.events)
    },

    findMask(name, numWays) {
      return this.masks.find((m) => m.maskName == name && m.numWays == numWays)
    },

    setMaskType(event) {
      let val = event.target.value
      let numWays = val.split('-way ')[0]
      let name = val.split('-way ')[1]
      let query = JSON.parse(JSON.stringify(this.$route.query))

      Object.assign(query, {
        mask: name,
        numWays: numWays
      })

      this.$router.push({
        name: 'MapEvents',
        query: query
      })

    },

    sortByRisk() {
      this.computeRiskAll(this.eventDisplayRiskTime, this.selectedMask)

      let copy = JSON.parse(JSON.stringify(this.$route.query))
      let newQuery;

      if (!this.$route.query.sort || this.$route.query.sort != 'risk') {
        newQuery = {
          'sort': 'risk',
          'sort-how': 'ascending'
        }
      }

      else if (this.$route.query['sort-how'] == "descending" && this.$route.query.sort == 'risk') {
        newQuery = {
          'sort': 'risk',
          'sort-how': 'ascending'
        }

      } else if (this.$route.query['sort-how'] == 'ascending' && this.$route.query.sort == "risk") {
        newQuery = {
          'sort': 'risk',
          'sort-how': 'descending'
        }

      }

      Object.assign(copy, newQuery)
      this.$router.push(
        {
          name: 'MapEvents',
          query: copy
        }
      )
    },
    sortByInfectorRisk() {
      // this one is not dependent on occupancy. We're assuming that there's one person sick

      let copy = JSON.parse(JSON.stringify(this.$route.query))
      let newQuery;

      if (this.$route.query.sort != 'risk-infector') {
        newQuery = {
          'sort': 'risk-infector',
          'sort-how': 'ascending'
        }
      }

      else if (this.$route.query['sort-how'] == "descending" && this.$route.query.sort == 'risk-infector') {
        newQuery = {
          'sort': 'risk-infector',
          'sort-how': 'ascending'
        }
      }

      else if (this.$route.query['sort-how'] == 'ascending' && this.$route.query.sort == "risk-infector") {
        newQuery = {
          'sort': 'risk-infector',
          'sort-how': 'descending'
        }
      }

      Object.assign(copy, newQuery)
      this.$router.push(
        {
          name: 'MapEvents',
          query: copy
        }
      )
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
    text-align: center;
    vertical-align: center;
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
    display: flex;
    justify-content: center;
    padding: 0.5em;
    margin: 0 1em;
  }
  th {
    padding-top: 1em;
    padding-left: 1em;
    padding-right: 1em;
  }

  .scrollable {
    overflow-y: scroll;
    height: 50vh;
  }

  .row {
    display: flex;
  }

  .col {
    display: flex;
    flex-direction: column;
  }

  .justify-space-between {
    display: flex;
    justify-items: space-between;
    align-items: center;
  }

  .centered {

  }

  .table-header-title {
  }

  .controls {
    padding-top: 1em;
    padding-bottom: 1em;
    width: 100vw;
    background-color: #eee;
  }

  .button {
    color: white;
    border: none;
    font-weight: bold;
    border-radius: 2%;
    background-color: #aaa;
    text-shadow: 1px 1px 2px black;
    box-shadow: 1px 1px 2px black;
    text-decoration: none;
  }

  @media (max-width: 800px) {
    .middle-controls {
      display: flex;
      flex-direction: column;
    }
    .controls {
      width: auto;
    }
    .desktop {
      display: none;
    }
  }
  @media (min-width: 800px) {
    .middle-controls {
      display: flex;
      flex-direction: row;
    }
    .desktop {
      display: table-cell;
    }
  }
</style>
