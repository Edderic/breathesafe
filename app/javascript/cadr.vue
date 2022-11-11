<template>
  <div>
    <br id='clean-air-delivery-rate'>
    <br>
    <br>
    <h2>Clean Air Delivery Rate</h2>

    <div class='container'>
      <div class='centered'>
        <CleanAirDeliveryRateTable
          :measurementUnits='measurementUnits'
          :systemOfMeasurement='systemOfMeasurement'
          :intervention='selectedIntervention'
          :cellCSS='cellCSS'
        />
      </div>
    </div>
  </div>
</template>

<script>
import CleanAirDeliveryRateTable from './clean_air_delivery_rate_table.vue'
import ColoredCell from './colored_cell.vue';

import {
  displayCADR,
  round
} from  './misc';

export default {
  name: 'CADR',
  components: {
    ColoredCell,
    CleanAirDeliveryRateTable,
  },
  data() {
    return {}
  },
  computed: {
    newCADRcubicMetersPerHour() {
      return this.totalFlowRateCubicMetersPerHour + this.airCleanerSuggestion.cubicMetersPerHour * this.numSuggestedAirCleaners
    },
    totalFlowRatePlusExtraPacRounded() {
      // TODO: could pull from risk.js airCleaners instead


      return round(displayCADR(this.systemOfMeasurement, this.newCADRcubicMetersPerHour), 0)
    },
    factor() {
      return this.newCADRcubicMetersPerHour / this.totalFlowRateCubicMetersPerHour
    },
    totalFlowRatePerAirCleanerSuggestion() {
      return this.totalFlowRateCubicMetersPerHour / this.airCleanerSuggestion.cubicMetersPerHour
    }
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  },
  props: {
    'airCleanerSuggestion': Object,
    'cellCSS': Object,
    'cellCSSMerged': Object,
    'measurementUnits': Object,
    'numSuggestedAirCleaners': Number,
    'colorScheme': Object,
    'selectedIntervention': Object,
    'systemOfMeasurement': String,
    'totalFlowRate': Number,
    'totalFlowRateCubicMetersPerHour': Number,
  }
}
</script>

<style scoped>
  .bold {
    font-weight: bold;
  }
  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }

</style>
