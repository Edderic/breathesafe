/<template>

  <div class='grid'>
    <div class='item controls'>
      <div class='container'>
        <h3 class='subsection'>Analysis & Recommendations for {{this.roomName}}</h3>
        <h4 class='subsection' v-if='event && event.placeData'>{{event.placeData.formattedAddress}}</h4>
        <h4 class='subsection' v-if='event && event.firstName'>Measurements taken by {{event.firstName}} {{event.lastName}}</h4>
        <h4 class='subsection'>on {{datetimeInWords}}</h4>
      </div>

      <div class='centered col'>
        <div>
          <router-link :to='{ name: "UpdateOrCopyMeasurements", params: {action: "update", id: this.$route.params.id} }' v-if='currentUser && (currentUser.admin || event.authorId == currentUser.id)'>
            ✎ Update
          </router-link>
        </div>
        <div>
          <router-link :to='{ name: "UpdateOrCopyMeasurements", params: {action: "copy", id: this.$route.params.id} }' v-if='currentUser'>
            ➕ Add New Measurements
          </router-link>
        </div>
      </div>

      <div class='centered col'>
        <Menu backgroundColor='transparent'>
          <Button  text='Remove the Source' :selected='selectedInterventionType == "Remove the Source"' @click='selectInterventionType("Remove the Source")'/>
          <Button  text='Dilute the Air' :selected='selectedInterventionType == "Dilute the Air"' @click='selectInterventionType("Dilute the Air")'/>
        </Menu>
      </div>

      <div class='centered col' v-show='selectedInterventionType  == "Remove the Source"'>
        <Menu backgroundColor='transparent'>
          <Button text='Prevalence' :selected='selectedRemoveSourceTab == "Prevalence"' @click='selectRemoveSourceTab("Prevalence")'/>
          <Button text='Occupancy & Results' :selected='selectedRemoveSourceTab == "Occupancy & Results"' @click='selectRemoveSourceTab("Occupancy & Results")'/>
        </Menu>

        <Prevalence v-show='selectedRemoveSourceTab == "Prevalence"'/>
        <HasInfector v-show='selectedRemoveSourceTab == "Occupancy & Results"'/>
      </div>


      <Controls v-show='selectedInterventionType == "Dilute the Air"'
        :maskInstances='maskInstances'
        :airCleanerInstances='airCleanerInstances'
        :riskColorScheme='riskColorScheme'
      />
    </div>

    <div class='second-column'>
      <div class='col item' >
        <div class='item'>
          <div class='item-span-wide' id='section-risk-assessment-summary'>
            <br id='risk-assessment-summary'>
            <h2 class='centered'>Risk Assessment</h2>
          </div>

          <LineGraph
            class='centered'
            :lines="[marginalRiskLine, conditionalRiskLine]"
            xlabel="Time (hours)"
            ylabel='Risk'
            :ylim='[0, 1]'
            :title="riskTitle"
            :xHighlighter='selectedHour * 60'
            setYTicksToPercentages='true'
            :xTickLabels="[0, 10, 20, 30, 40]"
            @point='point'
          />

          <table class='item-span-wide stuff'>
            <ProbaAtLeastOneInfectorPresent/>
            <PeopleAffected
              id='section-average-new-infections'
              :event='event'
              :selectedIntervention='selectedIntervention'
              :numInfectors='numInfectors'
              class='align-items-center'
            />

            <IndividualRisk
              id='section-individual-risk'
              :riskColorScheme='riskColorScheme'
              class='align-items-center'
            />


          </table>

          <IndoorAirQuality/>

          <table>
            <CleanAirDeliveryRateTable :cellCSS='cellCSS' :intervention='selectedIntervention' :measurementUnits='measurementUnits' :systemOfMeasurement='systemOfMeasurement'/>
            <TotalACHTable
              :measurementUnits='measurementUnits'
              :systemOfMeasurement='systemOfMeasurement'
              :totalFlowRate='totalFlowRate'
              :roomUsableVolume='roomUsableVolume'
              :selectedIntervention='selectedIntervention'
              :cellCSS='cellCSS'
              :roomUsableVolumeCubicMeters='roomUsableVolumeCubicMeters'
            />

            <AchToDuration
              :intervention='selectedIntervention'
            />
          </table>
        </div>
      </div>

      <div class='item'>
        <div class='item-span-wide' id='section-ventilation'>
          <br>
          <h2 class='centered'>
            <VentIcon :showText='false' height='3em' width='3em' />
            Ventilation
          </h2>
        </div>

        <LineGraph
          class='centered'
          :lines="[co2Projection, readings]"
          xlabel="Time (minutes)"
          ylabel='CO₂ Concentration (ppm)'
          :ylim='[400, readingsMax + 300]'
          title="CO₂ concentration over Time"
          :roundYTicksTo='0'
          :roundXTicksTo='0'
        />

        <table>
          <VentilationNDIR
            :cadr='ventilationCadr'
            :systemOfMeasurement='systemOfMeasurement'
            :measurementUnits='measurementUnits'
            :ventilationNotes='ventilationNotes'
          />
          <SteadyState
            :activityGroups='activityGroups'
            :generationRate='generationRate'
            :roomUsableVolumeCubicMeters='roomUsableVolumeCubicMeters'
            :c0='c0'
            :cBackground='ventilationCo2AmbientPpm'
            :cadr='ventilationCadr'
            />

        </table>


        <Behaviors
        />
        <table>
          <InhalationActivity
            :worstCaseInhalation='worstCaseInhalation'
            :inhalationActivityScheme='inhalationActivityScheme'
            :susceptibleBreathingActivityFactorMappings='susceptibleBreathingActivityFactorMappings'
            :inlineCellCSS='inlineCellCSS'
            :tableColoredCellWithHorizPadding='tableColoredCellWithHorizPadding'
          />
          <InfectorActivity
            :aerosolGenerationActivity='aerosolGenerationActivity'
            :riskiestAerosolGenerationActivityScheme='riskiestAerosolGenerationActivityScheme'
            :aerosolActivityToFactor='aerosolActivityToFactor'
            :riskiestPotentialInfector='riskiestPotentialInfector'
            :inlineCellCSS='inlineCellCSS'
            :tableColoredCell='tableColoredCell'
          />
          <Masking
            :riskColorScheme='riskColorScheme'
            :cellCSSMerged='cellCSSMerged'
            :intervention='selectedIntervention'
          />
        </table>

        <div class='item-span-wide' id='section-details'>
          <br id='details'>
          <h2 class='centered'>Details</h2>

          <RiskEquation/>
          <ComputationalDetails
            :aerosolActivityToFactor='aerosolActivityToFactor'
            :numSusceptibles='numSusceptibles'
            :numInfectors='numInfectors'
            :riskColorScheme='riskColorScheme'
            :riskiestPotentialInfector='riskiestPotentialInfector'
            :roomUsableVolumeCubicMeters='roomUsableVolumeCubicMeters'
            :selectedInfectorMask='selectedInfectorMask'
            :selectedIntervention='selectedIntervention'
            :selectedSusceptibleMask='selectedSusceptibleMask'
            :selectedHour='selectedHour'
            :roomLengthMeters='roomLengthMeters'
            :roomWidthMeters='roomWidthMeters'
            :worstCaseInhalation='worstCaseInhalation'
            :activityGroups='activityGroups'
          />
        </div>
      </div>



    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import Behaviors from './behaviors.vue';
import Button from './button.vue';
import CircularButton from './circular_button.vue';
import ColoredCell from './colored_cell.vue';
import Controls from './controls.vue';
import ComputationalDetails from './computational_details.vue';
import CleanAirDeliveryRateTable from './clean_air_delivery_rate_table.vue'
import InhalationActivity from './inhalation_activity.vue'
import InfectorActivity from './infector_activity.vue'
import Masking from './masking.vue'
import CADR from './cadr.vue'
import DayHourHeatmap from './day_hour_heatmap.vue';
import HasInfector from './has_infector.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import Menu from './menu.vue';
import Prevalence from './prevalence.vue';
import { Intervention } from './interventions.js'
import TotalACHTable from './total_ach_table.vue';
import TotalACH from './total_ach.vue';
import VentIcon from './vent_icon.vue';
import IndividualRisk from './individual_risk.vue';
import IndoorAirQuality from './indoor_air_quality.vue';
import PacIcon from './pac_icon.vue';
import PeopleAffected from './people_affected.vue';
import ProbaAtLeastOneInfectorPresent from './proba_at_least_one_infector_present.vue';
import RiskIcon from './risk_icon.vue';
import RiskEquation from './risk_equation.vue';
import SideBar from './side_bar.vue';
import { airCleaners, AirCleaner } from './air_cleaners.js';
import { datetimeEnglish } from './date.js'
import { getSampleInterventions } from './sample_interventions.js'
import {
  AEROSOL_GENERATION_BOUNDS,
  colorSchemeFall,
  colorPaletteFall,
  assignBoundsToColorScheme,
  riskColorInterpolationScheme,
  infectedPeopleColorBounds,
  convertColorListToCutpoints,
  generateEvenSpacedBounds } from './colors.js';
import AchToDuration from './ach_to_duration.vue'
import LineGraph from './line_graph.vue'
import SteadyState from './steady_state.vue'
import VentilationNDIR from './ventilation_ndir.vue'
import {
  findRiskiestMask,
  findRiskiestPotentialInfector,
  riskOfEncounteringInfectious,
  riskIndividualIsNotInfGivenNegRapidTest,
  reducedRisk } from './risk.js';
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';
import { useAnalyticsStore } from './stores/analytics_store'
import { Mask, MASKS, MaskingBarChart } from './masks.js';
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  CO2_TO_MET,
  QUANTA,
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  computeCO2EmissionRate,
  findWorstCaseInhFactor,
  genConcCurve,
  getCO2Rate,
  infectorActivityTypes,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  susceptibleBreathingActivityToFactor,
  round

} from  './misc';

export default {
  name: 'Analytics',
  components: {
    AchToDuration,
    Behaviors,
    Button,
    CADR,
    CircularButton,
    CleanAirDeliveryRateTable,
    ColoredCell,
    ComputationalDetails,
    Controls,
    DayHourHeatmap,
    Event,
    HasInfector,
    HorizontalStackedBar,
    IndividualRisk,
    IndoorAirQuality,
    InhalationActivity,
    InfectorActivity,
    LineGraph,
    Masking,
    Menu,
    Prevalence,
    PacIcon,
    PeopleAffected,
    ProbaAtLeastOneInfectorPresent,
    RiskEquation,
    RiskIcon,
    SideBar,
    SteadyState,
    TotalACHTable,
    TotalACH,
    VentIcon,
    VentilationNDIR
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'focusTab',
        ]
    ),
    ...mapState(
        usePrevalenceStore,
        [
          'riskOfOne',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'lengthMeasurementType',
          'airDeliveryRateMeasurementType',
          'carbonDioxideMonitors',
          'measurementUnits',
          'systemOfMeasurement'
        ]
    ),
    ...mapWritableState(
      useAnalyticsStore,
      [
        'numPeopleToInvestIn',
        'selectedAirCleaner',
        'selectedSusceptibleMask',
        'numInfectors',
        'numSusceptibles',
        'selectedInterventionType',
        'selectedIntervention',
        'selectedHour',
        'selectedInfectorMask',
        'selectedRemoveSourceTab',
        'probabilityOneInfectorIsPresent',
        'priorProbabilityOfInfectiousness'
      ]
    ),
    ...mapWritableState(
        useShowMeasurementSetStore,
        [
          'roomName',
          'activityGroups',
          'ageGroups',
          'co2Readings',
          'carbonDioxideActivities',
          'ventilationCo2AmbientPpm',
          'ventilationCo2MeasurementDeviceModel',
          'ventilationCo2MeasurementDeviceName',
          'ventilationCo2MeasurementDeviceSerial',
          'ventilationCo2SteadyStatePpm',
          'duration',
          'private',
          'formatted_address',
          'initialCo2',
          'infectorActivity',
          'infectorActivityTypeMapping',
          'maskTypes',
          'numberOfPeople',
          'occupancy',
          'maximumOccupancy',
          'placeData',
          'portableAirCleaners',
          'rapidTestResult',
          'rapidTestResults',
          'roomHeightMeters',
          'roomLengthMeters',
          'roomWidthMeters',
          'roomUsableVolumeFactor',
          'roomUsableVolumeCubicMeters',
          'singlePassFiltrationEfficiency',
          'startDatetime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes',
          'ventilationAch',
          'portableAch',
          'totalAch'
        ]
    ),
    riskTitle() {
      return `COVID-19 Transmission Risk`
    },
    readings() {
      if (!this.co2Readings) {
        return [[0, this.ventilationCo2SteadyStatePpm]]
      }

      let collection = []
      for (let i = 0; i < this.co2Readings.length; i++) {
        collection.push([i, this.co2Readings[i].value])
      }
      return { points: collection, color: 'blue', 'legend': 'readings' }
    },

    readingsMax() {
      let maximum = -100000000

      for (let i = 0; i < this.co2Projection.points.length; i++) {
        if (this.co2Projection.points[i][1] > maximum) {
          maximum = this.co2Projection.points[i][1]
        }
      }

      return maximum
    },
    generationRate() {
      return computeCO2EmissionRate(this.activityGroups) * 1000 * 3600
    },
    ventilationCadr() {
      return this.ventilationAch * this.roomUsableVolumeCubicMeters
    },
    initialCarbonDioxideReading() {
      if (!parseInt(this.initialCo2)) {
        return this.ventilationCo2SteadyStatePpm
      } else {
        return this.initialCo2
      }
    },
    co2Projection() {
      let windowLength = 0

      let producerArgs = {
        roomUsableVolumeCubicMeters: this.roomUsableVolumeCubicMeters,
        cadr: this.ventilationCadr,
        c0: this.initialCarbonDioxideReading,
        generationRate: this.generationRate,
        cBackground: this.ventilationCo2AmbientPpm,
        windowLength: 120
      }

      let projection = genConcCurve(producerArgs)
      if (!projection[0]) {
        projection = []
      }

      let collection = []
      for (let i = 0; i < projection.length; i++) {
        collection.push([i, projection[i]])
      }
      return { points: collection, color: 'red', legend: 'estimate' }
    },
    marginalRiskLine() {
      // Assumes that the presence of an infector is probabilistic
      let loop = this.selectedIntervention.computeRisk(
          40, this.numInfectors, true
      )

      let collection = []
      for (let i = 1; i <= loop.length; i++) {
        collection.push([i, loop[i] * this.probabilityOneInfectorIsPresent])
      }

      return { 'color': 'red', points: collection, 'legend': 'marginal'}
    },
    conditionalRiskLine() {
      // Assumes the presence of an infector
      let loop = this.selectedIntervention.computeRisk(
          40, this.numInfectors, true
      )

      let collection = []
      for (let i = 1; i <= loop.length; i++) {
        collection.push([i, loop[i]])
      }

      return { 'color': 'blue', points: collection, 'legend': 'conditional on 1 infector'}
    },
    cellCSSMerged() {
      let def = {
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'display': 'inline-block',
        'padding': '1em'
      }

      return Object.assign(def, this.cellCSS)
    },
    cellCSS() {
      return {
        'padding-top': '1em',
        'padding-bottom': '1em',
      }
    },
    airCleanerInstances() {
      let collection = []
      for (let a of airCleaners) {
        collection.push(new AirCleaner(a, this.event))
      }

      return collection
    },
    maskInstances() {
      let collection = []
      for (let m of MASKS) {
        collection.push(new Mask(m, this.maximumOccupancy))
      }

      return collection
    },
    interventions() {
      return getSampleInterventions(this.event, this.numPeopleToInvestIn)
    },
    datetimeInWords() {
      return datetimeEnglish(this.startDatetime)
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
    maskingBarChart() {
      return new MaskingBarChart(this.activityGroups)
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
    riskiestMask() {
      return findRiskiestMask(this.activityGroups)
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
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': 'None'
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      // 1 infector
      const occupancy = 1
      const probaRandomSampleOfOneIsInfectious = 1.0

      const flowRate = this.totalFlowRateCubicMetersPerHour

      // TODO: consolidate this information in one place
      const quanta = QUANTA
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptible() {
      return round(this.maximumOccupancy * this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible, 1)
    },
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': 'None'
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      const occupancy = 1
      const flowRate = this.totalFlowRateCubicMetersPerHour + this.numSuggestedAirCleaners * this.airCleanerSuggestion.cubicMetersPerHour

      // TODO: consolidate this information in one place
      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.3
      const quanta = QUANTA
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const probaRandomSampleOfOneIsInfectious = 1.0
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleanersAndMasks() {
      const riskiestActivityGroup = {
        'numberOfPeople': 1,
        'aerosolGenerationActivity': this.riskiestPotentialInfector['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': this.riskiestPotentialInfector['carbonDioxideGenerationActivity'],
        'maskType': this.maskSuggestion['filtrationType']
      }

      if (!this.riskiestPotentialInfector['aerosolGenerationActivity'])  {
        return 0
      }

      const occupancy = 1
      const flowRate = this.totalFlowRateCubicMetersPerHour + this.numSuggestedAirCleaners * this.airCleanerSuggestion.cubicMetersPerHour

      // TODO: consolidate this information in one place
      const quanta = QUANTA
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = maskToPenetrationFactor[
        this.maskSuggestion['filtrationType']
      ]

      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const probaRandomSampleOfOneIsInfectious = 1.0
      const duration = 1 // hour

      return round(simplifiedRisk(
        [riskiestActivityGroup],
        occupancy,
        flowRate,
        quanta,
        susceptibleMaskPenentrationFactor,
        susceptibleAgeGroup,
        probaRandomSampleOfOneIsInfectious,
        duration
      ), 6)
    },
    riskEncounteringInfectiousAllNegRapid() {
      const testSpecificity = 0.999
      const testSensitivity = 0.97

      const value =  1 - riskIndividualIsNotInfGivenNegRapidTest(
          testSpecificity,
          testSensitivity,
          this.riskOfOne
        ) ** this.maximumOccupancy
      return round(value, 6)
    },
    riskEncounteringInfectiousAllNegRapid() {
      const testSpecificity = 0.999
      const testSensitivity = 0.97

      const value =  1 - riskIndividualIsNotInfGivenNegRapidTest(
          testSpecificity,
          testSensitivity,
          this.riskOfOne
        ) ** this.maximumOccupancy
      return round(value, 6)
    },
    heatmapShowable() {
      return !!this.occupancy.parsed['Mondays']
    },
    riskOfOneRounded() {
      return round(this.riskOfOne, 6)
    },
    maxOccupancyEncounterRisk() {
      return round(riskOfEncounteringInfectious(this.riskOfOne, this.maximumOccupancy), 6)
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
    // TODO: delete this
    cutoffsVolume() {
      let factor = 500 // cubic meters per hour
      let collection = []

      if (this.measurementUnits['airDeliveryRateMeasurementType'] == 'cubic feet per minute') {
        factor = factor / 60 * 35.3147 // cubic feet per minute
      }
      for (let i = 0; i < colorSchemeFall.length; i++) {
        collection.push(
          {
            'lowerBound': (i) * factor,
            'upperBound': (i + 1) * factor,
          }
        )
      }

      return collection
    },
    colorInterpolationSchemeRoomVolume() {
      return assignBoundsToColorScheme(colorSchemeFall, this.cutoffsVolume)
    },
    numSuggestedAirCleaners() {
      return computeAmountOfPortableAirCleanersThatCanFit(
        this.roomLengthMeters * this.roomWidthMeters,
        this.airCleanerSuggestion.areaInSquareMeters
      )
    },
    maskSuggestion() {
      return MASKS[0]
    },
    roomUsableVolume() {
      const profileStore = useProfileStore()

      return convertVolume(
        this.roomUsableVolumeCubicMeters,
        'meters',
        profileStore.measurementUnits.lengthMeasurementType
      )
    },
    totalFlowRateCubicMetersPerHour() {
      return this.roomUsableVolumeCubicMeters * this.totalAch
    },
    totalFlowRate() {
      return displayCADR(this.systemOfMeasurement, this.totalFlowRateCubicMetersPerHour)
    },
    airCleanerSuggestion() {
      return airCleaners.find((ac) => ac.singular == 'CR box (Max Speed)')
    },
    portableAchRounded() {
      return round(this.portableAch, 1)
    },
    totalAchRounded() {
      return round(this.totalAch, 1)
    },
    ventilationAchRounded() {
      return round(this.ventilationAch, 1)
    },
  },
  async created() {
    this.event = await this.showAnalysis(this.$route.params.id)

    this.processQuery(this.$route.query, {})


    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        this.processQuery(toQuery, previousQuery)
        // react to route changes...
      }
    )

  },
  mounted() {
  },
  data() {
    return {
      event: {
        activityGroups: [],
        portableAirCleaners: [],
        totalAch: 0.1,
        roomUsableVolumeCubicMeters: 1,
      },
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
      tableColoredCellWithHorizPadding: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding': '0.5em',
      },
      tableColoredCell: {
        'color': 'white',
        'font-weight': 'bold',
        'text-shadow': '1px 1px 2px black',
        'padding-top': '0.5em',
        'padding-bottom': '0.5em',
      },
      infectorActivities: infectorActivityTypes,
      inlineCellCSS: {
        'display': 'inline-block',
        'font-weight': 'bold',
        'color': 'white',
        'text-shadow': '1px 1px 2px black',
        'padding': '1em',
        'margin': '0.5em',
      },
      susceptibleBreathingActivityFactorMappings: susceptibleBreathingActivityToFactor
    }
  },
  methods: {
    ...mapActions(
        useAnalyticsStore,
        [
          'setNumPeopleToInvestIn',
          'setInfectorGroups',
          'showAnalysis',
          'selectAirCleaner',
          'selectSusceptibleMask',
          'selectInfectorMask',
          'selectInterventionType',
          'selectRemoveSourceTab',
          'setNumPACs',
          'setDuration',
          'setNumInfectors',
          'setNumSusceptibles'
        ]
    ),
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    processQuery(toQuery, fromQuery) {
      if (this.$route.name == 'Analytics') {
        this.selectSusceptibleMask(toQuery['susceptibleMask'])
        this.selectInfectorMask(toQuery['infectorMask'])
        this.setNumInfectors(toQuery['numInfectors'])
        this.setNumPACs(toQuery['numPACs'])
        this.selectAirCleaner(toQuery['pacName'])
        this.setDuration(toQuery['duration'])
        this.setInfectorGroups(toQuery)
        this.setPrevalence(toQuery)
      }
    },
    scrollFix(event, hashbang) {
      let element_to_scroll_to = document.getElementById(hashbang);
      element_to_scroll_to.scrollIntoView();
    },
    setPrevalence(toQuery) {
      if (toQuery['prevalenceDenominator']) {
        this.priorProbabilityOfInfectiousness = 1 / toQuery['prevalenceDenominator']
      }
    },

    point(event) {
      this.selectedHour = round(event[0] / 60, 2)
    },
    aerosolActivityToFactor(key) {
      return infectorActivityTypes[key]
    },
    reduceRisk(before, after) {
      return reducedRisk(before, after)
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
    roundOutRisk(riskA, riskB) {
      return `${round(reducedRisk(riskA, riskB) * 100, 4)}%`
    },
    setNumPeople(event) {
      this.setNumPeopleToInvestIn(parseInt(event.target.value))
    },
    computeTotalFlowRateCubicMetersPerHour(totalACH) {
      return this.roomUsableVolumeCubicMeters * totalACH
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

  .hide-horizontal-border {
    border: 0;
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
    margin: 0 auto;
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

  .controls {
    border-right: 1px solid grey;
    position: sticky;
    height: 92vh;
    top: 3.2em;
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
    grid-template-columns: 40vw 60vw;
  }

  .column-controls {
    display: none;
  }

  .second-column {
    display: flex;
    flex-direction: row
  }

  @media (max-width: 1400px) {
    .grid {
      grid-template-columns: 40vw 60vw;
    }

    .third-col {
      display:
    }

    .column-controls {
      display: block;
    }

    .second-column {
      flex-direction: column;
    }
  }

  @media (max-width: 1000px) {
    .grid {
      grid-template-columns: 100vw;
    }

    .column-controls {
      display: block;
    }

    .controls {
      position: static;
      height: auto;
      border-right: 0;
    }
  }

  @media (max-width: 750px) {
    .grid {
      grid-template-columns: 100vw;
    }

    .column-controls {
      display: block;
    }

    .masking-table, .equations {
      font-size: 0.5em;
    }

    .masking-table text {
      font-size: 1em;
    }

    .controls {
      position: static;
      height: auto;
      border-right: 0;
    }
  }

  .item-span-wide {
    grid-column-start: 1;
    grid-column-end: 3;
    grid-row-start: auto;
    grid-row-end: auto;
  }

  .sticky {
    position: sticky;
    top: 3.2em;
    height: 80vh;
  }

  .scrollableY {
  }

  .equations {
    font-style: italic;
  }

  .stuff td {
    text-align: center;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .menu {
    background-color: transparent;
  }
</style>

