<template>
  <div class='body row'>
    <div class='col' v-show="focusTab == 'maps'">
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
          >
            <GMapMarker
                :key="index"
                v-for="(m, index) in displayables"
                :position="m.placeData.center"
                :clickable="true"
                :draggable="false"
                @click="this.clickMarker(m)"
            />
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
import Events from './events.vue';
import { useEventStores } from './stores/event_stores';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'MapEvents',
  components: {
    Events,
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ["focusTab", "focusSubTab", "signedIn", "markers"]),
    ...mapWritableState(useMainStore, ['center', 'zoom']),
    ...mapWritableState(
        useEventStores,
        [
          'displayables'
        ]
    ),

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

    await this.getCurrentUser();
    this.loadProfile()
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile']),
    clickMarker(displayable) {
      this.center = displayable.placeData.center
      for (let d of this.displayables) {
        if (d == displayable) {
          d.clicked = true
        } else {
          d.clicked = false
        }
      }

      let element_to_scroll_to = document.getElementById(`measurements-${displayable.id}`);
      element_to_scroll_to.scrollIntoView();
    },
    save() {
      // send data to backend.
    },
    setPlace(place) {
      console.log(place);
      const loc = place.geometry.location;
      this.center = { lat: loc.lat(), lng: loc.lng() };
      this.zoom = 15;
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

  .width {
    max-width: 70em;
  }

  @media (max-width: 70em) {
    .width {
      width: 100vw;
    }
  }

  .map {
    width: 100vw;
    height: 60vw;
  }

  @media (max-width: 840em) {
    .map {
      height: 30vw;
    }
  }

  @media ((max-height: 1200px) and (orientation: landscape)) {
    .map {
      height: 25vw;
    }
  }

  @media ((max-height: 1180px) and (orientation: portrait)) {
    .map {
      height: 25vw;
    }
  }


  @media ((max-height: 670px) and (orientation: landscape)) {
    .map {
      height: 15vw;
    }
  }


</style>
