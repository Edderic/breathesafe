

<template>
  <table>
    <tr>
      <th class='col centered'>
        <span>Total ACH</span>
        <span class='font-light'>(1 / h)</span>
      </th>
      <th></th>
      <th class='col centered'>
        <span>Ventilation ACH</span>
        <span class='font-light'>(1 / h)</span>
      </th>
      <th></th>
      <th class='col centered'>
        <span>Portable ACH</span>
        <span class='font-light'>(1 / h)</span>
      </th>
      <th></th>
      <th class='col centered'>
        <span>Upper-Room UV ACH</span>
        <span class='font-light'>(1 / h)</span>
      </th>
    </tr>
    <tr>
      <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='totalAchRounded'
        :style='cellCSSMerged'
      />
      </td>
      <td class='operator'>=</td>
      <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='ventilationAchRounded'
        :style='cellCSSMerged'
      />
      </td>
      <td class='operator'>+</td>
      <td>
      <ColoredCell
        :colorScheme="colorInterpolationSchemeTotalAch"
        :maxVal=1
        :value='portableAchRounded'
        :style='cellCSSMerged'
      />
      </td>
      <td class='operator'>+</td>
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
</template>


<script>
import {
  colorSchemeFall,
  assignBoundsToColorScheme,
} from './colors.js';

import {
  round,
} from  './misc';

import ColoredCell from './colored_cell.vue'

export default {
  name: 'TotalACH',
  components: {
    ColoredCell
  },
  props: {
    cellCSS: Object,
    measurementUnits: Object,
    systemOfMeasurement: String,
    portableAch: Number,
    ventilationAch: Number,
    uvAch: Number,
    roomUsableVolumeCubicMeters: Number,
  },
  computed: {
    colorInterpolationSchemeRoomVolume() {
      return assignBoundsToColorScheme(colorSchemeFall, this.cutoffsVolume)
    },
    colorInterpolationSchemeTotalAch() {
      return [
        {
          'lowerBound': 0,
          'upperBound': 2,
          'upperColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
          'lowerColor': {
            name: 'darkRed',
            r: 174,
            g: 17,
            b: 0
          },
        },
        {
          'lowerBound': 2,
          'upperBound': 4,
          'upperColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
          'lowerColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
        },
        {
          'lowerBound': 4,
          'upperBound': 8,
          'upperColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'lowerColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
        },
        {
          'lowerBound': 8,
          'upperBound': 16,
          'lowerColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'upperColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
        },
        {
          'lowerBound': 16,
          'upperBound': 100,
          'lowerColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
          'upperColor': {
            name: 'dark green',
            r: 11,
            g: 161,
            b: 3
          },
        },
      ]
    },
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'text-align': 'center',
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
</style>
