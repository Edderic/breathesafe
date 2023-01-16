<template>
    <DrillDownSection

      title='Steady State Concentration'
      :value='roundOut(steadyState, 0)'
      :text='steadyStateText'
      :colorScheme='carbonDioxideColorScheme'
    >
      <p class='explainer'>In the long run, this is what the steady state CO2 concentration would be. </p>
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
</style>
