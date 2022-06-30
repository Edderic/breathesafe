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
      <div v-for='carbonDioxideMonitor in carbonDioxideMonitors'>
        <div class='container'>
          <label>Brand</label>
          <input
            :value="carbonDioxideMonitor['brand']"
            @change="setCarbonDioxideMonitorBrand">
        </div>

        <div class='container'>
          <label>Model ({{ lengthMeasurementType }})</label>
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
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useEventStore } from './stores/event_store';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'App',
  components: {
    Event
  },
  computed: {
    ...mapWritableState(
        useProfileStore,
        [
          'carbonDioxideMonitors',
          'systemOfMeasurement'
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
