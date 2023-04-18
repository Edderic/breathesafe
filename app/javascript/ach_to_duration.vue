<template>

  <DrillDownSection
    title='Time to Steady State'
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
            least {{ durationMinutesToRemove(0.99) }} minutes to drastically
            reduce the risk of inhaling a large dose of infectious particles
            that are residuals from an infector having been there.
        </p>

        <h3>Mathematical Details</h3>


        <p>
          You may recall in the "Derivation of the Concentration Curve" section under "Individual Risk" that when there is an initial concentration <vue-mathjax formula='$c_0$'></vue-mathjax> that is non-zero, we have:
        </p>

        <p>
          <vue-mathjax formula='$$C_t = g/Q + (1 \cdot C_0 - g/Q) \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        </p>

        <p>
        Once the infector leaves, the generation rate of dirty air <vue-mathjax formula='$g$'></vue-mathjax> becomes 0, and we have a decay curve that starts at <vue-mathjax formula='$C_0$'></vue-mathjax> and then drops to 0 as time goes by. How long it takes depends on ACH
        <vue-mathjax formula='$Q/V$'></vue-mathjax>:
        </p>

        <p>
          <vue-mathjax formula='$$C_t = C_0 \cdot e^{-\frac{Q}{V} \cdot t} $$'></vue-mathjax>
        </p>


        <p>
          Plugging in <span class='bold'>{{totalAchRounded}}</span> ACH, then we'll want to solve for <vue-mathjax formula='$t$'></vue-mathjax>:
        </p>
        <p>
          <vue-mathjax :formula='achToDurationFormula'></vue-mathjax>
        </p>

        <p>
          If <vue-mathjax formula='$C_t$'></vue-mathjax> was one-hundredth of the initial concentration
          <vue-mathjax formula='$C_0$'></vue-mathjax>, then we have:
        </p>
        <p>
          <vue-mathjax :formula='achToDurationFormulaContinuation'
></vue-mathjax>
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
    achToDurationFormulaContinuation() {
      return `
        $$

        \\begin{equation}
        \\begin{aligned}
        -ln(0.01)/${this.totalAchRounded} &= t \\\\
        ${round(this.durationMinutesToRemove(0.99) / 60, 2)} \\text{ hours} &= \\\\
        ${this.durationMinutesToRemove(0.99)} \\text{ minutes} &= \\\\
        \\end{aligned}
        \\end{equation}
        $$'
      `
    },
    achToDurationFormula() {
      return `

$$
\\begin{equation}
\\begin{aligned}
C_t &= C_0 \\cdot e^{-${this.totalAchRounded} \\cdot t} \\\\
C_t / C_0 &= e^{-${this.totalAchRounded} \\cdot t} \\\\
ln(C_t / C_0) &= -${this.totalAchRounded} \\cdot t \\\\
- ln(C_t / C_0) / ${this.totalAchRounded} &= t \\\\
\\end{aligned}
\\end{equation}
$$
`
    },
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
