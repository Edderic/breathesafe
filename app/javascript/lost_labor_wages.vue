<template>
  <div
    class='item'
   >

    <div
      class='item'
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
        class='italic'>lost wages/labor</span>.
      </p>
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
  name: 'LostLaborWages',
  components: {
    ColoredCell,
    PersonIcon
  },
  computed: {
    // TODO: could pull in information from event/1 from Rails.
    ...mapState(useAnalyticsStore, ['risk']),
    numInfected() {
      return round(this.numSusceptibles * this.risk, 0) || 0
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
