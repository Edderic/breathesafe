<template>
  <tr @click="centerMapTo(this.measurements.id)" class='clickable' :class='{ clicked: this.measurements.clicked }'>
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
      <div class='tag' @click="showAnalysis(this.measurements.id)">See Analysis</div>
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
import { riskColorInterpolationScheme } from './colors.js'
import { mapWritableState, mapState, mapActions } from 'pinia'

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
      return riskColorInterpolationScheme
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
          'centerMapTo',
          'showAnalysis'
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
