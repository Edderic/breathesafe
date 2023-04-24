<template>
  <DrillDownSection

    title='Individual Risk'
    :value='risk'
    :text='english(risk)'
    :colorScheme='riskColorScheme'
    :showStat='false'
  >
  </DrillDownSection>
</template>

<script>
import { useAnalyticsStore } from './stores/analytics_store'
import { mapWritableState, mapState, mapActions } from 'pinia';
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue';
import DrillDownSection from './drill_down_section.vue';
import LineGraph from './line_graph.vue';
import {
  round,
  genConcCurve
} from  './misc';

export default {
  name: 'IndividualRisk',
  components: {
    CircularButton,
    ColoredCell,
    DrillDownSection,
    LineGraph
  },
  data() {
    return { show: true }
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
    numberOfDailyDrivesToEqualRisk() {
      /* Example: Let's say 0.036 was the individual risk.
       * Individual risk can be thought of getting into at least one accident
       * in one of the many drives. That many drives is x,  which is what we're
       * trying to find out.
       *
       * 0.036 = 1 - P(no accident | drive)^x
       * 1- 0.036 = P(no accident | drive)^x
       * 0.964 = P(no accident | drive)^x
       * log(.964) = x * log(.999904)
       * log(.964) / log (0.999904) = x
       */
      return Math.log(1 - this.risk) / Math.log(1 - this.averageDailyDrivingRisk)
    },
    constantConcentration() {
      // let curve = genConcCurve({
        // roomUsableVolumeCubicMeters: 10,
        // c0: 0,
        // generationRate: 1.6,
        // cadr: 20,
        // cBackground: 0,
        // windowLength: 180
      // })

      let collection = []
      for (let i = 0; i < 180; i++) {
        collection.push([i, 0.08])
      }

      return { points: collection, color: 'red', legend: 'constant concentration, g * b_r / Q' }
    },

    incorporatingACH() {
      let curve = genConcCurve({
        roomUsableVolumeCubicMeters: 10,
        c0: 0,
        generationRate: 1.6,
        cadr: 20,
        cBackground: 0,
        windowLength: 180
      })

      let collection = []
      for (let i = 0; i < curve.length; i++) {
        collection.push([i, curve[i]])
      }

      return { points: collection, color: 'blue', legend: 'incorporating ACH, g * b_r / Q * r_ss(t)' }
    },
    contaminationGenerationRateFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            g &= q \\cdot r_{ea} \\ r_{mi}
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    inhalationRateFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            \\text{inhalation rate} &= r_{ms} \\cdot r_{i} \\cdot r_{b}
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    contaminationRemovalRateFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            r &= V \\cdot \\lambda
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    rssFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            r_{ss}(t) &= \\frac{1}{t} \\int_0^{t} (1 - exp(-Q / V \\cdot t)) dt
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    doseFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            \\text{dose}&= \\text{concentration} \\cdot \\text{time}
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    transmissionFormula() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
            P(s \\mid e, I=1) &= 1 - \\text{exp}^{-\\text{dose}}
        \\end{aligned}
        \\end{equation}
        $$
      `
    },
    formula() {
      // t: transmission
      // h: duration
      // r_ss: steady state factor

      return ` $$


      $$
      `
    },
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
    english(val) {
      return `1 in ${round(1 / val, 1)}`
    },
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
  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .align-items-center {
    display: flex;
    align-items: center;
  }

  .col {
    display: flex;
    flex-direction: column;
  }

  .second-td {
    width: 8em;
  }
  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .italic {
    font-style: italic;
  }

  p, h1, h2, h3, h4, h5, h6 {
    text-align: left;
  }
</style>

