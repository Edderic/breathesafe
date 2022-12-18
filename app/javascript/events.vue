<template>
<div class='col'>
    <div class='middle-controls horizontally-center controls'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">

      <select class='margined' :value='`${selectedMask.numWays}-way ${selectedMask.maskName}`' @change='setMaskType'>
        <option v-for='m in masks'>{{ m.numWays }}-way {{ m.maskName }}</option>
      </select>
      <div class='space-around'>
      <Pin class='pin' @click='setLocation' height='48px' width='48px'/>
      <router-link to="/events/new" v-if='signedIn'>
        <CircularButton class='circular-button' text='+'/>
      </router-link>
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
                1-hr Risk w/ 1 Infector
                <div class='row horizontally-center'>
                  <span :style="circleCSS" @click='sortByInfectorRisk'>{{this.sortRiskInfectorArrow}}</span>

                  <router-link :style="circleCSS" to='/faqs#one-hr-risk-with-infector'
                  title="This risk assumes that there is an infector is in the room."
                  >
                  ?
                  </router-link>
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
          <tr>
            <th></th>
            <th></th>
            <th></th>
            <th v-if='permittedGeolocation'></th>
            <th>
            </th>
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
import MeasurementsRow from './measurements_row.vue';
import Pin from './pin.vue';
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
    Button,
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
          'masks',
          'numWays',
          'selectedMask',
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
    this.eventDisplayRiskTime = this.$route.query['eventDisplayRiskTime'] || 'At max occupancy'
    // await this.getWhereabouts()

    if (this.$route.query['mask']) {
      this.selectedMask = this.findMask(
        this.$route.query['mask'],
        this.$route.query['numWays']
      )
    }
    await this.load()
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
      'permittedGeolocation': false,
      'search': "",
      'eventDisplayRiskTime': 'At max occupancy'
    }
  },
  methods: {
    async setLocation() {
      let coordinates = await this.$getLocation()
      // test if the getLocation

      this.whereabouts = coordinates
      this.center = { lat: coordinates.lat, lng: coordinates.lng };
      this.zoom = 15;
      this.permittedGeolocation = true;

      await this.load()
      this.computeRiskAll(this.eventDisplayRiskTime, this.selectedMask)
      this.sortByParams()
    },

    setDisplayRiskTime(e) {
      this.eventDisplayRiskTime = e.target.value
      let oldQuery = JSON.parse(JSON.stringify(this.$route.query))

      let newQuery = {
        eventDisplayRiskTime: this.eventDisplayRiskTime
      }

      Object.assign(oldQuery, newQuery)

      this.$router.push({
        name: 'Venues',
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
          'focusEvent',
          'getWhereabouts'
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
        name: 'Venues',
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
    height: 80vh
  }

  .scrollable thead th {
    position: sticky;
    top: 0;
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

  .pin {
    border: 0;
    padding: 0;
  }

  .space-around {
    display: flex;
    justify-content: space-around;
  }

  .circular-button {
    margin: 0;
  }



  @media (max-width: 1400px) {
    .scrollable {
      height: 45vh;
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
