<template>
  <table>
    <tr>
      <th></th>
      <th>1 hour</th>
      <th>4 hours</th>
      <th>8 hours</th>
      <th>40 hours</th>
    </tr>

    <tr>
      <th>Risk w/ 1 infector</th>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='intervention.computeRiskRounded()'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**4, 6)'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**8, 6)'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**40, 6)'
          :style="styleProps"
      />
      </td>
    </tr>
    <tr>
      <th>Average # of Susceptibles Infected under Max Occupancy</th>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :text='roundOut(this.maximumOccupancy * intervention.computeRiskRounded(), 1)'
          :value='this.maximumOccupancy * intervention.computeRiskRounded()'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**4), 1)'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**8), 1)'
          :style="styleProps"
      />
      </td>
      <td>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**40), 1)'
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
</style>
