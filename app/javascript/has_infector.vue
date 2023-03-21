<template>
  <div class='blah'>
    <div class='column centered'>
      <div class='row'>
        <span class='padded'>Groups</span>
          <CircularButton text='+' @click='addInfectorGroup'/>
        </div>

        <table>
          <thead>
            <tr>
              <th class='padded'>Number of People</tH>
              <th class='test'>PCR</tH>
              <th class='test'>Rapid</tH>
              <th class='test'>Symp</tH>
              <th class='test'>Del</tH>
            </tr>
          </thead>

          <tbody>
            <tr v-for='v in possibleInfectorGroups' @click="choosePossibleInfectorGroup(v)" :style='{"border-color": backgroundColorGroup(v)}' class='clickable-row'>
              <td class='padded'>
                <Number
                  class='row'
                  :leftButtons="[{text: '-10', emitSignal: 'increment'}, {text: '-1', emitSignal: 'increment'}]"
                  :rightButtons="[{text: '+1', emitSignal: 'increment'}, {text: '+10', emitSignal: 'increment'}]"
                  :value='v.numPeople'
                  :identifier='v.identifier'
                  @increment='incrementNumberOfPeople'
                  @update='updateNumberOfPeople'
                />
              </td>
              <td v-for='e in v.evidence' :style="{'background-color': backgroundColorResult(e.result), 'color': colorResult(e.result)}" @click='cycleResult(e, v)'>{{e.result}}</td>
              <td class='padded' >
                <CircularButton text='x' @click='removePossibleInfectorGroup(v.identifier)'/>
              </td>
            </tr>
          </tbody>
        </table>
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
    created() {
      this.possibleInfectorGroup = this.possibleInfectorGroups[0]
    },
    data() {
      // P(+ | inf) P(inf) = 0.95 * 0.01
      // P(+ | inf) P(inf) + P(+ | not inf) P(not inf)  = 0.95 * 0.01 + 0.01 * 0.99


      return {
        possibleInfectorGroup: {}
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
    addInfectorGroup() {
      this.addPossibleInfectorGroup()
      this.possibleInfectorGroup = this.possibleInfectorGroups[this.possibleInfectorGroups.length - 1]
    },
    cycleResult(evidence, group) {
      if (evidence.result == '?')  {
        evidence.result = '+'
      } else if (evidence.result == '+') {
        evidence.result = '-'
      } else {
        evidence.result = '?'
      }
    },
    colorResult(result) {
      if (result == '+') {
        return 'white'
      } else if (result == '-') {
        return 'white'
      } else {
        return 'black'
      }
    },
    backgroundColorResult(result) {
      if (result == '+') {
        return 'red'
      } else if (result == '-') {
        return 'green'
      } else {
        return '#cacaca'
      }
    },
    removeInfectorGroup(identifier) {
      this.removePossibleInfectorGroup(identifier)
      this.possibleInfectorGroup = this.possibleInfectorGroups[this.possibleInfectorGroups.length - 1]
    },
    backgroundColorGroup(group) {
      if (group == this.possibleInfectorGroup) {
        return 'rgb(200,200,200)'
      } else {
        return '#eee'
      }
    },
    choosePossibleInfectorGroup(pig) {
      this.possibleInfectorGroup = pig
    },
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

  .blah {
    display: grid;
    grid-template-columns: 10em auto;
  }

  .padded {
    padding: 0.5em;
  }

  .unselected {
    background-color: #cacaca;
  }

  td {
    text-align: center;
  }

  .clickable-row {
    cursor: pointer;
    border-collapse: collapse;
  }

  .test {
    min-width: 3em;
  }
</style>
