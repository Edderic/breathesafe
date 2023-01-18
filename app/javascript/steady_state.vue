<template>
    <DrillDownSection
      title='Steady State CO2 (at the time of measurement)'
      :value='roundOut(steadyState, 0)'
      :text='steadyStateText'
      :colorScheme='carbonDioxideColorScheme'
    >
      <p class='explainer'>In the long run, this is what the steady state CO2
      concentration would be, assuming that the number of people <span
      class='bold'>at the time the measurement was taken</span>, along with their
      activities, along with the ventilation rate, stay constant.
      </p>

    <p>See the table below for more information about the number of people and the activities that were taken during measurement:</p>

    <br>

      <table>
        <tr>
          <th># people</th>
          <th>Activity</th>
          <th>Age Group</th>
        </tr>
        <tr v-for='activityGroup in activityGroups'>
          <td>{{activityGroup.numberOfPeople}}</td>
          <td>{{activityGroup.carbonDioxideGenerationActivity}}</td>
          <td>{{activityGroup.ageGroup}}</td>
        </tr>
      </table>
  </DrillDownSection>
</template>

<script>
import { round, steadyStateFac } from './misc.js'
import { co2ColorScheme } from './colors.js'
import ColoredCell from './colored_cell.vue'
import DrillDownSection from './drill_down_section.vue'
import CircularButton from './circular_button.vue'

export default {
  name: 'SteadyState',
  components: {
    ColoredCell,
    CircularButton,
    DrillDownSection
  },
  data() {
    return { show: false }
  },
  props: {
    activityGroups: Array,
    generationRate: Number,
    roomUsableVolumeCubicMeters: Number,
    c0: Number,
    cBackground: Number,
    cadr: Number
  },
  computed: {
    steadyStateText() {
      return `${this.roundOut(this.steadyState, 0)} ppm`
    },
    steadyState() {
      return steadyStateFac({
        roomUsableVolumeCubicMeters: this.roomUsableVolumeCubicMeters,
        c_0: this.c0,
        generationRate: this.generationRate,
        cadr: this.cadr,
        cBackground: this.cBackground
      }, 1000000)
    },
    carbonDioxideColorScheme() {
      return co2ColorScheme
    },
    styleProps() {
      return {
          'font-weight': 'bold',
          'color': 'white',
          'text-shadow': '1px 1px 2px black',
          'padding': '1em'
        }
    },

  }, methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  }

}
</script>

<style scoped>
  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .align-items-center {
    display: flex;
    align-items: center;
  }


  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .second-td {
    width: 8em;
  }

  .bold {
    font-weight: bold;
  }

  td {
    padding: 1em;
  }
</style>
