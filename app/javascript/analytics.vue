<template>
  <div class='col border-showing scrollable'>
    <div class='container'>
      <label class='subsection'>Occupancy</label>

      <div class='container'>
      <span>Assuming a COVID infectious prevalence rate of {{this.riskOfOneRounded}}, and that the room is at max occupancy ~{{maximumOccupancy}}, the probability of having at least one infector in the room is
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='maxOccupancyEncounterRisk'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          />.
      </span>
      </div>

      <div class='container col centered' v-if="heatmapShowable">
        <h4 :style="{'margin-bottom': 0}">Popular Times at {{this.roomName}}</h4>
        <DayHourHeatmap
          :dayHours="occupancy.parsed"
        />
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Rapid Testing</label>
      <div class='container'>
        <span>If, at max occupancy, everyone did rapid testing beforehand, and all got negative results, the probability that at least one person is infectious drops down to
            <ColoredCell
              :colorScheme="riskColorScheme"
              :maxVal=1
              :value='riskEncounteringInfectiousAllNegRapid'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
            />.
        </span>
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Clean Air Delivery Rate</label>
      <div class='container'>
        <span>What happens if there's an infectious individual present at max occupancy and no one is masked? How robust is the environment in preventing transmission? With a clean air delivery rate of
            <ColoredCell
            :colorScheme="colorInterpolationSchemeRoomVolume"
            :maxVal=1
            :value='totalFlowRateRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
            />
        </span> {{ this.measurementUnits.airDeliveryRateMeasurementTypeShort }}, assuming the infector is {{ this.riskiestPotentialInfector['aerosolGenerationActivity'] }}, the risk of long-range airborne transmission is
          <ColoredCell
              :colorScheme="riskColorScheme"
              :maxVal=1
              :value='riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
            />. On average,
          <ColoredCell
              :colorScheme="averageInfectedPeopleInterpolationScheme"
              :maxVal=1
              :value='averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptible'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          /> susceptibles would be infected.
     </div>
      <div class='centered'>
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
          </tr>
          <tr>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeTotalAch"
              :maxVal=1
              :value='totalAchRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
            <td>=</td>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeTotalAch"
              :maxVal=1
              :value='ventilationAchRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
            <td>+</td>
            <ColoredCell
              :colorScheme="colorInterpolationSchemeTotalAch"
              :maxVal=1
              :value='portableAchRounded'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
            />
          </tr>
        </table>
      </div>
    </div>

    <div class='centered'>
      <table>
        <tr>
          <th class='col centered'>
            <span>Clean Air Delivery Rate</span>
            <span class='font-light'>({{this.measurementUnits.airDeliveryRateMeasurementTypeShort}})</span>
          </th>
          <th></th>
          <th class='col centered'>
            <span>Unoccupied Room Volume</span>
            <span class='font-light'>({{this.measurementUnits.cubicLengthShort}})</span>
          </th>
          <th></th>
          <th class='col centered'>
            <span>Total ACH</span>
            <span class='font-light'>(1 / h)</span>
          </th>
          <th v-if="systemOfMeasurement == 'imperial'"></th>
          <th class='col centered' v-if="systemOfMeasurement == 'imperial'">
            <span></span>
            <span class='font-light'>(min / h)</span>
          </th>
        </tr>
        <tr>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeRoomVolume"
            :maxVal=1
            :value='totalFlowRateRounded'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
          />
          <td>=</td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeRoomVolume"
            :maxVal=1
            :value='roomUsableVolumeRounded'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
          />
          <td>x</td>
          <ColoredCell
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='totalAchRounded'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em' }"
          />
          <td v-if="systemOfMeasurement == 'imperial'">/</td>
          <ColoredCell
            v-if="systemOfMeasurement == 'imperial'"
            :colorScheme="colorInterpolationSchemeTotalAch"
            :maxVal=1
            :value='60'
            :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '2em', 'background-color': 'grey'}"
          />
        </tr>
      </table>
    </div>

    <div class='container'>
      <div class='container'>
        <span>Adding {{ this.numSuggestedAirCleaners }} {{ this.airCleanerSuggestion.plural }} would improve the clean air delivery rate (CADR)</span> to

        <ColoredCell
        :colorScheme="colorInterpolationSchemeRoomVolume"
        :maxVal=1
        :value='totalFlowRatePlusExtraPacRounded'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
        />
  {{ this.measurementUnits.airDeliveryRateMeasurementTypeShort }}, bringing down the long-range airborne transmission risk to
         <ColoredCell
              :colorScheme="riskColorScheme"
              :maxVal=1
              :value='riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          />. On average,
          <ColoredCell
              :colorScheme="averageInfectedPeopleInterpolationScheme"
              :maxVal=1
              :value='averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'padding': '1em', 'margin': '0.5em', 'display': 'inline-block' }"
          /> susceptibles would be infected. Initial cost of adding {{ this.numSuggestedAirCleaners }} {{ this.airCleanerSuggestion.plural }} is ${{ this.airCleanerSuggestion.initialCostDollars * this.numSuggestedAirCleaners}}, with a recurring cost of ${{ this.airCleanerSuggestion.recurringCost * this.numSuggestedAirCleaners }} every {{this.airCleanerSuggestion.recurringCostDuration}}.
       </div>
     </div>
    <div class='container'>
      <label class='subsection'>Masking</label>
      <div class='centered'>
        <HorizontalStackedBar
          :values="maskingValues"
          :colors="maskingColors"
        />
      </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import { airCleaners } from './air_cleaners.js';
import BarGraph from './bar_graph.vue';
import { colorSchemeFall, assignBoundsToColorScheme, riskColorInterpolationScheme, infectedPeopleColorBounds } from './colors.js';
import { findRiskiestPotentialInfector, riskOfEncounteringInfectious, riskIndividualIsNotInfGivenNegRapidTest } from './risk.js';
import { convertVolume, computeAmountOfPortableAirCleanersThatCanFit } from './measurement_units.js';
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  displayCADR,
  findWorstCaseInhFactor,
  maskToPenetrationFactor,
  setupCSRF,
  simplifiedRisk,
  round,

} from  './misc';

export default {
  name: 'App',
  components: {
    BarGraph,
    ColoredCell,
    DayHourHeatmap,
    Event,
    HorizontalStackedBar
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
        useShowMeasurementSetStore,
        [
          'roomName',
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'ventilationCo2AmbientPpm',
          'ventilationCo2MeasurementDeviceModel',
          'ventilationCo2MeasurementDeviceName',
          'ventilationCo2MeasurementDeviceSerial',
          'ventilationCo2SteadyStatePpm',
          'duration',
          'private',
          'formatted_address',
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
    ...mapWritableState(
        useEventStores,
        [
          'events'
        ]
    ),
    maskingValues() {
      let key;
      let color;

      let dict = {}
      for (let p in maskToPenetrationFactor) {
        dict[p] = 0
      }

      for (let ag of this.activityGroups) {
        dict[ag.maskType] += parseFloat(ag.numberOfPeople)
      }

      return dict
    },
    maskingColors() {
      let index = 0
      let key = 'lowerColor'
      let colors = []
      let color;

      for (let colorPair of colorSchemeFall) {
        color = colorPair[key]

        colors.push(
          `rgb(${color.r}, ${color.g}, ${color.b})`
        )
      }


      color = colorSchemeFall[index]['upperColor']
      colors.push(`rgb(${color.r}, ${color.g}, ${color.b})`)

      return colors
    },
    riskiestPotentialInfector() {
      return findRiskiestPotentialInfector(this.activityGroups)
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

      const occupancy = 1
      const flowRate = this.totalFlowRateCubicMetersPerHour

      // TODO: consolidate this information in one place
      const basicInfectionQuanta = 18.6
      const variantMultiplier = 3.3
      const quanta = basicInfectionQuanta * variantMultiplier
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const infectorSpecificTerm = 1.0
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
    averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptible() {
      return round(this.maximumOccupancy * this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptible, 1)
    },
    averageTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners() {
      return round(this.maximumOccupancy * this.riskTransmissionOfUnmaskedInfectorToUnmaskedSusceptibleWithSuggestedAirCleaners, 1)
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
      const quanta = basicInfectionQuanta * variantMultiplier
      const susceptibleAgeGroup = '30 to <40'
      const susceptibleMaskPenentrationFactor = 1
      const susceptibleInhalationFactor = findWorstCaseInhFactor(
        this.activityGroups,
        susceptibleAgeGroup
      )
      const infectorSpecificTerm = 1.0
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
    averageInfectedPeopleInterpolationScheme() {
      const copy = JSON.parse(JSON.stringify(riskColorInterpolationScheme))
      return assignBoundsToColorScheme(copy, infectedPeopleColorBounds)
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
    roomLength() {
      const profileStore = useProfileStore()
      return convertLengthBasedOnMeasurementType(
        this.roomLengthMeters,
        'meters',
        profileStore.measurementUnits.lengthMeasurementType
      )
    },
    roomWidth() {
      const profileStore = useProfileStore()

      return convertLengthBasedOnMeasurementType(
        this.roomWidthMeters,
        'meters',
        profileStore.measurementUnits.lengthMeasurementType
      )
    },
    roomHeight() {
      const profileStore = useProfileStore()

      return convertLengthBasedOnMeasurementType(
        this.roomHeightMeters,
        'meters',
        profileStore.measurementUnits.lengthMeasurementType
      )
    },
    roomUsableVolumeRounded() {

      const profileStore = useProfileStore()
      return round(
        convertVolume(
          this.roomUsableVolumeCubicMeters,
          'meters',
          profileStore.measurementUnits.lengthMeasurementType
        ),
        1
      )
    },
    totalFlowRateCubicMetersPerHour() {
      return this.roomUsableVolumeCubicMeters * this.totalAch
    },
    totalFlowRate() {
      return displayCADR(this.systemOfMeasurement, this.totalFlowRateCubicMetersPerHour)
    },
    totalFlowRateRounded() {
      return round(this.totalFlowRate, 1)
    },
    airCleanerSuggestion() {
      return airCleaners.find((ac) => ac.singular == 'Corsi-Rosenthal box')
    },
    totalFlowRatePlusExtraPacRounded() {
      // TODO: could pull from risk.js airCleaners instead

      const newCADRcubicMetersPerHour = this.totalFlowRateCubicMetersPerHour + this.airCleanerSuggestion.cubicMetersPerHour * this.numSuggestedAirCleaners

      return round(displayCADR(this.systemOfMeasurement, newCADRcubicMetersPerHour), 1)
    },
    portableAchRounded() {
      return round(this.portableAch, 1)
    },
    totalAchRounded() {
      return round(this.totalAch, 1)
    },
    ventilationAchRounded() {
      return round(this.ventilationAch, 1)
    }
  },
  async created() {
  },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    ...mapState(useProfileStore, ['measurementUnits']),
    addActivityGrouping() {
      this.activityGroups.unshift({
        'id': this.generateUUID(),
        'aerosolGenerationActivity': "",
        'carbonDioxideGenerationActivity': "",
        'ageGroup': "",
        'sex': "",
        'maskType': "",
        'numberOfPeople': "",
        'rapidTestResult': 'Unknown'
      })
    },
    cancel() {
      this.focusTab = 'events'
    },
    parseOccupancyData(event) {
      this.occupancy.unparsedOccupancyData = event.target.value
      this.occupancy.parsed = parseOccupancyHTML(this.occupancy)
    },
    airDeliveryRate(num) {
      return convertCubicMetersPerHour(
        num,
        this.measurementUnits.airDeliveryRateMeasurementType
      )
    },
    generateUUID() {
        // https://stackoverflow.com/questions/105034/how-to-create-guid-uuid
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
          (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    },
    setSex(event, id) {
      let activityGroup = this.findActivityGroup()(id)
      activityGroup['sex'] = event.target.value
    },
    cloneActivityGroup(id) {
      const activityGroup = this.activityGroups.find(
        (activityGroup) => activityGroup.id == id
      );

      this.activityGroups.push({
        'id': this.generateUUID(),
        'aerosolGenerationActivity': activityGroup['aerosolGenerationActivity'],
        'carbonDioxideGenerationActivity': activityGroup['carbonDioxideGenerationActivity'],
        'ageGroup': activityGroup['ageGroup'],
        'maskType': activityGroup['maskType'],
        'sex': activityGroup['sex'],
        'numberOfPeople': activityGroup['numberOfPeople'],
        'rapidTestResult': activityGroup['rapidTestResult']
      });
    },
    removeActivityGroup(id) {
      const activityGroupIndex = this.activityGroups.findIndex(
        (activityGroup) => activityGroup.id == id
      );

      this.activityGroups.splice(activityGroupIndex, 1);
    },
    removeAirCleaner(id) {
      const index = this.portableAirCleaners.findIndex(
        (airCleaner) => airCleaner.id == id
      );

      this.portableAirCleaners.splice(index, 1);
    },
    setPlace(place) {
      console.log(place)
      const loc = place.geometry.location;

      this.placeData = {
        'place_id': place.place_id,
        'formatted_address': place.formatted_address,
        'center': {
          'lat': loc.lat(),
          'lng': loc.lng()
        },
        'types': place.types,
        'website': place.website,
        'opening_hours': place.opening_hours,
      }

      this.setGMapsPlace(this.placeData.center)
    },
    setDuration(event) {
      this.duration = event.target.value;
    },
    setEventPrivacy(event) {
      this.private = event.target.value;
    },
    setRoomName(event) {
      this.roomName = event.target.value;
    },
    setSinglePassFiltrationEfficiency(event) {
      this.singlePassFiltrationEfficiency = event.target.value;
    },
    setCarbonDioxideAmbient(event) {
      this.ventilationCo2AmbientPpm = event.target.value;
    },
    setCarbonDioxideMonitor(event) {
      let val = event.target.value;
      this.ventilationCo2MeasurementDeviceName = val

      let found = this.carbonDioxideMonitors.find((m) => m.name == val)
      this.ventilationCo2MeasurementDeviceSerial = found.serial
      this.ventilationCo2MeasurementDeviceModel = found.model
    },
    setCarbonDioxideSteadyState(event) {
      this.ventilationCo2SteadyStatePpm = event.target.value;
    },
    setAerosolGenerationActivity(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['aerosolGenerationActivity'] = event.target.value;
    },
    setCarbonDioxideGenerationActivity(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['carbonDioxideGenerationActivity'] = event.target.value;
    },
    setAgeGroup(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['ageGroup'] = event.target.value;
    },
    setMaskType(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['maskType'] = event.target.value;
    },
    setNumberOfPeople(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['numberOfPeople'] = event.target.value;
    },
    setPortableAirCleaningNotes(event, id) {
      let portableAirCleaner = this.findPortableAirCleaningDevice()(id);
      portableAirCleaner['notes'] = event.target.value;
    },

    setVentilationNotes(event) {
      this.ventilationNotes = event.target.value;
    },

    setRapidTestResult(event, id) {
      let activityGroup = this.findActivityGroup()(id);
      activityGroup['rapidTestResult'] = event.target.value;
    },
    setPortableAirCleaningDeviceAirDeliveryRate(event, id) {
      let portableAirCleaner = this.findPortableAirCleaningDevice()(id);
      portableAirCleaner['airDeliveryRate'] = event.target.value;
      portableAirCleaner['airDeliveryRateCubicMetersPerHour'] = cubicFeetPerMinuteTocubicMetersPerHour(
        this.airDeliveryRateMeasurementType,
        event.target.value
      );
    },
    setPortableAirCleaningDeviceSinglePassFiltrationEfficiency(event, id) {
      let portableAirCleaner = this.findPortableAirCleaningDevice()(id);
      portableAirCleaner['singlePassFiltrationEfficiency'] = event.target.value;
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
    font-weight: bold;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  .row {
    display: flex;
    flex-direction: column;
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
    justify-content: center;
    align-items: center;
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

  .col {
    display: flex;
    flex-direction: column;
  }

  .margined {
    margin: 2em;
  }

  th {
    padding: 1em;
  }

  .font-light {
    font-weight: 400;
  }
</style>
