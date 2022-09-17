<template>
  <div class='centered column'>
    <table>
      <tr>
        <th>Duration</th>
        <td>
          <select @change='setDuration'>
            <option :value="i" v-for='(v, i) in hoursToSelect'>{{v}}</option>
          </select>
        </td>
      </tr>
      <tr>
        <th>Risk</th>

        <ColoredCell
            v-if="intervention"
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='roundOut(1 - (1-intervention.computeRiskRounded())**selectedHour, 6)'
            :style="styleProps"
        />
        </tr>
    </table>

    <div
      class='people'
     >
      <PersonIcon
        backgroundColor='red'
        :amount='numInfected'
      />
      <PersonIcon
        backgroundColor='green'
        :amount='maximumOccupancy - numInfected'
      />
    </div>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import PersonIcon from './person_icon.vue'

import { round } from './misc.js'
import {
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
} from './colors.js';

export default {
  name: 'RiskTable',
  components: {
    ColoredCell,
    PersonIcon
  },
  data() {
    return {
      numInfected: round(this.maximumOccupancy * (1 - (1-this.intervention.computeRiskRounded())), 0),
      selectedHour: 1,
      hoursToSelect: [
        '1 hour',
        '4 hours',
        '8 hours',
        '40 hours',
      ]
    }
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },

    setDuration(event) {
      this.selectedHour = this.hoursToSelect[event.target.value].split(' ')[0]
      this.risk = (1 - (1-this.intervention.computeRiskRounded())**this.selectedHour)
      this.numInfected = round(this.maximumOccupancy * this.risk, 0)
    }
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
    padding: 1em;
  }
  th {
    padding: 1em;
    width: 4em;
  }

  .people {
    width: 22em;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

</style>
