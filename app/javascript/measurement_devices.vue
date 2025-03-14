<template>
  <div class='top-container'>
    <div class='flex align-items-center justify-content-center row'>
      <h2 class='tagline'>Measurement Devices</h2>
      <CircularButton text="+" @click="newDevice"/>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <div class='main'>
      <p class='narrow'>

Do you have a quantitative fit testing (QNFT) device? If so, please add information below so we could understand more about how fit testing data is generated, for quality control purposes. When fit testing, these devices will show up as selectable options. In terms of reporting, e.g. a research paper, aggregate data might be reported. For example, "QNFT results in Breathesafe's data set had 200 entries, and QNFT devices were mostly done using TSI 8020A. Median calibration date was 2013 (11 years ago), and min and max are 2009 and 2018."

      </p>

      <div class='centered cards'>
        <table class='mobile-card'
          v-for='r in measurementDevices' text='Edit' @click='visit(r.id)'>
          <tr>
            <th>Type</th>
            <td>
                {{r.measurement_device_type}}
            </td>
            <th>Manufacturer</th>
            <td>
                {{r.manufacturer}}
            </td>
          </tr>
          <tr>
            <th>Model</th>
            <td>
                {{r.model}}
            </td>
            <th>Serial</th>
            <td>
              {{r.serial}}
            </td>
          </tr>
          <tr>
            <th>Notes</th>
            <td colspan='3'>
                {{r.notes}}
            </td>
          </tr>
          <tr>
            <th>Removed from service</th>
            <td colspan='3'>
                {{r.remove_from_service}}
            </td>
          </tr>
        </table>

        <table class='card'>
          <thead>
            <tr>
              <th>Type</th>
              <th>Manufacturer</th>
              <th>Model</th>
              <th>Serial</th>
              <th>Notes</th>
              <th>Removed from service</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in measurementDevices' text='Edit' @click='visit(r.id)'>
              <td >
                {{r.measurement_device_type}}
              </td>
              <td >
                {{r.manufacturer}}
              </td>
              <td >
                {{r.model}}
              </td>
              <td >
                {{r.serial}}
              </td>
              <td >
                {{r.notes}}
              </td>
              <td >
                {{r.remove_from_service}}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ClosableMessage from './closable_message.vue'
import CircularButton from './circular_button.vue'
import { setupCSRF } from './misc.js'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import SearchIcon from './search_icon.vue'
import { useManagedUserStore } from './stores/managed_users_store.js'
import { useMeasurementDeviceStore } from './stores/measurement_devices_store.js'

export default {
  name: 'MeasurementDevices',
  components: {
    CircularButton,
    ClosableMessage,
    SearchIcon
  },
  data() {
    return {
      measurement_devices: []
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
          'messages'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'messages'
        ]
    ),
    ...mapState(
        useMeasurementDeviceStore,
        [
          'measurementDevices'
        ]
    ),
    ...mapWritableState(
        useManagedUserStore,
        [
          'managedUsers'
        ]
    ),
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadMeasurementDevices()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    ...mapActions(useMeasurementDeviceStore, ['loadMeasurementDevices']),
    async newDevice() {
      setupCSRF();

      this.$router.push(
        {
          'name': 'NewMeasurementDevice',
        }
      )
    },

    visit(id) {
      this.$router.push({
        name: 'ShowMeasurementDevice',
        params: {
          id: id
        },
      })
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  p {
    margin: 1em;
  }

  th, td {
    padding: 0.5em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }

  .main {
    display: flex;
    align-items: center;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  img {
    width: 30em;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .align-items-center {
    align-items: center;
  }

  .justify-content-center {
    justify-content: center;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  thead th {
    background-color: #eee;
    padding: 1em;
  }

  .colored-cell {
    text-align: center;
  }

  .narrow {
    max-width: 50em;
  }

  th {
    background-color: #eee;
  }

  .mobile-card {
    display: none;
    cursor: pointer;
  }

  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .card {
      display: none;
    }
    .mobile-card {
      display: block;
    }

    .cards {
      display: flex;
      flex-direction: column;
    }

    .top-container {
      margin-bottom: 5em;
    }
  }
</style>
