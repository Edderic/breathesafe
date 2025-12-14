<template>
  <vue3-progress/>
  <LegalFormsConsentPopup/>
  <div class='column'>
    <NavBar></NavBar>

    <Spinner v-show="isWaiting"/>
    <div class='router-view-container'>
      <router-view></router-view>
    </div>

    <Footer/>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import Footer from './footer.vue';
import NavBar from './navbar.vue';
import Spinner from './spinner.vue'
import LegalFormsConsentPopup from './legal_forms_consent_popup.vue'
import { useMainStore } from './stores/main_store';
import { useProfileStore } from './stores/profile_store';
import { mapActions, mapWritableState, mapState, mapStores } from 'pinia'

export default {
  name: 'App',
  components: {
    Footer,
    Spinner,
    NavBar,
    LegalFormsConsentPopup
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapWritableState(useMainStore, ['center', 'zoom']),
    ...mapState(useMainStore, ['isWaiting'])

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

  .router-view-container {
    position: relative;
    top: 3em;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;

  }

</style>
