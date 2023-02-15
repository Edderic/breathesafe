<template>
  <DrillDownSection

    title='Average New Infections'
    :value='roundOut(numSusceptibles * risk, 1)'
    :text='roundOut(numSusceptibles * risk, 1)'
    :colorScheme='averageInfectedPeopleInterpolationScheme'
  >
    <tr>
      <td colspan=2>
        <div class='explainer'>
          <span>On average, assuming {{ numInfectors }} COVID infector(s) in
          the room, and that everyone stays there for {{selectedHour}} hour(s), the
          number of people that would be infected is <span
          class='bold'>{{roundOut(numSusceptibles * risk, 1)}}</span>:

          </span>
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

          <p>If the average number of new infections is less than 1 everywhere,
          COVID-19 will become extinct. Business owners can do their part by making their
          environments less conducive to spread, for example, by adopting higher indoor
          air quality standards and masking. <span class='bold'>At the very least,
          aim for a combination of interventions to keep the average new infections below 1</span>.
          </p>
        </div>
      </td>
    </tr>
  </DrillDownSection>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import CircularButton from './circular_button.vue'
import DrillDownSection from './drill_down_section.vue'
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
    CircularButton,
    ColoredCell,
    DrillDownSection,
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
      show: false
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

  .col {
    display: flex;
    flex-direction: column;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .second-td {
    width: 8em;
  }
</style>
