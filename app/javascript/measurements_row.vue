<template>
  <tr @click="focusEvent(this.measurements.id)" class='clickable' :class='{ clicked: this.measurements.clicked }'>
    <td>{{this.measurements.roomName}}</td>
    <td>{{this.measurements.placeData.formattedAddress}}</td>
    <td>{{Math.round(this.measurements.totalAch * 10) / 10}}</td>
    <td>
      <div class='tag' v-for="t in this.measurements.placeData.types">{{ t }}</div>
    </td>
    <td>
      <div class='tag' v-for="t in getOpenHours(this.measurements.placeData)">{{ t }}</div>
    </td>
  </tr>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { filterEvents, getWeekdayText } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'MeasurementsRow',
  components: {
  },
  computed: {
  },
  data() {
    return {
    }
  },
  props: {
    measurements: Object
  },
  methods: {
    getOpenHours(x) {
      return getWeekdayText(x)
    },
    ...mapActions(
        useMainStore,
        [
          'focusEvent'
        ]
    ),
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
</style>
