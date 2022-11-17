<template>
  <div class='body grid'>
    <GMapMap
      :center="center"
      :zoom="zoom"
      map-type-id="terrain"
      class='map'
    >
      <GMapCluster
          :styles="[
            {
              textColor: 'black',
              url: 'https://raw.githubusercontent.com/googlemaps/v3-utility-library/37c2a570c318122df57b83140f5f54665b9359e5/packages/markerclustererplus/images/m1.png',
              height: 52,
              width: 53,
            },
            {
              textColor: 'black',
              url: 'https://raw.githubusercontent.com/googlemaps/v3-utility-library/37c2a570c318122df57b83140f5f54665b9359e5/packages/markerclustererplus/images/m2.png',
              height: 55,
              width: 56,
            },
            {
              textColor: 'black',
              url: 'https://raw.githubusercontent.com/googlemaps/v3-utility-library/37c2a570c318122df57b83140f5f54665b9359e5/packages/markerclustererplus/images/m3.png',
              height: 65,
              width: 66,
            },
            {
              textColor: 'black',
              url: 'https://raw.githubusercontent.com/googlemaps/v3-utility-library/37c2a570c318122df57b83140f5f54665b9359e5/packages/markerclustererplus/images/m4.png',
              height: 77,
              width: 78,
            },
            {
              textColor: 'black',
              url: 'https://raw.githubusercontent.com/googlemaps/v3-utility-library/37c2a570c318122df57b83140f5f54665b9359e5/packages/markerclustererplus/images/m5.png',
              height: 89,
              width: 90,
            },
          ]"
        :zoomOnClick='true'
      >
        <GMapMarker
            :key="index"
            v-for="(m, index) in displayables"
            :position="m.placeData.center"
            :clickable="true"
            :draggable="false"
            :icon="icon(m)"
            @click="openMarker(m.id)"
        >
        </GMapMarker>
      </GMapCluster>
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
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import Events from './events.vue';
import TotalACHTable from './total_ach_table.vue';
import AchToDuration from './ach_to_duration.vue';
import { binValue, getColor, riskColorInterpolationScheme } from './colors';
import { getPlaceType } from './icons';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'MapEvents',
  components: {
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
    ...mapState(useMainStore, ["focusTab", "focusSubTab", "signedIn", "markers"]),
    ...mapState(useEventStores, ["selectedMask"]),
    ...mapWritableState(useMainStore, ['center', 'zoom', 'openedMarkerID']),
    ...mapWritableState(
        useEventStores,
        [
          'displayables'
        ]
    ),
    cellCSS(){
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
  },
  async created() {
    // TODO: modify the store
    this.$getLocation()
      .then((coordinates) => {
        this.center = { lat: coordinates.lat, lng: coordinates.lng };
        this.zoom = 15;
      })
      .catch((error) => {
        console.log(error);
      });

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
        name: 'MapEvents',
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
    openMarker(id) {
      this.openedMarkerID = id
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
