<template>
  <div>
    <br id='clean-air-delivery-rate'>
    <br>
    <br>
    <h4>Clean Air Delivery Rate</h4>

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

    <p>
    To give context of what <ColoredCell
          :colorScheme="colorScheme"
          :maxVal=1
          :value='roundOut(totalFlowRate, 0)'
          :style='cellCSSMerged'
        />
    {{
    measurementUnits.airDeliveryRateMeasurementType}} means, that is
    about {{
      roundOut(totalFlowRatePerAirCleanerSuggestion, 1)}} times the amount 1
      <a :href="airCleanerSuggestion.website"> {{
        airCleanerSuggestion['singular']}}
      </a> outputs.
      <span>
        Adding {{
        numSuggestedAirCleaners }} {{ airCleanerSuggestion['plural'] }} would
        increase the CADR to

        <ColoredCell
          :colorScheme="colorScheme"
          :maxVal=1
          :value='totalFlowRatePlusExtraPacRounded'
          :style='cellCSSMerged'
        />
          {{ measurementUnits.airDeliveryRateMeasurementType}}, which would
          decrease the probability of infection by a factor of <span class='bold'>{{
            roundOut(factor, 1)
          }}</span> (assuming the risk was low to begin with).
      </span>
    </p>

    <p>
    A combination of larger rooms along with high ACH can reduce the risk
    of contracting COVID-19 and other airborne viruses. The product of the two
    gives us the Clean Air Delivery Rate (CADR). The higher it is,
    relative to the production rate of contaminants such as airborne
    viruses like that of COVID-19, the safer the environment.
    </p>

  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue';

import {
  displayCADR,
  round
} from  './misc';

export default {
  name: 'CADR',
  components: {
    ColoredCell,
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
    'cellCSSMerged': Object,
    'measurementUnits': Object,
    'numSuggestedAirCleaners': Number,
    'colorScheme': Object,
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

</style>
