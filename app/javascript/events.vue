<template>
<div class='col'>
    <div class='middle-controls horizontally-center controls'>
      <div class='space-around row'>
        <Pin class='pin' @click='setLocation' height='48px' width='48px'/>
        <router-link to="/events/new">
          <CircularButton class='circular-button' text='+'/>
        </router-link>
      </div>

      <input class='margined' @change="updateSearch" placeholder="Search for events">

      <div class='row space-around'>
        <select class='margined' :value='durationHours' @change='setDuration'>
          <option value=1>1 hour</option>
          <option value=2>2 hours</option>
          <option value=4>4 hours</option>
          <option value=8>8 hours</option>
          <option value=40>40 hours</option>
        </select>

        <select class='margined' :value='`${selectedMask.numWays}-way ${selectedMask.maskName}`' @change='setMaskType'>
          <option v-for='m in masks'>{{ m.numWays }}-way {{ m.maskName }}</option>
        </select>
      </div>
    </div>

    <div class='scrollable'>
      <table>
        <!--//add thead th element in the scrollable element for sticky col headers in .scrollable css-->
        <thead>
          <tr>
            <th></th>
            <th>Room</th>
            <th>Address</th>
            <th class='desktop'>
              <div>
                Risk w/ 1 Infector
                <div class='row space-around'>
                  <span :style="circleCSS" @click='sortByInfectorRisk'>{{this.sortRiskInfectorArrow}}</span>

                  <div :style="circleCSS" @click='showGradeInfo = !showGradeInfo'>
                    ?
                  </div>
                </div>
              </div>
            </th>
            <th v-if='permittedGeolocation'>
              <div>
                Est. Distance
                <div class='row horizontally-center'>
                  <span :style="circleCSS" @click='sortByDistance'>{{this.sortDistanceArrow}}</span>

                </div>
              </div>
            </th>
            <th v-if="adminView">User ID</th>
            <th v-if="adminView">Approve</th>
          </tr>
        </thead>
        <MeasurementsRow v-for="ev in displayables" :key="ev.id" :measurements="ev" :permittedGeolocation='permittedGeolocation'/>
      </table>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import Button from './button.vue';
import CircularButton from './circular_button.vue';
import ColoredCell from './colored_cell.vue';
import MeasurementsRow from './measurements_row.vue';
import Pin from './pin.vue';
import { Mask, MASKS } from './masks.js'
import { gradeColorMapping, toggleCSS } from './colors.js'
import { Intervention } from './interventions.js';
import { useProfileStore } from './stores/profile_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { filterEvents, getWeekdayText, sortArrow } from './misc'
import { riskColorInterpolationScheme } from './colors'
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'Events',
  components: {
    Button,
    ColoredCell,
    CircularButton,
    Event,
    Pin,
    MeasurementsRow
  },
  computed: {
    ...mapWritableState(
        useEventStores,
        [
          'events',
          'displayables',
          'durationHours',
          'masks',
          'numWays',
          'selectedMask',
          'showGradeInfo'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'center',
          'focusTab',
          'signedIn',
          'zoom',
          'whereabouts'
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
    },
    sortDistanceArrow() {
      return sortArrow(this.$route.query['sort-how'], this.$route.query.sort == 'distance')
    }
  },
  async created() {
    // await this.getWhereabouts()
    this.loadMasks()

    if (this.$route.query['mask']) {
      this.selectedMask = this.findMask( this.$route.query['mask'], this.$route.query['numWays'])
    }

    if (this.$route.query['durationHours']) {
      this.durationHours = parseInt(this.$route.query['durationHours'])
    }

    await this.load()
    this.computeRiskAll(this.selectedMask)
    this.sortByParams()

    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        if (!toQuery['mask']) {
          let selectedMask= this.findMask(
            'No mask',
            1,
          )
          this.selectedMask = selectedMask
        } else if (toQuery['mask'] != previousQuery['mask'] || toQuery['numWays'] != previousQuery['numWays']) {
          this.selectedMask = this.findMask(
            toQuery['mask'],
            toQuery['numWays'],
          )
        }

        if (toQuery['durationHours']) {
          this.durationHours = parseInt(toQuery['durationHours'])
        }

        this.computeRiskAll(this.selectedMask)
        this.sortByParams()
        // react to route changes...
      }
    )
  },
  mounted() {
  },
  data() {
    return {
      'permittedGeolocation': false,
      'search': "",
      'riskColorScheme': riskColorInterpolationScheme
    }
  },
  methods: {
    async setLocation() {
      this.showGradeInfo = false
      let coordinates = await this.$getLocation()
      // test if the getLocation

      this.whereabouts = coordinates
      this.center = { lat: coordinates.lat, lng: coordinates.lng };
      this.zoom = 15;
      this.permittedGeolocation = true;

      await this.load()
      this.computeRiskAll(this.selectedMask)
      this.sortByParams()
    },

    getOpenHours(x) {
      return getWeekdayText(x)
    },
    pluralize(property, word) {
      if (this[property] > 1) {
        return `${this[property]} ${word}s`
      }

      return `${this[property]} ${word}`
    },
    ...mapActions(
        useMainStore,
        [
          'setFocusTab',
          'focusEvent',
          'getWhereabouts'
        ]
    ),
    ...mapActions(
        useEventStores,
        [
          'load',
          'loadMasks',
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
      return this.masks.find((m) => m.maskName == name && m.numWays == parseInt(numWays))
    },

    setDuration(event) {
      let val = parseInt(event.target.value)
      let query = JSON.parse(JSON.stringify(this.$route.query))

      Object.assign(query, {
        durationHours: val,
      })

      this.$router.push({
        name: 'Venues',
        query: query
      })

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
        name: 'Venues',
        query: query
      })

    },

    sortByRisk() {
      this.computeRiskAll(this.selectedMask)

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
          name: 'Venues',
          query: copy
        }
      )
    },
    sortByDistance() {
      let copy = JSON.parse(JSON.stringify(this.$route.query))
      let newQuery;

      if (this.$route.query.sort != 'distance') {
        newQuery = {
          'sort': 'distance',
          'sort-how': 'ascending'
        }
      }

      else if (this.$route.query['sort-how'] == "descending" && this.$route.query.sort == 'distance') {
        newQuery = {
          'sort': 'distance',
          'sort-how': 'ascending'
        }
      }

      else if (this.$route.query['sort-how'] == 'ascending' && this.$route.query.sort == 'distance') {
        newQuery = {
          'sort': 'distance',
          'sort-how': 'descending'
        }
      }

      Object.assign(copy, newQuery)
      this.$router.push(
        {
          name: 'Venues',
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
          name: 'Venues',
          query: copy
        }
      )
    },

    sortByParams() {
      if (this.$route.query.sort == 'risk-infector' && this.$route.query['sort-how'] == 'ascending') {
        this.displayables = this.displayables.sort((a, b) => a.risk - b.risk)
      }

      else if (this.$route.query.sort == 'risk-infector' && this.$route.query['sort-how'] == 'descending') {
        this.displayables = this.displayables.sort((a, b) => b.risk - a.risk)
      }
      else if (this.$route.query.sort == 'distance' && this.$route.query['sort-how'] == 'ascending') {
        this.displayables = this.displayables.sort(
          (a, b) => a.distance - b.distance
        )
      }
      else if (this.$route.query.sort == 'distance' && this.$route.query['sort-how'] == 'descending') {
        this.displayables = this.displayables.sort(
          (a, b) => b.distance - a.distance
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

    text-align: center;
    vertical-align: center;
    /*
    padding: 1em;
    padding: 8px 16px;
    border: 1px solid #ccc;
    */
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
    background: #eee;
    /*
    padding: 8px 16px;
    border: 1px solid #ccc;
    padding-top: 1em;
    padding-left: 1em;
    padding-right: 1em;
    */
  }

  .scrollable {
    overflow-y: auto;
    height: 85vh;
    width: 100%;
  }

  .scrollable table {
    width: 100%;
  }

  .scrollable thead th {
    position: sticky;
    top: 0;
  }

  .row {
    display: flex;
    flex-direction: row;
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
    width: 100%;
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

  .pin {
    border: 0;
    padding: 0;
  }

  th {
    padding: 1em;
  }
  .space-around {
    display: flex;
    justify-content: space-around;
  }

  .circular-button {
    margin: 0;
  }

  @media (max-width: 1400px) {
    .col {
      height: 60vh;
    }
  }

  @media (max-width: 800px) {
    .middle-controls {
      display: flex;
      flex-direction: column;
    }
    .controls {
      width: 100%;
    }

    .scrollable {
      font-size: 0.9em;
    }
    .desktop {
      /*display: none;*/
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
