<template>
  <div class='body row'>
    <div class='col'>
      <div class='row'>
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
              <GMapInfoWindow
                :closeclick="true"
                @closeclick="openMarker(null)"
                :opened="openedMarkerID === m.id"
                :options="{
                       pixelOffset: {
                         width: 10, height: 0
                       },
                       maxWidth: 700,
                }"
              >
                <div class='row'>
                  <div class='col absolute space-between icon-col'>
                    <div :class='{"icon": true, "clicked": isClicked("information")}' @click='clickIcon("information", m.id)'>ℹ️ </div>
                    <div :class='{"icon": true, "clicked": isClicked("risk")}' @click='clickIcon("risk", m.id)'>⚠️ </div>
                    <div :class='{"icon": true, "clicked": isClicked("CADR")}' @click='clickIcon("CADR", m.id)'>💨</div>
                    <div :class='{"icon": true, "clicked": isClicked("masking")}' @click='clickIcon("masking", m.id)'>😷</div>
                    <div :class='{"icon": true, "clicked": isClicked("occupancy")}' @click='clickIcon("occupancy", m.id)'>🕤</div>
                  </div>
                  <div class='col scrollable'>
                    <div :id='`information-${m.id}`'>{{ m.roomName }}</div>
                    <div>{{ m.placeData.formattedAddress }} </div>
                    <a v-if="m.placeData.website" :href="m.placeData.website">{{ m.placeData.website }}</a>
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>

                    <RiskTable
                      :id='`risk-${m.id}`'
                      :intervention="createIntervention(m)"
                      :maximumOccupancy="m.maximumOccupancy"
                    />
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>

                    <div class='centered'>
                      <TotalACHTable
                        :id='`CADR-${m.id}`'
                        :measurementUnits='measurementUnits'
                        :systemOfMeasurement='systemOfMeasurement'
                        :portableAch='m.portableAch'
                        :ventilationAch='m.ventilationAch'
                        :uvAch=0
                        :roomUsableVolumeCubicMeters='m.roomUsableVolumeCubicMeters'
                      />
                    </div>
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>
                    <div :id='`masking-${m.id}`' class='centered'>
                      <HorizontalStackedBar
                        :values="maskingValues(m)"
                        :colors="maskingColors(m)"
                        verticalPadding='0.20em'
                      />
                    </div>
                    <br>

                    <DayHourHeatmap
                      :id='`occupancy-${m.id}`'
                      :dayHours="m.occupancy.parsed"
                    />
                  </div>
                </div>
              </GMapInfoWindow>
            </GMapMarker>
          </GMapCluster>
        </GMapMap>
      </div>

      <div>
        <Events/>
      </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { MaskingBarChart } from './masks.js';
import { Intervention } from './interventions.js';
import DayHourHeatmap from './day_hour_heatmap.vue';
import HorizontalStackedBar from './horizontal_stacked_bar.vue';
import Events from './events.vue';
import RiskTable from './risk_table.vue';
import TotalACHTable from './total_ach_table.vue';
import { binValue, getColor, riskColorInterpolationScheme } from './colors';
import { getPlaceType } from './icons';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'MapEvents',
  components: {
    DayHourHeatmap,
    Events,
    HorizontalStackedBar,
    RiskTable,
    TotalACHTable
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useProfileStore, ["measurementUnits", 'systemOfMeasurement']),
    ...mapState(useMainStore, ["focusTab", "focusSubTab", "signedIn", "markers"]),
    ...mapWritableState(useMainStore, ['center', 'zoom', 'openedMarkerID']),
    ...mapWritableState(
        useEventStores,
        [
          'displayables'
        ]
    ),
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

    await this.load();
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
      return new Intervention(m, [])
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

      return `https://breathesafe.s3.us-east-2.amazonaws.com/images/generated/${placeType}--${color.letterGrade}.svg`
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
    top: 4.2em;
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
    width: 100vw;
    height: 32vh;
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

</style>
