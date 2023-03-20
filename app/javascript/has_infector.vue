<template>
  <div>
    <div v-for='possibleInfectorGroup in possibleInfectorGroups' class='centered column bordered'>
      <div class='container column centered '>
        <label for="">Number of people</label>

        <Number
          class='row'
          :leftButtons="[{text: '-10', emitSignal: 'increment'}, {text: '-1', emitSignal: 'increment'}]"
          :rightButtons="[{text: '+1', emitSignal: 'increment'}, {text: '+10', emitSignal: 'increment'}]"
          :value='possibleInfectorGroup.numPeople'
          :identifier='possibleInfectorGroup.identifier'
          @increment='incrementNumberOfPeople'
          @update='updateNumberOfPeople'
        />
      </div>

      <div class='container column centered' v-for='ev in possibleInfectorGroup.evidence'>
        <label for="">{{ ev.name }}</label>

        <select :value='ev.result' @change='setResult($event, possibleInfectorGroup, ev.name)'>
          <option value="?">Unknown</option>
          <option value="-">Negative</option>
          <option value="+">Positive</option>
        </select>

      </div>

      <div class='container'>
        <CircularButton text='+' @click='addPossibleInfectorGroup'/>
        <CircularButton text='x' @click='removePossibleInfectorGroup(possibleInfectorGroup.identifier)'/>
      </div>
    </div>
  </div>
</template>

<script>

import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store.js'
import { ProbaInfectious } from './proba_infectious.js';
import { round, oneInFormat } from './misc.js';
import CircularButton from './circular_button.vue'
import Number from './number.vue'
export default {
  name: 'HasInfector',
  components: {
    CircularButton,
    Number
  },
  data() {
    // P(+ | inf) P(inf) = 0.95 * 0.01
    // P(+ | inf) P(inf) + P(+ | not inf) P(not inf)  = 0.95 * 0.01 + 0.01 * 0.99


    return {
    }
  },
  props: {
  },
  computed: {
    ...mapWritableState(
        useAnalyticsStore,
        [
          'possibleInfectorGroups',
          'priorProbabilityOfInfectiousness'
        ]
    ),
  },
  methods: {
    ...mapActions(
        useAnalyticsStore,
        [
          'addPossibleInfectorGroup',
          'removePossibleInfectorGroup',
        ]
    ),
    incrementNumberOfPeople(obj) {
      let possibleInfectorGroup = this.possibleInfectorGroups.find((ev) => { return ev.identifier == obj.identifier})
      possibleInfectorGroup.numPeople += parseInt(obj.value)
    },
    posteriorInfectiousness(possibleInfectorGroup) {
      let calculator = new ProbaInfectious(this.priorProbabilityOfInfectiousness)
      return calculator.compute(possibleInfectorGroup.evidence)
    },
    setResult(event, posInfectorGroup, evName) {
      let possibleInfectorGroup = this.possibleInfectorGroups.find((infGroup) => { return posInfectorGroup.identifier == infGroup.identifier})

      let evidence = possibleInfectorGroup.evidence.find((ev) => { return ev.name == evName})
      evidence.result = event.target.value
    },
    updateNumberOfPeople(obj) {
      let possibleInfectorGroup = this.possibleInfectorGroups.find((ev) => { return ev.identifier == obj.identifier})
      possibleInfectorGroup.numPeople = parseInt(obj.value)
    }
  }

}
</script>

<style scoped>
  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

  .bordered {
    border: 1px solid black;
    padding: 1em;
  }

  .container {
    margin: 0.5em;
  }

</style>
