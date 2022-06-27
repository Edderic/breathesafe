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
      <label>System of Measurement</label>

      <select :value='systemOfMeasurement' @change='setSystemOfMeasurement'>
        <option>imperial</option>
        <option>metric</option>
      </select>
    </div>


    <div class='container'>
      <label>Number of people</label>
      <input
        :value="numberOfPeople"
        @change="setNumberOfPeople">
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
      <div class='container'>
        <label>Air delivery rate ({{ airDeliveryRateMeasurementType }})</label>
        <input
          :value="airDeliveryRate"
          @change="setAirDeliveryRate">
      </div>

      <div class='container'>
        <label>Single-pass filtration efficiency (dimensionless)</label>
        <input
          :value="singlePassFiltrationEfficiency"
          @change="setSinglePassFiltrationEfficiency">
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Ventilation</label>
      <div class='container'>
        <label>CO2 Measurement Device</label>
        <input
          :value="carbonDioxideMeasurementDevice"
          @change="setCarbonDioxideMeasurementDevice">
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
    </div>

    <div class='container'>
      <label class='subsection'>Masking</label>
      <div class='container'>
        <label>Percent of people with no masks</label>
        <input
          :value="percentOfPeopleWithNoMasks"
          @change="setPercentOfPeopleWithNoMasks">
      </div>

      <div class='container'>
        <label>Percent of people with cloth/surgical masks</label>
        <input
          :value="percentOfPeopleWithClothSurgicalMasks"
          @change="setPercentOfPeopleWithClothSurgicalMasks">
      </div>

      <div class='container'>
        <label>Percent of people with N95s</label>
        <input
          :value="percentOfPeopleWithN95s"
          @change="setPercentOfPeopleWithN95s">
      </div>

      <div class='container'>
        <label>Percent of people with elastomerics</label>
        <input
          :value="percentOfPeopleWithElastomerics"
          @change="setPercentOfPeopleWithElastomerics">
      </div>
    </div>

    <div class='container'>
      <label class='subsection'>Activity</label>
      <div class='container'>
        <label>What best describes what others are doing?</label>
        <select :value='infectorActivity' @change='setInfectorActivity'>
          <option v-for='(value, infectorActivityType, index) in infectorActivityTypeMapping'>{{ infectorActivityType }}</option>
        </select>
      </div>

      <div class='container'>
        <label>What best describes what you were doing?</label>
        <select :value='susceptibleActivity' @change='setSusceptibleActivity'>
          <option v-for='susceptibleActivityType in susceptibleActivities'>{{ susceptibleActivityType }}</option>
        </select>
      </div>

      <div class='container'>
        <label>Susceptible age group</label>
        <select :value='susceptibleAgeGroup' @change='setSusceptibleAgeGroup'>
          <option v-for='s in susceptibleAgeGroups'>{{ s }}</option>
        </select>
      </div>
    </div>

    <div class='container centered'>
      <button class='normal-padded' @click='save'>Save</button>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Event from './event';
import { useEventStore } from './stores/event_store';
import { useMainStore } from './stores/main_store';
import { mapStores, mapActions } from 'pinia'

export default {
  name: 'App',
  components: {
    Event
  },
  computed: {
    ...mapStores(useEventStore)
  },
  created() { },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setPlace']),
    save() {
      // TODO: call save on the Event store? send data to backend.
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
    },
    setRoomWidth(event) {
      this.roomWidth = event.target.value;
    },
    setRoomHeight(event) {
      this.roomHeight = event.target.value;
    },
    setSinglePassFiltrationEfficiency(event) {
      this.singlePassFiltrationEfficiency = event.target.value;
    },
    setCarbonDioxideAmbient(event) {
      this.carbonDioxideAmbient = event.target.value;
    },
    setCarbonDioxideMeasurementDevice(event) {
      this.carbonDioxideMeasurementDevice = event.target.value;
    },
    setCarbonDioxideSteadyState(event) {
      this.carbonDioxideSteadyState = event.target.value;
    },
    setInfectorActivity(event) {
      this.infectorActivity = event.target.value;
    },
    setSusceptibleActivity(event) {
      this.susceptibleActivity = event.target.value;
    },
    setSusceptibleAgeGroup(event) {
      this.susceptibleAgeGroup = event.target.value;
    },
    setNumberOfPeople(event) {
      this.numberOfPeople = event.target.value;
    },
    setPercentOfPeopleWithElastomerics(event) {
      this.percentOfPeopleWithElastomerics = event.target.value;
    },
    setPercentOfPeopleWithN95s(event) {
      this.percentOfPeopleWithN95s = event.target.value;
    },
    setPercentOfPeopleWithClothSurgicalMasks(event) {
      this.percentOfPeopleWithClothSurgicalMasks = event.target.value;
    },
    setPercentOfPeopleWithNoMasks(event) {
      this.percentOfPeopleWithNoMasks = event.target.value;
    },
    setSystemOfMeasurement(event) {
      this.systemOfMeasurement = event.target.value;
      if (this.systemOfMeasurement == 'imperial') {
        this.lengthMeasurementType = 'feet';
        this.airDeliveryRateMeasurementType = 'cubic feet per minute';
      } else {
        this.lengthMeasurementType = 'meters';
        this.airDeliveryRateMeasurementType = 'cubic meters per minute';
      }
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
    flex-direction: column;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  button {
    padding: 1em 3em;
  }
</style>
