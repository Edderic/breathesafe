<template>
  <div class='row spaced-between main fixed-nav-bar'>
    <h2 class='side-padding'>Breathesafe 😷</h2>

    <div class='vertical-centered'>
      <a class='clickable side-padding' href="#recommendations">Recommendations</a>
      <a class='clickable side-padding' href="#events" @click="navToEvents" v-if=signedIn>Events</a>
      <a class='clickable side-padding' href="#profile" @click="navToProfile" v-if=signedIn>Profile</a>
      <a class='clickable side-padding' href="#register" @click="navToRegister" v-if=!signedIn>Register</a>
      <a class='clickable side-padding' href="#register" @click="navToSignIn" v-if=!signedIn>Sign in</a>
      <a class='clickable side-padding' href="#sign_out" @click="signOut" v-if="signedIn">Sign out</a>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios'
import { useMainStore } from './stores/main_store';
import { useEventStores } from './stores/event_stores';
import { mapActions, mapState, mapWritableState, mapStores } from 'pinia'

export default {
  name: 'NavBar',
  components: {
    Event
  },
  computed: {
    ...mapStores(useMainStore),
    ...mapState(useMainStore, ['signedIn']),
    ...mapWritableState(useMainStore, ['focusTab'])
  },
  created() {
  },
  data() {
    return {}
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useEventStores, [ 'load']),
    navToEvents() {
      this.focusTab = 'events'
      this.load()
    },
    navToProfile() {
      this.focusTab = 'profile'
    },
    navToRegister() {
      this.focusTab = 'register'
    },
    navToSignIn() {
      this.focusTab = 'signIn'
    },
    async signOut() {
      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'
      await axios.delete('/users/log_out')
      .then(response => {
        console.log(response)
        if (response.status == 204 || response.status == 200) {
          this.focusTab = 'events';
          this.getCurrentUser();
        }

        // whatever you want
      })
      .catch(error => {
        console.log(error)
        // whatever you want
      })
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

  .fixed-nav-bar {
     position: fixed;
     top: 0;
     left: 0;
     z-index: 9999;
     width: 100%;
     height: 50px;
     background-color: white;
     padding-bottom: 1em;
  }
</style>
