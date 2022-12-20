<template>
  <div class='body grid'>
    <table class='grade-info' v-if='showGradeInfo'>
      <tr>
        <th>Grade</th>
        <th>Text</th>
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
    <GMapMap
      :center="center"
      :zoom="zoom"
      map-type-id="terrain"
      class='map'
      v-if='!showGradeInfo'
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
import { getPlaceType } from './icons';
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
    ...mapState(useProfileStore, ["measurementUnits", 'systemOfMeasurement']),
    ...mapState(useMainStore, ["centerMapTo"]),
    ...mapState(useEventStores, ['showGradeInfo', "selectedMask"]),

    ...mapWritableState(useMainStore, ['center', 'whereabouts', 'zoom', 'openedMarkerID']),
    ...mapWritableState(
        useEventStores,
        [
          'displayables'
        ]
    ),
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
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile']),
    ...mapActions(useEventStores, ['load']),
    createIntervention(m) {
      return new Intervention(m, [this.selectedMask])
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

      const placeType = getPlaceType(marker.placeData.types)

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

  .column {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  button {
    padding: 1em 3em;
  }

  .map {
    height: 90vh;
  }

  .icon {
    font-size: large;
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
  }

  p {
    padding: 1em;
  }

  .grid {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;

  }

  .grade-info {
    text-align: center;
  }

  @media (max-width: 1400px) {
    .grid {
      display: flex;
      flex-direction: column;
    }
    .map {
      height: 40vh;
    }
  }

</style>
