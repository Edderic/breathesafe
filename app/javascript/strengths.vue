<template>
  <div class='item'>
    <br id='strengths'>
    <br>
    <br>
    <h3>Strengths</h3>
    <ul>
      <li v-if="selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement) > 1000">

        <span class='italic bold'>
          <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`">
            Clean Air Delivery Rate (CADR):
          </router-link>
        </span>&nbsp;&nbsp;


        Assuming that the air is well-mixed (i.e. infector's air
        particles are distributed evenly throughout the space (i.e. via fans),
        people are getting

        <ColoredCell
          :colorScheme="colorInterpolationSchemeRoomVolume"
          :maxVal=1
          :value='roundOut(selectedIntervention.computeCleanAirDeliveryRate(systemOfMeasurement), 0)'
          :style='cellCSSMerged'
        />

      {{ measurementUnits.airDeliveryRateMeasurementType }} of clean air.
      </li>

      <li v-if='maskingBarChart.isStrength(0.2)'>
      <span class='italic bold'>
        <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
          Masking
        </router-link>
      </span>&nbsp;&nbsp;

      <ColoredCell
        :colorScheme="reducedRiskColorScheme"
        :maxVal=1
        :value='roundOut(maskingBarChart.fractionOfSubparMasks(), 2)'
        :style='cellCSSMerged'
      />
      </li>

      <li v-if='exhalationActivityIsStrength'>
        <span class='italic bold'>
          <router-link :to="`/analytics/${this.$route.params.id}#exhalation`">
            Exhalation activity:
          </router-link>
        </span>&nbsp;&nbsp;


        <span>
        The riskiest aerosol generation activity recorded during this measurement is <ColoredCell
              :colorScheme="riskiestAerosolGenerationActivityScheme"
              :maxVal=1
              :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
              :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
              :style="inlineCellCSS"
          />.
        </span>
      </li>

      <li v-if='inhalationActivityIsStrength'>
        <span class='italic bold'>
          <router-link :to="`/analytics/${this.$route.params.id}#inhalation`">
            Inhalation activity:
          </router-link>
        </span>&nbsp;&nbsp;

        <span>The worst case inhalation activity is <ColoredCell
              :colorScheme="inhalationActivityScheme"
              :maxVal=1
              :value='worstCaseInhalation["inhalationFactor"]'
              :text='worstCaseInhalation["inhalationActivity"]'
              :style="inlineCellCSS"
          />.
        </span>
      </li>

      <li v-if='maskingBarChart.isStrength(0.2)'>
      <span class='italic bold'>
        <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
          Masking
        </router-link>
      </span>&nbsp;&nbsp;
      </li>
    </ul>

  </div>

</template>

<script>
// Have a VueX store that maintains state across components
import ColoredCell from './colored_cell.vue';
import { airCleaners, AirCleaner } from './air_cleaners.js';
import { datetimeEnglish } from './date.js'
import { getSampleInterventions } from './sample_interventions.js'
import {
  AEROSOL_GENERATION_BOUNDS,
  colorPaletteFall,
  assignBoundsToColorScheme,
  convertColorListToCutpoints,
  generateEvenSpacedBounds } from './colors.js';
import {
  findRiskiestPotentialInfector,
  riskOfEncounteringInfectious,
  riskIndividualIsNotInfGivenNegRapidTest,
  reducedRisk } from './risk.js';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState } from 'pinia';
import {
  findWorstCaseInhFactor,
  infectorActivityTypes,
  susceptibleBreathingActivityToFactor,
  round

} from  './misc';

export default {
  name: 'Analytics',
  components: {
    ColoredCell,
  },
  computed: {
    ...mapState(
        useProfileStore,
        [
          'airDeliveryRateMeasurementType',
          'measurementUnits',
          'systemOfMeasurement'
        ]
    ),
    ...mapWritableState(
        useShowMeasurementSetStore,
        [
          'activityGroups',
          'infectorActivityTypeMapping',
        ]
    ),
    cellCSS() {
      return {
        'padding-top': '1em',
        'padding-bottom': '1em',
      }
    },
    inhalationActivityIsStrength() {
      // highest range for Sedentary / Sedentary passive is 6 to <11
      return this.worstCaseInhalation['inhalationFactor']
        <= susceptibleBreathingActivityToFactor['Sedentary / Passive']['6 to <11'][
          'mean cubic meters per hour'
        ]
    },

    exhalationActivityIsStrength() {
      return this.aerosolActivityToFactor(this.riskiestPotentialInfector["aerosolGenerationActivity"])
        <= this.infectorActivityTypeMapping["Standing – Speaking"]
    },
    inhalationActivityScheme() {
      const minimum = 0.258
      const maximum = 3
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall)).reverse()
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },
    reducedRiskColorScheme() {
      const minimum = 0
      const maximum = 1
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall)).reverse()
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },

    riskiestPotentialInfector() {
      return findRiskiestPotentialInfector(this.activityGroups)
    },
    riskiestAerosolGenerationActivityScheme() {
      const copy = [
        colorPaletteFall[4],
        colorPaletteFall[3],
        colorPaletteFall[2],
        colorPaletteFall[1],
        colorPaletteFall[0]]
      const cutPoints = convertColorListToCutpoints(copy)
      return assignBoundsToColorScheme(cutPoints, AEROSOL_GENERATION_BOUNDS)
    },
    worstCaseInhalation() {
      return findWorstCaseInhFactor(this.activityGroups)
    },
  },
  props: {
    cellCSSMerged: Object,
    colorInterpolationSchemeRoomVolume: Object,
    maskingBarChart: Object,
    selectedIntervention: Object
  },
  methods: {
    aerosolActivityToFactor(key) {
      return infectorActivityTypes[key]
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  }
}

</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    text-align: center;
    font-weight: bold;
    margin-left: 1em;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .textarea-label {
    padding-top: 0;
  }

  textarea {
    width: 30em;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wider-input {
    width: 30em;
  }

  button {
    padding: 1em 3em;
  }

  table {
    text-align: center;
    padding: 2em;
  }

  .scrollable {
    overflow-y: scroll;
    height: 72em;
  }

  .scroll-table {
    height: 40em;

    overflow-y: scroll;
  }


  .col {
    display: flex;
    flex-direction: column;
  }

  .margined {
    margin: 2em;
  }

  .padded {
    padding: 1em;
  }

  th {
    padding: 1em;
  }

  .font-light {
    font-weight: 400;
  }

  td {
    padding: 1em;
  }

  span {
    line-height: 2em;
  }

  .highlight {
    font-style: italic;
    font-weight: bold;
  }

  img {
    width: 4em;
  }

  p {
    line-height: 2em;
  }

  li {
    line-height: 2em;
  }

  .bold {
    font-weight: bold;
  }
  .italic {
    font-style: italic;
  }

  .clicked {
    background-color: #e6e6e6;
  }

  .color-cell {
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px black;
    padding: 1em;
  }

  .quote {
    font-style: italic;
    padding-left: 2em;
  }

  div {
    scroll-behavior: smooth;
  }

  .left-pane {
    width: 20rem;
    height: 50em;
    position: fixed;
    left: 0em;
    border-right: 1px solid black;
    height: 100vh;
    border-top: 0px;
    border-bottom: 0px;
  }

  .right-pane {
    height: auto;
    margin-left: 20rem;
  }

  .link-h1 {
    margin-left: 2em;
    margin-top: 1em;
  }

  .link-h2 {
    margin-left: 3em;
    margin-top: 1em;
  }

  @media (max-width: 840em) {
    .centered {
      overflow-x: auto;
    }
  }

  @media (max-width: 1080px) {

    .left-pane {
      display: none;
      position: unset;
    }

    .right-pane {
      margin-left: 0;
      width: 100vw;
    }
  }

  .icon-bar {
    position: fixed;
    background-color: white;
  }

  .italic {
    font-style: italic;
  }

  .bold {
    font-weight: bold;
  }

  .table-td-mask {
    padding: 0;
    width: 3em;
  }

  .table-td {
    padding: 0 0.5em;
  }

  .tilted-header {
    font-size: 0.5em;
  }

  th.table-td-mask {
    font-size: 0.5em;
  }

  .parameters td img {
    height: 3.5em;
  }

  .parameters td {
    padding: 0.25em;
  }

  .grid {
    display: grid;
    grid-template-columns: 40% 15% 45%;
  }

  .content {
    display: grid;
    grid-template-columns: 50% 50%;
  }

  .item {
    padding: 1em;
  }

  .sticky {
    position: sticky;
    top: 3.2em;
    height: 100vh;
  }

  .scrollableY {
  }

</style>
