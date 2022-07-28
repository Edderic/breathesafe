<template>
  <div class='col border-showing scrollable'>
    <div class='container'>
      <label class='subsection'>Occupancy</label>

      <div class='container'>
        <label class='textarea-label'>Max occupancy</label>
        <input
          disabled
          :value="maximumOccupancy"
        >
      </div>

      <div class='container wide'>
        <label class='textarea-label'>Parsed</label>
        <DayHourHeatmap
          :dayHours="occupancy.parsed"
        />
      </div>

    </div>

    <div class='centered'>
      <table>
        <tr>
          <th>Total ACH</th>
          <th></th>
          <th>Ventilation ACH</th>
          <th></th>
          <th>Portable ACH</th>
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

    <div class='centered'>
      <table>
        <tr>
          <th>Total Flow Rate</th>
          <th></th>
          <th>Usable Room Volume</th>
          <th></th>
          <th>Total ACH</th>
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
        </tr>
      </table>
    </div>

    <div class='container'>
      <label class='subsection'>Activity Groups</label>
      <div class='container border-showing' v-for='activityGroup in activityGroups' :key=activityGroup.id>

        <div class='container'>
          <label>Number of people</label>
          <input
            :value="activityGroup['numberOfPeople']"
            disabled>
        </div>

        <div class='container'>
          <label>Sex</label>
          <select :value='activityGroup["sex"]' disabled>
            <option>Male</option>
            <option>Female</option>
          </select>
        </div>

        <div class='container'>
          <label>Aerosol generation</label>
          <select :value='activityGroup["aerosolGenerationActivity"]' disabled>
            <option v-for='(value, infectorActivityType, index) in infectorActivityTypeMapping'>{{ infectorActivityType }}</option>
          </select>
        </div>

        <div class='container'>
          <label>CO2 generation</label>
          <select :value='activityGroup["carbonDioxideGenerationActivity"]' disabled>
            <option v-for='(value, carbonDioxideActivity, index) in carbonDioxideActivities'>{{ carbonDioxideActivity }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Age group</label>
          <select :value='activityGroup["ageGroup"]' disabled>
            <option v-for='s in ageGroups'>{{ s }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Mask Type</label>
          <select :value='activityGroup["maskType"]' disabled>
            <option v-for='m in maskTypes'>{{ m }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Rapid test results</label>
          <select :value='activityGroup["rapidTestResult"]' disabled>
            <option v-for='r in rapidTestResults'>{{ r }}</option>
          </select>
        </div>
      </div>
    </div>


    <div class='container centered'>
      <button disabled class='normal-padded' @click='cancel'>Cancel</button>
      <button disabled class='normal-padded' @click='save'>Save</button>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import DayHourHeatmap from './day_hour_heatmap.vue';
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  computePortableACH,
  computeVentilationACH,
  convertCubicMetersPerHour,
  convertLengthBasedOnMeasurementType,
  cubicFeetPerMinuteTocubicMetersPerHour,
  setupCSRF,
  round
} from  './misc';

export default {
  name: 'App',
  components: {
    ColoredCell,
    DayHourHeatmap,
    Event
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
        useProfileStore,
        [
          'lengthMeasurementType',
          'airDeliveryRateMeasurementType',
          'carbonDioxideMonitors',
          'measurementUnits'
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

    colorInterpolationSchemeTotalAch() {
      return [
        {
          'lowerBound': 0,
          'upperBound': 1,
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
          'lowerBound': 1,
          'upperBound': 2,
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
          'lowerBound': 2,
          'upperBound': 4,
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
          'lowerBound': 4,
          'upperBound': 8,
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
          'lowerBound': 8,
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
    colorInterpolationSchemeRoomVolume() {
      return [
        {
          'lowerBound': 0,
          'upperBound': 198,
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
          'lowerBound': 198,
          'upperBound': 396,
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
          'lowerBound': 396,
          'upperBound': 594,
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
          'lowerBound': 594,
          'upperBound': 792,
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
          'lowerBound': 991,
          'upperBound': 1189,
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
      return round(this.roomUsableVolumeCubicMeters, 1)
    },
    totalFlowRateRounded() {
      return round(this.roomUsableVolumeCubicMeters * this.totalAch, 1)
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
  },
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
    flex-directior: column;
  }

  .margined {
    margin: 2em;
  }

  th {
    padding: 1em;
  }
</style>