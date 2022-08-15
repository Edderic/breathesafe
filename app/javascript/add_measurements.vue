<template>
  <div class='border-showing'>
    <div class='container centered'>
      <h2>Add Measurements</h2>
    </div>
    <div class='container'>
      <label>Google Search</label>
      <GMapAutocomplete
           placeholder="This is a placeholder"
           @place_changed="setPlace"
          style='width: 20em;'
        >
      </GMapAutocomplete>
    </div>

    <div class='container'>
      <label>Room name</label>
      <input
        :value="roomName"
        @change="setRoomName">
    </div>

    <div class='container'>
      <label>Start time</label>
      <input class='wider-input'
        v-model="startDatetime"
      >
    </div>

    <div class='container'>
      <label>Duration</label>

      <select :value='duration' @change='setDuration'>
        <option>1 minute</option>
        <option>5 minutes</option>
        <option>10 minutes</option>
        <option>15 minutes</option>
        <option>30 minutes</option>
        <option>45 minutes</option>
        <option>1 hour</option>
        <option>1.25 hours</option>
        <option>1.5 hours</option>
        <option>2 hours</option>
        <option>3 hours</option>
        <option>4 hours</option>
        <option>5 hours</option>
        <option>6 hours</option>
        <option>7 hours</option>
        <option>8 hours</option>
      </select>
    </div>

    <div class='container'>
      <label>Make this information private</label>
      <select :value='private' @change='setEventPrivacy'>
        <option>public</option>
        <option>private</option>
      </select>
    </div>


    <div class='container'>
      <label class='subsection'>Room Dimensions</label>
      <div class='container'>
        <label>Length ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomLength"
          @change="setRoomLength">
      </div>

      <div class='container'>
        <label>Width ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomWidth"
          @change="setRoomWidth">
      </div>

      <div class='container'>
        <label>Height ({{ measurementUnits.lengthMeasurementType }})</label>
        <input
          :value="roomHeight"
          @change="setRoomHeight">
      </div>

      <div class='container'>
        <label>Usable Volume Factor (dimension-less)</label>
        <input
          v-model="roomUsableVolumeFactor"
        >
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Portable Air Cleaning</label>
      <button @click='addPortableAirCleaner'>+</button>
      <div class='container border-showing' v-for='portableAirCleaner in portableAirCleaners' :key=portableAirCleaner.id>
        <div class='container'>
          <label>Air delivery rate ({{ measurementUnits.airDeliveryRateMeasurementType }})</label>
          <input
            :value="portableAirCleaner['airDeliveryRate']"
            @change="setPortableAirCleaningDeviceAirDeliveryRate($event, portableAirCleaner.id)">
        </div>

        <div class='container'>
          <label>Single-pass filtration efficiency (dimensionless)</label>
          <input
            :value="portableAirCleaner['singlePassFiltrationEfficiency']"
            @change="setPortableAirCleaningDeviceSinglePassFiltrationEfficiency($event, portableAirCleaner.id)">
        </div>

        <div class='container wide'>
          <label class='textarea-label'>Notes</label>
          <textarea type="textarea" rows=5 columns=80  @change='setPortableAirCleaningNotes($event, portableAirCleaner.id)'>{{ portableAirCleaner['notes'] }}</textarea>
        </div>

        <div class='container centered'>
          <button class='normal-padded' @click='removeAirCleaner(portableAirCleaner.id)'>Remove</button>
        </div>
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Ventilation</label>
      <div class='container'>
        <label>CO2 Measurement Device</label>

        <select :value='ventilationCO2MeasurementDeviceName' @change='setCarbonDioxideMonitor'>
          <option v-for='carbonDioxideMonitor in carbonDioxideMonitors'>{{ carbonDioxideMonitor['name'] }}</option>
        </select>
      </div>

      <div class='container'>
        <label>CO2 Ambient (parts per million)</label>
        <input
          :value="ventilationCO2AmbientPPM"
          @change="setCarbonDioxideAmbient">
      </div>

      <div class='container'>
        <label>CO2 Steady State (parts per million)</label>
        <input
          :value="ventilationCO2SteadyStatePPM"
          @change="setCarbonDioxideSteadyState">
      </div>

      <div class='container wide'>
        <label class='textarea-label'>Notes</label>
        <textarea type="textarea" rows=5 columns=80  @change='setVentilationNotes'>{{ ventilationNotes }}</textarea>
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Activity Groups</label>
      <button @click='addActivityGrouping'>+</button>
      <div class='container border-showing' v-for='activityGroup in activityGroups' :key=activityGroup.id>

        <div class='container'>
          <label>Number of people</label>
          <input
            :value="activityGroup['numberOfPeople']"
            @change="setNumberOfPeople($event, activityGroup.id)">
        </div>

        <div class='container'>
          <label>Sex</label>
          <select :value='activityGroup["sex"]' @change='setSex($event, activityGroup.id)'>
            <option>Male</option>
            <option>Female</option>
          </select>
        </div>

        <div class='container'>
          <label>Aerosol generation</label>
          <select :value='activityGroup["aerosolGenerationActivity"]' @change='setAerosolGenerationActivity($event, activityGroup.id)'>
            <option v-for='(value, infectorActivityType, index) in infectorActivityTypeMapping'>{{ infectorActivityType }}</option>
          </select>
        </div>

        <div class='container'>
          <label>CO2 generation</label>
          <select :value='activityGroup["carbonDioxideGenerationActivity"]' @change='setCarbonDioxideGenerationActivity($event, activityGroup.id)'>
            <option v-for='(value, carbonDioxideActivity, index) in carbonDioxideActivities'>{{ carbonDioxideActivity }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Age group</label>
          <select :value='activityGroup["ageGroup"]' @change='setAgeGroup($event, activityGroup.id)'>
            <option v-for='s in ageGroups'>{{ s }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Mask Type</label>
          <select :value='activityGroup["maskType"]' @change='setMaskType($event, activityGroup.id)'>
            <option v-for='m in maskTypes'>{{ m }}</option>
          </select>
        </div>

        <div class='container'>
          <label>Rapid test results</label>
          <select :value='activityGroup["rapidTestResult"]' @change='setRapidTestResult($event, activityGroup.id)'>
            <option v-for='r in rapidTestResults'>{{ r }}</option>
          </select>
        </div>

        <div class='container centered'>
          <button class='normal-padded' @click='removeActivityGroup(activityGroup.id)'>Remove</button>
          <button class='normal-padded' @click='cloneActivityGroup(activityGroup.id)'>Clone</button>
        </div>
      </div>
    </div>


    <div class='container'>
      <label class='subsection'>Occupancy</label>

      <div class='container'>
        <label class='textarea-label'>Max occupancy</label>
        <input
          v-model="maximumOccupancy"
        >
      </div>

      <div class='container wide'>
        <label class='textarea-label'>Unparsed HTML</label>
        <textarea type="textarea" rows=5 columns=80  @change='parseOccupancyData'>{{ occupancy.unparsedOccupancyData }}</textarea>
      </div>

      <div class='container wide'>
        <label class='textarea-label'>Parsed</label>
        <DayHourHeatmap
          :dayHours="occupancy.parsed"
        />
      </div>

    </div>
    <div class='container centered'>
      <button class='normal-padded' @click='cancel'>Cancel</button>
      <button class='normal-padded' @click='save'>Save</button>
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
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
   setupCSRF, cubicFeetPerMinuteTocubicMetersPerHour, daysToIndexDict,
   convertLengthBasedOnMeasurementType, computeVentilationACH, computePortableACH,
   parseOccupancyHTML
} from  './misc';

export default {
  name: 'AddMeasurements',
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
          'measurementUnits',
          'carbonDioxideMonitors',
        ]
    ),
    ...mapWritableState(
        useEventStore,
        [
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'ventilationCO2AmbientPPM',
          'ventilationCO2MeasurementDeviceModel',
          'ventilationCO2MeasurementDeviceName',
          'ventilationCO2MeasurementDeviceSerial',
          'ventilationCO2SteadyStatePPM',
          'duration',
          'private',
          'formatted_address',
          'infectorActivity',
          'infectorActivityTypeMapping',
          'maskTypes',
          'numberOfPeople',
          'placeData',
          'portableAirCleaners',
          'rapidTestResult',
          'rapidTestResults',
          'roomHeight',
          'roomLength',
          'roomName',
          'roomWidth',
          'roomHeightMeters',
          'roomLengthMeters',
          'roomWidthMeters',
          'roomName',
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
  },
  async created() {
    // TODO: fire and forget. Make asynchronous.
    await this.getCurrentUser()
    await this.loadProfile()
    this.loadCO2Monitors()
  },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
      occupancy: {
        unparsedOccupancyData: "",
        parsed: {
        },
      },
      maximumOccupancy: 0,
      roomUsableVolumeFactor: 0.8
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['loadCO2Monitors', 'loadProfile']),
    ...mapActions(useEventStores, ['load']),
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
      // TODO: clear out data for Add New Event
      this.focusTab = 'maps'
    },
    parseOccupancyData(event) {
      this.occupancy.unparsedOccupancyData = event.target.value
      this.occupancy.parsed = parseOccupancyHTML(this.occupancy.unparsedOccupancyData)
    },
    async save() {
      this.roomUsableVolumeCubicMeters = parseFloat(this.roomWidthMeters)
        * parseFloat(this.roomHeightMeters)
        * parseFloat(this.roomLengthMeters)
        * parseFloat(this.roomUsableVolumeFactor)

      this.ventilationACH = computeVentilationACH(
        this.activityGroups,
        this.ventilationCO2AmbientPPM,
        this.ventilationCO2SteadyStatePPM,
        this.roomUsableVolumeCubicMeters
      )

      this.portableACH = computePortableACH(
        this.portableAirCleaners,
        this.roomUsableVolumeCubicMeters
      )

      this.totalACH = this.portableACH + this.ventilationACH

      // TODO: compute portable air cleaners ACH
      // update controller
      // update database schema

      let toSave = {
          'event': {
            'author_id': this.currentUser.id,
            'activity_groups': this.activityGroups,
            'ventilation_ach': this.ventilationACH,
            'ventilation_co2_ambient_ppm': this.ventilationCO2AmbientPPM,
            'ventilation_co2_measurement_device_name': this.ventilationCO2MeasurementDeviceName,
            'ventilation_co2_measurement_device_model': this.ventilationCO2MeasurementDeviceModel,
            'ventilation_co2_measurement_device_serial': this.ventilationCO2MeasurementDeviceSerial,
            'ventilation_co2_steady_state_ppm': this.ventilationCO2SteadyStatePPM,
            'ventilation_notes': this.ventilationNotes,
            'start_datetime': this.startDatetime,
            'duration': this.duration,
            'private': this.private,
            'place_data': this.placeData,
            'occupancy': {
              'parsed': this.occupancy.parsed,
            },
            'maximum_occupancy': this.maximumOccupancy,
            'portable_air_cleaners': this.portableAirCleaners,
            'portable_ach': this.portableACH,
            'total_ach': this.totalACH,
            'room_width_meters': this.roomWidthMeters,
            'room_height_meters': this.roomHeightMeters,
            'room_length_meters': this.roomLengthMeters,
            'room_usable_volume_cubic_meters': this.roomUsableVolumeCubicMeters,
            'room_name': this.roomName,
            'room_usable_volume_factor': this.roomUsableVolumeFactor
        }
      }

      setupCSRF()

      await axios.post('/events', toSave)
        .then(response => {
          console.log(response)
          if (response.status == 201 || response.status == 200) {
            this.load()
            this.setFocusTab('events')
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Something went wrong."
          // whatever you want
        })

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
    setRoomLength(event) {
      this.roomLength = event.target.value;
      this.roomLengthMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    setRoomWidth(event) {
      this.roomWidth = event.target.value;
      this.roomWidthMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    setRoomHeight(event) {
      this.roomHeight = event.target.value;
      this.roomHeightMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    setSinglePassFiltrationEfficiency(event) {
      this.singlePassFiltrationEfficiency = event.target.value;
    },
    setCarbonDioxideAmbient(event) {
      this.ventilationCO2AmbientPPM = event.target.value;
    },
    setCarbonDioxideMonitor(event) {
      let val = event.target.value;
      this.ventilationCO2MeasurementDeviceName = val

      let found = this.carbonDioxideMonitors.find((m) => m.name == val)
      this.ventilationCO2MeasurementDeviceSerial = found.serial
      this.ventilationCO2MeasurementDeviceModel = found.model
    },
    setCarbonDioxideSteadyState(event) {
      this.ventilationCO2SteadyStatePPM = event.target.value;
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
        this.measurementUnits.airDeliveryRateMeasurementType,
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
</style>
