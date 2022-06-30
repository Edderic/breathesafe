<template>
  <div>
    <button @click='newEvent'>Add New Event</button>
    <table>
      <tr>
        <th>Address</th>
        <th>Room</th>
      </tr>
      <tr v-for="ev in events">
        <td>{{ev.placeData.formattedAddress}}</td>
        <td>{{ev.roomName}}</td>
      </tr>
    </table>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
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
    ...mapActions(
        useMainStore,
        [
          'setFocusTab'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'focusTab'
        ]
    )
  },
  created() { },
  data() {
  },
  methods: {

    newEvent() {
      this.setFocusTab('event')
    }
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
