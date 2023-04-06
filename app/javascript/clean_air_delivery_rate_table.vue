
<template>
  <DrillDownSection

    title='Non-Infectious Air Delivery Rate'
    :value='totalFlowRateRounded'
    :text='totalFlowRateText'
    :colorScheme='colorInterpSchemeRoomVol'
  >
  <tr>
    <td colspan='2'>

      <h3>How does this NADR compare to being outside?</h3>
      <p>
      How does a non-infectious air delivery rate of {{totalFlowRateRounded}} {{measurementUnits.airDeliveryRateMeasurementTypeShort}} compare to being outside?

      Let's assume there's "light air". According to the U.S. National Weather Service, this is characterized as having the

      </p>

      <p class='quote'>
        <a href="https://www.weather.gov/pqr/wind">
        ...direction of wind shown by smoke drift, not by wind vanes. Little if any movement with flags. Wind barely moves tree leaves.
        </a>
      </p>
      <p>
      The speed of moving air when there is "light air" is around 1 to 3 miles per hour. Let's look at the lower bound of 1 mph.


      </p>
      <vue-mathjax :formula='windspeedMPHtoCFM'></vue-mathjax>

      <p>Non-infectious air delivery rates are measured in volume per time. If
we have the windspeed, for example, in feet per minute, we still need to select
an appropriate area (e.g. sq. ft.) to go along with the windspeed to get volume
per time (e.g. cubic feet per minute).
      </p>

      <div class='justify-content-center'>
        <table>
          <thead>
          <tr>
            <th>Type</th>
            <th>Measurement ({{measurementUnits.lengthMeasurementType}})</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            <th>Length</th>
            <th>{{ convertLengthTo(this.event.roomLengthMeters) }}</th>
          </tr>
          <tr>
            <th>Width</th>
            <th>{{ convertLengthTo(this.event.roomWidthMeters) }}</th>
          </tr>
          <tr>
            <th>Height</th>
            <th>{{ convertLengthTo(this.event.roomHeightMeters) }}</th>
          </tr>
          </tbody>
        </table>
      </div>


      <p>
      If we imagine the sides made up of the length and height were chopped off (i.e. the two sides with {{convertLengthTo(this.event.roomLengthMeters)}} x {{convertLengthTo(this.event.roomHeightMeters)}} square {{measurementUnits.lengthMeasurementType}} = {{this.roundOut(convertLengthTo(this.event.roomLengthMeters * convertLengthTo(this.event.roomHeightMeters)), 1)}} square {{this.measurementUnits.lengthMeasurementType}}), then the non-infectious air delivery rate would have been:
      </p>

      <vue-mathjax :formula='outdoorsNADRDerivation'></vue-mathjax>

      <p>
      {{ outdoorsNADRText }} from being outside is {{ outdoorsIsNumTimesTheNADR}} times the estimated NADR from being inside in this room! As you may recall from earlier sections, NADR, represented as <vue-mathjax formula='$Q$'></vue-mathjax> in the concentration curve, is the denominator of the first term, which is the steady state concentration.



      </p>

      <p>
        <vue-mathjax formula='$$C_t = g/Q \cdot (1 - e^{-\frac{Q}{V} \cdot t}) $$'></vue-mathjax>
      </p>
      <p>
      So in the long run, if Q is very large, then the concentration curve is
      basically hovering around 0.
      <p>
        <vue-mathjax formula='$$g/Q \approx 0  \text{     if Q} >> 0$$'></vue-mathjax>
      </p>

      Dose is essentially concentration times time, so
      if the concentration part is very small, the dose is also small, which means
      that <span class='italic'>it is much safer being outdoors relative to being inside in this room.</span>
      </p>
      <h3>Mathematical Details</h3>
      <table class='explainer mathematical-details'>
        <tr>
          <th class='centered'>
            <div class='col'>
              <span>Clean Air Delivery Rate</span>
              <span class='font-light'>({{this.measurementUnits.airDeliveryRateMeasurementTypeShort}})</span>
            </div>
          </th>
          <td>
          <ColoredCell
            :colorScheme="colorInterpSchemeRoomVol"
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
            :colorScheme="colorInterpSchemeRoomVol"
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
  </DrillDownSection>
</template>

<script>
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import DrillDownSection from './drill_down_section.vue'
import { useAnalyticsStore } from './stores/analytics_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import { convertVolume } from './measurement_units.js';
import {
  assignBoundsToColorScheme,
  colorSchemeFall,
  colorInterpolationSchemeAch,
  colorInterpolationSchemeRoomVolume,
  cutoffsVolume,
} from './colors.js';
import {
  convertLengthBasedOnMeasurementType,
  displayCADR,
  round
} from './misc.js'

export default {
  name: 'CleanAirDeliveryRateTable',
  components: {
    ColoredCell,
    CircularButton,
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
        'styleProps',
        'event'
      ]
    ),

    outdoorsNADRDerivation(){
      return `$$${
        round(
            this.convertLengthTo(this.event.roomLengthMeters)
            * this.convertLengthTo(this.event.roomHeightMeters),
            1
        )
      } \\text{ ${this.measurementUnits.squareLengthShort}} \\cdot ${this.windSpeed} \\text{ ft / min} = ${this.outdoorsNADR} \\text{ ${this.measurementUnits.airDeliveryRateMeasurementTypeShort}}$$`
    },
    outdoorsNADR() {
      return this.convertLengthTo(this.event.roomLengthMeters) * this.convertLengthTo(this.event.roomHeightMeters) * this.windSpeed
    },
    outdoorsNADRText() {
      return `${this.outdoorsNADR} ${this.measurementUnits.airDeliveryRateMeasurementTypeShort}`
    },
    outdoorsIsNumTimesTheNADR() {
      return round(this.outdoorsNADR / this.totalFlowRate, 0)
    },
    windSpeed() {
      // feet per minute
      return convertLengthBasedOnMeasurementType(88, 'feet', this.measurementUnits.lengthMeasurementType)
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
    colorInterpSchemeRoomVol() {
      return colorInterpolationSchemeRoomVolume(this.measurementUnits)
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
    totalFlowRateText() {
      let roundTo = 1;
      if (this.totalFlowRate > 1) {
        roundTo = 0
      }

      return `${round(this.totalFlowRate, roundTo)} ${this.measurementUnits.airDeliveryRateMeasurementTypeShort}`
    },
    totalFlowRate() {
      return displayCADR(
        this.systemOfMeasurement,
        this.intervention.roomUsableVolumeCubicMeters * this.intervention.computeACH()
      )
    },
    windspeedMPHtoCFM() {
      return `
        $$
        \\begin{equation}
        \\begin{aligned}
          1 \\text{mi}/\\text{h} &= 88 \\text{ ft} / \\text{min}
        \\end{aligned}
        \\end{equation}
        $$
      `
    }
  },
  props: {
    cellCSS: Object,
    intervention: Object,
    measurementUnits: Object,
    systemOfMeasurement: String,
  },
  methods: {
    convertLengthTo(fromNum) {
      return convertLengthBasedOnMeasurementType(
        fromNum,
        'meters',
        this.measurementUnits.lengthMeasurementType
      )
    },
    roundOut(x,y) {
      return round(x,y)
    }
  }
}
</script>

<style scoped>
  th, .bold {
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
    font-weight: bold;
  }

  .mathematical-details td {
    text-align: center;
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

  .italic {
    font-style: italic;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
</style>
