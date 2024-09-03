<template>
  <div>
    <div class='flex align-items-center justify-content-center row'>
      <h2 class='tagline'>Measurement Device</h2>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <div class='main'>
        <p class='narrow'>

Do you have a quantitative fit testing (QNFT) device? If so, please add information below so we could understand more about how fit testing data is generated, for quality control purposes. When fit testing, these devices will show up as selectable options.

        </p>

        <p class='narrow'>
        In terms of reporting, e.g. a research paper, aggregate data might be reported. For example, "QNFT results in Breathesafe's data set had 200 entries, and QNFT devices were mostly done using TSI 8020A. Median calibration date was 2013 (11 years ago), and min and max are 2009 and 2018."

        </p>
      <div class='centered'>
        <table>
          <tbody>
            <tr>
              <th>Measurement Device Type</th>
              <td>
                <select v-model='measurement_device.measurement_device_type' :disabled='mode == "Show"'>
                  <option>QNFT</option>
                </select>
              </td>
            </tr>
            <tr>
              <th>Manufacturer</th>
              <td>
                <input type="text" placeholder="e.g. TSI" v-model='measurement_device.manufacturer'
                  :disabled='mode == "Show"'
                >
              </td>
            </tr>
            <tr>
              <th>Model</th>
              <td>
                <input type="text" placeholder="e.g. 8020A" v-model='measurement_device.model'
                  :disabled='mode == "Show"'
                >
              </td>
            </tr>
            <tr>
              <th>Serial</th>
              <td>
                <input type="text" placeholder="" v-model='measurement_device.serial'
                  :disabled='mode == "Show"'
                >
              </td>
            </tr>
            <tr>
              <th>Notes</th>
              <td>
              <textarea type="textarea" rows=5 columns=80  v-model='measurement_device.notes'
                placeholder="e.g. Calibration dates, and results, if possible."
                :disabled='mode == "Show"'
                >{{ measurement_device.notes }}</textarea>
              </td>
            </tr>
            <tr>
              <th>Removed from service</th>
              <td>
                <input type="checkbox" v-model='measurement_device.remove_from_service'
                  :disabled='mode == "Show"'
                >
              </td>
            </tr>
          </tbody>
        </table>

      </div>
        <div class="row justify-content-center">
          <Button class='button' text="Edit" @click='mode = "Edit"' v-if='mode == "Show"'/>
          <Button class='button' text="Delete" @click='deleteMeasurementDevice' v-if='mode == "Edit" '/>
          <Button class='button' text="Save" @click='saveMeasurementDevice' v-if='mode == "New" || mode == "Edit"'/>
          <Button class='button' text="Cancel" @click='handleCancel' v-if='(mode == "New" || mode == "Edit")'/>
        </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import CircularButton from './circular_button.vue'
import ColoredCell from './colored_cell.vue'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import { userSealCheckColorMapping } from './colors.js'
import { RespiratorUser } from './respirator_user.js'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { useManagedUserStore } from './stores/managed_users_store.js'
import { useMeasurementDeviceStore } from './stores/measurement_devices_store.js'

export default {
  name: 'MeasurementDevice',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
  },
  data() {
    return {
      mode: 'Edit'
    }
  },
  props: {
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
          'messages'
        ]
    ),
    ...mapWritableState(
        useMeasurementDeviceStore,
        [
          'measurement_device'
        ]
    ),
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else if (this.$route.params.id){
      this.id = this.$route.params.id
      this.loadMeasurementDevice(this.id)
    }

    if (this.$route.name == "NewMeasurementDevice") {
      this.mode = "New"
      this.measurement_device = {
        id: null,
        device_type: '',
        anufacturer: '',
        model: '',
        serial: '',
        notes: ''
      }

    }
    else if (this.$route.name == "ShowMeasurementDevice") {
      this.mode = "Show"
    }

    this.$watch(
      () => this.$route.params,
      (toParams, fromParams) => {
        if (this.$route.name == "NewMeasurementDevice") {
          this.mode = "New"
        }
        else if (this.$route.name == "ShowMeasurementDevice") {
          this.mode = "Show"
        }
        if (toParams['id'] && this.$route.name == "ShowMeasurementDevice") {
          this.id = toParams.id
          this.loadMeasurementDevice(this.id)
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useMeasurementDeviceStore, ['loadMeasurementDevice']),
    handleCancel() {
      if (this.mode == 'New') {
        this.$router.push(
          {
            name: "MeasurementDevices"
          }
        )
      } else {
        this.mode = 'Show'
      }
    },
    runValidations() {
      let arrayOfProperties = [
        'measurement_device_type',
        'manufacturer',
        'model',
      ]

      for(let a of arrayOfProperties) {
        if (!this.measurement_device[a]) {
          this.addMessages([`Please select a ${a}.`])
        }
      }
    },
    async deleteMeasurementDevice() {
      setupCSRF();

      if (this.id) {
        await axios.delete(
          `/measurement_devices/${this.id}.json`, {
            measurement_device: this.measurement_device,
          }
        )
          .then(response => {
            this.$router.push({
              path: `/measurement_devices`,
              force: true
            })
          })
          .catch(error => {
            if (error && error.response && error.response.data && error.response.data.messages) {
              this.addMessages(error.response.data.messages)
            } else {
              this.addMessages(
                [error.message]
              )
            }
          })
      }
    },
    async saveMeasurementDevice() {
      this.runValidations()

      if (this.messages.length > 0) {
        return
      }

      setupCSRF();

      if (this.id) {
        await axios.put(
          `/measurement_devices/${this.id}.json`, {
            measurement_device: this.measurement_device,
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            // this.mode = 'Show'
            this.$router.push({
              path: `/measurement_devices/${this.id}`,
              force: true
            })
          })
          .catch(error => {
            //  TODO: actually use the error message
            this.messages.push({
              str: "Failed to update fit test."
            })
          })
      } else {
        if (this.messages.length > 0) {
          return
        }

        // create
        await axios.post(
          `/measurement_devices.json`, {
            measurement_device: this.measurement_device,
          }
        )
          .then(response => {
            let data = response.data

            // TODO: could get the id from data
            // We could save it
            // whatever you want

            this.id = response.data.measurement_device.id

            // We assume that the user hits save first at the "Mask" section.
            // It might not be always the case, but good enough

            this.$router.push({
              name: 'MeasurementDevices',
            })
          })
          .catch(error => {
            //  TODO: actually use the error message
            if (error && error.response && error.response.data && error.response.data.messages) {
              this.addMessages(error.response.data.messages)
            } else {
              this.addMessages(
                [error.message]
              )
            }
          })
      }
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
