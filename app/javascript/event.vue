<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Add Event</h2>
    </div>
    <div class='container'>
      <label>Google Search</label>
      <GMapAutocomplete
           placeholder="This is a placeholder"
           @place_changed="setPlace"
          style='width: 15vw;'
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
        v-model="startDateTime"
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
      <select :value='eventPrivacy' @change='setEventPrivacy'>
        <option>public</option>
        <option>private</option>
      </select>
    </div>


    <div class='container'>
      <label class='subsection'>Room Dimensions</label>
      <div class='container'>
        <label>Length ({{ lengthMeasurementType }})</label>
        <input
          :value="roomLength"
          @change="setRoomLength">
      </div>

      <div class='container'>
        <label>Width ({{ lengthMeasurementType }})</label>
        <input
          :value="roomWidth"
          @change="setRoomWidth">
      </div>

      <div class='container'>
        <label>Height ({{ lengthMeasurementType }})</label>
        <input
          :value="roomHeight"
          @change="setRoomHeight">
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Portable Air Cleaning</label>
      <button @click='addPortableAirCleaner'>+</button>
      <div class='container border-showing' v-for='portableAirCleaner in portableAirCleaners' :key=portableAirCleaner.id>
        <div class='container'>
          <label>Air delivery rate ({{ airDeliveryRateMeasurementType }})</label>
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

        <select :value='carbonDioxideMeasurementDeviceName' @change='setCarbonDioxideMonitor'>
          <option v-for='carbonDioxideMonitor in carbonDioxideMonitors'>{{ carbonDioxideMonitor['name'] }}</option>
        </select>
      </div>

      <div class='container'>
        <label>CO2 Ambient (parts per million)</label>
        <input
          :value="carbonDioxideAmbient"
          @change="setCarbonDioxideAmbient">
      </div>

      <div class='container'>
        <label>CO2 Steady State (parts per million)</label>
        <input
          :value="carbonDioxideSteadyState"
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

    <div class='container centered'>
      <button class='normal-padded' @click='cancel'>Cancel</button>
      <button class='normal-padded' @click='save'>Save</button>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia';
import { cubicFeetPerMinuteTocubicMetersPerHour, feetToMeters } from  './misc';

export default {
  name: 'App',
  components: {
    Event
  },
  computed: {
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
        ]
    ),
    ...mapWritableState(
        useEventStore,
        [
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'carbonDioxideAmbient',
          'carbonDioxideMeasurementDeviceModel',
          'carbonDioxideMeasurementDeviceName',
          'carbonDioxideMeasurementDeviceSerial',
          'carbonDioxideSteadyState',
          'duration',
          'eventPrivacy',
          'formattedAddress',
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
          'startDateTime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes'
        ]
    ),
  },
  created() { },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab']),
    ...mapActions(useEventStores, ['addEvent']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),
    addActivityGrouping() {
      this.activityGroups.unshift({
        'id': this.generateUUID(),
        'aerosolGenerationActivity': "",
        'carbonDioxideGenerationActivity': "",
        'ageGroup': "",
        'maskType': "",
        'numberOfPeople': "",
        'rapidTestResult': 'Unknown'
      })
    },
    cancel() {
      this.focusTab = 'events'
    },
    async save() {
      let toSave = {
          'activityGroups': this.activityGroups,
          'airDeliveryRateMeasurementType': this.airDeliveryRateMeasurementType,
          'carbonDioxideAmbient': this.carbonDioxideAmbient,
          'carbonDioxideMeasurementDeviceName': this.carbonDioxideMeasurementDeviceName,
          'carbonDioxideMeasurementDeviceModel': this.carbonDioxideMeasurementDeviceModel,
          'carbonDioxideMeasurementDeviceSerial': this.carbonDioxideMeasurementDeviceSerial,
          'carbonDioxideSteadyState': this.carbonDioxideSteadyState,
          'startDateTime': this.startDateTime,
          'duration': this.duration,
          'eventPrivacy': this.eventPrivacy,
          'lengthMeasurementType': this.lengthMeasurementType,
          'placeData': this.placeData,
          'portableAirCleaners': this.portableAirCleaners, // TODO: each one should have an air delivery rate in cubic meters per hour
          'rapidTestResult': this.rapidTestResult,
          'roomWidthMeters': this.roomWidthMeters,
          'roomHeightMeters': this.roomHeightMeters,
          'roomLengthMeters': this.roomLengthMeters,
          'roomName': this.roomName,
          'roomWidth': this.roomWidth,
      }

      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'
      await axios.post('/events', toSave)
        .then(response => {
          console.log(response)
          if (response.status == 204 || response.status == 200) {
            this.events.unshift(event);
            this.addEvent(toSave)
            this.focusTab = 'events'
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          // whatever you want
        })

    },
    generateUUID() {
        // https://stackoverflow.com/questions/105034/how-to-create-guid-uuid
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
          (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
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
        'placeId': place.place_id,
        'formattedAddress': place.formatted_address,
        'center': {
          'lat': loc.lat(),
          'lng': loc.lng()
        }
      }

      this.setGMapsPlace(this.placeData.center)
    },
    setDuration(event) {
      this.duration = event.target.value;
    },
    setEventPrivacy(event) {
      this.eventPrivacy = event.target.value;
    },
    setRoomName(event) {
      this.roomName = event.target.value;
    },
    setRoomLength(event) {
      this.roomLength = event.target.value;
      this.roomLengthMeters = feetToMeters(this.lengthMeasurementType, event.target.value)
    },
    setRoomWidth(event) {
      this.roomWidth = event.target.value;
      this.roomWidthMeters = feetToMeters(this.lengthMeasurementType, event.target.value)
    },
    setRoomHeight(event) {
      this.roomHeight = event.target.value;
      this.roomHeightMeters = feetToMeters(this.lengthMeasurementType, event.target.value)
    },
    setSinglePassFiltrationEfficiency(event) {
      this.singlePassFiltrationEfficiency = event.target.value;
    },
    setCarbonDioxideAmbient(event) {
      this.carbonDioxideAmbient = event.target.value;
    },
    setCarbonDioxideMonitor(event) {
      let val = event.target.value;
      this.carbonDioxideMeasurementDeviceName = val

      let found = this.carbonDioxideMonitors.find((m) => m.name == val)
      this.carbonDioxideMeasurementDeviceSerial = found.serial
      this.carbonDioxideMeasurementDeviceModel = found.model
    },
    setCarbonDioxideSteadyState(event) {
      this.carbonDioxideSteadyState = event.target.value;
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
</style>
