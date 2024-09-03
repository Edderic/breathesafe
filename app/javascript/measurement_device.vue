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

Do you have a quantitative fit testing (QNFT) device? If so, please add information below so we could understand more about how fit testing data is generated, for quality control purposes. When fit testing, these devices will show up as selectable options. In terms of reporting, e.g. a research paper, aggregate data might be reported. For example, "QNFT results in Breathesafe's data set had 200 entries, and QNFT devices were mostly done using TSI 8020A. Median calibration date was 2013 (11 years ago), and min and max are 2009 and 2018."

        </p>
      <div class='centered'>
        <table>
          <tbody>
            <tr>
              <th>Measurement Device Type</th>
              <select v-model='quantitativeTestingMode' :disabled='mode == "Show"'>
                <option>QNFT</option>
              </select>
            </tr>
            <tr>
              <th>Manufacturer</th>
              <input type="text" placeholder="e.g. TSI" v-model='measurement_device.manufacturer'
                :disabled='mode == "Show"'
              >
            </tr>
            <tr>
              <th>Model</th>
              <input type="text" placeholder="e.g. 8020A" v-model='measurement_device.model'
                :disabled='mode == "Show"'
              >
            </tr>
            <tr>
              <th>Serial</th>
              <input type="text" placeholder="" v-model='measurement_device.serial'
                :disabled='mode == "Show"'
              >
            </tr>
            <tr>
              <th>Notes</th>
              <textarea type="textarea" rows=5 columns=80  v-model='measurement_device.notes'
                :disabled='mode == "Show"'
                >{{ measurement_device.notes }}</textarea>
            </tr>
          </tbody>
        </table>

      </div>
        <div class="row justify-content-center">
          <Button class='button' text="Edit" @click='mode = "Edit"' v-if='mode == "Show"'/>
          <Button class='button' text="Delete" @click='deleteMeasurementDevice' v-if='deletable && (mode != "Show")'/>
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
      measurement_device: {
        manufacturer: '',
        model: '',
        serial: '',
        notes: ''
      },
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
        useProfileStore,
        [
          'profileId',
          'readyToAddFitTestingDataPercentage',
          'nameComplete',
          'genderAndSexComplete',
          'raceEthnicityComplete',
          'facialMeasurementsComplete',
          'loadFacialMeasurements',
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
    displayables() {
      if (this.search == "") {
        return this.measurementDevice
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.measurementDevice.filter(
          function(mu) {
            return mu.firstName.toLowerCase().match(lowerSearch)
              || mu.lastName.toLowerCase().match(lowerSearch)

          }
        )
      }
    },
    facialMeasurementsIncomplete() {
      return this.facialMeasurementsLength == 0
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
    }

    if (this.$route.name == "NewMeasurementDevice") {
      this.mode = "New"
    }
    this.$watch(
      () => this.$route.params,
      (toParams, fromParams) => {
        if (this.$route.name == "NewMeasurementDevice") {
          this.mode = "New"
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
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
