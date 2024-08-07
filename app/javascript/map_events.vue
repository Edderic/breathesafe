<template>
  <div class='body grid'>
    <div v-show='display == "gradeInfo"' class='centered column'>
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

    <div v-show='display == "filter"' class='filters col scrollable'>

      <div class='row centered padded topFilterRow'>
        <div>
          <input type="checkbox" :value='filterForDraft' @click="setDraft($route.query.draft)" id='filterForDraft'>
          <label for="filterForDraft">
          Draft
          </label>
        </div>
      </div>

      <div class='location-types'>
        <div :class='{"location-type": true, row: true, "align-items-center": true, clicked: placeTypePicked == k}' v-for='(v, k) in placeTypeCounts' @click='pickPlaceKind(k)'>
          <span class='icon'>{{icons[k]}}</span>
          <label :for="k">
            {{k}}
          </label>
          <span>{{v}}</span>
        </div>
      </div>
    </div>
    <GMapMap
      :center="center"
      :zoom="zoom"
      map-type-id="terrain"
      class='map'
      v-show='display == "map"'
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
import Button from './button.vue';
import CircularButton from './circular_button.vue';
import { binValue, getColor, gradeColorMapping, riskColorInterpolationScheme } from './colors';
import { getPlaceType, ICONS } from './icons';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'Venues',
  components: {
    Button,
    CircularButton,
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
    ...mapState(useEventStores, ['displayables', "filterForDraft", "selectedMask", 'placeTypeCounts', 'updateSearch']),

    ...mapWritableState(useMainStore, ['center', 'whereabouts', 'zoom', 'openedMarkerID']),
    ...mapWritableState(
        useEventStores,
        [
          'display',
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
  },
  data() {
    return {
      iconClicked: null
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'showAnalysis']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useEventStores, ['load', 'setDisplayables']),
    setDraft(val) {
      let query = JSON.parse(JSON.stringify(this.$route.query))
      let newQuery = {draft: val !== 'true'}

      Object.assign(query, newQuery)

      this.$router.push({ name: 'Venues', query: query })
    },
    pickPlaceKind(placeType) {
      let prevQuery = JSON.parse(JSON.stringify(this.$route.query))

      if (placeType == this.$route.query['placeType']) {
        delete prevQuery['placeType']
      } else {
        Object.assign(prevQuery, { placeType: placeType })
      }

      this.$router.push({
        name: 'Venues',
        query: prevQuery
      })
    },
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
    top: 0;
    left: 0;
    height: 90vh;
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

  .clicked {
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
    overflow-y: auto;
  }

  p {
    padding: 1em;
  }

  .padded {
    padding: 0.5em;
  }

  .grid {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;

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

  .location-type:hover {
    background-color: #efefef;
    cursor: pointer;
  }

  .location-types {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
  }
  .topFilterRow {
    border-bottom: 1px solid #eee;
  }

  @media (max-width: 700px) {
    .location-type {
      width: 100vw;
      display: flex;
      justify-content: center;
    }
    .location-types {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
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

    .filters {
      width: 100vw;
    }

  }

</style>
