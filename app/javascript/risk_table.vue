<template>
  <div>
    <table>
      <tr>
        <th></th>
        <th class='header'>Risk w/ 1 infector</th>
        <th class='header'>Average # of Susceptibles Infected under Max Occupancy</th>
      </tr>

      <tr v-for='h in [1, 4, 8, 40]' @click='click(roundOut(this.maximumOccupancy* (1 - (1-intervention.computeRiskRounded())**h), 1))'>
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
    <div
      class='people'
     >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="#000000"
        viewBox="13 22 13 33"
        height='2em'
        width='1em'
        v-for="index in 200"
        :key="index"
      >
        <g>
          <circle cx="19" cy="27" r="5" fill="red" />
          <path d='m 23 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' fill='red'/>
        </g>
      </svg>
    </div>
  </div>
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
  data() {
    numInfected: 100
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },

    click(numInfected) {
      this.numInfected = round(numInfected, 1)
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

  .people {
    width: 22em;
  }
</style>
