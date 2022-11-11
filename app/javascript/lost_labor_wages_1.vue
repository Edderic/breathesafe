<template>
  <div
    class='item'
   >

    <div
      class='item'
     >
      <br id='lost-labor-and-wages'>
      <br>
      <br>

      <h2>Lost Labor & Lost Wages</h2>

      <div class='align-items-center'>
        <table>
          <tr>
            <th>
            </th>
            <th>
              Lost Labor and Wages
            </th>
          </tr>
          <tr>
            <th>
              Per Event
            </th>
            <td>
              <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(peopleCost, 1)'
                  :text='`$${roundOut(peopleCost, 1)}`'
                  :style="styleProps"
              />
            </td>
          </tr>
          <tr>
            <th>
              Per Year
            </th>
            <td>
              <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='yearlyPeopleCost'
                  :text='yearlyPeopleCostText'
                  :style="styleProps"
              />
            </td>
          </tr>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import PersonIcon from './person_icon.vue'
import { round } from './misc.js'
import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store.js'
import {
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
} from './colors.js';

export default {
  name: 'LostLaborWages1',
  components: {
    ColoredCell,
    PersonIcon
  },
  computed: {
    // TODO: could pull in information from event/1 from Rails.
    ...mapState(
      useAnalyticsStore,
      [
        'risk',
        'peopleCost',
        'averageNumTimesAnInfectorShowsUpPerYear',
        'yearlyPeopleCost',
        'yearlyPeopleCostText'
      ]
    ),
    numInfected() {
      return round(this.numSusceptibles * this.risk, 1) || 0
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
