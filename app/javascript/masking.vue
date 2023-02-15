<template>
  <DrillDownSection
    title='Masking Reduction Factor'
    :value='maskingFactor'
    :text='maskingFactorText'
    :colorScheme='riskColorScheme'
  >

  <tr>
    <td colspan='2'>
      <div class='explainer' id='section-masking'>
        <p>
        To see the effects of masking by yourself vs. when everyone is
        masked, see graph below, which shows the relative amount of particles left when
        a susceptible (x-axis) wears some type of mask and an infector (y-axis) also
        wears some type of mask.

        </p>
        <div class='centered masking-table'>
          <table>
            <tr>
              <th></th>
              <th style='padding: 0;' v-for='(value1, key1) in maskFactors'>



                <svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" transform='rotate(-40, 40, 40)' class='tilted-header'>{{key1}}</text>
                </svg>

              </th>
            </tr>
            <tr v-for='(value1, key1) in maskFactors'>
              <th class='table-td-mask'>{{key1}}</th>
              <td class='table-td-mask' v-for='(value2, key2) in maskFactors'>
                <ColoredCell
                  :colorScheme="riskColorScheme"
                  :maxVal=1
                  :value='roundOut(value1 * value2, 6)'
                  :style="tableColoredCellMasking"
                />
              </td>
            </tr>
          </table>
        </div>

        <p>
        For example, when the infector is unmasked (i.e.
            "None"), but the susceptible is wearing a KN95, then 0.15 of infectious
        particles are left over for the susceptible to inhale, which is an 85%
        reduction of particles. If both wore KN95s, then the left over particles is
        0.0225 (i.e. a 98.75% reduction of infectious airborne particles a susceptible
            can inhale).  <span class='bold'>If both wore elastomeric N99 respirators, then
        we get a 10,000-fold reduction!</span> Upgrading to N95 respirators and above
        (i.e. tight-fitting, high filtration efficiency), and having mask mandates
        especially in times of surges, is a very effective and cost-efficient way to
        prevent the spread of COVID-19 and other airborne respiratory viruses.
        </p>
      </div>
    </td>
  </tr>
  </DrillDownSection>

</template>


<script>
import {
  assignBoundsToColorScheme,
  colorSchemeFall,
  colorInterpolationSchemeAch,
  cutoffsVolume
} from './colors.js';

import {
  maskToPenetrationFactor,
  round,
} from  './misc';

import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import DrillDownSection from './drill_down_section.vue'

export default {
  name: 'TotalACH',
  components: {
    CircularButton,
    ColoredCell,
    DrillDownSection
  },
  data() {
    return {
      show: false,
      maskFactors: maskToPenetrationFactor,
      tableColoredCellMasking: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding-top': '0.5em',
        'padding-bottom': '0.5em',
        'width': '5em',
      },
    }
  },
  props: {
    riskColorScheme: Array,
    cellCSSMerged: Object,
    intervention: Object
  },
  computed: {
    maskingFactor() {
      return (1 - this.intervention.mask1.filtrationEfficiency()) * (1 - this.intervention.mask2.filtrationEfficiency())
    },
    maskingFactorText() {
      if (this.maskingFactor == 0) {
        return 0
      }

      return `1 in ${round(1 / this.maskingFactor, 0)}`
    }
  },
  methods: {
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
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

  .operator {
    font-weight: bold;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .bold {
    font-weight: bold;
  }

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
  .masking-table, .equations {
    font-size: 0.5em;
  }

  .masking-table text {
    font-size: 1em;
  }

</style>
