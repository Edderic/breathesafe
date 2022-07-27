<template>
  <div class='container'>
    <label>Number of positive cases last seven days</label>
    <input
      :value="numPositivesLastSevenDays" @change='setNumPositivesLastSevenDays'>
  </div>

  <div class='container'>
    <label>Number of people in the population</label>
    <input
      :value="numPopulation" @change='setNumPopulation'>
  </div>

  <div class='container'>
    <label>Multiplier to account for Uncounted Cases</label>
    <input
      :value="uncountedFactor" @change='setUncountedFactor'>
  </div>

  <div class='container'>
    <label>Probability that one individual sampled from the population is infectious</label>
    <input disabled
      :value="probabilityInfectious">
  </div>

  <div class='container'>
    <label>Mask Type</label>
    <select :value='maskType' @change='setMaskType'>
      <option v-for='m in maskValues'>{{ m }}</option>
    </select>
  </div>

</template>

<script>
import { useMainStore } from './stores/main_store'
import { useEventStores } from './stores/event_stores'
import { usePrevalenceStore } from './stores/prevalence_store';
import { useProfileStore } from './stores/profile_store';
import { maskToPenetrationFactor } from './misc'
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
  },
  computed: {
    ...mapState(useMainStore, ["focusSubTab"]),
    ...mapWritableState(usePrevalenceStore, ['numPositivesLastSevenDays', 'numPopulation', 'uncountedFactor', 'maskType']),
    ...mapWritableState(useMainStore, ['center', 'zoom']),
    probabilityInfectious() {
      return parseFloat(this.numPositivesLastSevenDays)
        * parseFloat(this.uncountedFactor) / parseFloat(this.numPopulation)
    },
    maskValues() {
      let values = []
      for (let mask in maskToPenetrationFactor) {
        values.push(mask)
      }

      return values
    }
  },
  created() {
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useProfileStore, ['updateProfile']),
    ...mapActions(useEventStores, ['computeRiskAll']),
    setNumPopulation(e) {
      this.numPopulation = e.target.value
      this.updateProfile()
      this.computeRiskAll()
    },
    setUncountedFactor(e) {
      this.uncountedFactor = e.target.value
      this.updateProfile()
      this.computeRiskAll()
    },
    setNumPositivesLastSevenDays(e) {
      this.numPositivesLastSevenDays = e.target.value
      this.updateProfile()
      this.computeRiskAll()
    },
    setMaskType(e) {
      this.maskType = e.target.value
      this.updateProfile()
      this.computeRiskAll()
    }
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
