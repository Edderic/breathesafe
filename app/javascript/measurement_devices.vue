<template>
  <div>
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
      <div class='centered'>
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Manufacturer</th>
              <th>Model</th>
              <th>Serial</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for='r in measurement_devices' text='Edit' @click='visit(r.id)'>
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
    ...mapWritableState(
        useManagedUserStore,
        [
          'managedUsers'
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity',
          'genderAndSex',
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
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    async newDevice() {
      setupCSRF();

      this.$router.push(
        {
          'name': 'NewMeasurementDevice',
        }
      )
    },

    async loadMeasurementDevices() {
      await axios.get(
        `/measurement_devices.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.measurement_devices) {
            this.measurement_devices = data.measurement_devices
          }
        })
        .catch(error => {
          if (error && error.response && error.response.data && error.response.data.messages) {
            this.addMessages(error.response.data.messages)
          } else {
            this.addMessages([error.message])
          }
        })
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
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
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
</style>
