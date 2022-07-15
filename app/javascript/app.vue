<template>
  <div class='column'>
    <NavBar></NavBar>

    <div class='body row'>
      <div class='col'>
        <div class='row'>
          <GMapMap
              :center="center"
              :zoom="zoom"
              map-type-id="terrain"
              style="width: 50vw; height: 500px"
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
          <Events v-if='focusTab == "events"'/>
        </div>
      </div>
      <div class='col'>
        <ShowMeasurementSet v-if='focusTab == "events" && signedIn'/>
        <Event v-if='focusTab == "event" && signedIn'/>
        <Profile v-if='focusTab == "profile"'/>
        <Registration v-if='!signedIn && focusTab == "register"'/>
        <Confirmation v-if='!signedIn && focusTab == "confirmation"'/>
        <SignIn v-if='!signedIn && focusTab == "signIn"'/>
      </div>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Event from './event.vue';
import Events from './events.vue';
import NavBar from './navbar.vue';
import Profile from './profile.vue';
import Registration from './registration.vue';
import Confirmation from './confirmation.vue';
import SignIn from './sign_in.vue';
import ShowMeasurementSet from './show_measurement_set.vue';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
    Confirmation,
    Event,
    Events,
    NavBar,
    Profile,
    Registration,
    ShowMeasurementSet,
    SignIn
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ["focusTab", "signedIn", "markers"]),
    ...mapWritableState(useMainStore, ['center', 'zoom'])

  },
  created() {
    // TODO: modify the store
    this.$getLocation()
      .then((coordinates) => {
        this.center = { lat: coordinates.lat, lng: coordinates.lng };
        this.zoom = 15;
      })
      .catch((error) => {
        console.log(error);
      });

    this.getCurrentUser();
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
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
  }

  button {
    padding: 1em 3em;
  }
</style>
