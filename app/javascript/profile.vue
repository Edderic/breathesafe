<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Profile</h2>
    </div>

    <div class='container centered'>
      <h3>{{ message }}</h3>
    </div>

    <div class='container'>
      <label>First name</label>
      <input :value='firstName' @change='updateFirstName' :disabled="this.status == 'saved'">
    </div>
    <div class='container'>
      <label>Last name</label>
      <input :value='lastName' @change='updateLastName' :disabled="this.status == 'saved'">
    </div>
    <div class='container'>
      <div class='row'>
        <label>Height ({{ measurementUnits.lengthMeasurementType }})</label>
        <div :style='circle'
          @click='toggle("showWhyHeight")'>?
        </div>
        <input :value='height' @change='updateHeightMeters' :disabled="this.status == 'saved'">
      </div>
      <p v-show="showWhyHeight">
        We need the room volume to assess risk. You could enter the length,
        width, and height of the room in terms of feet or meters. However, it's
        unlikely that you'll be carrying measuring tape with you everywhere you
        go. Instead, you could use your height as a reference to estimate the
        dimensions of the room.  When you add a measurement, for example, you will be
        asked how many times you can fit your height into the room's width.
      </p>
    </div>

    <div class='container'>
      <div class='row'>
        <label>Stride length ({{ measurementUnits.lengthMeasurementType }})</label>
        <div :style='circle'
          @click='toggle("showWhyStrideLength")'>?
        </div>
        <input :value='strideLength' @change='updateStrideLengthMeters' :disabled="this.status == 'saved'">
      </div>
      <p v-show="showWhyStrideLength">
        We need the room volume to assess risk.
        To estimate the length and width of the room, one could use one's
stride length as a way to estimate. Take a step as you normally would while
walking. The distance between the very tip of your toes of the back foot and
the very tip of your toes of the front foot is the stride length.
      </p>
    </div>

    <div class='container centered'>
      <button @click='save' v-if='this.status == "edit"'>Save</button>
      <button @click='editProfile' v-if='this.status == "saved"'>Edit</button>
    </div>

    <div class='container'>
      <label>System of Measurement</label>

      <select :value='systemOfMeasurement' @change='setSystemOfMeasurement'>
        <option>imperial</option>
        <option>metric</option>
      </select>
    </div>

    <div class='container'>
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
          'status'
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
      circle: toggleCSS
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['setSystemOfMeasurement', 'loadProfile', 'loadCO2Monitors', 'updateProfile']),
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
    updateHeightMeters(event) {
      this.heightMeters = convertLengthBasedOnMeasurementType(
        event.target.value,
        this.measurementUnits.lengthMeasurementType,
        'meters'
      )
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


</style>
