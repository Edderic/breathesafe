<template>
  <div class='border-showing' id='message'>
    <h2>Add Measurements</h2>
    <div class='container row centered menu'>
      <button id='whereabouts' :class='{ "tab-item": true, "selected": display == "whereabouts"}' @click='setDisplay("whereabouts")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <circle cx="40" cy="25" r="20" fill="white"/>

          <path d='m 21 28 c 0 15 10 22 19 40 c 10 -18 19 -28 19 -40' stroke='white' fill='white'/>

          <circle cx="40" cy="25" r="10" fill="rgb(150, 29, 2)"/>
        </svg>
      </button>
      <button id='room_dimensions' :class='{ "tab-item": true, "selected": display == "room_dimensions"}' @click='setDisplay("room_dimensions")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <path d="M 31 20 l -5 13 h 25 l 3 -13 z m -5 13 v 20 h 25 v -20 m 0 20 l 3 -13.5 l 0 -19" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
          <text x="34" y="59">L</text>
          <text x="12" y="38">H</text>
          <text x="57" y="44">W</text>

        </svg>
      </button>
      <button id='ventilation' :class='{ "tab-item": true, "selected": display == "ventilation"}' @click='setDisplay("ventilation")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <path d="m 20 30 h 40 l -20 -20 z" stroke='black' fill='#ccc'/>
          <path d="m 20 30 h 40 v 30 h -40 z" stroke='black' fill='#eee'/>

          <path d="m 20 30 m 4 4 v 15 h 10 v -15 z" stroke='black' fill='#ddd'/>
          <path d="m 20 30 m 25 4 v 15 h 10 v -15 z" stroke='black' fill='#ddd'/>

          <path d='m 20 30 m -10 1 c 3 4 5 5 21 8' stroke='green' fill='transparent'/>
          <path d='m 20 30 m -10 1 m 21 8 l -2 2 l 3 -2 l -2 -2 l -0.5 4' stroke='green' fill='green'/>

          <path d='m 20 30 m -13 12 h 19' stroke='green' fill='transparent'/>
          <path d='m 20 30 m -13 12 m 19 0 l 0 2 l 2 -2 l -2 -2 z' stroke='green' fill='green'/>

          <path d='m 20 30 m -10 23 c 4 -3 5 -4 19 -7' stroke='green' fill='transparent'/>
          <path d='m 20 30 m -10 23 m 19 -7 l 1 2 l 2 -3 l -3.5 -1 z' stroke='green' fill='green'/>


          <path d='m 20 30 m 29 8 c 4 0 15 -3 19 -7' stroke='red' fill='transparent'/>
          <path d='m 20 30 m 29 8 m 19 -7 l 1 2 l 2 -3 l -3.5 -0.8 z' stroke='red' fill='red'/>

          <path d='m 20 30 m 29 12 h 20' stroke='red' fill='transparent'/>
          <path d='m 20 30 m 29 12 m 20 0 l 0 2 l 2.5 -2 l -2.5 -2 z' stroke='red' fill='red'/>

          <path d='m 20 30 m 29 16 c 4 0 17 2 20 5' stroke='red' fill='transparent'/>
          <path d='m 20 30 m 29 16 m 20 5 l -2 1.5 l 3 0 l 0 -3 z' stroke='red' fill='red'/>
          <text x="25" y="65">VENT</text>
        </svg>
      </button>

      <button id='pac' :class='{ "tab-item": true, "selected": display == "pac"}' @click='setDisplay("pac")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <path d="M 30 20 l -5 17 h 25 l 3 -17 z m -5 17 v 23 h 25 v -23 m 0 23 l 3 -17.5 l 0 -19" fill="white" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
          <path d="M 27 43 v 17 m 5 0 v -17 m 5 0 v 17 m 5 0 v -17 m 5 0 v 17 " fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
          <path d="M 25 43 h 24" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>

          <ellipse cx="39" cy="28" rx="10" ry="7" stroke="black" fill="transparent" stroke-width="1"/>
          <ellipse cx="39" cy="28" rx="7" ry="5" stroke="black" fill="transparent" stroke-width="1"/>
          <ellipse cx="39" cy="28" rx="4" ry="3" stroke="black" fill="transparent" stroke-width="1"/>

          <path d="M 34 25 c 0 -5 0 -5 -5 -13 " stroke='green' fill='transparent'/>
          <path d="M 34 25 m -5 -13 l 2 -2 l -5 0 l 1 5 z" stroke='green' fill='green' />

          <path d="M 40 25 l 0 -17 " stroke='green'/>
          <path d="M 40 25 m 0 -17 l 3 0 l -3 -3 l -3 3 z" stroke='green' fill='green'/>


          <path d="M 46 25 c 0 -5 0 -5 5 -13" stroke='green' fill='transparent'/>
          <path d="M 46 25 m 5 -13 l 2.5 2.5 l 0 -5 l -5 1 z" stroke='green' fill='green'/>


          <path d="M 46 55 c 2 7 0 10 6 15" stroke='red' fill='transparent'/>
          <path d="M 46 55 l 3 -1 l -4 -2 l -2 4.5" stroke='red' fill='red'/>

          <path d="M 31 55 c 0 5 0 10 -7 14" stroke='red' fill='transparent'/>
          <path d="M 31 55 l 3 2 l -2 -5 l -3 3 z" stroke='red' fill='red'/>


          <text x="55" y="38">PAC</text>
        </svg>
      </button>

      <button id='behaviors' :class='{ "tab-item": true, "selected": display == "behaviors"}' @click='setDisplay("behaviors")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <path d="m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z" stroke='black' fill='#eee'/>
          <path d="m 20 30 l 5 -3" stroke='black' fill='transparent'/>

          <circle cx="23" cy="30" r="1" fill="black"/>

          <path d="m 25 50 c 10 0 25 0 25 -3" stroke='red' fill='transparent'/>
          <path d="m 50 47 l 1 3 l 3 -3 l -4.5 -2 z" stroke='red' fill='red'/>

          <path d="m 25 50 c 10 -5 18 0 21 -12" stroke='red' fill='transparent'/>
          <path d="m 47 38 l 2 1 l -1 -6 l -5 2 z" stroke='red' fill='red'/>


          <g transform='rotate(-30, 30, 22.5) scale(0.75) translate(-8, 30)'>
            <circle cx="40" cy="30" r="2" fill="black"/>
            <path d="m 41 30 v -10 h 5 v 10" stroke='black' fill='transparent'/>
            <circle cx="44.5" cy="30" r="2" fill="black"/>
          </g>

          <g transform='translate(10, 0) rotate(20, 40, 30)'>
            <circle cx="40" cy="30" r="2" fill="black"/>
            <path d="m 41 30 v -10 h 5 v 10" stroke='black' fill='transparent'/>
            <circle cx="44.5" cy="30" r="2" fill="black"/>
          </g>

          <g transform='translate(8, 5) rotate(30, 40, 30) scale(1.5)'>
            <circle cx="40" cy="30" r="2" fill="black"/>
            <path d="m 41 30 v -10 h 5 v 10" stroke='black' fill='transparent'/>
            <circle cx="44.5" cy="30" r="2" fill="black"/>
          </g>
        </svg>
      </button>
    </div>

    <div class='container chunk'>
      <div class='container bold message' v-for='message in messages'>
        {{ message }}
      </div>
      <br>
    </div>

    <div class='whereabouts chunk' v-if='display == "whereabouts"'>
      <div class='container'>
        <label><span class='bold'>Google Search</span></label>
        <GMapAutocomplete
           class='autocomplete'
           placeholder="This is a placeholder"
           @place_changed="setPlace"
        >
        </GMapAutocomplete>
      </div>

      <div class='container whereabouts'>
        <label><span class='bold'>Room name</span></label>
        <input
          :value="roomName"
          @change="setRoomName">
      </div>

      <div class='container'>
        <label><span class='bold'>Start time</span></label>
        <input class='wider-input'
          v-model="startDatetime"
        >
      </div>

      <div class='container'>
        <label class='centered'><span class='bold'>Make this information private</span>
          <CircularButton text='?' @click='toggleInfo("privacyInfo")'/>
        </label>
        <p v-if='privacyInfo'>Select <span class='bold'>private</span> if you don't want the rest of the public to see it. Useful for assessing risk at places like your home. On the other hand, if you want the public to benefit with this measurement, select <span class='bold'>public</span>.</p>
        <select :value='private' @change='setEventPrivacy'>
          <option>public</option>
          <option>private</option>
        </select>
      </div>

      <div class='container'>
        <label class='bold'>Maximum Occupancy</label>
        <div class='continuous'>
          <CircularButton text='-10' @click='addMaxOccupancy(-10)'/>
          <CircularButton text='-1' @click='addMaxOccupancy(-1)'/>
          <input
            type='number'
            v-model="maximumOccupancy"
          >

          <CircularButton text='+1' @click='addMaxOccupancy(1)'/>
          <CircularButton text='+10' @click='addMaxOccupancy(10)'/>
        </div>
      </div>
    </div>

    <div class='room_dimensions chunk page' v-if='display == "room_dimensions"'>
      <div class='container'>
        <div class='row'>
          <button :class="{ selected: this.useOwnHeight }" @click='setUseOwnHeight(true)'>Use own height and stride length to estimate</button>
          <button :class="{ selected: !this.useOwnHeight }" @click='setUseOwnHeight(false)'>Input Directly</button>
        </div>

        <div v-if="this.useOwnHeight">
          <div class='container'>
            <label>How many steps does it take to traverse the <span class='bold'>length</span> of the room?</label>
            <div class='continuous'>
              <CircularButton text='-10' @click='addStrideLength(-10, "Length")'/>
              <CircularButton text='-1' @click='addStrideLength(-1, "Length")'/>
              <input
                type='number'
                :value="strideLengthForLength"
                @change='setStrideLengthEvent($event, "Length")'
                >

              <CircularButton text='+1' @click='addStrideLength(1, "Length")'/>
              <CircularButton text='+10' @click='addStrideLength(10, "Length")'/>
            </div>
          </div>

          <div class='container'>
            <label>How many steps does it take to traverse the <span class='bold'>width</span> of the room?</label>
            <div class='continuous'>
              <CircularButton text='-10' @click='addStrideLength(-10, "Width")'/>
              <CircularButton text='-1' @click='addStrideLength(-1, "Width")'/>
              <input
                type='number'
                :value="strideLengthForWidth"
                @change='setStrideLengthEvent($event, "Width")'
                >
              <CircularButton text='+1' @click='addStrideLength(1, "Width")'/>
              <CircularButton text='+10' @click='addStrideLength(10, "Width")'/>
            </div>
          </div>

          <div class='container'>
            <label>How many times can you fit your height into the <span class='bold'>height</span> of the room?</label>

            <div class='continuous'>
              <CircularButton text='-10' @click='addRoomHeightUsingOwnHeight(-10)'/>
              <CircularButton text='-1' @click='addRoomHeightUsingOwnHeight(-1)'/>
              <input
                type='number'
                :value="personHeightToRoomHeight"
                @change="setPersonHeightToRoomHeight">
              <CircularButton text='+1' @click='addRoomHeightUsingOwnHeight(1)'/>
              <CircularButton text='+10' @click='addRoomHeightUsingOwnHeight(10)'/>
            </div>
          </div>
        </div>

        <div v-if="!this.useOwnHeight">
          <div class='container'>
            <label><span class='bold'>Length</span> ({{ measurementUnits.lengthMeasurementType }})</label>

            <div class='continuous'>
              <CircularButton text='-10' @click='addRoomDim(-10, "Length")'/>
              <CircularButton text='-1' @click='addRoomDim(-1, "Length")'/>
              <input
                type='number'
                :value="roomLength"
                @change="setRoomDim($event, 'Length')">
              <CircularButton text='+1' @click='addRoomDim(1, "Length")'/>
              <CircularButton text='+10' @click='addRoomDim(10, "Length")'/>
            </div>
          </div>

          <div class='container'>
            <label><span class='bold'>Width</span> ({{ measurementUnits.lengthMeasurementType }})</label>

            <div class='continuous'>
              <CircularButton text='-10' @click='addRoomDim(-10, "Width")'/>
              <CircularButton text='-1' @click='addRoomDim(-1, "Width")'/>
              <input
                type='number'
                :value="roomWidth"
                @change="setRoomDim($event, 'Width')">
              <CircularButton text='+1' @click='addRoomDim(1, "Width")'/>
              <CircularButton text='+10' @click='addRoomDim(10, "Width")'/>
            </div>
          </div>

          <div class='container'>
            <label><span class='bold'>Height</span> ({{ measurementUnits.lengthMeasurementType }})</label>

            <div class='continuous'>
              <CircularButton text='-10' @click='addRoomHeight(-10)'/>
              <CircularButton text='-1' @click='addRoomHeight(-1)'/>
              <input
                type='number'
                :value="roomHeight"
                @change="setRoomHeight">
              <CircularButton text='+1' @click='addRoomHeight(1)'/>
              <CircularButton text='+10' @click='addRoomHeight(10)'/>
            </div>
          </div>
        </div>

        <div class='container'>
          <label>Usable Volume Factor (dimension-less)</label>
          <div class='continuous'>
            <CircularButton text='-0.1' @click='addVolumeFactor(-0.1)'/>
            <input
              type='number'
              v-model="roomUsableVolumeFactor"
            >
            <CircularButton text='+0.1' @click='addVolumeFactor(0.1)'/>
          </div>
        </div>
      </div>
    </div>


    <div class='container chunk' v-if='display == "pac"'>
      <div class='centered'>
        <label class='subsection'>Portable Air Cleaning</label>
        <CircularButton text='+' @click='addPortableAirCleaner'/>
      </div>
      <div class='container border-showing' v-for='portableAirCleaner in portableAirCleaners' :key=portableAirCleaner.id>
        <div class='container'>
          <label><span class='bold'>Air delivery rate</span> ({{ measurementUnits.airDeliveryRateMeasurementType }})</label>
          <input
            type='number'
            :value="portableAirCleaner['airDeliveryRate']"
            @change="setPortableAirCleaningDeviceAirDeliveryRate($event, portableAirCleaner.id)">
        </div>

        <div class='container'>
          <label><span class='bold'>Single-pass filtration efficiency </span>(dimensionless)</label>
          <input
            type='number'
            :value="portableAirCleaner['singlePassFiltrationEfficiency']"
            @change="setPortableAirCleaningDeviceSinglePassFiltrationEfficiency($event, portableAirCleaner.id)">
        </div>

        <div class='container wide'>
          <label class='textarea-label bold'>Notes</label>
          <textarea type="textarea" rows=5 columns=80  @change='setPortableAirCleaningNotes($event, portableAirCleaner.id)'>{{ portableAirCleaner['notes'] }}</textarea>
        </div>

        <div class='container centered'>
          <button class='normal-padded' @click='removeAirCleaner(portableAirCleaner.id)'>Remove</button>
        </div>
      </div>
    </div>

    <div class='container chunk' v-if='display == "ventilation"'>
      <div class='container'>
        <label><span class='bold'>CO2 Measurement Device</span></label>

        <select :value='ventilationCO2MeasurementDeviceName' @change='setCarbonDioxideMonitor'>
          <option v-for='carbonDioxideMonitor in carbonDioxideMonitors'>{{ carbonDioxideMonitor['name'] }}</option>
        </select>
      </div>

      <div class='container'>
        <label class='centered'><span class='bold'>CO2 Ambient </span>(parts per million)
          <CircularButton text='?' @click='toggleInfo("ambientInfo")'/>
        </label>
        <p v-if='ambientInfo'>This is the reading outdoors.</p>

        <div class='continuous mega'>
          <CircularButton text='-100' @click='addCO2Ambient(-100)'/>
          <CircularButton text='-10' @click='addCO2Ambient(-10)'/>
          <CircularButton text='-1' @click='addCO2Ambient(-1)'/>

          <input
            type='number'
            :value="ventilationCO2AmbientPPM"
            @change="setCarbonDioxideAmbient">

          <CircularButton text='+1' @click='addCO2Ambient(1)'/>
          <CircularButton text='+10' @click='addCO2Ambient(10)'/>
          <CircularButton text='+100' @click='addCO2Ambient(100)'/>
        </div>
      </div>

      <div class='container'>
        <label class='centered'><span class='bold'>CO2 Steady State </span>(parts per million)
          <CircularButton text='?' @click='toggleInfo("steadyStateInfo")'/>
        </label>
        <p v-if='steadyStateInfo'>This is the CO2 reading indoors, taken when the CO2 readings have flattened over time, while the occupancy has stayed the same.</p>
        <div class='continuous mega'>
          <CircularButton text='-100' @click='addCO2SteadyState(-100)'/>
          <CircularButton text='-10' @click='addCO2SteadyState(-10)'/>
          <CircularButton text='-1' @click='addCO2SteadyState(-1)'/>

          <input
            type='number'
            :value="ventilationCO2SteadyStatePPM"
            @change="setCarbonDioxideSteadyState">

          <CircularButton text='+1' @click='addCO2SteadyState(1)'/>
          <CircularButton text='+10' @click='addCO2SteadyState(10)'/>
          <CircularButton text='+100' @click='addCO2SteadyState(100)'/>
        </div>
      </div>

      <div class='container wide'>
        <label class='textarea-label'><span class='bold'>Notes</span></label>
        <textarea type="textarea" rows=5 columns=80  @change='setVentilationNotes'>{{ ventilationNotes }}</textarea>
      </div>
    </div>

    <div class='container chunk' v-if='display == "behaviors"'>
      <div class='container grouping' v-for='activityGroup in activityGroups' :key=activityGroup.id>

        <div class='container'>
          <label># people</label>
          <CircularButton class='circular-button' text='-5' @click='addNumPeople(-5, activityGroup.id)'/>
          <CircularButton class='circular-button' text='-1' @click='addNumPeople(-1, activityGroup.id)'/>
          <input
            :value="activityGroup['numberOfPeople']"
            type='number'
            @change="setNumberOfPeople($event, activityGroup.id)">
          <CircularButton class='circular-button' text='+1' @click='addNumPeople(1, activityGroup.id)'/>
          <CircularButton class='circular-button' text='+5' @click='addNumPeople(5, activityGroup.id)'/>
        </div>

        <div class='container'>
          <label>Aerosol generation</label>
          <select :value='activityGroup["aerosolGenerationActivity"]' @change='setAerosolGenerationActivity($event, activityGroup.id)'>
            <option v-for='(value, infectorActivityType, index) in infectorActivityTypeMapping'>{{ infectorActivityType }}</option>
          </select>
        </div>

        <div class='container'>
          <label>CO2 gen.</label>
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

        <div class='container centered'>
          <button class='normal-padded' @click='removeActivityGroup(activityGroup.id)'>Remove</button>
          <button class='normal-padded' @click='cloneActivityGroup(activityGroup.id)'>Clone</button>
        </div>

      </div>

      <div class='container centered col final'>
        <button class='normal-padded' @click='cancel'>Cancel</button>
        <button class='normal-padded' @click='save'>Save</button>
      </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import CircularButton from './circular_button.vue';
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
    CircularButton,
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
          'heightMeters',
          'strideLengthMeters'
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
          'roomName',
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
    roomLength() {
      return convertLengthBasedOnMeasurementType(
        this.roomLengthMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType,
      )
    },
    roomWidth() {
      return convertLengthBasedOnMeasurementType(
        this.roomWidthMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType,
      )
    },
    roomHeight() {
      return convertLengthBasedOnMeasurementType(
        this.roomHeightMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType,
      )
    }
  },
  async created() {
    // TODO: fire and forget. Make asynchronous.
    await this.getCurrentUser()
    if (!this.currentUser) {
      this.$router.push({
        name: 'SignIn',
        query: {
          'attempt-name': 'AddMeasurements'
        }
      })
    }

    this.$watch(
      () => this.$route.name,
      (toName, previousName) => {
        if (toName == 'AddMeasurements') {
          // check to see if the currentUser
          if (!this.currentUser) {
            this.$router.push({
              name: 'SignIn',
              query: {
                'attempt-name': 'AddMeasurements'
              }
            })
          }
        }
      }
    )
    await this.loadProfile()
    this.loadCO2Monitors()

    this.roomLengthMeters = this.strideLengthForLength * this.strideLengthMeters
    this.roomWidthMeters = this.strideLengthForWidth * this.strideLengthMeters
    this.roomHeightMeters = this.personHeightToRoomHeight * this.heightMeters

    this.addActivityGrouping()

    this.setCarbonDioxideMonitor({ target: { value: this.carbonDioxideMonitors[0].name }})
    // this.$watch(
      // () => this.$route.name,
      // (toName, previousName) => {
        // debugger

        // react to route changes...
      // }
    // )


  },
  data() {
    return {
      center: {lat: 51.093048, lng: 6.842120},
      ambientInfo: false,
      privacyInfo: false,
      steadyStateInfo: false,
      ventilationACH: 0.0,
      portableACH: 0.0,
      totalACH: 0.0,
      occupancy: {
        unparsedOccupancyData: "",
        parsed: {
        },
      },
      maximumOccupancy: 0,
      messages: [],
      roomUsableVolumeFactor: 0.8,
      useOwnHeight: true,
      display: 'whereabouts',
      personHeightToRoomHeight: 1,
      strideLengthForWidth: 1,
      strideLengthForLength: 1,
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setGMapsPlace', 'setFocusTab', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['loadCO2Monitors', 'loadProfile']),
    ...mapActions(useEventStores, ['load', 'addEvent']),
    ...mapActions(useEventStore, ['addPortableAirCleaner']),
    ...mapState(useEventStore, ['findActivityGroup', 'findPortableAirCleaningDevice']),

    toggleInfo(info) {
      this[info] = !this[info]
    },
    setDisplay(string) {
      this.display = string
    },
    addMaxOccupancy(amount) {
      this.maximumOccupancy += parseInt(amount)
    },
    addActivityGrouping() {
      this.activityGroups.unshift({
        'id': this.generateUUID(),
        'aerosolGenerationActivity': "",
        'carbonDioxideGenerationActivity': "",
        'ageGroup': "",
        'maskType': "",
        'numberOfPeople': 1,
      })
    },
    cancel() {
      // TODO: clear out data for Add New Event
      this.$router.go(-1)
    },
    parseOccupancyData(event) {
      this.occupancy.unparsedOccupancyData = event.target.value
      this.occupancy.parsed = parseOccupancyHTML(this.occupancy.unparsedOccupancyData)
    },
    async save() {
      this.messages = []

      if (!this.placeData || !this.placeData.place_id) {
        this.messages.push("Error: Google Maps data missing. Please use the Google Search to search for the place of interest.")
      }
      if (this.activityGroups.length == 0) {
        this.messages.push("Error: Please fill out activities done by people so we can compute clean air delivery rate through ventilation.")
      }

      if (!this.ventilationCO2SteadyStatePPM) {
        this.messages.push("Error: Please fill out CO2 steady state so we can compute clean air delivery rate of ventilation.")
      }

      if (!this.ventilationCO2AmbientPPM) {
        this.messages.push("Error: Please fill out CO2 ambient so we can compute clean air delivery rate of ventilation.")
      }

      if (this.maximumOccupancy == 0) {
        this.messages.push("Error: maximum occupancy of a room cannot be 0.")
      }
      if (!this.roomName) {
        this.messages.push("Error: Room name cannot be blank.\n ")
      }

      if (!this.startDatetime) {
        this.messages.push("Error: Start time cannot be blank.\n ")
      }

      if (!this.roomHeightMeters) {
        this.messages.push("Error: Room height cannot be blank.\n ")
      }

      if (!this.roomLengthMeters) {
        this.messages.push("Error: Room length cannot be blank.\n ")
      }

      if (!this.roomWidthMeters) {
        this.messages.push("Error: Room width cannot be blank.\n ")
      }

      if (this.messages.length > 0) {
        let element_to_scroll_to = document.getElementById('message');
        element_to_scroll_to.scrollIntoView();
        return
      }

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

      let successful = false
      let newEvent = null

      await axios.post('/events', toSave)
        .then(response => {
          console.log(response)
          if (response.status == 201 || response.status == 200) {
            // TODO: could make this more efficient by just adding the event
            // directly to the store?
            newEvent = response.data.event
            this.addEvent(newEvent)
            successful = true
          }

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Something went wrong."
          // whatever you want
        })

      if (successful) {
        // if admin and private - don't alert
        // if admin and public - don't alert
        // if not admin and public - alert
        // if not admin and private - don't alert

        this.$router.push({ name: 'Analytics', params: { 'id': newEvent.id }})
      }
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
        'numberOfPeople': activityGroup['numberOfPeople'],
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
    setEventPrivacy(event) {
      this.private = event.target.value;
    },
    setRoomName(event) {
      this.roomName = event.target.value;
    },
    addNumPeople(amount, activityGroupId) {
      let activityGroup = this.findActivityGroup()(activityGroupId);
      activityGroup.numberOfPeople += parseInt(amount)
    },
    addCO2SteadyState(amount) {
      this.ventilationCO2SteadyStatePPM += parseInt(amount)
    },
    addCO2Ambient(amount) {
      this.ventilationCO2AmbientPPM += parseInt(amount)
    },
    addRoomHeight(amount) {
      let newEvent = {
        target: {
          value: this.roomHeight + amount
        }
      }
      this.setRoomHeight(newEvent)
    },
    setRoomHeight(event) {
      this['roomHeightMeters'] = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )

      this.personHeightToRoomHeight = this['roomHeightMeters'] / this.heightMeters
    },
    setRoomDim(event, dimension) {
      this[`room${dimension}Meters`] = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )

      this[`strideLengthFor${dimension}`] = this[`room${dimension}Meters`] / this.strideLengthMeters
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
    setUseOwnHeight(value) {
      this.useOwnHeight = value
    },
    setPersonHeightToRoomHeight(event) {
      let value = event.target.value
      this.roomHeightMeters = parseFloat(value) * this.heightMeters
      this.personHeightToRoomHeight = parseFloat(value)
    },
    addVolumeFactor(value) {
      this.roomUsableVolumeFactor += parseFloat(value)
    },
    addRoomHeightUsingOwnHeight(value) {
      this.setPersonHeightToRoomHeight({
        target: {
          value: parseFloat(value) + this.personHeightToRoomHeight
        }
      })
    },
    addRoomDim(amount, dimension) {
      let newEvent = {
        'target': {
          'value': this[`room${dimension}`] + amount
        }
      }

      this.setRoomDim(newEvent, dimension)
    },
    addStrideLength(value, axes) {
      this.setStrideLength(this[`strideLengthFor${axes}`] + parseInt(value), axes)
    },
    setStrideLength(value, axes) {
      this[`room${axes}Meters`] = value * this.strideLengthMeters
      this[`strideLengthFor${axes}`] = value
    },
    setStrideLengthEvent(event, axes) {
      this.setStrideLength(parseFloat(event.target.value), axes)
    }

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

  .autocomplete {
    width: 20em;
  }

  .wider-input {
    width: 30em;
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
    align-items: center;
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
    border: 0;
  }

  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  table {
    text-align: center;
  }

  .bold {
    font-weight: bold;
  }

  .selected {
    background-color: #e6e6e6;
  }

  h2 {
    text-align: center;
  }

  text {
    dominant-baseline: hanging;
    font: 10px Verdana, Helvetica, Arial, sans-serif;
    font-weight: bold;
  }

  .round {
  }

  .continuous {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }
  .continuous input {
    width: 3em;
    height: 1em;
    font-weight: bold;
    font-size: 24px;
    margin-left: 0.5em;
    margin-right: 0.5em;
    text-align: center;
  }

  .continuous.mega .round {
    margin-left: 0.25em;
    margin-right: 0.25em;
  }

  .grouping {
    padding: 1em;
    border: 1px solid #e6e6e6;
  }

  .add-activity-groups {
    font-weight: bold;
    font-size: 2em;
    height: 2em;
    width: 2em;
  }

  .message {
    padding-left: 1em;
    padding-right: 1em;
  }

  .menu {
    min-width: 500px;
    justify-content: space-around;
    background-color: #eee;
    margin-top: 0;
    margin-bottom: 0;
  }

  .space-around {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
  }

  .menu button {
    border: 0;
  }

  .menu .tab-item {
    border-top: 4px solid #eee;
    border-bottom: 4px solid #eee;
  }

  .menu button.selected {
    border-bottom: 4px solid black;
  }

  textarea {
  }
  br {
    display: none;
  }
  .container {
    display: flex;
    flex-direction: column;
    margin-left: 0;
    margin-right: 0;
  }

  .grouping .container {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin-top: 0;
    margin-bottom: 0;
  }

  p {
    padding: 1em;
  }

  .grouping input[type='number'] {
    width: 2em;
    font-size: 24px;
  }

  .continuous.mega {
  }

  .container input {
    height: 2em;
    margin-left: 1em;
    margin-right: 1em;
  }

  .container select {
    height: 3em;
    margin-left: 1em;
    margin-right: 1em;
  }

  .add-measurements {
    display: none;
  }

  .autocomplete {
    width: auto;
  }

  .row {
    flex-direction: row;
  }

  .row button {
    width: 100%;
    padding-top: 1em;
    padding-bottom: 1em;
  }

  label, h2 {
    text-align: center;
  }

  .wider-input, input {
    width: auto;
  }
  .chunk {
    width: 100vw;
  }

  .container.centered button {
    width: 50%;
    padding-top: 1em;
    padding-bottom: 1em;
  }

  .final {
    justify-content: center;
    align-items: center;
  }

  .final button {
    font-weight: bold;
    font-size: 1em;
  }


  @media(min-width: 750px) {
    .border-showing, .chunk {
      width: 750px;
    }

  }
</style>
