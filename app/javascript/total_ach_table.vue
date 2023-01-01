<template>
  <tr id='section-total-ach'>
    <td>
      <div class='row justify-content-center align-items-center'>
        <h3 class='bold'>Total ACH</h3>
        <CircularButton text='?' @click='show = !show'/>
      </div>
    </td>
    <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='totalAchRounded'
        :style='cellCSSMerged'
      />
    </td>
  </tr>

  <tr v-if='show'>
    <td colspan='2'>
      <table class='explainer'>
        <tr>
          <th class='col centered'>
            <span>Total ACH</span>
            <span class='font-light'>(1 / h)</span>
          </th>
          <td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='totalAchRounded'
            :style='cellCSSMerged'
          />
          </td>
        </tr>
        <tr>
          <th></th>
          <td class='operator'>=</td>
        </tr>
        <tr>
          <th class='col centered'>
            <span>Ventilation ACH</span>
            <span class='font-light'>(1 / h)</span>
          </th>
          <td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='ventilationAchRounded'
            :style='cellCSSMerged'
          />
          </td>
        </tr>
        <tr>
          <td></td>
          <td class='operator'>+</td>
        </tr>
        <tr>
          <th class='col centered'>
            <span>Portable ACH</span>
            <span class='font-light'>(1 / h)</span>
          </th>
          <td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='portableAchRounded'
            :style='cellCSSMerged'
          />
          </td>
        </tr>
        <tr>
          <td></td>
          <td class='operator'>+</td>
        </tr>
        <tr>
          <th class='col centered'>
            <span>Upper-Room UV ACH</span>
            <span class='font-light'>(1 / h)</span>
          </th>
          <td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='uvAchRounded'
            :style='cellCSSMerged'
          />
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr v-if='show'>
    <td colspan='2'>
      <p class='explainer'>
        Air Changes per Hour (ACH) tells us how much clean air is generated
        relative to the volume of the room. If a device outputs 5 ACH, that means it
        produces clean air that is 5 times the volume of the room in an hour.  Total
        ACH for a room can be computed by summing up the ACH of different types (e.g.
        ventilation, filtration, upper-room germicidal UV).
      </p>
    </td>
  </tr>

</template>


<script>
import {
  assignBoundsToColorScheme,
  colorSchemeFall,
  colorInterpolationSchemeAch,
  cutoffsVolume
} from './colors.js';

import {
  round,
} from  './misc';

import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'

export default {
  name: 'TotalACH',
  components: {
    CircularButton,
    ColoredCell
  },
  data() {
    return {
      show: false
    }
  },
  props: {
    cellCSS: Object,
    measurementUnits: Object,
    systemOfMeasurement: String,
    roomUsableVolumeCubicMeters: Number,
    selectedIntervention: Object
  },
  computed: {
    portableAch() {
      return this.selectedIntervention.computePortableAirCleanerACH()
    },
    ventilationAch() {
      return this.selectedIntervention.computeVentilationACH()
    },
    uvAch() {
      return this.selectedIntervention.computeUVACH()
    },
    colorInterpolationSchemeTotalAch() {
      return colorInterpolationSchemeAch
    },
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'text-align': 'center',
        'padding-left': '1em',
        'padding-right': '1em',
      }

      // return Object.assign(this.cellCSS, default)
      return Object.assign(def, this.cellCSS)
    },
    portableAchRounded() {
      return round(this.portableAch, 1)
    },
    ventilationAchRounded() {
      return round(this.ventilationAch, 1)
    },
    uvAchRounded() {
      return round(this.uvAch, 1)
    },
    roomUsableVolumeRounded() {
      return round(
        this.roomUsableVolume,
        1
      )
    },
    totalAchRounded() {
      return round(this.totalAch, 1)
    },
    totalFlowRate() {
      return displayCADR(
        this.systemOfMeasurement,
        (this.roomUsableVolumeCubicMeters * this.totalAch)
      )
    },
    totalFlowRateRounded() {
      return round(this.totalFlowRate, 1)
    },

    roomUsableVolume() {
      const profileStore = useProfileStore()

      return convertVolume(
        this.roomUsableVolumeCubicMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType
      )
    },

    totalAch() {
      return this.ventilationAch + this.uvAch + this.portableAch
    }
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
</style>
