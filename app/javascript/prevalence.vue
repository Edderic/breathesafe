<template>
  <div class='container centered col'>
    <p>Your estimate of how many COVID-19 cases there are currently:</p>
    <p><span class='bold'>1 in {{denominator}}</span></p>
    <h3>Update the denominator:</h3>

        <Number
          class='row'
          :leftButtons="[{text: '-10', emitSignal: 'increment'}, {text: '-1', emitSignal: 'increment'}]"
          :rightButtons="[{text: '+1', emitSignal: 'increment'}, {text: '+10', emitSignal: 'increment'}]"
          :value='denominator'
          @increment='increment'
          @update='update'
        />

  </div>

</template>

<script>
import { useAnalyticsStore } from './stores/analytics_store'
import Number from './number.vue'
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'
import { round } from './misc.js'

export default {
  name: 'Prevalence',
  components: {
    Number
  },
  computed: {
    ...mapWritableState(useAnalyticsStore, ['priorProbabilityOfInfectiousness']),
    denominator() {
      return round(1 / this.priorProbabilityOfInfectiousness, 0)
    }
  },
  created() {
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useAnalyticsStore, ['setPriorProbabilityOfInfectiousness']),
    increment(obj) {
      let denominator = 1 / this.priorProbabilityOfInfectiousness

      denominator += parseInt(obj.value)

      this.priorProbabilityOfInfectiousness = 1 / denominator
    },
    update(obj) {
      this.priorProbabilityOfInfectiousness = 1 / parseInt(obj.value)
    }
  },
}
</script>


<style scoped>
  .container {
    margin: 1em;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .col {
    flex-direction: column;
  }

  .bold {
    font-weight: bold;
    font-style: italic;
  }
</style>
