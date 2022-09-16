<template>
  <table>
    <tr>
      <th></th>
      <th class='header'>Risk w/ 1 infector</th>
      <th class='header'>Average # of Susceptibles Infected under Max Occupancy</th>
    </tr>

    <tr v-for='h in [1, 4, 8, 40]'>
      <th>{{h}} hour</th>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**h, 6)'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**h), 1)'
          :style="styleProps"
      />
      </td>
    </tr>
  </table>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import { round } from './misc.js'
import {
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
} from './colors.js';

export default {
  name: 'RiskTable',
  components: {
    ColoredCell
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },

  },
  computed: {
    styleProps() {
      return {
          'font-weight': 'bold',
          'color': 'white',
          'text-shadow': '1px 1px 2px black',
          'padding': '1em'
        }
    },
    averageInfectedPeopleInterpolationScheme() {
      const copy = JSON.parse(JSON.stringify(riskColorInterpolationScheme))
      return assignBoundsToColorScheme(copy, infectedPeopleColorBounds)
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
  },
  props: {
    intervention: Object,
    maximumOccupancy: Number,
  }
}
</script>

<style scoped>
  table {
    border-spacing: 0;
  }
  th {
    padding: 1em;
    width: 4em;
  }
</style>
