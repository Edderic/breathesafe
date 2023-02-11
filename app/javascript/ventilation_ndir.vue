<template>
    <DrillDownSection

      title='Non-Infectious Air Delivery Rate'
      :value='roundOut(cadrLocale, 0)'
      :text='cadrText'
      :colorScheme='colorInterpSchemeRoomVol'
    >
      <p class='explainer'>This is the amount of estimated non-infectious air that is from mechanical ventilation, open windows, and infiltration.</p>
      <h3 v-if='ventilationNotes.length > 0'>Notes</h3>
      <p>{{ventilationNotes}}</p>

    </DrillDownSection>
</template>

<script>
import { displayCADR, round } from './misc.js'
import { co2ColorScheme } from './colors.js'
import ColoredCell from './colored_cell.vue'
import DrillDownSection from './drill_down_section.vue'
import CircularButton from './circular_button.vue'

import {
  colorInterpolationSchemeRoomVolume,
} from './colors.js';

export default {
  name: 'VentilationNDIR',
  components: {
    ColoredCell,
    CircularButton,
    DrillDownSection
  },
  data() {
    return { show: false }
  },
  props: {
    cadr: Number,
    systemOfMeasurement: String,
    measurementUnits: Object,
    ventilationNotes: String
  },
  computed: {
    cadrLocale() {
      return displayCADR(
        this.systemOfMeasurement,
        this.cadr
      )
    },

    cadrText() {
      return `${this.roundOut(this.cadrLocale, 0)} ${this.measurementUnits.airDeliveryRateMeasurementTypeShort}`
    },
    carbonDioxideColorScheme() {
      return co2ColorScheme
    },

    colorInterpSchemeRoomVol() {
      return colorInterpolationSchemeRoomVolume(this.measurementUnits)
    },
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  }

}
</script>

<style scoped>
</style>
