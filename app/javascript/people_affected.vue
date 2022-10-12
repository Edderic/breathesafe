<template>
  <div
    class='item'
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
        :amount='roundOut(numInfected, 0)'
      />
      <PersonIcon
        backgroundColor='green'
        :amount='numSusceptibles - roundOut(numInfected, 0)'
      />
    </div>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import PersonIcon from './person_icon.vue'
import { round } from './misc.js'
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
} from './colors.js';
import { useAnalyticsStore } from './stores/analytics_store.js'

export default {
  name: 'PeopleAffected',
  components: {
    ColoredCell,
    PersonIcon
  },
  computed: {
    // TODO: could pull in information from event/1 from Rails.
    ...mapWritableState(
        useAnalyticsStore,
        [
          'numInfected',
          'numSusceptibles',
          'selectedHour',
          'risk'
        ]
    ),
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
    }
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },

  },
  props: {
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
