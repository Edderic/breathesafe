<template>
  <DrillDownSection

    title='...Assuming One Infector is Present'
    :value='conditionalRisk'
    :text='english(conditionalRisk)'
    :colorScheme='riskColorScheme'
  >

    <p>
    This is the risk of transmission assuming that there is one infector in the room, and takes into account air cleaning tools along with behavioral information.
    </p>

    <p>Things that affect this risk:</p>

    <ul>
      <li>masking</li>
      <li>ventilation</li>
      <li>filtration</li>
      <li>inhalation activity</li>
      <li>infector activity</li>
      <li>infectiousness of SARS-CoV-2</li>
    </ul>



        <h3>Mathematical Details</h3>

        <p>The probability of tranmission <vue-mathjax formula='$s$'></vue-mathjax>, assuming we know environmental (e.g. ventilation/filtration) and behavioral variables (e.g. susceptible and infector behaviors such as masking), and assuming that there is one infector is as follows:

</p>

        <p>
<vue-mathjax :formula='transmissionFormula'></vue-mathjax>
        </p>

        <p>The dose can take a value between 0 and positive infinity. Zero dose leads to a 0 probability of transmission, while a very large dose basically leads to a probability of 1.</p>

        <p>
        The dose that one gets is the following:
        <vue-mathjax formula='$$ \text{dose} = \int_0^t \text{c(t)} \cdot dt$$'></vue-mathjax>

        In other words, take the area under the curve of the concentration with respect to time. When an infector and susceptible come in at the same time and stay there, the concentration curve starts at 0 and then increases. The rate of increase slows down until it reaches 0. At that point the steady state concentration is reached.
        </p>


        <LineGraph
          :lines="[constantConcentration, incorporatingACH]"
          :ylim='[0, 0.09]'
          title='Contaminant concentration over time'
          xlabel='Time (min)'
          ylabel='Contaminant concentration (quanta / min)'
          :legendStartOffset='[0.45, 0.55]'
          :roundXTicksTo='0'
        />
        <p>



        The higher the concentration of infectious air when a susceptible breathes, the less time it takes to infect someone. Likewise, the more time a susceptible spends inhaling some concentration, the higher the
        probability of transmission for that susceptible.
        </p>
        <p>
        <vue-mathjax formula='$\text{concentration(t)}$'></vue-mathjax> can be broken down into the following:

        <vue-mathjax formula='$$\text{concentration}(t) = g \cdot b_r / Q \cdot r_{ss}(t)$$'></vue-mathjax>
        where <vue-mathjax formula='$g$'></vue-mathjax> is the contamination generation rate (quanta / h), <vue-mathjax formula='$r_{mi}$'> is the masking penetration of the infector, </vue-mathjax> <vue-mathjax formula='$b_r$'></vue-mathjax> is the inhalation rate (m3 / h), <vue-mathjax formula='$Q$'></vue-mathjax> is the contamination removal rate (m3 / h),  <vue-mathjax formula='$t$'></vue-mathjax> is the duration (hours), and <vue-mathjax formula='$r_{ss}(t)$'></vue-mathjax> is a factor that tells us the height of the curve at a given <vue-mathjax formula='$t$'></vue-mathjax>.
        </p>

        <h4>Contamination generation rate</h4>
        <vue-mathjax formula='$$g = q \cdot b_a \cdot r_{mi}$$'></vue-mathjax>

        <p>The contamination generation rate is composed of the basic quanta generation rate <vue-mathjax formula='$q$'></vue-mathjax> times the infector exhalation factor <vue-mathjax formula='$b_a$'></vue-mathjax>, times the masking penetration factor <vue-mathjax formula='$r_{mi}$'></vue-mathjax>.</p>

        <h5>Quanta generation rates</h5>
        <p>
        Quanta generation rate <vue-mathjax formula='$q$'></vue-mathjax> is the parameter that corresponds with how infectious an airborne pathogen is. For SARS-CoV-2, researchers have estimated as high as 18.6 quanta per hour for the Wuhan variant, and as high as <a href="https://docs.google.com/spreadsheets/d/16K1OQkLD4BjgBdO8ePj6ytf-RpPMlJ6aXFg3PrIQBbQ/edit#gid=1425126572">60 quanta per hour for Omicron BA.2</a>. In our calculations we use 100 to be on the more cautious side.
        </p>

        <h5>Infector Exhalation Factor</h5>
        <p>
          The infector exhalation factor <vue-mathjax formula='$b_a$'></vue-mathjax> is a multiplier. <span class='italic'>Staying quiet is less risky than talking, which is less risky than loud talking. </span>
        </p>

        <h5>Masking Penetration of Infector</h5>
        <p>
          The masking penetration of infector <vue-mathjax formula='$r_{mi}$'></vue-mathjax> is a multiplier that corresponds to how much pollution goes through the infector's mask (or leaks around it), a value between 0 and 1. <span class='italic'>N95s have much lower penetration factors than surgical masks and cloth masks.</span>
        </p>

        <h4>Inhalation rate</h4>
        <p>Inhalation rate <vue-mathjax formula='$b_r$'></vue-mathjax> is equal to the following:
        <vue-mathjax formula='$$ b_r = b \cdot r_i \cdot r_{mi}$$'></vue-mathjax>
        </p>
        <h5>Basic breathing rate</h5>
        <p>
        <vue-mathjax formula='$b$'></vue-mathjax> is the basic breathing rate. It depends on age and activity. For a 20 - 30 year old at rest, it's 0.288
<vue-mathjax formula='$m^3 / \text{hr}$'></vue-mathjax>.

        <h5>Susceptible activity factor</h5>

        <vue-mathjax formula='$r_i$'></vue-mathjax> is a factor of the susceptible taking into account the increase of breathing rate relative to being at rest when taking into account more strenuous activities. <span class='italic'>The faster a susceptible breathes in (e.g. when exercising), the higher the risk, relative to breathing slowly (e.g. at rest).</span>

        <h5>Susceptible masking penetration factor</h5>
        <vue-mathjax formula='$r_{mi}$'></vue-mathjax> is the masking penetration factor for the susceptible (between 0 and 1). Like masking for source control for the infector, masks also protect in terms of lowering the inhalation dose. <span class='italic'>N95s have much low penetration factors than surgical masks and cloth masks.</span>
        </p>

        <h4>Non-infectious air delivery rate</h4>
        <p>The non-infectious air delivery rate <vue-mathjax formula='$Q$'></vue-mathjax> is the product of the room volume <vue-mathjax formula='$V$'></vue-mathjax> and the total Air Changes per Hour (ACH) <vue-mathjax formula='$\lambda$'></vue-mathjax>:</p>

        <p><vue-mathjax formula='$$Q = \lambda \cdot V$$'></vue-mathjax></p>

        <p>The total air changes per hour <vue-mathjax formula='$\lambda$'></vue-mathjax> is the sum of air changes from portable air cleaners <vue-mathjax formula='$\lambda_{\text{PAC}}$'></vue-mathjax>, ventilation <vue-mathjax formula='$\lambda_{\text{Vent}}$'></vue-mathjax>, and UV <vue-mathjax formula='$\lambda_{\text{UV}}$'></vue-mathjax>:</p>
        <p><vue-mathjax formula='$$\lambda = \lambda_{\text{PAC}} + \lambda_{\text{Vent}} + \lambda_{\text{UV}}$$'></vue-mathjax></p>

        <h4>Steady-state factor</h4>
        <p>
        The steady-state factor <vue-mathjax formula='$r_{ss}(t)$'></vue-mathjax> gives us the height of the concentration curve at time <vue-mathjax formula='$t$'></vue-mathjax>.

        <vue-mathjax formula='$$r_{ss}(t) = 1 - \text{exp}(-Q / V \cdot t)$$'></vue-mathjax>

        At time <vue-mathjax formula='$t = 0$'></vue-mathjax>, we get 0. When enough time has passed, we get <vue-mathjax formula='$1$'></vue-mathjax> (i.e. the concentration has reached steady state).

        </p>
        <p>
        The <vue-mathjax formula='$Q/V$'></vue-mathjax> term is the ACH. When ACH is high, it takes less time to reach steady state (<vue-mathjax formula='$r_{ss}(t) = 1$'></vue-mathjax>). This happens when <vue-mathjax formula='$Q$'></vue-mathjax> is high relative to <vue-mathjax formula='$V$'></vue-mathjax>. When we have the opposite, when <vue-mathjax formula='$V$'></vue-mathjax> is relatively large relative to <vue-mathjax formula='$Q$'></vue-mathjax>, it takes a longer time to reach the steady state concentration.

        </p>

        <h3>Derivation of the Concentration Curve</h3>

        <p>The scenario we are considering is when the infector and susceptibles come in into the room at the same time, and that there were no infectors prior to the location (and therefore the initial concentration of dirty air is 0. The change in concentration over time is then dictated by the following equation:</p>

        <vue-mathjax formula='$$\frac{dC}{dt} = \frac{-Q \cdot C_{t} + g}{V}$$'></vue-mathjax>

        <p>where <vue-mathjax formula='$Q$'></vue-mathjax> is the non-infectious air delivery rate, <vue-mathjax formula='$C_t$'></vue-mathjax> is the concentration at time <vue-mathjax formula='$t$'></vue-mathjax>, <vue-mathjax formula='$g$'></vue-mathjax> is the quanta generation rate, and <vue-mathjax formula='$V$'></vue-mathjax> is the volume of the room. What the above says is that some amount of air <vue-mathjax formula='$g$'></vue-mathjax> is being generated by the infector. We then divide it by the volume of the room <vue-mathjax formula='$V$'></vue-mathjax> to get the added concentration. In other words, <vue-mathjax formula='$g / V$'></vue-mathjax> is the proportion of dirty air that's being added. However, some non-infectious air is being delivered at a rate <vue-mathjax formula='$Q$'></vue-mathjax>, made up of concentration <vue-mathjax formula='$C_{t}$'></vue-mathjax>. In other words, <vue-mathjax formula='$Q$'></vue-mathjax> with a concentration of <vue-mathjax formula='$C_t$'></vue-mathjax> is being removed.</p>
        <vue-mathjax formula='$$V \cdot \frac{dC}{dt} = -Q \cdot C_t + g$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$B_t = -Q \cdot C_t + g$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$B_0 = -Q \cdot C_0 + g$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$\frac{dB_t}{dt} = -Q \frac{dC_t}{dt}$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-\frac{1}{Q} \cdot \frac{dB_t}{dt} = \frac{dC_t}{dt}$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-\frac{1}{Q} \cdot \frac{dB_t}{dt} = \frac{B_t}{V}$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-\frac{V}{Q} \cdot \frac{dB_t}{dt} = B_t$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-\frac{V}{Q} \cdot \frac{dB_t}{B_t} = dt$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$\frac{dB_t}{B_t} = -\frac{Q}{V} \cdot dt$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$\int_0^t \frac{1}{B_t} \cdot dB_t = -\frac{Q}{V} \int_0^t dt$$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$ln(B_t) - ln(B_0) = -\frac{Q}{V} \cdot t $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$e^{ln(B_t) - ln(B_0)} = e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$e^{ln(B_t)} /e^{ln(B_0)} = e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$B_t / B_0 = e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$B_t = B_0 \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-Q \cdot C_t + g = (-Q \cdot C_0 + g) \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$-Q \cdot C_t = -g + (-Q \cdot C_0 + g) \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$C_t = g/Q + (C_0 - g/Q) \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <p>Given the scenario we are considering, where there were no infectors in the space before, so <vue-mathjax formula='$C_0 = 0$'></vue-mathjax>, we have:
        <vue-mathjax formula='$$C_t = g/Q - g/Q \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        <br>
        <vue-mathjax formula='$$C_t = g/Q \cdot (1 - e^{-\frac{Q}{V} \cdot t}) $$'></vue-mathjax>
        </p>

        <p>We have two factors:
          <vue-mathjax formula='$g/Q$'></vue-mathjax>
          and <vue-mathjax formula='$(1 - e^{-\frac{Q}{V} \cdot
              t})$'></vue-mathjax>. The first one is essentially the ratio of how much dirty
          air, <vue-mathjax formula='$g$'></vue-mathjax>, there is relative to the non-infectious air, <vue-mathjax formula='$Q$'></vue-mathjax>. It determines the height of the curve
          in the long run. The lower this number is, the lower the amount of
          dirty air inhaled per breath. The latter term, affected by ACH, <vue-mathjax
          formula='$Q/V$'></vue-mathjax>, determines how fast the steady state concentration is reached.
        </p>


        <LineGraph
          :lines="[constantConcentration, incorporatingACH]"
          :ylim='[0, 0.09]'
          title='Contaminant concentration over time'
          xlabel='Time (min)'
          ylabel='Contaminant concentration (quanta / min)'
          :legendStartOffset='[0.45, 0.55]'
          :roundXTicksTo='0'
        />






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
  name: 'IndividualRiskConditional',
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
        'conditionalRisk',
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
</style>

