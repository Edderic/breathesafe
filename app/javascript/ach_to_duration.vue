<template>

  <tr>
    <td>
      <div class='justify-content-center align-items-center row'>
        <h3 class='bold'>Time to 99% Dilution</h3>

        <CircularButton text='?' @click='show = !show'/>
      </div>
    </td>
    <td>
      <ColoredCell
        :colorScheme="removalScheme"
        :maxVal=1
        :value='durationMinutesToRemove(0.99)'
        :style='headerCellCSS'
      />
    </td>
  </tr>
  <tr v-if='show'>
    <td  colspan='2'>
      <div class='explainer'>
        <p>
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
            /> minutes to remove 99% of the virus that have been exhaled by the infector (after the infector has left).
          </span>

          <span>Increasing total ACH, whether done by added ventilation, portable
          air cleaning, or upper room germicidal ultra violet irradiation, the faster
          the rate of removal of airborne pathogens, and the safer it is for
          everyone.
          </span>
        </p>
      </div>
    </td>
  </tr>

</template>

<script>
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store'
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
    CircularButton,
    ColoredCell
  },
  data() {
    return {
      show: false
    }
  },
  computed: {
    ...mapState(
      useAnalyticsStore,
      [
        'styleProps'
      ]
    ),
    headerCellCSS() {
      let def = {
        'display': 'block',
        'padding': '1em'
      }
      return Object.assign(JSON.parse(JSON.stringify(this.cellCSSMerged)), def)
    },
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'text-align': 'center',
        'padding': '0.5em',
        'display': 'inline-block'
      }

      // return Object.assign(this.cellCSS, default)
      return Object.assign(this.cellCSS, def)
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
  .align-items-center {
    display: flex;
    align-items: center;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }


  .bold {
    font-weight: bold;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }
</style>
