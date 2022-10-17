<template>
  <div>
    <h2>Savings</h2>
    <p>
      Compared to the scenario where no one is wearing masks and no portable air cleaner is added, doing this intervention as a business saves you

        <ColoredCell
          :colorScheme="interpolationScheme"
          :maxVal=1
          :value='difference'
          :text='differenceText'
          class='inline'
          :style="styleProps"
        />.
    </p>

    <table>
      <tr>
        <th>Total Cost of Not Masking and Not Adding PACs</th>
        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='nullCost'
            :text='nullCostText'
            :style="styleProps"
          />
        </td>
      </tr>
      <tr>
        <th>Total Cost of this Intervention</th>
        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='totalCost'
            :text='totalCostText'
            :style="styleProps"
          />
        </td>
      </tr>
      <tr>
        <th>Savings</th>
        <td>
          <ColoredCell
            :colorScheme="interpolationScheme"
            :maxVal=1
            :value='difference'
            :text='differenceText'
            :style="styleProps"
          />
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'

import { useAnalyticsStore } from './stores/analytics_store'
import { round } from './misc.js'
import { mapWritableState, mapState, mapActions } from 'pinia';
import { getSampleInterventions } from './sample_interventions.js'
import {
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  colorInterpolationSchemeAch,
  infectedPeopleColorBounds,
} from './colors.js';

export default {
  name: 'Savings',
  components: {
    ColoredCell,
  },
  computed: {
    // TODO: could pull in information from event/1 from Rails.
    ...mapState(
        useAnalyticsStore,
        [
          'averageNumTimesAnInfectorShowsUpPerYear',
          'nullIntervention',
          'numInfectors',
          'numSusceptibles',
          'peopleCost',
          'selectedHour',
          'styleProps',
          'totalCost',
          'totalCostText',
        ]
    ),
    peopleCostText() { return `$${this.peopleCost}` },
    implementationCostText() {
      return `$${this.selectedIntervention.implementationCostInYears(1)}`
    },
    peopleCostArgs() {
      return {
        wage: 15,
        duration: this.selectedHour,
        numInfectors: this.numInfectors,
        numSusceptibles: this.numSusceptibles,
        numDaysOff: 5,
        numHoursPerDay: 8,
      }
    },
    nullCost() {
      return round(
        this.nullIntervention.implementationCostInYears(1)
        + this.averageNumTimesAnInfectorShowsUpPerYear
        * this.nullIntervention.peopleCost(this.peopleCostArgs),
      -2)
    },

    nullCostText() {
      return `$${round(this.nullCost, 0)}`
    },

    interpolationScheme() {
      return colorInterpolationSchemeAch
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },

    difference() {
      return this.nullCost - this.totalCost
    },

    differenceText() {
      return `$${round(this.difference, 0)}`
    },
  },
  data() {
    return {
      wage: 15,
      numDaysOff: 5,
      numHoursPerDay: 8
    }
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },

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
    margin: 1em;
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

  .container {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
  }

</style>
