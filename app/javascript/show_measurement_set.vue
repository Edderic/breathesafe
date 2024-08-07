<template>
  <div class='wide border-showing scrollable'>

    <div class='container'>
      <label>Make this information private</label>
      <select :value='private' disabled>
        <option>public</option>
        <option>private</option>
      </select>
    </div>

    <div class='container'>
      <label class='subsection'>Occupancy</label>

      <div class='container'>
        <label class='textarea-label'>Max occupancy</label>
        <input
          disabled
          :value="maximumOccupancy"
        >
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Room Dimensions</label>
      <div class='container'>
        <label>Length ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomLength"
          disabled
        >
      </div>

      <div class='container'>
        <label>Width ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomWidth"
          disabled
        >
      </div>

      <div class='container'>
        <label>Height ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomHeight"
          disabled
        >
      </div>

      <div class='container'>
        <label>Usable Volume Factor (dimension-less)</label>
        <input
          v-model="roomUsableVolumeFactor"
          disabled
        >
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Portable Air Cleaning</label>
      <div class='container border-showing' v-for='portableAirCleaner in portableAirCleaners' :key=portableAirCleaner.id>
        <div class='container'>
          <label>Air delivery rate ({{ measurementUnits.airDeliveryRateMeasurementType }})</label>
          <input
            :value="airDeliveryRate(portableAirCleaner['airDeliveryRateCubicMetersPerHour'])"
            disabled>
        </div>

        <div class='container'>
          <label>Single-pass filtration efficiency (dimensionless)</label>
          <input
            :value="portableAirCleaner['singlePassFiltrationEfficiency']"
            disabled>
        </div>

        <div class='container wide'>
          <label class='textarea-label'>Notes</label>
          <textarea disabled type="textarea" rows=5 columns=80  @change='setPortableAirCleaningNotes($event, portableAirCleaner.id)'>{{ portableAirCleaner['notes'] }}</textarea>
        </div>
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Ventilation</label>
      <div class='container'>
        <label>CO2 Measurement Device</label>

        <input :value='ventilationCo2MeasurementDeviceName' disabled>
      </div>

      <div class='container'>
        <label>CO2 Ambient (parts per million)</label>
        <input
          :value="ventilationCo2AmbientPpm"
          disabled>
      </div>

      <div class='container'>
        <label>CO2 Steady State (parts per million)</label>
        <input
          :value="ventilationCo2SteadyStatePpm"
          disabled>
      </div>

      <div class='container wide'>
        <label class='textarea-label'>Notes</label>
        <textarea disabled type="textarea" rows=5 columns=80>{{ ventilationNotes }}</textarea>
      </div>
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
  generateUUID,
  setupCSRF
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
          'singlePassFiltrationEfficiency',
          'startDatetime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes'
        ]
    ),
    ...mapWritableState(
        useEventStores,
        [
          'events'
        ]
    ),

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
        'id': generateUUID(),
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
  }

  .scrollable {
    overflow-y: scroll;
    height: 72em;
  }
</style>
