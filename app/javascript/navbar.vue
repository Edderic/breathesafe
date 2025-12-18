<template>
  <div class='navbar-top-container'>

    <div class='row spaced-between main fixed-nav-bar'>
      <div class='left row vertical-centered'>
        <router-link :to='{ name: "Landing"}' class='logo-link'>
          <div class='row'>
            <div class='logo vertical-centered'>😷</div>
            <h2 class='title'>Breathesafe</h2>
          </div>
        </router-link>
      </div>

      <div class='vertical-centered'>
        <router-link class='desktop clickable side-padding' :to='{ name: "MaskRecommenderOnboarding"}' @click='toggleShowSubNavBar("MaskRecommenderOnboarding")'>Onboarding</router-link>
        <router-link class='desktop clickable side-padding' :to='{ name: "RespiratorUsers"}' @click='toggleShowSubNavBar("RespiratorRecommender")'>Users</router-link>
        <router-link class='desktop clickable side-padding' :to='{ name: "Masks"}' @click='toggleShowSubNavBar("Masks")'>Masks</router-link>
        <router-link class='desktop clickable side-padding' :to='{ name: "FitTests"}' @click='toggleShowSubNavBar("FitTests")'>Fit Tests</router-link>
        <router-link class="desktop clickable side-padding" :to="{ name: 'AdminStudyParticipants'}" @click="toggleShowSubNavBar('AdminStudyParticipants')" v-if="isAdmin">Study Participants</router-link>
        <router-link class='desktop clickable side-padding' to='/signin' v-if=!signedIn @click='showSubNavBar = null'>Sign up/Sign in</router-link>
        <a class='desktop clickable side-padding' href="#sign_out" @click="signOut" v-if="signedIn"  >Sign out</a>

        <Accordion class='mobile' @click='toggleMobileCol'/>
      </div>
    </div>

    <div class='mobile-col' v-if="showMobile()">
      <h2 class='vertical-centered'>Respirator</h2>
      <router-link class='mobile-row clickable side-padding' :to='{ name: "ConsentForm"}' @click='toggleShowSubNavBar("ConsentForm")'>Consent Form</router-link>
      <router-link class='mobile-row clickable side-padding' :to='{ name: "MaskRecommenderOnboarding"}' @click='toggleShowSubNavBar("MaskRecommenderOnboarding")'>Onboarding</router-link>
      <router-link class='mobile-row clickable side-padding' :to='{ name: "RespiratorUsers"}' @click='toggleShowSubNavBar("RespiratorRecommender")'>Users</router-link>
      <router-link class='mobile-row clickable side-padding' :to='{ name: "Masks"}' @click='toggleShowSubNavBar("Masks")'>Masks</router-link>
      <router-link class='mobile-row clickable side-padding' :to='{ name: "FitTests"}' @click='toggleShowSubNavBar("FitTests")'>Fit Tests</router-link>
      <router-link class="mobile-row clickable side-padding" :to="{ name: 'AdminStudyParticipants'}" @click="toggleShowSubNavBar('AdminStudyParticipants')" v-if="isAdmin">Study Participants</router-link>
      <h2 class='vertical-centered'>Misc</h2>

      <router-link class='mobile-row clickable side-padding' to='/signin' v-if=!signedIn>Sign up/Sign in</router-link>
      <a class='mobile-row clickable side-padding' href="#sign_out" @click="signOut" v-if="signedIn">Sign out</a>
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
    ...mapState(useMainStore, ['signedIn', 'currentUser', 'isAdmin']),
    ...mapWritableState(useMainStore, ['focusTab']),
  },
  created() {
  },
  data() {
    return {
      showSubNavBar: null
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useEventStores, [ 'load']),
    toggleShowSubNavBar(string) {
      if (string == this.showSubNavBar) {
        this.showSubNavBar = null
      } else if (!!this.showSubNavBar && string != this.showSubNavBar) {
        this.showSubNavBar = string
      } else if (this.showSubNavBar == null) {
        this.showSubNavBar = string
      }
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
          this.getCurrentUser();
          window.location.href = window.location.origin
        }

        // whatever you want
      })
      .catch(error => {
        console.log(error)
        // whatever you want
      })
    },
    showMobile() {
      return !!this.$route.query['showNavLinks']
    },

    toggleMobileCol() {
      let query = JSON.parse(JSON.stringify(this.$route.query))

      if (query['showNavLinks'] && query['showNavLinks'] == 'true') {
        delete query['showNavLinks']
      } else {
        Object.assign(query, { showNavLinks: true })
      }

      this.$router.push({
        params: this.$route.params,
        query: query,
        hash: this.$route.hash
      })
    }
  },
}
</script>


<style scoped>
  a {
    cursor: pointer;
  }

  .clickable {
    padding: 1em;
    font-size: 1.3em;
  }

  .logo-link {
    text-decoration: none;
    color: black;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .col {
    display: flex;
    flex-direction: column;
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

  .bunched-vertically-in-the-middle {
    margin: 0 auto;
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
  .fixed-nav-bar-bottom {
     position: fixed;
     top: 3em;
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

  .mobile-row {
    display: flex;
    flex-direction: row;
  }

  .mobile-row:hover {
    background-color: #efefef;
    cursor: pointer;
  }

  .mobile-col {
    overflow: auto;
    max-height: 100vh;
  }
  @media (max-width: 800px) {
    .desktop {
      display: none;
    }
    .mobile {
      display: inline-block;
    }
    .navbar-top-container {
      display: flex;
      z-index: 999;
      flex-direction: column;
      width: 100vw;
      background-color: white;
      position: fixed;
      top: 3em;
    }

    .fixed-nav-bar-bottom {
      display: none;
    }

    .mobile-col {
      max-height: 86vh;
    }
  }

  @media (min-width: 800px) {
    .desktop {
      display: inline-block;
    }
    .mobile {
      display: none;
    }
    .mobile-col {
      display: none;
    }
  }
</style>
