<template>
  <tr @click="focusEvent(this.measurements.id)" class='clickable' :class='{ clicked: this.measurements.clicked }'>
    <td>{{this.measurements.roomName}}</td>
    <td>{{this.measurements.placeData.formattedAddress}}</td>
    <td>{{risk}}</td>
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
import { useEventStore } from './stores/event_store';
import { useMainStore } from './stores/main_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { filterEvents, getWeekdayText } from './misc'
import { mapWritableState, mapState, mapActions } from 'pinia'
import { sampleComputeRisk, maskToPenetrationFactor } from './misc'

export default {
  name: 'MeasurementsRow',
  components: {
  },
  computed: {
    ...mapState(usePrevalenceStore, ['numPositivesLastSevenDays', 'numPopulation', 'uncountedFactor', 'maskType']),
    ...mapState(useEventStore, ['infectorActivityTypeMapping']),
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

      return sampleComputeRisk(
        numSamples,
        activityGroups,
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious
      )
    }
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
