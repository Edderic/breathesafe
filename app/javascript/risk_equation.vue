<template>
  <div class='row centered'>
    <h3 class='bold'>Risk Equation</h3>
    <CircularButton text='?' @click='show = !show'/>
  </div>

  <div v-if='show' class='explainer' id='section-risk-equation'>
    <p>
    The probability of infection is proportional to the dose of contaminants
    (e.g. viruses) inhaled. That dose is a fraction of contaminants over the
    amount of clean air inhaled.
    </p>

    <div class='container centered'>
      <table class='equations'>
        <tr>
          <th></th>
          <th></th>
          <th>amount of contaminants generated</th>
        </tr>
        <tr>
          <th>dose</th>
          <th>≃</th>
          <td><hr></td>
          <th><span class='unbold'> x </span></th>
          <th>inhalation rate</th>
          <th><span class='unbold'> x </span></th>
          <th>duration</th>
        </tr>
        <tr>
          <th></th>
          <th></th>
          <th>amount of clean air generated</th>
        </tr>
      </table>
    </div>
    <div class='container centered'>
      <table class='equations'>
        <tr>
          <th>amount of contaminants generated</th>
          <th>=</th>
          <th>quanta generation rate<span class='unbold'> x </span>infector activity factor<span class='unbold'> x </span>infector mask penetration</th>
        </tr>
        <tr>
          <th>inhalation rate</th>
          <th>=</th>
          <th>susceptible mask penetration<span class='unbold'> x </span>susceptible basic breathing rate<span class='unbold'> x </span>susceptible activity factor</th>
        </tr>
        <tr>
          <th>amount of clean air generated</th>
          <th>=</th>
          <th>air changes per hour (ACH) <span class='unbold'> x </span> volume</th>
        </tr>
      </table>
    </div>

    <table class='variable-explanations'>
      <tr>
        <th>Variable</th>
        <th>Explanation</th>
      </tr>
      <tr>
        <th>quanta</th>
        <td>A variable that essentially captures how infectious an airborne virus is. The higher, the more contagious. 1 quanta leads to a infection probability of <span class='italic'>1 - exp(-1) = 0.63</span>. 2 quanta, on the other hand, corresponds to an infection probability of <span class='italic'>1 - exp(-2) = 0.88</span>, etc.</td>
      </tr>
      <tr>
        <th>quanta generation rate</th>
        <td>For SARS-CoV-2, some researchers have observed an
<a href="https://docs.google.com/spreadsheets/d/16K1OQkLD4BjgBdO8ePj6ytf-RpPMlJ6aXFg3PrIQBbQ/edit#gid=519189277">
average value of 63 quanta per hour</a>, specifically for the BA.2 variant. That's the value we're using here. However, some people are superspreaders, with researchers estimating about
<a href="https://onlinelibrary.wiley.com/doi/full/10.1111/ina.12751">
970 quanta per hour</a> in some cases. Quanta generation rate with new variants is currently unknown, so we're using 63 quanta per hour since it is convenient to do so.</td>
      </tr>
      <tr>
        <th>
          <router-link :to="`/analytics/${this.$route.params.id}#infector-activity`">
            infector activity factor
          </router-link>
        </th>
        <td>Staying quiet is less risky than talking, which is less risky than loud talking. </td>
      </tr>
      <tr>
        <th>
          <router-link :to="`/analytics/${this.$route.params.id}#masking`">
            infector masking penetration
          </router-link>
        </th>
        <td>How effective an infector's mask lets through, whether it be through gaps between the face and mask, or the filter media itself.</td>
      </tr>
      <tr>
        <th>
          <router-link :to="`/analytics/${this.$route.params.id}#inhalation-activity`">
            susceptible activity factor
          </router-link>
        </th>
        <td>The faster a susceptible breathes in (e.g. when exercising), the higher the risk, relative to breathing slowly (e.g. at rest).</td>
      </tr>
      <tr>
        <th>
          <router-link :to="`/analytics/${this.$route.params.id}#masking`">
            susceptible masking penetration
          </router-link>
        </th>
        <td>How much the susceptible's mask lets through, whether it be through gaps between the face and mask, or the filter media itself.</td>
      </tr>
      <tr>
        <th>
          susceptible basic breathing rate
        </th>
        <td>For age 30 to 40, this is about 0.288 cubic meters per hour. This is the value that we're using.</td>
      </tr>
      <tr>
        <th>
          volume
        </th>
        <td>Room volume occupied by air.</td>
      </tr>
      <tr>
        <th>
          <router-link :to="`/analytics/${this.$route.params.id}#total-ach`">
            air changes per hour (ACH)
          </router-link>
        </th>
        <td>The clean air delivery rate divided by the volume. The larger this is, the faster the rate of removal/deactivation of pathogens in the air.</td>
      </tr>
    </table>

  </div>
</template>

<script>
import CircularButton from './circular_button.vue'
export default {
  name: '',
  components: {
    CircularButton
  },
  data() {
    return {
      show: false
    }
  },
  props: {
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
  .container {
    margin: 1em;
  }
  table {
    border-collapse: collapse;
  }
  td, th {
    padding-top: 1em;
    padding-bottom: 1em;
  }
  .variable-explanations tr {
    border-bottom: 1px solid black;
  }
  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .equations {
    font-style: italic;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .unbold {
    font-weight: 100;
  }

</style>
