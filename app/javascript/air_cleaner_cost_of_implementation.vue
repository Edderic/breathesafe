<template>
  <div class='justify-content-center column'>
    <div>
      <br id='air-cleaner-cost-details'>
      <br>
      <br>
      <h2>Air Cleaner Cost Details</h2>
      <p>
        Implementation cost of the intervention (initial +
          recurring for a whole year) is

        <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='implementationCost'
            :text='implementationCostText'
            class='inline'
            :style="styleProps"
        />.
      </p>
      <table>
        <tr>
          <th>Air Cleaner</th>
          <td>{{airCleaner.amountText()}}</td>
        </tr>
        <tr>
          <th>Initial Cost</th>
          <td>{{airCleaner.initialCostText()}}</td>
        </tr>
        <tr>
          <th>Recurring Cost</th>
          <td>{{airCleaner.recurringCostText()}}</td>
        </tr>
      </table>
    </div>
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
  infectedPeopleColorBounds,
} from './colors.js';

export default {
  name: 'AirCleanerCostOfImplementation',
  components: {
    ColoredCell,
  },
  computed: {
    // TODO: could pull in information from event/1 from Rails.
    ...mapState(
        useAnalyticsStore,
        [
          'styleProps'
        ]
    ),
    airCleaner() {
      return this.selectedIntervention.findPortableAirCleaners()
    },
    numInfected() {
      return round(this.numSusceptibles * this.risk, 0) || 0
    },
    ...mapState(useAnalyticsStore, ['risk']),
    implementationCost() {
      return this.airCleaner.costInYears(1)
    },
    implementationCostText() {
      return `$${this.implementationCost}`
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
