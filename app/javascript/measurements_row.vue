<template>
  <tr class='clickable' :class='{ clicked: this.measurements.clicked }' :id='`measurements-${this.measurements.id}`'>
    <td>
      <div class='emojis'>
      {{emojis}}
      </div>
    </td>
    <td @click="centerMapTo(this.measurements.id)" >{{this.measurements.roomName}}</td>
    <td @click="centerMapTo(this.measurements.id)" >{{this.measurements.placeData.formattedAddress}}</td>
    <td class='containing-cell score' @click="showAnalysis(this.measurements.id)">
      <router-link :to='link' v-if='measurements.status == "complete"'>
        <ColoredCell
          class='risk-score'
          :colorScheme="colorInterpolationScheme"
          :maxVal=1
          :value='roundOut(this.measurements.risk, 6)'
          :text='gradeLetter(this.measurements.risk)'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black' }"
          :title='roundOut(this.measurements.risk, 6)'
        />
      </router-link >
        <ColoredCell
          v-if='measurements.status == "draft"'
          :colorScheme="colorInterpolationScheme"
          :maxVal=1
          :value=1
          text='Draft'
          :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'background-color': 'grey' }"
          title='Draft'
        />
    </td>
    <td v-if='permittedGeolocation'>
      {{ measurements.distance }}
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
import { Mask } from './masks.js'

export default {
  name: 'MeasurementsRow',
  components: {
    ColoredCell
  },
  computed: {
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
      if (types) {
        return getPlaceIcon(types)
      }

      return getPlaceIcon(['premise'])
    },
    link() {
      return `/analytics/${this.measurements.id}`
    },
  },
  data() {
    return {
    }
  },
  created() {
  },
  props: {
    measurements: Object,
    permittedGeolocation: Boolean
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
            name: 'Venues',
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

  a {
    text-decoration: none;
  }

  .score:hover:after {
    content: "Click grade for full analysis"
  }

  @media (max-width: 800px) {
    .middle-controls {
      display: flex;
      flex-direction: column;
    }
    .controls {
      width: auto;
    }
    .desktop {
      display: none;
    }
  }
  @media (min-width: 800px) {
    .middle-controls {
      display: flex;
      flex-direction: row;
    }
    .desktop {
      display: table-cell;
    }
  }
</style>
