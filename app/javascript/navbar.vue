<template>
  <div class='row spaced-between main fixed-nav-bar'>
    <div class='left row vertical-centered'>
      <span class='logo'>😷</span>
      <h2 class='title'>Breathesafe</h2>
    </div>

    <div class='vertical-centered'>
      <router-link class='desktop clickable side-padding' to='/faqs'>FAQs</router-link>
      <router-link class='desktop clickable side-padding' to='/'>Events</router-link>
      <router-link class='desktop clickable side-padding' to='/profile' v-if='signedIn'>Profile</router-link>
      <router-link class='desktop clickable side-padding' to='/register' v-if=!signedIn>Register</router-link>
      <router-link class='desktop clickable side-padding' to='/signin' v-if=!signedIn>Sign in</router-link>
      <a class='desktop clickable side-padding' href="#sign_out" @click="signOut" v-if="signedIn">Sign out</a>
      <Accordion class='mobile'/>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import axios from 'axios'
import Accordion from './accordion.vue'
import { useMainStore } from './stores/main_store';
import { useEventStores } from './stores/event_stores';
import { mapActions, mapState, mapWritableState, mapStores } from 'pinia'

export default {
  name: 'NavBar',
  components: {
    Accordion,
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
          this.getCurrentUser();
          this.$router.push({
            path: '/'
          });
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
    align-items: center;
  }

  .fixed-nav-bar {
     position: fixed;
     top: 0;
     left: 0;
     z-index: 9999;
     width: 100%;
     height: 50px;
     background-color: white;
  }

  .logo {
    font-size: 3em;
    margin-left: 0.25em;
  }
  .title {
    margin-left: 0.5em;
  }
  .left {
  }

  @media (max-width: 800px) {
    .desktop {
      display: none;
    }
    .mobile {
      display: inline-block;
    }
  }

  @media (min-width: 800px) {
    .desktop {
      display: inline-block;
    }
    .mobile {
      display: none;
    }
  }
</style>
