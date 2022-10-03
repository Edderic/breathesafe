
<template>
  <table>
    <tr>
      <th class='col centered'>
        <span>Clean Air Delivery Rate</span>
        <span class='font-light'>({{this.measurementUnits.airDeliveryRateMeasurementTypeShort}})</span>
      </th>
      <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeRoomVolume"
        :maxVal=1
        :value='totalFlowRateRounded'
        :style='cellCSSMerged'
      />
      </td>
    </tr>
    <tr>
      <td></td>
      <td>=</td>
    </tr>
    <tr>
      <th class='col centered'>
        <span>Unoccupied Room Volume</span>
        <span class='font-light'>({{this.measurementUnits.cubicLengthShort}})</span>
      </th>
      <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeRoomVolume"
        :maxVal=1
        :value='roomUsableVolumeRounded'
        :style='cellCSSMerged'
      />
      </td>
    </tr>
    <tr>
      <td></td>
      <td>x</td>
    </tr>
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
    <tr v-if="systemOfMeasurement == 'imperial'">
      <th></th>
      <th>/</th>
    </tr>
    <tr v-if="systemOfMeasurement == 'imperial'">
      <th class='col centered' v-if="systemOfMeasurement == 'imperial'">
        <span></span>
        <span class='font-light'>(min / h)</span>
      </th>
      <td>
      <ColoredCell
        v-if="systemOfMeasurement == 'imperial'"
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='60'
        class='color-cell'
        :style='cellCSSMerged'
        style='background-color: grey'
      />
      </td>
    </tr>
  </table>
</template>

<script>
import ColoredCell from './colored_cell.vue'
import { convertVolume } from './measurement_units.js';
import {
  assignBoundsToColorScheme,
  colorSchemeFall,
  colorInterpolationSchemeAch,
  cutoffsVolume,
} from './colors.js';
import {
  displayCADR,
  round
} from './misc.js'

export default {
  name: 'CleanAirDeliveryRateTable',
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
        'padding-left': '0.5em',
        'padding-right': '0.5em',
      }

      // return Object.assign(this.cellCSS, default)
      return Object.assign(def, this.cellCSS)
    },
    colorInterpolationSchemeRoomVolume() {
      return assignBoundsToColorScheme(colorSchemeFall, cutoffsVolume(this.measurementUnits))
    },
    colorInterpolationSchemeTotalAch(){
      return colorInterpolationSchemeAch
    },
    roomUsableVolumeRounded() {
      return round(this.roomUsableVolume, 1)
    },
    roomUsableVolume() {
      return convertVolume(
        this.intervention.roomUsableVolumeCubicMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType
      )
    },
    totalAchRounded() {
      return round(this.intervention.computeACH(), 1)
    },
    totalFlowRateRounded() {
      return round(this.totalFlowRate, 1)
    },
    totalFlowRate() {
      return displayCADR(
        this.systemOfMeasurement,
        this.intervention.roomUsableVolumeCubicMeters * this.intervention.computeACH()
      )
    }
  },
  props: {
    cellCSS: Object,
    intervention: Object,
    measurementUnits: Object,
    systemOfMeasurement: String,
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


</style>
