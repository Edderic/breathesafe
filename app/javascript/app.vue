<template>
  <div class='main'>
    <GMapMap
        :center="center"
        :zoom="zoom"
        map-type-id="terrain"
        style="width: 50vw; height: 500px"
    >
    </GMapMap>

    <Event/>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Event from './event.vue';
import { useMainStore } from './stores/main_store';
import { mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
    Event
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ['center', 'zoom'])

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
  .main {
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

  button {
    padding: 1em 3em;
  }
</style>
