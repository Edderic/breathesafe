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
          <th>Risk</th>
          <th>Measurements taken on</th>
          <th>Open Hours</th>
        </tr>
        <MeasurementsRow v-for="ev in displayables" :key="ev.id" :measurements="ev" />
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
    )
  },
  created() {
    this.load()
  },
  data() {
    return {
      'search': ""
    }
  },
  methods: {
    setDisplayRiskTime(e) {
      this.eventDisplayRiskTime = e.target.value
      this.updateProfile()
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
          'load'
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
    height: 40em;
  }
</style>
