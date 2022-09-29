<template>
  <div class='justify-content-center column'>
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
        <th>Individual risk given 1 infector</th>

        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='roundOut(this.risk, 6)'
            :style="styleProps"
            />
        </td>
      </tr>
      <tr>
        <th>
          Average New infections
        </th>

        <td>
            <ColoredCell
                :colorScheme="riskColorScheme"
                :maxVal=1
                :value='roundOut(numSusceptibles * risk, 1)'
                class='inline'
                :style="styleProps"
            />
        </td>
      </tr>

    </table>
    <div class='multi-column'>
      <div
        class='align-items-center column'
       >

        <h2>Average New Infections</h2>
        <div class='justify-content-center column'>
          <span>On average, assuming {{ numInfectors }} COVID infector(s) in the room, and that everyone stays there for {{selectedHour}} hour(s), the number of people that would be infected is

              <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(numSusceptibles * risk, 1)'
                  class='inline'
                  :style="styleProps"
              />:
          </span>
        </div>
        <div class='people-icons people '>
          <PersonIcon
            backgroundColor='red'
            :amount='numInfected'
          />
          <PersonIcon
            backgroundColor='green'
            :amount='numSusceptibles - numInfected'
          />
        </div>
      </div>

      <div
        class='align-items-center column'
       >

        <h2>Lost Labor & Lost Wages</h2>

        <table>
          <tr>
            <th>
              Lost Labor and Wages
            </th>
            <td>
              <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(peopleCost(), 1)'
                  :text='`$${roundOut(peopleCost(), 1)}`'
                  class='inline'
                  :style="styleProps"
              />
            </td>
          </tr>
        </table>
        <p>
          We define <span class='italic'>lost labor</span> as businesses paying for employees taking sick
          days. For those employees that no longer have sick days, then the time they are
          taking off is considered to be <span class='italic'>lost wages</span>.

          <span class='bold'>
          Either way, when someone is sick, someone is paying for it, whether it
          be a business or the individual itself.
          </span>

          This metric combines both concepts.
        </p>

        <p>
          Assuming a wage of
          ${{wage}}/hour, and that each infected person takes off for 5 days after
          infection, doing this intervention costs at least
          <span class='bold'>${{ peopleCost() }}</span> in terms of <span
          class='italic'>lost wages/labor</span>.  Implementation cost of the intervention (initial +
          recurring cost of 3 months) is
          <span class='bold'> ${{ selectedIntervention.implementationCostInYears(0.25) }}</span>, for a total cost of
          <span class='bold'> ${{ selectedIntervention.implementationCostInYears(0.25) + peopleCost() }}</span>.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import PersonIcon from './person_icon.vue'

import { useAnalyticsStore } from './stores/analytics_store'
import { round } from './misc.js'
import { Intervention } from './interventions.js'
import { mapWritableState, mapState, mapActions } from 'pinia';
import { getSampleInterventions } from './sample_interventions.js'
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
    // TODO: could pull in information from event/1 from Rails.
    ...mapWritableState(
        useAnalyticsStore,
        [
          // 'selectedIntervention'
        ]
    ),
    numInfected() {
      return round(this.numSusceptibles * this.risk, 0) || 0
    },
    risk() {
      const duration = 1
      return (1 - (1-this.selectedIntervention.computeRiskRounded(duration, this.numInfectors))**this.selectedHour)
    },
    interventions() {
      let numPeopleToInvestIn = 1
      return getSampleInterventions(this.event, numPeopleToInvestIn)
    },

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
  data() {
    return {
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
    }
  },
  props: {
    numSusceptibles: Number,
    event: Object,
    numInfectors: Number,
    selectedIntervention: Object,
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
  }

  .people-icons {
    padding-top: 1em;
    padding-bottom: 1em;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .align-items-center {
    display: flex;
    align-items: center;
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

  .multi-column {
    display: flex;
    flex-direction: row;
  }

</style>
