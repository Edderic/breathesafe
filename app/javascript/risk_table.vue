<template>
  <div class='centered column'>
    <table>
      <tr>
        <th>
           Intervention
        </th>
        <td>
          <select class='centered' >
            <option :value="interv.id" v-for='interv in interventions'>{{interv.websitesAndText[0].text}}</option>
          </select>
        </td>
      </tr>

      <tr>
        <th>Duration</th>
        <td>
          <select @change='setDuration'>
            <option :value="i" v-for='(v, i) in hoursToSelect'>{{v}}</option>
          </select>
        </td>
      </tr>
      <tr>
        <th>Individual risk given 1 infector</th>

        <td>
          <ColoredCell
            v-if="intervention"
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='roundOut(1 - (1-intervention.computeRiskRounded())**selectedHour, 6)'
            :style="styleProps"
            />
        </td>
      </tr>
    </table>
    <div
      class='people centered column'
     >

      <div class='centered column'>
        <span>On average, assuming max occupancy (~{{maximumOccupancy}}), and that there is one COVID infector in the room, and that everyone stays there for {{selectedHour}} hour(s), the number of people that would be infected is

            <ColoredCell
                v-if="intervention"
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='roundOut(maximumOccupancy * (1 - (1-intervention.computeRiskRounded())**selectedHour), 1)'
                class='inline'
                :style="styleProps"
            />:
        </span>
      </div>
      <div class='people-icons'>
        <PersonIcon
          backgroundColor='red'
          :amount='numInfected'
        />
        <PersonIcon
          backgroundColor='green'
          :amount='maximumOccupancy - numInfected'
        />
      </div>

      <p>
        Assuming a wage of ${{wage}}/hour, and that each infected person takes
        off for 5 days after infection, doing this intervention costs at least
        <span class='bold'>${{ peopleCost() }}</span> in terms of <span
        class='italic'>lost wages/labor</span>. Lost wages here are the wages not
        received by sick employees who no longer have sick days. Similarly,
        lost labor in terms of some business paying money for people being out on
        sick days.
      </p>
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
  computed: {
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
      ],
      wage: 15,
      numDaysOff: 5,
      numHoursPerDay: 8
    }
  },
  methods: {
    peopleCost() {
      return this.numInfected * this.wage * this.numDaysOff * this.numHoursPerDay
    },
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

  .people-icons {
    padding-top: 1em;
    padding-bottom: 1em;
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

  .inline {
    display: inline-block;
  }

  .bold {
    font-weight: bold;
  }

  .italic {
    font-style: italic;
  }


</style>
