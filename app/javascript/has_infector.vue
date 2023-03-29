<template>
  <div class='column centered'>
    <div class='row'>
      <span class='padded'>Groups</span>
        <CircularButton text='+' @click='addInfectorGroup'/>
        <CircularButton text='?' @click='showExplanation = !showExplanation'/>
      </div>

      <div class='centered col'>
        <Menu backgroundColor='transparent' v-show='showExplanation'>
          <Button text='PCR' :selected='selectedTestType == "PCR"' @click='selectedTestType = "PCR"'/>
          <Button text='Rapid' :selected='selectedTestType == "Rapid"' @click='selectedTestType = "Rapid"'/>
          <Button text='Symptoms' :selected='selectedTestType == "Symptoms"' @click='selectedTestType = "Symptoms"'/>
        </Menu>
      </div>

      <div class='centered container'>
        <p v-show='showExplanation' class='container'>
          <h3 class='centered'>Assumptions</h3>

          <div v-show='selectedTestType == "PCR"'>
            <h4>PCR</h4>
            <ul>
              <li>PCR has a <span class='italic'>sensitivity</span> of <a href="https://academic.oup.com/jid/article/227/1/9/6649627#:~:text=Sensitivity%20peaks%204%E2%80%935%20days%20postinfection%20at%2092.7%25%20(91.4%25%E2%80%9394.0%25)%20and%20remains%20over%2088%25%20between%205%20and%2014%20days%20postinfection.">92.7%</a> (i.e. out of those with a COVID infection, 92.7% test positive.)</li>
              <li>PCR has a <span class='italic'>specificity</span> of 99.9% (i.e. out of those without a COVID infection, 99.9% test negative.)</li>
            </ul>
          </div>
          <div v-show='selectedTestType == "Symptoms"'>
            <h4>Symptoms</h4>
            <ul>
              <li><a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9321237/#:~:text=In%20addition%2C%20the%20study%20conducted,asymptomatic%20infections%20percentage%20of%2035.93%25.">67.6% of people with a COVID infection are symptomatic.</a></li>
              <li>32.4% of people with a COVID infection aren't showing symptoms.</li>
              <li>8% of people without a COVID infection are symptomatic.</li>
              <li>92% of people without a COVID infection are asymptomatic.</li>
            </ul>

            <p>Symptomatic is defined as having <span class='italic'>any</span> of the following symptoms:</p>

            <table>
              <tr>
                <td>Runny nose</td><td>Sore throat</td>
                <td>Dizzy or light headed</td><td>Altered smell</td>
              </tr>
              <tr>
                <td>Sneezing</td>
                <td>Persistent Cough</td>
                <td>Nausea</td>
                <td>Diarrhea</td>
              </tr>
              <tr>
                <td>Hoarse voice</td>
                <td>Chills</td>
                <td>Eye soreness</td>
                <td>Ear ringing</td>
              </tr>
              <tr>
                <td>Unusual joint pain</td>
                <td>Brain fog</td>
                <td>Delirium</td>
                <td>Skin burning</td>
              </tr>

              <tr>
                <td>Fever</td>
                <td>Loss of smell</td>
              </tr>
            </table>

          </div>
          <div v-show='selectedTestType == "Rapid"'>
            <h4>Rapid Tests</h4>
            <ul>
              <li>Rapid tests have a <span class='italic'>specificity</span> of
<a href="the specificity was 99.9% ">99.9%</a> (i.e. out of those people without a COVID infection, 99.9% test negative.)</li>
              <li>For those who are symptomatic and have COVID, rapid tests are <a href="https://www.idsociety.org/covid-19-real-time-learning-network/diagnostics/rapid-testing/#:~:text=The%20authors%20found%20the%20antigen%20test%20to%20have%20a%20sensitivity%20of%2079%25%20and%2044%25%20in%20symptomatic%20and%20asymptomatic%20people%2C%20respectively.">
79%</a> sensitive (i.e. 79% of symptomatic and have a COVID infection will test positive.)</li>
              <li>For those who are asymptomatic at the time and have COVID, rapid tests are only <a href="https://www.idsociety.org/covid-19-real-time-learning-network/diagnostics/rapid-testing/#:~:text=The%20authors%20found%20the%20antigen%20test%20to%20have%20a%20sensitivity%20of%2079%25%20and%2044%25%20in%20symptomatic%20and%20asymptomatic%20people%2C%20respectively."> 44%</a> sensitive (i.e. 44% of those without symptoms but with a COVID infection will test positive.)</li>
            </ul>
          </div>
        </p>
      </div>
      <div class='column' v-for='(v, index) in possibleInfectorGroups' v-show='!showExplanation'>
        <div class='centered column'>
          <h4>Number of People</h4>

          <Number
            class='row'
            :leftButtons="[{text: '-10', emitSignal: 'increment'}, {text: '-1', emitSignal: 'increment'}]"
            :rightButtons="[{text: '+1', emitSignal: 'increment'}, {text: '+10', emitSignal: 'increment'}]"
            :value='v.numPeople'
            :identifier='v.identifier'
            @increment='incrementNumberOfPeople'
            @update='updateNumberOfPeople'
          />
        </div>

        <table>
          <thead>
            <tr>
              <th class='test'>PCR</tH>
              <th class='test'>Rapid</tH>
              <th class='test'>Symp</tH>
              <th class='test'>Del</tH>
            </tr>
          </thead>

          <tbody>
            <tr @click="choosePossibleInfectorGroup(v)" :style='{"border-color": backgroundColorGroup(v)}' class='clickable-row'>
              <td v-for='(value, key) in v.evidence' :style="{'background-color': backgroundColorResult(value), 'color': colorResult(value)}" @click='cycleResult(key, value, index)'>{{getValue(value)}}</td>
              <td class='padded' >
                <CircularButton text='x' @click='removeInfectorGroup(v.identifier)'/>
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
  import Button from './button.vue'
  import CircularButton from './circular_button.vue'
  import Number from './number.vue'
  import Menu from './menu.vue'
  export default {
    name: 'HasInfector',
    components: {
      Button,
      CircularButton,
      Number,
      Menu
    },
    created() {
      this.possibleInfectorGroup = this.possibleInfectorGroups[0]
    },
    data() {
      // P(+ | inf) P(inf) = 0.95 * 0.01
      // P(+ | inf) P(inf) + P(+ | not inf) P(not inf)  = 0.95 * 0.01 + 0.01 * 0.99


      return {
        selectedTestType: 'PCR',
        showExplanation: false,
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
        ],
      ),
      addInfectorGroup() {
        this.addPossibleInfectorGroup()
        this.possibleInfectorGroup = this.possibleInfectorGroups[this.possibleInfectorGroups.length - 1]
      },
      cycleResult(key, value, index) {
        let newQuery = {}
        let query = JSON.parse(JSON.stringify(this.$route.query))

        if (value == '?')  {
          value = '+'
        } else if (value == '+') {
          value = '-'
        } else {
          value = '?'
        }

        newQuery[`${key}-${index}`] = value
        Object.assign(query, newQuery)

        this.$router.push({
          name: 'Analytics',
          query: query
        })
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

      getValue(value) {
        if (!value) {
          return "?"
        } else {
          return value
        }
      },

      removeInfectorGroup(identifier) {
        let index = this.possibleInfectorGroups.findIndex((g) => g.identifier == identifier)

        // clean up the route query
        let query = JSON.parse(JSON.stringify(this.$route.query))

        for (let k in query) {
          let split = k.split('-')
          if (split.length == 2) {
            let i = split[1]

            if (i == index) {
              delete query[k]
            }
          }
        }

        this.removePossibleInfectorGroup(identifier)
        this.$router.push(
          {
            name: 'Analytics',
            query: query
          }
        )

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
        this.updatePeople(obj,
          function(newQuery, key, possibleInfectorGroup, obj) {
            newQuery[key] = parseInt(possibleInfectorGroup.numPeople) + parseInt(obj.value)
          }
        )
      },
      setResult(event, posInfectorGroup, evName) {
        let possibleInfectorGroup = this.possibleInfectorGroups.find((infGroup) => { return posInfectorGroup.identifier == infGroup.identifier})

        let evidence = possibleInfectorGroup.evidence.find((ev) => { return ev.name == evName})
        evidence.result = event.target.value
      },
      updatePeople(obj, func) {
        let possibleInfectorGroup = this.possibleInfectorGroups.find((ev) => { return ev.identifier == obj.identifier})

        let index = this.possibleInfectorGroups.findIndex((ev) => { return ev.identifier == obj.identifier})


        let query = JSON.parse(JSON.stringify(this.$route.query))
        let key = `numPeople-${index}`
        let newQuery = {}

        func(newQuery, key, possibleInfectorGroup, obj)

        Object.assign(query, newQuery)

        this.$router.push({
          name: 'Analytics',
          query: query
        })
      },
      updateNumberOfPeople(obj) {
        this.updatePeople(obj,
          function(newQuery, key, possibleInfectorGroup, obj) {
            newQuery[key] = parseInt(obj.value)
          }
        )
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
    padding: 0.5em;
  }

  .container {
    margin: 0.5em;
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

  .italic {
    font-style: italic;
  }
</style>
