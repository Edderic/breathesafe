<template>
  <div class='container'>
    <label>Number of positive cases last seven days</label>
    <input
      v-model="numPositivesLastSevenDays">
  </div>

  <div class='container'>
    <label>Number of people in the population</label>
    <input
      v-model="numPopulation">
  </div>

  <div class='container'>
    <label>Multiplier to account for Uncounted Cases</label>
    <input
      v-model="uncountedFactor">
  </div>

  <div class='container'>
    <label>Probability that one individual sampled from the population is infectious</label>
    <input disabled
      :value="probabilityInfectious">
  </div>
</template>

<script>
import { useMainStore } from './stores/main_store'
import { usePrevalenceStore } from './stores/prevalence_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
  },
  computed: {
    ...mapState(useMainStore, ["focusSubTab"]),
    ...mapWritableState(usePrevalenceStore, ['numPositivesLastSevenDays', 'numPopulation', 'uncountedFactor']),
    ...mapWritableState(useMainStore, ['center', 'zoom']),
    probabilityInfectious() {
      return parseFloat(this.numPositivesLastSevenDays)
        * parseFloat(this.uncountedFactor) / parseFloat(this.numPopulation)
    }
  },
  created() {
  },
  data() {
    return {}
  },
  methods: {
  },
}
</script>


<style scoped>
  .col {
    display: flex;
    flex-direction: column;
  }
  .row {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    font-weight: bold;
  }
  .body {
    position: absolute;
    top: 4.2em;
  }
  .wide {
    flex-direction: column;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

  button {
    padding: 1em 3em;
  }
</style>
