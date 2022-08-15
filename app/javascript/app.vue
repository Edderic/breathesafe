<template>
  <div class='column'>
    <NavBar></NavBar>

    <div class='body row'>
      <div class='col' v-show="focusTab == 'maps'">
        <div class='row'>
          <GMapMap
              :center="center"
              :zoom="zoom"
              map-type-id="terrain"
              class='map'
          >
            <GMapCluster>
              <GMapMarker
                  :key="index"
                  v-for="(m, index) in markers"
                  :position="m.center"
                  :clickable="true"
                  :draggable="true"
                  @click="center=m.center"
              />
            </GMapCluster>
          </GMapMap>
        </div>

        <div>
          <Events v-show='focusTab == "maps"'/>
        </div>
      </div>
      <Tabs v-if='focusTab == "events"'/>
      <Prevalence v-if='focusTab == "events" && focusSubTab == "Prevalence"'/>
      <Analytics class='width' v-if='focusTab == "Analytics"'/>
      <ShowMeasurementSet v-if='focusTab == "events" && focusSubTab == "Measures"'/>
      <AddMeasurements v-if='focusTab == "event" && signedIn'/>
      <Profile v-if='focusTab == "profile" && signedIn'/>
      <Registration v-if='!signedIn && focusTab == "register"'/>
      <Confirmation v-if='!signedIn && focusTab == "confirmation"'/>
      <SignIn v-if='!signedIn && focusTab == "signIn"'/>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Analytics from './analytics.vue';
import AddMeasurements from './add_measurements.vue';
import Events from './events.vue';
import NavBar from './navbar.vue';
import Profile from './profile.vue';
import Prevalence from './prevalence.vue';
import Registration from './registration.vue';
import Confirmation from './confirmation.vue';
import SignIn from './sign_in.vue';
import ShowMeasurementSet from './show_measurement_set.vue';
import Tabs from './tabs.vue';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
    Analytics,
    AddMeasurements,
    Confirmation,
    Events,
    NavBar,
    Profile,
    Prevalence,
    Registration,
    ShowMeasurementSet,
    SignIn,
    Tabs
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ["focusTab", "focusSubTab", "signedIn", "markers"]),
    ...mapWritableState(useMainStore, ['center', 'zoom'])

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

    await this.getCurrentUser();
    this.loadProfile()
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile']),
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
