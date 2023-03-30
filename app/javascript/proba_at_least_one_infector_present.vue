<template>
  <DrillDownSection

    title='Probability that at least one infector is present'
    :value='probabilityOneInfectorIsPresent'
    :text='drillDownText'
    :colorScheme='riskColorScheme'
  >
    <tr>
      <td colspan=2>
        <div class='centered column'>
          <div class='centered row'>
            <RapidTest height='13em' width='13em'/>
            <table class='symptoms has-borders'>

              <thead>
                <tr>
                  <th>Has symptom</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class='asymptomatic'>cough</td>
                </tr>
                <tr>
                  <td class='symptomatic'>runny nose</td>
                </tr>

                <tr>
                  <td class='asymptomatic'>fever</td>
                </tr>

                <tr>
                  <td>...</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class='fig-title'>Rapid Test and Symptoms Checklist</p>
      </div>

        <p>
          There are two ways to decrease risk of airborne transmission.

          One can:
          <ul>
            <li><span class='italic'>remove the source of pathogens</span></li>
            <li>dilute the air</li>
          </ul>

          This metric is focused on the former, and is affected by the prevalence of infectious persons. We gain more knowledge about the presence of an infector by using rapid test/PCR results and checking for presence of symptoms).

          If this is super low, then the risk of transmission is also super low -- one needs to have an infector to be present in order to infect someone.
        </p>


        <h3>Takeaways</h3>
        <ul>
          <li>If one gets a positive PCR or rapid test, assume that they have it, and ask them to not come to the event.</li>
          <li>A negative PCR is more trustworthy than a negative Rapid Test. </li>

          <li>Keep occupancy small. The smaller the number of people, the less likely that an infector is present.</li>
          <li>The higher the occupancy, the higher the probability that there is at least one infector in the room, even with a rapid-test-negative-and-no-symptoms-to-entry strategy. </li>
        </ul>

        <h3>Mathematical Details</h3>
        <p class='explainer'>

          The probability that at least one infector is present is all the possibilities minus probability that no one is infectious. If there are <span class='italic'>n</span> people:

          <vue-mathjax formula="$$1 - P(I_1 = 0, I_2 = 0, ..., I_n = 0)$$"></vue-mathjax>

          If each individual has the same probability of being infectious, and each person's infectiousness is independent from one another, we can simplify the above to:

          <vue-mathjax formula="$$1 - P(I_1 = 0)^n$$"></vue-mathjax>

          In this implementation, we have "potential infector groups." A potential infector group can have its own pattern of PCR, Rapid Test, and Symptoms results. These results give us more information about someone's probability of being infectious. If there are two groups,

          taking into account these results, we have:
          <vue-mathjax formula="$$1 - P(I = 0 | P_a, R_a, S_a) ^ {n_{a}} \cdot P(I_b = 0 | P_b, R_b, S_b) ^ {n_{b}}$$"></vue-mathjax>

          And in general, if there are <span class='italic'>x</span> groups, we have:
          <vue-mathjax formula="$$1 - \prod_x P(I = 0 | P_x, R_x, S_x) ^ {n_{x}} $$"></vue-mathjax>

          where for group <vue-mathjax formula="$x$"></vue-mathjax>, <vue-mathjax formula="$P_x$"></vue-mathjax> is the result of the PCR (positive, negative, unknown),
          <vue-mathjax formula="$R_x$"></vue-mathjax> is the result of the Rapid Test (positive, negative, unknown), <vue-mathjax formula="$S_x$"></vue-mathjax> is whether or not someone is symptomatic, and <vue-mathjax formula="$n_x$"></vue-mathjax> is the number of people.

      </p>
      <p>
          <h4>
          How is <vue-mathjax formula="$P(I = 0 | P_x, R_x, S_x) $"></vue-mathjax> calculated?
          </h4>


          <vue-mathjax formula="$$

            P(I = 0 | P_x=p, R_x=r, S_x=s) =
            \frac{P(P_x=p, R_x=r, S_x=s, I = 0)}{P(P_x=p, R_x=r, S_x=s)}
            = \frac{P(P_x=p, R_x=r, S_x=s, I = 0)}{\sum_i P(P_x=p, R_x=r, S_x=s, I = i)}

          $$"></vue-mathjax>

          The numerator and denominator can each be seen as a product of conditional probability tables.
          For example, with the numerator, we can use the chain rule of probability:

          <vue-mathjax formula="$$

          P(P_x=p, R_x=r, S_x=s, I = 0) =
          P(I=0) \cdot P(P_x=p \mid I=0) \cdot P(S_x=s \mid I = 0) \cdot P(R_x=r \mid I = 0, S_x=s)

          $$"></vue-mathjax>

          Each of those factors encodes assumptions that were listed under the <span class='italic'>Occupancy</span> tab. Clicking the question mark button there shows all the assumptions.  For example, PCR sensitivity of 92.7% can be represented as a probability statement:

          <vue-mathjax formula="$$

          P(P_x = 1 \mid I = 1) = 92.7\%

          $$"></vue-mathjax>

          ... as well as the assumed specificity of 99.9%:

          <vue-mathjax formula="$$

          P(P_x = 0 \mid I = 0) = 99.9\%

          $$"></vue-mathjax>



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

        </p>
      </td>
    </tr>
  </DrillDownSection>
</template>


<script>

import { round, oneInFormat } from './misc.js'
import { assignBoundsToColorScheme, infectedPeopleColorBounds, riskColorInterpolationScheme } from './colors.js'
import DrillDownSection from './drill_down_section.vue'
import RapidTest from './rapid_test.vue'
import { useAnalyticsStore } from './stores/analytics_store.js'
import { mapWritableState, mapState, mapActions } from 'pinia';

export default {
  name: 'ProbaAtLeastOneInfectorPresent',
  components: {
    DrillDownSection,
    RapidTest,
  },
  data() {
    return {
      formula: "$$\\sum_a P(X \mid a)$$"
    }
  },
  props: {
  },
  computed: {
    ...mapWritableState(
        useAnalyticsStore,
        [
          'possibleInfectorGroups',
          'probabilityOneInfectorIsPresent',
        ]
    ),
    riskColorScheme() {
      return riskColorInterpolationScheme
    },

    drillDownText() {
      return `1 in ${oneInFormat(this.probabilityOneInfectorIsPresent)}`
    }
  },

  methods: {
    roundOut(x, y) {
      return round(x, y)
    }
  }

}
</script>

<style scoped>
  .has-borders {
    border-collapse: collapse;
    border: 2px solid gray;
  }
  .symptomatic {
    background-color: red;
  }
  .asymptomatic {
    background-color: green;
    text-decoration: line-through;
    color: white;
  }


  .row {
    display: flex;
    flex-direction: row;
  }

  .fig-title, .italic {
    font-style: italic;
  }


  .symptoms {
    height: 10em;
  }
  .symptoms th, .symptoms td {
    padding: 0 0.25em;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

</style>
