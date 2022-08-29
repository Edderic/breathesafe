<template>

  <div class='container'>
    Imagine an infectious person exhaling 1 breath. With
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='totalAchRounded'
        :style='cellCSSMerged'
      />
      ACH, it takes <ColoredCell
        :colorScheme="removalScheme"
        :maxVal=1
        :value='durationMinutesToRemove(0.99)'
        :style='cellCSSMerged'
      /> minutes to remove 99% of the virus from the air from that 1 breath. The higher the ACH, the faster the rate of removal of airborne pathogens, and the safer it is for everyone.
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
    cellCSS: Object,
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

  container {
    width: 80%;

  }
</style>
