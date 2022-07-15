<template>
  <div class='col'>
    <div class='row horizontally-center'>
      <input class='margined' @change="updateSearch" placeholder="Search for events">
      <button class='margined' @click='newEvent'>Add New Event</button>
    </div>
    <table>
      <tr>
        <th>Room</th>
        <th>Address</th>
        <th>Total ACH</th>
        <th>Types</th>
        <th>Open Hours</th>
      </tr>
      <tr class='clickable' v-for="ev in displayables" :key="ev.id" @click="focusEvent(ev.id)">
        <td>{{ev.roomName}}</td>
        <td>{{ev.placeData.formattedAddress}}</td>
        <td>{{Math.round(ev.totalAch * 10) / 10}}</td>
        <td>
          <div class='tag' v-for="t in ev.placeData.types">{{ t }}</div>
        </td>
        <td>
          <div class='tag' v-for="t in getOpenHours(ev.placeData)">{{ t }}</div>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { filterEvents, getWeekdayText } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'App',
  components: {
    Event
  },
  computed: {
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
    background-color: #e6e6e6;
    cursor: pointer;
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
</style>
