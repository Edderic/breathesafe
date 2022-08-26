<template>
  <table>
    <tr>
      <th></th>
      <th>1 hour</th>
      <th>8 hours</th>
      <th>40 hours</th>
      <th>80 hours</th>
    </tr>

    <tr>
      <th>Risk w/ 1 infector</th>
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='intervention.computeRiskRounded()'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**8, 6)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**40, 6)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="riskColorScheme"
          :maxVal=1
          :value='roundOut(1 - (1-intervention.computeRiskRounded())**80, 6)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
    </tr>
    <tr>
      <th>Average # of Susceptibles Infected under Max Occupancy</th>
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :text='roundOut(this.maximumOccupancy * intervention.computeRiskRounded(), 1)'
          :value='this.maximumOccupancy * intervention.computeRiskRounded()'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**8), 1)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**40), 1)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
      <ColoredCell
          v-if="intervention"
          :colorScheme="averageInfectedPeopleInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**80), 1)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em'}"
      />
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
    maximumOccupancy: Number
  }
}
</script>
