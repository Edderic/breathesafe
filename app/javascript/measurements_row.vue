<template>
  <tr @click="focusEvent(this.measurements.id)" class='clickable' :class='{ clicked: this.measurements.clicked }'>
    <td>{{this.measurements.roomName}}</td>
    <td>{{this.measurements.placeData.formattedAddress}}</td>
    <ColoredCell
      :colorScheme="colorInterpolationScheme"
      :maxVal=1
      :value='risk'
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
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { filterEvents, getWeekdayText } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'
import { sampleComputeRisk, simplifiedRisk, maskToPenetrationFactor } from './misc'

export default {
  name: 'MeasurementsRow',
  components: {
    ColoredCell
  },
  computed: {
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
    risk: function() {
      const probaRandomSampleOfOneIsInfectious = this.numPositivesLastSevenDays
        * this.uncountedFactor / this.numPopulation || 0.001
      const flowRate = this.measurements.roomUsableVolumeCubicMeters * this.measurements.totalAch
      const susceptibleAgeGroup = '30 to <40' // TODO:
      const susceptibleMaskType = this.maskType
      const susceptibleMaskPenentrationFactor = maskToPenetrationFactor[susceptibleMaskType]

      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.33
      const quanta = basicInfectionQuanta * variantMultiplier

      // TODO: randomly pick from the set of activity groups. Let's say there
      // are two activity groups, one with 10 people who are doing X and 5
      // people doing Y.
      // Activity Factor for Y should be sampled about 5 out of 15 times?
      const activityGroups = this.measurements.activityGroups
      const occupancyFactor = 1.0 // ideally, would change based on time and day
      const maximumOccupancy = this.measurements.maximumOccupancy


      let occupancy = parseFloat(maximumOccupancy) * occupancyFactor
      const numSamples = 1000000

      let risk = simplifiedRisk(
        activityGroups,
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious
      )

      let digitsFactor = 1000000
      return Math.round(risk * digitsFactor) / digitsFactor
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
