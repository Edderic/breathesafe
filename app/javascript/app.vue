<template>
  <div class='column'>
    <NavBar></NavBar>

    <div class='row'>
      <GMapMap
          :center="center"
          :zoom="zoom"
          map-type-id="terrain"
          style="width: 50vw; height: 500px"
      >
      </GMapMap>

      <Event v-if='focusTab == "event"'/>
      <Events v-if='focusTab == "events"'/>
      <Profile v-if='focusTab == "profile"'/>
      <Registration v-if='!signedIn && focusTab == "register"'/>
      <SignIn v-if='!signedIn && focusTab == "signIn"'/>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Profile from './profile.vue';
import Event from './event.vue';
import NavBar from './navbar.vue';
import Events from './events.vue';
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
    Profile,
    Event,
    Events,
    NavBar
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ["focusTab"]),
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
  },
  data() {
  },
  methods: {
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
