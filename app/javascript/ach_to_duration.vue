<template>

  <DrillDownSection
    title='Time to 99% Dilution'
    :value='durationMinutesToRemove(0.99)'
    :text='text'
    :colorScheme='removalScheme'
  >
  <tr>
    <td  colspan='2'>
      <div class='explainer'>
        <p>
          Imagine an infectious person stays at this room and then leaves. With
          <span class='bold'>{{totalAchRounded}}</span> ACH,
          <span class='highlight'>
            it takes {{ durationMinutesToRemove(0.99)}}
            minutes to remove 99% of the virus from the air that has been
            exhaled by the infector.  </span> This is useful for situations when you know
            there's been an infector in the room, you have your mask, and you are trying to
            figure out how long you should wait to remove your mask. One should wait at
            least {{ durationMinutesToRemove(0.99) }} minutes to be safe.
        </p>
      </div>
    </td>
  </tr>
  </DrillDownSection>

</template>

<script>
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import DrillDownSection from './drill_down_section.vue'
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
    ColoredCell,
    DrillDownSection
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
    text() {
      let val = this.durationMinutesToRemove(0.99)
      let maybeRounded;

      if (val > 1) {
        maybeRounded = round(val, 0)
      } else {
        maybeRounded = val
      }
      return `${maybeRounded} min`
    },
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
    font-style: italic;
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
