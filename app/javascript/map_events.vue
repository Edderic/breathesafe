<template>
  <div class='body grid'>
    <div v-if='display == "gradeInfo"' class='centered column'>
      <table class='grade-info'>
        <tr>
          <th>Grade</th>
          <th>Probability of Transmission</th>
        </tr>

        <tr v-for='item in gradeColors'>
          <td>
            <ColoredCell
              class='risk-score'
              :colorScheme="riskColorScheme"
              :maxVal=1
              :backgroundColor='item.color'
              :text='item.grade'
              :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black', 'border-radius': '100%', 'width': '2em', 'height': '2em' }"
            />
          </td>
          <td>{{ item.text }}</td>
        </tr>
      </table>
    </div>

    <div v-if='display == "filter"' class='filters col scrollable'>
      <div class='row'>
        <input type="checkbox" v-model='filterForDraft' id='filterForDraft'>
        <label for="filterForDraft">
        Draft
        </label>
      </div>
      <div class='location-types'>
        <div class='row centered' v-for='(v, k) in icons'>
          <span class='icon'>{{v}}</span>
          <label :for="k">
            {{k}}
          </label>
        </div>
      </div>
    </div>
    <GMapMap
      :center="center"
      :zoom="zoom"
      map-type-id="terrain"
      class='map'
      v-if='display == "map"'
    >
        <GMapMarker
            :key="index"
            v-for="(m, index) in displayables"
            :position="m.placeData.center"
            :clickable="true"
            :draggable="false"
            :icon="icon(m)"
            @click="centerMapTo(m.id)"
        >
          <GMapInfoWindow :opened="m.id == openedMarkerId">

            <table>
              <tr>
                <th>Room Name</th>
                <td>
                  {{ m.roomName }}
                </td>
              </tr>
              <tr>
                <th v-if='m.placeData && m.placeData.website'>Website</th>
                <td>
                  <a :href="m.placeData && m.placeData.website" target='_blank'>
                    {{ shortenLink(m.placeData.website, 30) }}
                  </a>
                </td>
              </tr>
              <tr>
                <th>Links</th>
                <td>
                  <div class='column'>
                    <a :href='`https://www.google.com/maps/place/?q=place_id:${m.placeData.placeId}`' target='_blank'>📍 Google Maps</a>
                    <router-link :to='{ name: "Analytics", params: {id: m.id}}' @click="showAnalysis(m.id)">
                      ☣️  Risk Analysis
                    </router-link>
                    <router-link :to='{ name: "UpdateOrCopyMeasurements", params: {action: "update", id: m.id} }' v-if='currentUser && (m.authorId == currentUser.id || currentUser.admin)'>
                      ✏️  Update
                    </router-link>
                    <router-link :to='{ name: "UpdateOrCopyMeasurements", params: {action: "copy", id: m.id} }' v-if='showAddNewMeasurements'>
                      ➕ Add New Measurements
                    </router-link>
                  </div>
                </td>
              </tr>
            </table>
          </GMapInfoWindow>
        </GMapMarker>
    </GMapMap>
    <Events/>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { displayCADR } from './misc.js';
import { MaskingBarChart } from './masks.js';
import { Intervention } from './interventions.js';
import CleanAirDeliveryRateTable from './clean_air_delivery_rate_table.vue';
import ColoredCell from './colored_cell.vue';
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import Events from './events.vue';
import TotalACHTable from './total_ach_table.vue';
import AchToDuration from './ach_to_duration.vue';
import { binValue, getColor, gradeColorMapping, riskColorInterpolationScheme } from './colors';
import { getPlaceType, ICONS } from './icons';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'Venues',
  components: {
    ColoredCell,
    CleanAirDeliveryRateTable,
    DayHourHeatmap,
    Events,
    HorizontalStackedBar,
    TotalACHTable,
    AchToDuration
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ['currentUser']),
    ...mapState(useProfileStore, ["measurementUnits", 'systemOfMeasurement']),
    ...mapState(useMainStore, ["centerMapTo", 'openedMarkerId']),
    ...mapState(useEventStores, ['display', "selectedMask"]),

    ...mapWritableState(useMainStore, ['center', 'whereabouts', 'zoom', 'openedMarkerID']),
    ...mapWritableState(
        useEventStores,
        [
          'displayables',
          'filterForDraft',
          'placeTypePicked'
        ]
    ),
    icons() {
      return ICONS;
    },
    gradeColors() {
      let objs = []
      let thing

      for (let gradeToColor in gradeColorMapping) {
          thing = gradeColorMapping[gradeToColor]
          objs.push({
            grade: gradeToColor,
            text: `Between ${thing.bounds[0]} and ${thing.bounds[1]}`,
            color: `rgb(${thing.color['r']}, ${thing.color['g']}, ${thing.color['b']} )`
          })
      }

      return objs
    },

    cellCSS(){
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
    showAddNewMeasurements() {
      return true
    },
  },
  async created() {
    // TODO: modify the store

    // TODO: handle case where no one is signed in
  },
  data() {
    return {
      iconClicked: null
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'showAnalysis']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useEventStores, ['load']),
    createIntervention(m) {
      return new Intervention(m, [this.selectedMask])
    },
    shortenLink(link, allowableLength) {
      if (!link) {
        return link
      }
      let length = link.length
      let suffix = ''

      if (link.length > allowableLength) {
        length = allowableLength
        suffix = '...'
      }

      return link.substring(0, allowableLength) + suffix
    },
    isClicked(value) {
      return this.$route.query['iconFocus'] == value
    },
    clickIcon(value, id) {
      let prevQuery = JSON.parse(JSON.stringify(this.$route.query))
      prevQuery['iconFocus'] = value

      this.$router.push({
        name: 'Venues',
        query: prevQuery
      })

      let element_to_scroll_to = document.getElementById(`${value}-${id}`);
      element_to_scroll_to.scrollIntoView();
    },
    icon(marker) {
      let color = binValue(riskColorInterpolationScheme, marker.risk || 0)

      let placeType;

      if (marker && marker.placeData && marker.placeData.types) {
        placeType = getPlaceType(marker.placeData.types)
      } else {
        placeType = 'premise'
      }

      return `${window.gon.S3_HTTPS}/images/generated/${placeType}--${color.letterGrade}.svg`
    },
    gradeLetter(marker) {
      return binValue(riskColorInterpolationScheme, marker.risk)['upperColor']['letterGrade']
    },
    maskingValues(m) {
      return new MaskingBarChart(m.activityGroups).maskingValues()
    },
    maskingColors(m) {
      return new MaskingBarChart(m.activityGroups).maskingColors()
    },
    nullIntervention(m) {
      return new Intervention(m, [])
    }
  },
}
</script>


<style scoped>
  .col {
    display: flex;
    flex-direction: column;
  }
  .row {
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
  .body {
    position: absolute;
    top: 3.2em;
    width: 100vw;
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
    align-items: center;
  }

  .column {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  button {
    padding: 1em 3em;
  }

  .filters {
    position: relative;
    top: 5em;
    left: 0;
    height: 80vh;
  }
  .map {
    height: 90vh;
  }

  .icon {
    font-size: 2em;
    padding-top: 0.125em;
    padding-bottom: 0.125em;
    padding-right: 0.25em;
    padding-left: 0.25em;
    text-shadow: 1px 1px 2px black;
  }

  .icon:hover {
    background-color: #efefef;
  }

  .icon.clicked {
    background-color: #e6e6e6;
  }

  .absolute {
    position: absolute;
  }

  .icon-col {
    background-color: #ccc;
    padding-right: 0.25em;
    padding-left: 0.25em;
    height: 9rem;
  }

  .space-between {
    display: flex;
    justify-content: space-between;
  }
  .scrollable {
    margin-left: 3em;
    overflow-y: auto;
  }

  p {
    padding: 1em;
  }

  .grid {
    display: flex;
    flex-direction: row;

  }

  .align-items-center {
    display: flex;
    align-items: center;
  }

  .grade-info {
    text-align: center;
    max-width: 20em;
  }

  th {
    padding: 0 1em;
  }

  .location-types {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  @media (max-width: 1400px) {
    .grid {
      display: flex;
      flex-direction: column;
    }
    .map {
      max-height: 33%;
    }
    .body {
      height: 90vh;
    }
  }

</style>
