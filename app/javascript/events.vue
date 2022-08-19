<template>
  <div class='col'>
    <div class='row horizontally-center'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">
      <select class='margined' :value='eventDisplayRiskTime' @change='setDisplayRiskTime'>
        <option>At this hour</option>
        <option>At max occupancy</option>
      </select>
      <button class='margined' @click='newEvent'>Add New Event</button>
    </div>

    <div class='scrollable'>
      <table>
        <tr>
          <th>Room</th>
          <th>Address</th>
          <th class='clickable' @click='sortByRisk'
          >1-hr Risk ({{this.sortRiskArrow}})</th>
          <th
            title="This risk assumes that there is an infector is in the room."
          >1-hr Risk w/ 1 Infector</th>
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
import { useProfileStore } from './stores/profile_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { filterEvents, getWeekdayText } from './misc'
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
      if (this.sortRisk == 'Ascending') {
        return "↑"
      } else if (this.sortRisk == "Descending") {
        return "↓"
      }
      else {
        return "⇵"
      }
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
      'sortRisk': "None"
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
      if (this.sortRisk == "None" || this.sortRisk == "Descending") {
        this.displayables = this.displayables.sort((a, b) => a.risk - b.risk)
        this.sortRisk = "Ascending"
      } else if (this.sortRisk == "Ascending") {
        this.displayables = this.displayables.sort((a, b) => b.risk - a.risk)
        this.sortRisk = "Descending"
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
  button {
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
    height: 60vw;
  }

  @media ((max-height: 1200px) and (orientation: landscape)) {
    .scrollable {
      height: 30vw;
    }
  }

  @media ((max-height: 1180px) and (orientation: portrait)) {
    .scrollable {
      height: 100vw;
    }
  }

  @media ((max-height: 670px) and (orientation: landscape)) {
    .scrollable {
      height: 20vw;
    }
  }
</style>
