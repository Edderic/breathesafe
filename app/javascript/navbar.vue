<template>
  <div class='row spaced-between main'>
    <h2 class='side-padding'>Breathesafe 😷</h2>

    <div class='vertical-centered'>
      <a class='clickable side-padding' href="#recommendations">Recommendations</a>
      <a class='clickable side-padding' href="#events" @click="navToEvents">Events</a>
      <a class='clickable side-padding' href="#events" @click="navToProfile">Profile</a>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useMainStore } from './stores/main_store';
import { mapWritableState, mapStores } from 'pinia'

export default {
  name: 'NavBar',
  components: {
    Event
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapWritableState(useMainStore, ['focusTab'])

  },
  created() {
  },
  data() {
  },
  methods: {
    navToEvents() {
      this.focusTab = 'events'
    },
    navToProfile() {
      this.focusTab = 'profile'
    }
  },
}
</script>


<style scoped>
  .clickable {
    padding: 1em;
    font-size: 1.3em;
  }
  .row {
    display: flex;
    flex-direction: row;
  }

  .main {
    border-bottom: 1px solid grey;
  }

  .spaced-between {
    justify-content: space-between;
  }

  .side-padding {
    padding-left: 2em;
    padding-right: 2em;
  }

  .vertical-centered {
    display: flex;
    justify-content: center;
  }
</style>
