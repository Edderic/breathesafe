<template>
  <DrillDownSection

    title='...Using Prevalence & Occupancy'
    :value='risk'
    :text='english(risk)'
    :colorScheme='riskColorScheme'
  >

    <p>
    This is the risk of transmission that uses "Probability that at least one
    infector is present." It weights the probability of transmission given one
    infector in the room by the "Probability that at least one infector is
    present." The probability of transmission given one infector is affected by
    environmental and behavioral factors (e.g. masking, ventilation, filtration).
    Here we also make use of prevalence and occupancy to assess risk of transmission.
    </p>

    <p>
    Things that affect this risk:

    <ul>
      <li>masking</li>
      <li>ventilation</li>
      <li>filtration</li>
      <li>inhalation activity</li>
      <li>infector activity</li>
      <li>infectiousness of SARS-CoV-2</li>
      <li>occupancy</li>
      <li>prevalence of infectors in the population</li>
    </ul>

    </p>
        <h3>Mathematical Details</h3>
        <p>
        The risk of transmission <vue-mathjax formula='$s$'></vue-mathjax>
incorporating environmental factors (e.g. air cleaning)
<vue-mathjax formula='$e_2$'></vue-mathjax> and evidence about people's infectiousness status <vue-mathjax formula='$e_1$'></vue-mathjax> (e.g. Rapid Tests, PCR, symptoms) is <vue-mathjax formula='$P(s \mid e_1, e_2)$'></vue-mathjax>. Through the sum and product rules of probability, we could expand it as such:
        </p>
        <p>

<vue-mathjax formula='$$P(\text{s} \mid e_1, e_2) = \sum_i P(\text{s} \mid e_2, e_1, i) \cdot P(i \mid e_2, e_1)$$'></vue-mathjax>

        </p>
        <p>Once we know how many people are infectious <vue-mathjax formula='$i$'></vue-mathjax>, then knowing about the result of rapid tests, PCR, or symptoms (<vue-mathjax formula='$e_1$'></vue-mathjax>) doesn't tell us anything about the probability of transmission. Therefore, we can omit it from the first term:
        </p>
        <p>
          <vue-mathjax formula='$$P(s \mid e_2, e_1, i) = P(s \mid e_2, i)$$'></vue-mathjax>
        </p>
        <p>Likewise, for the <vue-mathjax formula='$P(i \mid e_2, e_1)$'></vue-mathjax> term, we assume that knowing about venue type (e.g. bar, hospital) or behavior (e.g. masking) doesn't tell us anything about the probability of being infectious, so we'll omit <vue-mathjax formula='$e_2$'></vue-mathjax> from it:</p>

        <p>
        <vue-mathjax formula='$$P(i \mid e_2, e_1) = P(i \mid e_1)$$'></vue-mathjax>
        </p>

        <p>In practice, it probably does matter, but for convenience, we'll go with the above assumption.</p>
        <p>So far we have:</p>
        <p><vue-mathjax formula='$$P(\text{s} \mid e_1, e_2) = \sum_i P(\text{s} \mid e_2, i) \cdot P(i \mid e_1)$$'></vue-mathjax></p>

        <p>We can simplify this even more, assuming that at most, there could be one infector in the room (and not 2 or more):</p>
        <p><vue-mathjax formula='$$P(\text{s} \mid e_1, e_2) \approx P(\text{s} \mid e_2, I=1) \cdot P(I \geq 1 \mid e_1)$$'></vue-mathjax></p>

        <p>
        The right term
<vue-mathjax formula='$P(I \geq 1 \mid e_1)$'></vue-mathjax>
is the <span class='italic'>probability that at least one person is infectious, given some evidence
<vue-mathjax formula='e'></vue-mathjax>.
</span> See the "Probability that at least one person is infectious" section above to get more details about this.
        The left term
        <vue-mathjax formula='$P(s \mid e_2, I=1)$'></vue-mathjax>
        is the probability of transmission given evidence e, assuming there's one infector, where <vue-mathjax formula='$e_2$'></vue-mathjax> stands for environmental factors such as the non-infectious air delivery rate, masking behavior of people, and activities done by people. See the
 "Assuming One Infector is Present" statistic above for more details.

        </p>

        <p>Note that the approximation above is more likely to be true when the prevalence of COVID is very low, such that having two or more infectors in a space is unlikely. However, if the probability of having two or more infectors is high, this approximation might underestimate the risk  -- for example in a COVID ward of a hospital.</p>


  </DrillDownSection>
</template>

<script>
import { useAnalyticsStore } from './stores/analytics_store'
import { mapWritableState, mapState, mapActions } from 'pinia';
import { riskToGrade } from './colors.js';
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
    grade() {
      return `${riskToGrade(this.risk)}`
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
</style>

