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
import { mapStores } from 'pinia'

export default {
  name: 'App',
  setup () {
    const mainStore = useMainStore()
  },
  components: {
    Event
  },
  computed: {
    ...mapStores(useMainStore)
  },
  created() {
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
    return {
      center: {lat: 51.093048, lng: 6.842120},
      zoom: 7,
    }
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
