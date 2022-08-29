<template>
  <tr class='clickable' :class='{ clicked: this.measurements.clicked }' :id='`measurements-${this.measurements.id}`'>
    <td>
      <div class='emojis'>
      {{emojis}}
      </div>
    </td>
    <td @click="centerMapTo(this.measurements.id)" >{{this.measurements.roomName}}</td>
    <td @click="centerMapTo(this.measurements.id)" >{{this.measurements.placeData.formattedAddress}}</td>
    <td class='containing-cell'>
      <ColoredCell
        class='risk-score'
        :colorScheme="colorInterpolationScheme"
        :maxVal=1
        :value='measurements.risk'
        :text='gradeLetter(this.measurements.risk)'
        :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black' }"
        :title='roundOut(measurements.risk, 6)'
        :exception='{ "text": "NA", "value": 0, color: {r: 200, g: 200, b: 200}}'
      />
    </td>
    <td class='containing-cell'>
      <ColoredCell
        class='risk-score'
        :colorScheme="colorInterpolationScheme"
        :maxVal=1
        :value='roundOut(nullIntervention.computeRisk(1), 6)'
        :text='gradeLetter(nullIntervention.computeRisk(1))'
        :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black' }"
        :title='roundOut(nullIntervention.computeRisk(1), 6)'
      />
    </td>
    <td>
      <router-link :to='link' @click="showAnalysis(this.measurements.id)">Show Analysis</router-link>
    </td>
    <td v-if='adminView'>{{ measurements.authorId }}</td>
    <td v-if='adminView && approvable'>
      <button @click='approve'>
        Approve
      </button>
    </td>
    <td v-if='adminView && !approvable'>
      Approved
    </td>
  </tr>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios';
import ColoredCell from './colored_cell.vue';
import { Intervention } from './interventions.js';
import { getPlaceIcon } from './icons.js';
import { binValue } from './colors.js';
import { useEventStores } from './stores/event_stores';
import { useEventStore } from './stores/event_store';
import { useMainStore } from './stores/main_store';
import { usePrevalenceStore } from './stores/prevalence_store';
import { useProfileStore } from './stores/profile_store';
import { useShowMeasurementSetStore } from './stores/show_measurement_set_store';
import { findCurrentOccupancy, filterEvents, getWeekdayText, round, setupCSRF } from './misc'
import { riskColorInterpolationScheme } from './colors.js'
import { mapWritableState, mapState, mapActions } from 'pinia'

export default {
  name: 'MeasurementsRow',
  components: {
    ColoredCell
  },
  computed: {
    ...mapState(useProfileStore, ['eventDisplayRiskTime']),
    ...mapState(usePrevalenceStore, ['numPositivesLastSevenDays', 'numPopulation', 'uncountedFactor', 'maskType']),
    ...mapState(useEventStore, ['infectorActivityTypeMapping']),
    ...mapState(useEventStores, ['selectedMask']),
    ...mapState(useMainStore, ['isAdmin']),
    ...mapState(
        useShowMeasurementSetStore,
        [
          'roomName',
          'activityGroups',
          'ageGroups',
          'carbonDioxideActivities',
          'ventilationCo2AmbientPpm',
          'ventilationCo2MeasurementDeviceModel',
          'ventilationCo2MeasurementDeviceName',
          'ventilationCo2MeasurementDeviceSerial',
          'ventilationCo2SteadyStatePpm',
          'duration',
          'private',
          'formatted_address',
          'infectorActivity',
          'infectorActivityTypeMapping',
          'maskTypes',
          'numberOfPeople',
          'occupancy',
          'maximumOccupancy',
          'placeData',
          'portableAirCleaners',
          'rapidTestResult',
          'rapidTestResults',
          'roomHeightMeters',
          'roomLengthMeters',
          'roomWidthMeters',
          'roomUsableVolumeFactor',
          'singlePassFiltrationEfficiency',
          'startDatetime',
          'susceptibleActivities',
          'susceptibleActivity',
          'susceptibleAgeGroups',
          'ventilationNotes'
        ]
    ),
    adminView() {
      return this.isAdmin && this.$route.query['admin-view'] == 'true'
    },
    approvable() {
      return this.measurements.private == 'public' && (!this.measurements.approvedById && !this.measurements.authoredByAdmin)
    },

    colorInterpolationScheme() {
      return riskColorInterpolationScheme
    },
    emojis() {
      let types = this.measurements.placeData.types
      return getPlaceIcon(types)
    },
    link() {
      return `/analytics/${this.measurements.id}`
    },
    startDatetimeParsed() {
      let dt = new Date(this.measurements.startDatetime)
      let options = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
      return `${dt.toLocaleDateString(undefined, options)} ${dt.toLocaleTimeString()}`
    },
    nullIntervention() {
      return new Intervention(
        this.measurements,
        [
          this.selectedMask
        ]
      )
    }
  },
  data() {
    return {
    }
  },
  props: {
    measurements: Object,
  },
  methods: {
    async approve() {
      setupCSRF();

      await axios.post(
        `/events/${this.measurements.id}/approve.json`
      )
        .then(response => {
          this.message = data.message
          this.$router.push({
            name: 'MapEvents',
            query: {
              'admin-view': true
            }
          })

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load profile."
          // whatever you want
        })
    },
    getOpenHours(x) {
      return getWeekdayText(x)
    },
    gradeLetter(risk) {
      return binValue(riskColorInterpolationScheme, risk)['letterGrade']
    },
    ...mapActions(
        useMainStore,
        [
          'centerMapTo',
          'showAnalysis'
        ]
    ),
    roundOut(x, digits) {
      return round(x, digits)
    }
  },
}
</script>

<style scoped>
  tr:hover.clickable {
    background-color: #efefef;
    cursor: pointer;
  }
  .clicked {
    background-color: #e6e6e6;
  }
  td {
    padding: 1em;
    text-align: center;
    margin: auto;
    vertical-align: middle;
    border-top: 1px solid #e6e6e6;
    border-bottom: 1px solid #e6e6e6;
  }
  td.containing-cell {
    width: 7em;
  }
  button {
    padding: 1em 3em;
  }

  .tag {
  }

  .col {
    display: flex;
    flex-direction: column;
  }

  .horizontally-center {
    display: flex;
    justify-content: center;
  }

  .margined {
    margin: 1em;
  }

  .emojis {
    font-size: xx-large;
    text-shadow: 1px 1px 2px black;
  }

  .risk-score {
    border-radius: 100%;
    width: 2em;
    height: 2em;
  }
</style>
