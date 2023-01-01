
<template>
  <tr>
    <td class='justify-content-center align-items-center'>
      <h3 class='bold'>Clean Air Delivery Rate</h3>

      <div class='row'>
        <CircularButton text='?' @click='show = !show'/>

      </div>
    </td>
    <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeRoomVolume"
        :maxVal=1
        :value='totalFlowRateRounded'
        :style="styleProps"
      />
    </td>
  </tr>
  <tr v-if='show'>
    <td colspan='2'>
      <table class='explainer'>
        <tr>
          <th class='centered'>
            <div class='col'>
              <span>Clean Air Delivery Rate</span>
              <span class='font-light'>({{this.measurementUnits.airDeliveryRateMeasurementTypeShort}})</span>
            </div>
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
          <th class='centered'>
            <div class='col'>
              <span>Unoccupied Room Volume</span>
              <span class='font-light'>({{this.measurementUnits.cubicLengthShort}})</span>
            </div>
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
          <th class='centered'>
            <div class='col'>
              <span>Total ACH</span>
              <span class='font-light'>(1 / h)</span>
            </div>
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
          <th class='centered' v-if="systemOfMeasurement == 'imperial'">
            <div class='col'>
              <span></span>
              <span class='font-light'>(min / h)</span>
            </div>
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
    </td>
  </tr>
</template>

<script>
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import { useAnalyticsStore } from './stores/analytics_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
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
    ColoredCell,
    CircularButton,
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
  .bold {
    font-weight: bold;
  }

  .font-light {
    font-weight: 400;
  }

  .col {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }


  td {
    padding-top: 0.5em;
    padding-bottom: 0.5em;
    padding-left: 0.5em;
    padding-right: 0.5em;
    text-align: center;
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

  .row {
    display: flex;
    flex-direction: row;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }
</style>
