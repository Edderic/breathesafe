<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Profile</h2>
    </div>

    <div class='container row centered menu'>
      <button id='miscellaneous-button' @click='setDisplay("miscellaneous")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <text x="12" y="30">Misc</text>
        </svg>
      </button>

      <button id='ventilation' @click='setDisplay("ventilation")'>
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

      <button id='length_estimation' @click='setDisplay("length_estimation")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
          <path d="M 31 20 l -5 13 h 25 l 3 -13 z m -5 13 v 20 h 25 v -20 m 0 20 l 3 -13.5 l 0 -19" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
          <text x="34" y="59">L</text>
          <text x="12" y="38">H</text>
          <text x="57" y="44">W</text>

        </svg>
      </button>

      <button id='socials' @click='setDisplay("socials")'>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='6em' width='6em'>
          <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>

          <circle cx="10" cy="40" r="2" fill="black"/>
          <circle cx="70" cy="40" r="2" fill="black"/>
          <circle cx="40" cy="10" r="2" fill="black"/>
          <circle cx="40" cy="70" r="2" fill="black"/>

          <path d="M 10 40 L 70 40 L 40 10 L 40 70 z L 40 10 L 40 70 L 70 40" stroke='black' fill='transparent'/>

        </svg>
      </button>

    </div>
    <div class='container centered'>
      <h3>{{ message }}</h3>
    </div>


    <div class='container' v-if="display == 'miscellaneous'">
      <div class='container'>
        <label>First name</label>
        <input :value='firstName' @change='updateFirstName' :disabled="this.status == 'saved'">
      </div>
      <div class='container'>
        <label>Last name</label>
        <input :value='lastName' @change='updateLastName' :disabled="this.status == 'saved'">
      </div>
      <div class='container centered'>
        <button @click='save' v-if='this.status == "edit"'>Save</button>
        <button @click='editProfile' v-if='this.status == "saved"'>Edit</button>
      </div>
    </div>

    <div class='container' v-if='display == "length_estimation"'>
      <div class='container'>
        <label>System of Measurement</label>

        <select :value='systemOfMeasurement' @change='setSystemOfMeasurement'>
          <option>imperial</option>
          <option>metric</option>
        </select>
      </div>

      <div class='container'>
        <div class='row'>
          <label>Height ({{ measurementUnits.lengthMeasurementType }})</label>
          <div :style='circle'
            @click='toggle("showWhyHeight")'>?
          </div>
          <input :value='height' @change='updateHeightMeters' :disabled="this.status == 'saved'">
        </div>
        <div class='row' v-show="showWhyHeight">
          <p >
            How tall are you? We need the room volume to assess risk. We assume a box model, so
            the components are length, width, and height. To calculate room height, you
            could use your own height as a reference. When you add a measurement, for
            example, you will be asked how many times you can fit your height into the
            room's height.
          </p>


          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 200 200"
            height='15em'
            width='15em'
          >
            <g transform='translate(0 55)'>
              <circle cx="19" cy="27" r="5" fill="gray" />
              <path d='m 23 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' fill='gray' stroke='gray'/>

              <path d='m 28 22 h 5 v 33 h -5' stroke='black' fill='transparent'/>

              <path d='m 33 38 c 5 0 23 0 43 -10' stroke='black' fill='transparent'/>

              <text class='question-mark' x='43' y=13>x?</text>

            </g>


            <g transform='scale(2.5, 2.5) translate(-20)'>
              <path d="M 61 10 l -5 13 h 25 l 3 -13 z m -5 13 v 20 h 25 v -20 m 0 20 l 3 -13.5 l 0 -19" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
              <path d="M 51 24 h 3 h -3 v 19 h 3" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>

              <text x="64" y="49">L</text>
              <text x="57" y="28">H</text>
              <text x="87" y="34">W</text>
            </g>

        </svg>

        </div>
      </div>

      <div class='container'>
        <div class='row'>
          <label>Stride length ({{ measurementUnits.lengthMeasurementType }})</label>
          <div :style='circle'
            @click='toggle("showWhyStrideLength")'>?
          </div>
          <input :value='strideLength' @change='updateStrideLengthMeters' :disabled="this.status == 'saved'">
        </div>
        <div class='row' v-show="showWhyStrideLength">
          <p >
            How big is your step? To estimate the length and/or width of the
            room, one could use one's stride length as a way to estimate. Take a step as
            you normally would while walking. The distance between the very tip of your
            toes of the back foot and the very tip of your toes of the front foot is the
            stride length.
          </p>

          <svg
            class='stride-length-illustration'
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 100 100"
            height='15em'
            width='15em'
          >

            <g class='back-foot'>
              <g transform='translate(0 0)'>
                <path d='m 10 50 c 1 -5 5 -5 10 -5 v 5' fill='transparent' stroke='gray'/>
              </g>

              <g transform='scale(1 -1) translate(0 -100)'>
                <path d='m 10 50 c 1 -5 5 -5 10 -5 v 5' fill='transparent' stroke='gray'/>
              </g>

              <path d='m 23 50 v -5 c 10 0 15 2 15 5' fill='transparent' stroke='gray'/>
              <path transform='scale(1 -1) translate(0 -100)' d='m 23 50 v -5 c 10 0 15 2 15 5' fill='transparent' stroke='gray'/>
            </g>


            <g class='front-foot' transform='translate(60 0)'>
              <g transform='translate(0 0)'>
                <path d='m 10 50 c 1 -5 5 -5 10 -5 v 5' fill='transparent' stroke='gray'/>
              </g>

              <g transform='scale(1 -1) translate(0 -100)'>
                <path d='m 10 50 c 1 -5 5 -5 10 -5 v 5' fill='transparent' stroke='gray'/>
              </g>

              <path d='m 23 50 v -5 c 10 0 15 2 15 5' fill='transparent' stroke='gray'/>
              <path transform='scale(1 -1) translate(0 -100)' d='m 23 50 v -5 c 10 0 15 2 15 5' fill='transparent' stroke='gray'/>
            </g>


            <path d='m 38 40 v 5 v -5 h 60 v 5' fill='transparent' stroke='black'/>


          </svg>
        </div>
      </div>

      <div class='container centered'>
        <button @click='save' v-if='this.status == "edit"'>Save</button>
        <button @click='editProfile' v-if='this.status == "saved"'>Edit</button>
      </div>
    </div>

    <div class='container' v-if='display == "ventilation"'>
      <label class='subsection'>CO2 Monitors</label>
      <button @click='newCO2monitor'>+</button>
      <div class='border-showing' v-for='carbonDioxideMonitor in carbonDioxideMonitors' :key=carbonDioxideMonitor.id>
        <div class='container'>
          <label>Model</label>
          <input
            :value="carbonDioxideMonitor['model']"
            :disabled="carbonDioxideMonitor.status == 'display'"
            @change="setCarbonDioxideMonitorModel($event, carbonDioxideMonitor['id'])">
        </div>

        <div class='container'>
          <label>Name</label>
          <input
            :value="carbonDioxideMonitor['name']"
            :disabled="carbonDioxideMonitor.status == 'display'"
            @change="setCarbonDioxideMonitorName($event, carbonDioxideMonitor['id'])">
        </div>

        <div class='container'>
          <label>Serial</label>
          <input
            :value="carbonDioxideMonitor['serial']"
            :disabled="carbonDioxideMonitor.status == 'display'"
            @change='setCarbonDioxideMonitorSerial($event, carbonDioxideMonitor["id"])'>
        </div>

        <div class='container centered'
            v-if="carbonDioxideMonitor.status == 'editable'"
        >
          <button
            @click='removeCO2Monitor(carbonDioxideMonitor["id"])'
            v-if="carbonDioxideMonitor.status == 'editable' && hasBeenSaved(carbonDioxideMonitor['id'])"
          >Remove</button>
          <button @click='cancelEditing(carbonDioxideMonitor["id"])'>Cancel</button>
          <button @click='saveCO2Monitor(carbonDioxideMonitor["id"])' :disabled="!validCO2Monitor(carbonDioxideMonitor)">Save</button>
        </div>

        <div class='container centered'
            v-if="carbonDioxideMonitor.status == 'display'"
        >
          <button @click='editCO2Monitor(carbonDioxideMonitor["id"])'>Edit</button>
        </div>
      </div>
    </div>

    <div class='container' v-if='display == "socials"'>
      <div class='container'>
        <label>Twitter</label>
        <input :value='socials.twitter' @change='updateSocials($event, "twitter")' :disabled="this.status == 'saved'">
      </div>
      <div class='container'>
        <label>Mastodon</label>
        <input :value='socials.mastodon' @change='updateSocials($event, "mastodon")' :disabled="this.status == 'saved'">
      </div>
      <div class='container'>
        <label>Facebook</label>
        <input :value='socials.facebook' @change='updateSocials($event, "facebook")' :disabled="this.status == 'saved'">
      <div class='container centered'>
        <button @click='save' v-if='this.status == "edit"'>Save</button>
        <button @click='editProfile' v-if='this.status == "saved"'>Edit</button>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import { useEventStore } from './stores/event_store';
import { useMainStore } from './stores/main_store';
import { convertLengthBasedOnMeasurementType, generateUUID, setupCSRF } from './misc';
import { useEventStores } from './stores/event_stores';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia'
import { toggleCSS } from './colors.js'

export default {
  name: 'Profile',
  components: {
    Event
  },
  computed: {
    ...mapWritableState(
        useMainStore,
        [
          'currentUser',
          'message'
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'measurementUnits'
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'carbonDioxideMonitors',
          'systemOfMeasurement',
          'heightMeters',
          'strideLengthMeters',
          'firstName',
          'lastName',
          'status',
          'socials'
        ]
    ),
    height() {
      return convertLengthBasedOnMeasurementType(
        this.heightMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType
      )
    },
    strideLength() {
      return convertLengthBasedOnMeasurementType(
        this.strideLengthMeters,
        'meters',
        this.measurementUnits.lengthMeasurementType
      )
    }
  },
  // TODO: pull data from profiles for given current_user
  async created() {
    await this.getCurrentUser()
    this.loadCO2Monitors()
    this.loadProfile()

    if (!this.currentUser) {
      this.$router.push({ name: 'SignIn', query: {'attempt-name': 'Profile'} })
    }
  },
  data() {
    return {
      showWhyHeight: false,
      showWhyStrideLength: false,
      circle: toggleCSS,
      display: 'miscellaneous'
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['setSystemOfMeasurement', 'loadProfile', 'loadCO2Monitors', 'updateProfile']),
    setDisplay(string) {
      this.display = string
    },
    validCO2Monitor(monitor) {
      return !!monitor["model"] && !!monitor["name"] && !!monitor["serial"]
    },
    allBlank(monitor) {
      return !monitor["model"] && !monitor["name"] && !monitor["serial"]
    },
    cancelEditing(id) {
      let carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      if (this.allBlank(carbonDioxideMonitor)) {
        let index = this.carbonDioxideMonitors.findIndex(
          (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
        );

        this.carbonDioxideMonitors.splice(index, 1);
      }

      carbonDioxideMonitor['status'] = 'display'
    },
    newCO2monitor() {
      let uuid = generateUUID()
      this.carbonDioxideMonitors.unshift({
        'name': '',
        'serial': '',
        'model': '',
        'id': uuid,
        'status': 'editable',
      })
    },
    hasBeenSaved(id) {
      // id is integer in the backend
      return parseInt(id) == id
    },
    editCO2Monitor(id) {
      const carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      carbonDioxideMonitor['status'] = 'editable'
    },
    async saveCO2Monitor(id) {
      let carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      let toSave = {
          'carbonDioxideMonitor': {
            'name': carbonDioxideMonitor.name,
            'serial': carbonDioxideMonitor.serial,
            'model': carbonDioxideMonitor.model,
          },
      }

      setupCSRF();

      await axios.post(`/users/${this.currentUser.id}/carbon_dioxide_monitors.json`, toSave)
        .then(response => {
          console.log(response)
          if (response.status == 204 || response.status == 200) {
            this.message = response.data.message
            carbonDioxideMonitor['status'] = 'display'
          }
        })
        .catch(error => {
          console.log(error)
            this.message = "Something went wrong with saving."
          // whatever you want
        })
      this.carbonDioxideMonitors.splice(carbonDioxideMonitorIndex, 1);
    },
    async removeCO2Monitor(id) {
      const carbonDioxideMonitorIndex = this.carbonDioxideMonitors.findIndex(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      const carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (cm) => cm.id == id
      );

      setupCSRF();

      await axios.delete(`/users/${this.currentUser.id}/carbon_dioxide_monitors/${carbonDioxideMonitor.id}.json`)
        .then(response => {
          console.log(response)
          if (response.status == 204 || response.status == 200) {
            this.message = response.data.message
            this.carbonDioxideMonitors.splice(carbonDioxideMonitorIndex, 1);

          }
        })
        .catch(error => {
          console.log(error)
            this.message = "Something went wrong with saving."
          // whatever you want
        })
    },
    toggle(variable) {
      this[variable] = !this[variable]
    },
    save() {
      this.updateProfile()
    },
    setCarbonDioxideMonitorModel(event, id) {
      const carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      carbonDioxideMonitor['model'] = event.target.value;
    },
    setCarbonDioxideMonitorName(event, id) {
      const carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      carbonDioxideMonitor['name'] = event.target.value;
    },
    setCarbonDioxideMonitorSerial(event, id) {
      const carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      carbonDioxideMonitor['serial'] = event.target.value;
    },
    updateStrideLengthMeters(event) {
      this.strideLengthMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    updateHeightMeters(event) {
      this.heightMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
    },
    updateSocials(event, what) {
      this.socials[what] = event.target.value
    },
    updateFirstName(event) {
      this.firstName = event.target.value
    },
    updateLastName(event) {
      this.lastName = event.target.value
    },
    editProfile(event) {
      this.status = 'edit'
    }
  },
}

</script>

<style scoped>
  .row {
    display: flex;
    flex-direction: row;
    align-items: center;

  }
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

  p {
    padding: 1em;
    width: 20rem;
  }


  text {
    dominant-baseline: hanging;
    font: 10px Verdana, Helvetica, Arial, sans-serif;
    font-weight: bold;
  }

  #miscellaneous-button text {
    font: 2em Verdana, Helvetica, Arial, sans-serif;
  }

  .question-mark {
    font-size: 1.25em;
    fill: red;
  }
</style>
