<template>
  <tr @click="focusEvent(this.measurements.id)" class='clickable' :class='{ clicked: this.measurements.clicked }'>
    <td>{{this.measurements.roomName}}</td>
    <td>{{this.measurements.placeData.formattedAddress}}</td>
    <ColoredCell
      :colorScheme="colorInterpolationScheme"
      :maxVal=1
      :value='measurements.risk'
      :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black' }"
    />
    <td>
      {{ startDatetimeParsed }}
    </td>
    <td>
      <div class='tag' v-for="t in getOpenHours(this.measurements.placeData)">{{ t }}</div>
    </td>
  </tr>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import { useEventStores } from './stores/event_stores';
import { useEventStore } from './stores/event_store';
import { useMainStore } from './stores/main_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { useProfileStore } from './stores/profile_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { findCurrentOccupancy, filterEvents, getWeekdayText } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'
import { sampleComputeRisk, simplifiedRisk, maskToPenetrationFactor } from './misc'

export default {
  name: 'MeasurementsRow',
  components: {
    ColoredCell
  },
  computed: {
    ...mapState(useProfileStore, ['eventDisplayRiskTime']),
    ...mapState(usePrevalenceStore, ['numPositivesLastSevenDays', 'numPopulation', 'uncountedFactor', 'maskType']),
    ...mapState(useEventStore, ['infectorActivityTypeMapping']),
    ...mapState(
        useShowMeasurementSetStore,
        [
          'roomName',
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'ventilationCo2AmbientPpm',
          'ventilationCo2MeasurementDeviceModel',
          'ventilationCo2MeasurementDeviceName',
          'ventilationCo2MeasurementDeviceSerial',
          'ventilationCo2SteadyStatePpm',
          'duration',
          'private',
          'formatted_address',
          'infectorActivity',
          'infectorActivityTypeMapping',
          'maskTypes',
          'numberOfPeople',
          'occupancy',
          'maximumOccupancy',
          'placeData',
          'portableAirCleaners',
          'rapidTestResult',
          'rapidTestResults',
          'roomHeightMeters',
          'roomLengthMeters',
          'roomWidthMeters',
          'roomUsableVolumeFactor',
          'singlePassFiltrationEfficiency',
          'startDatetime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes'
        ]
    ),
    colorInterpolationScheme() {
      return [
        {
          'lowerBound': 0.1,
          'upperBound': 0.999999,
          'lowerColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
          'upperColor': {
            name: 'darkRed',
            r: 174,
            g: 17,
            b: 0
          },
        },
        {
          'lowerBound': 0.01,
          'upperBound': 0.1,
          'lowerColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
          'upperColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
        },
        {
          'lowerBound': 0.001,
          'upperBound': 0.01,
          'lowerColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'upperColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
        },
        {
          'lowerBound': 0.0001,
          'upperBound': 0.001,
          'upperColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'lowerColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
        },
        {
          'lowerBound': -0.000001,
          'upperBound': 0.0001,
          'upperColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
          'lowerColor': {
            name: 'dark green',
            r: 11,
            g: 161,
            b: 3
          },
        },
      ]
    },
    startDatetimeParsed() {
      let dt = new Date(this.measurements.startDatetime)
      let options = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
      return `${dt.toLocaleDateString(undefined, options)} ${dt.toLocaleTimeString()}`
    },
  },
  data() {
    return {
    }
  },
  props: {
    measurements: Object,
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
