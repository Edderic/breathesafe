<template>
  <div>
    <button @click='newEvent'>Add New Event</button>
    <table>
      <tr>
        <th>Address</th>
        <th>Room</th>
        <th>Total ACH</th>
      </tr>
      <tr v-for="ev in events" :key="ev.id">
        <td>{{ev.placeData.formattedAddress}}</td>
        <td>{{ev.roomName}}</td>
        <td>{{Math.round(ev.totalAch * 10) / 10}}</td>
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
