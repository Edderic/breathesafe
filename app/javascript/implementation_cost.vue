<template>
  <div class='justify-content-center column'>
    <div class='item'>
      <h2>Cost of Implementation</h2>
      <p>
        Implementation cost of the intervention (initial +
          recurring cost of 3 months) is
          <span class='bold'> ${{ selectedIntervention.implementationCostInYears(0.25) }}</span>
      </p>
    </div>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'

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
