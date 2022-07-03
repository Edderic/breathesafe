<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Profile</h2>
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
          <label>Name</label>
          <input
            :value="carbonDioxideMonitor['name']"
            @change="setCarbonDioxideMonitorName($event, carbonDioxideMonitor['id'])">
        </div>

        <div class='container'>
          <label>Serial</label>
          <input
            :value="carbonDioxideMonitor['serial']"
            @change='setCarbonDioxideMonitorSerial($event, carbonDioxideMonitor["id"])'>
        </div>

        <div class='container'>
          <button @click='removeCO2Monitor($event, carbonDioxideMonitor["id"])'>Remove</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
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
  created() { },
  data() {
    return {
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab']),
    ...mapActions(useProfileStore, ['setSystemOfMeasurement']),
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
