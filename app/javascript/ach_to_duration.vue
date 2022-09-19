<template>

  <div :style='containerCSSMerged'>
    Imagine an infectious person stays at this room and then leaves. With
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='totalAchRounded'
        :style='cellCSSMerged'
      />
      ACH,
      <span class='highlight'>
        it takes <ColoredCell
          :colorScheme="removalScheme"
          :maxVal=1
          :value='durationMinutesToRemove(0.99)'
          :style='cellCSSMerged'
        /> minutes to remove 99% of the virus that have been exhaled by the infector.
      </span>

      <span>Increasing total ACH, whether done by added ventilation, portable
      air cleaning, or upper room germicidal ultra violet irradiation, the faster
      the rate of removal of airborne pathogens, and the safer it is for
      everyone.
      </span>
    </div>

</template>

<script>
import ColoredCell from './colored_cell.vue'
import { convertVolume } from './measurement_units.js';
import { binSearch } from './interventions.js'
import {
  assignBoundsToColorScheme,
  colorSchemeFall,
  colorInterpolationSchemeAch,
  cutoffsVolume,
  minutesToRemovalScheme
} from './colors.js';
import {
  displayCADR,
  round
} from './misc.js'

export default {
  name: 'AchToDuration',
  components: {
    ColoredCell
  },
  computed: {
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'text-align': 'center',
        'display': 'inline-block',
        'padding': '0.5em'
      }

      // return Object.assign(this.cellCSS, default)
      return Object.assign(def, this.cellCSS)
    },
    containerCSSMerged() {
      let css = {
        'line-height': '2em',
      }
      Object.assign(css, this.containerCSS)
      return css
    },
    ach() {
      return this.intervention.computeACH()
    },
    colorInterpolationSchemeTotalAch(){
      return colorInterpolationSchemeAch
    },
    removalScheme() {
      return minutesToRemovalScheme()
    },
    totalAchRounded() {
      return round(this.ach, 1)
    },
  },
  methods: {
    durationMinutesToRemove(toRemove) {
      return round(60 * -Math.log(1 - toRemove) / this.ach, 1)
    }
  },
  props: {
    cellCSS: {
      default: {}
    },
    containerCSS: {
      default: {},
    },
    intervention: Object,
  }
}
</script>

<style scoped>
  .font-light {
    font-weight: 400;
  }

  .col {
    display: flex;
    flex-direction: column;
  }


  td {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
    padding-left: 0.5em;
    padding-right: 0.5em;
  }

  .highlight {
    font-weight: bold;
  }

  .container {

  }
</style>
