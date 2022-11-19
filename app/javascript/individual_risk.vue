<template>
  <div>
    <br id='individual-risk'>
    <br>
    <br>

    <h2>Individual risk</h2>
    <table>
      <tr>
        <th>Infection risk given {{numInfectors}} infector(s)</th>

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

        <th>Risk Relative to Having a Car Accident</th>

        <td>
        </td>
      </tr>
      <tr>
        <th>...Within the Average Daily Drive</th>

        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='roundOut(this.relativeRiskDailyDrive, 6)'
            :text='`${roundOut(this.relativeRiskDailyDrive, 0)}x`'
            :style="styleProps"
            />
        </td>
      </tr>
      <tr>
        <th>...Within Driving 1000 miles</th>

        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='this.relativeRisk1000Miles'
            :text='displayRelativeRisk1000Miles'
            :style="styleProps"
            />
        </td>
      </tr>
    </table>

    <p><a href="https://www.kbb.com/car-advice/average-miles-driven-per-year/">The average American drives 17.6 miles a day</a>. On average, the risk of getting into a car accident for driving that long is <span class='bold'>1 in {{roundOut(1 / averageDailyDrivingRisk, 0)}}</span>.
    Conditional on {{this.numInfectors}} infector(s) being present, the infection risk for the average susceptible individual is <span class='bold'>{{roundOut(this.relativeRiskDailyDrive, 0)}}x</span> that risk.
    </p>

    <p>

    <a href="https://carsurance.net/insights/odds-of-dying-in-a-car-crash/#:~:text=Odds%20of%20Getting%20in%20a%20Car%20Accident&text=In%20fact%2C%20your%20odds%20of,anywhere%20and%20at%20any%20time">The risk of getting into a car accident within the span of 1000 miles of driving is <span class='bold'>1 in {{roundOut(1 / thousandMilesRisk, 0)}}</span>.</a>

    Conditional on {{this.numInfectors}} infector(s) being present, the infection risk for the average susceptible individual is <span class='bold'>{{displayRelativeRisk1000Miles}}</span> that risk.
    </p>
  </div>
</template>

<script>
import { useAnalyticsStore } from './stores/analytics_store'
import { mapWritableState, mapState, mapActions } from 'pinia';
import ColoredCell from './colored_cell.vue';
import {
  round
} from  './misc';

export default {
  name: 'IndividualRisk',
  components: {
    ColoredCell
  },
  data() {
    return {}
  },
  props: {
    riskColorScheme: Array,
  },
  computed: {
    ...mapState(
      useAnalyticsStore,
      [
        'numInfectors',
        'risk',
        'styleProps'
      ]
    ),
    averageDailyDrivingRisk() {
      // The risk of getting into an accident when driving 1000 miles is 1 / 366
      // https://carsurance.net/insights/odds-of-dying-in-a-car-crash/#:~:text=Odds%20of%20Getting%20in%20a%20Car%20Accident&text=In%20fact%2C%20your%20odds%20of,anywhere%20and%20at%20any%20time.
      //
      // The average driver drives 35.4 miles a day (2020):
      // https://www.kbb.com/car-advice/average-miles-driven-per-year/
      //
      // P(car accident | distance=1000 miles) = 1 / 366
      // = 1 - P(no car accident | distance=35.4)^28.24 miles
      // P(no car accident | distance=35.4)^28.24 = 1 - 1 / 366
      // \sqrt[28.24]{1 - 1 / 366}

      return 0.000097
    },
    thousandMilesRisk() {
      return 1 / 366
    },
    relativeRiskDailyDrive() {
      return this.risk / this.averageDailyDrivingRisk
    },
    relativeRisk1000Miles() {
      return this.risk / this.thousandMilesRisk
    },

    displayRelativeRisk1000Miles() {
      if (this.relativeRisk1000Miles < 1) {
        return `${round(this.relativeRisk1000Miles, 3)}x`
      }

      return `${round(this.relativeRisk1000Miles, 0)}x`
    },
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  }

}
</script>

<style scoped>
  .bold {
    font-weight: bold;
  }
</style>