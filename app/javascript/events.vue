<template>
  <div class='col'>
    <div class='row horizontally-center'>
      <input class='margined' v-model="search" placeholder="Search for events">
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
      <tr v-for="ev in events" :key="ev.id">
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
          'events'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'focusTab'
        ]
    )
  },
  created() {
    this.load()
  },
  data() {
  },
  methods: {
    ...mapActions(
        useMainStore,
        [
          'setFocusTab'
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
  },
}
</script>

<style scoped>
  td {
    padding: 1em;
  }
  button {
    padding: 1em 3em;
  }
</style>
