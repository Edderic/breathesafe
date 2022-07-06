<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Profile</h2>
    </div>

    <div class='container centered'>
      <h3>{{ message }}</h3>
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
            :disabled="carbonDioxideMonitor.status == 'saved'"
            @change="setCarbonDioxideMonitorModel($event, carbonDioxideMonitor['id'])">
        </div>

        <div class='container'>
          <label>Name</label>
          <input
            :value="carbonDioxideMonitor['name']"
            :disabled="carbonDioxideMonitor.status == 'saved'"
            @change="setCarbonDioxideMonitorName($event, carbonDioxideMonitor['id'])">
        </div>

        <div class='container'>
          <label>Serial</label>
          <input
            :value="carbonDioxideMonitor['serial']"
            :disabled="carbonDioxideMonitor.status == 'saved'"
            @change='setCarbonDioxideMonitorSerial($event, carbonDioxideMonitor["id"])'>
        </div>

        <div class='container centered'
            v-if="carbonDioxideMonitor.status == 'editable'"
        >
          <button
            @click='removeCO2Monitor(carbonDioxideMonitor["id"])'
            v-if="carbonDioxideMonitor.status == 'editable'"
          >Remove</button>
          <button @click='cancelEditing(carbonDioxideMonitor["id"])'>Cancel</button>
          <button @click='saveCO2Monitor(carbonDioxideMonitor["id"])' :disabled="!validCO2Monitor(carbonDioxideMonitor)">Save</button>
        </div>

        <div class='container centered'
            v-if="carbonDioxideMonitor.status == 'saved'"
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
import { generateUUID } from './misc';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'Profile',
  components: {
    Event
  },
  computed: {
    ...mapState(
        useProfileStore,
        [
          'systemOfMeasurement'
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'carbonDioxideMonitors',
        ]
    )
  },
  // TODO: pull data from profiles for given current_user
  created() {
    this.load()
  },
  data() {
    return {
      message: ""
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab']),
    ...mapActions(useProfileStore, ['setSystemOfMeasurement']),
    validCO2Monitor(monitor) {
      return !!monitor["model"] && !!monitor["name"] && !!monitor["serial"]
    },
    cancelEditing(id) {
      let carbonDioxideMonitor = this.carbonDioxideMonitors.find(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      carbonDioxideMonitor['status'] = 'saved'
    },
    newCO2monitor() {
      let uuid = generateUUID()
      this.carbonDioxideMonitors.unshift({
        'name': '',
        'serial': '',
        'id': uuid,
        'status': 'editable'
      })
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

      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'

      await axios.post(`/users/${this.currentUser.id}/carbon_dioxide_monitors.json`, toSave)
        .then(response => {
          console.log(response)
          if (response.status == 204 || response.status == 200) {
            this.message = response.data.message
            carbonDioxideMonitor['status'] = 'saved'
          }
        })
        .catch(error => {
          console.log(error)
            this.message = "Something went wrong with saving."
          // whatever you want
        })
      this.carbonDioxideMonitors.splice(carbonDioxideMonitorIndex, 1);
    },
    removeCO2Monitor(id) {
      const carbonDioxideMonitorIndex = this.carbonDioxideMonitors.findIndex(
        (carbonDioxideMonitor) => carbonDioxideMonitor.id == id
      );

      this.carbonDioxideMonitors.splice(carbonDioxideMonitorIndex, 1);
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
    async load() {
      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'

      await axios.get('/users/get_current_user.json')
        .then(response => {
          this.currentUser = response.data.currentUser;

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Could not get current user."
          // whatever you want
        })

      await axios.get(`/users/${this.currentUser.id}/carbon_dioxide_monitors.json`)
        .then(response => {
          const monitors = response.data.carbonDioxideMonitors;
          for (let monitor of monitors) {
            monitor['status'] = 'saved'
          }
          this.carbonDioxideMonitors = monitors

          // whatever you want
        })
        .catch(error => {
          console.log(error)
          this.message = "Failed to load carbon dioxide monitors."
          // whatever you want
        })
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
