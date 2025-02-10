<template>
  <form class='top-container wide border-showing' action="">
    <br>
    <br>
    <br>

    <div class='container centered'>
      <h2>Sign up/Sign in</h2>
    </div>

    <div class='container centered'>
      <h3>{{ message }}</h3>
    </div>

    <div class='container' v-if='!registered'>
      <label>Email</label>

      <input
        :value="email"
        @change="setEmail">
    </div>

    <div class='container' v-if='!registered'>
      <label>Password</label>

      <input
        :value="password"
        type="password"
        @change="setPassword"
        @keyup.enter.stop="signIn"
      >
    </div>

    <div class='container row' v-if='!registered'>
      <Button shadow='true' @click="signIn" text='Sign In'/>
    </div>

    <div class='container' v-if='!registered'>
      <input
        v-model='agreeTOSMedicalDisclaimerPrivacyPolicy'
        type="checkbox"
        id='agreePolicies'
      >

      <label for="agreePolicies">
        By signing up, you agree to our <router-link :to="{'name': 'TermsOfService'}">Terms of Service</router-link>, <router-link :to="{'name': 'ConsentForm'}">Consent form</router-link>, <router-link :to="{'name': 'Disclaimer'}">Disclaimer</router-link>, and <router-link :to="{'name': 'PrivacyPolicy'}">Privacy Policy</router-link>.
        </label>
      </div>


    <div class='container row' v-if='!registered'>
      <Button shadow='true' @click="signUp" text='Sign up' :disabled='!agreeTOSMedicalDisclaimerPrivacyPolicy'/>

    </div>
  </form>
</template>

<script>
// Have a VueX store that maintains state across components
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { mapActions, mapWritableState } from 'pinia';
import Button from './button.vue';
import axios from 'axios';

export default {
  name: 'SignIn',
  components: {
    Button
  },
  computed: {
    ...mapWritableState(useMainStore, ['message', 'currentUser'])
  },
  created() { },
  data() {
    return {
      name: "",
      email: "",
      password: "",
      agreeTOSMedicalDisclaimerPrivacyPolicy: false,
      registered: false
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile']),
    setEmail(event) {
      this.email = event.target.value;
    },
    setPassword(event) {
      this.password = event.target.value;
    },
    signUp() {
      if (!this.agreeTOSMedicalDisclaimerPrivacyPolicy) {
        this.message = "Please check the box saying that you agree with the Terms of Service, Consent Form, Disclaimer"
        return
      }

      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'
      axios.post('/users', {
        user: {
          email: this.email,
          password: this.password
        }
      })
      .then(response => {
        console.log(response)
        if (response.status == 201) {
          this.message = `Sent a confirmation email to ${this.email}. Please check.`
          this.$router.push({
            path: '/signin'
          })
          this.registered = true
        }

        // whatever you want
      })
      .catch(error => {
        console.log(error)
        // whatever you want
      })
    },
    async signIn() {
      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'
      let success = false

      await axios.post('/users/log_in', {
        user: {
          email: this.email,
          password: this.password
        }
      })
      .then(response => {
        if (response.status == 201) {
          success = true
        }
        this.currentUser = response.data
        // whatever you want
        this.loadProfile()

        let attemptName = this.$route.query['attempt-name'];

        if (attemptName && attemptName != 'SignIn') {
          let query = JSON.parse(JSON.stringify(this.$route.query))
          delete query['attempt-name']

          let params = {}
          let paramKey = null;

          for(let k in query) {
            if (k.includes('params-')) {
              paramKey = k.split('params-')[1]
              params[paramKey] = query[k]
            }
          }

          let obj = {
            name: attemptName,
            params: params,
            query: query
          }

          // TODO: delete the params- query strings
          this.$router.push(obj);
        }
        else if (this.$router.options.history.state.back == '/' || this.$router.options.history.state.back == '/sign_out') {
          this.$router.push(
            {
              'name': 'RespiratorUsers'
            }
          )
        }
        else {
          this.$router.go(-1);
        }
      })
      .catch(error => {
        console.log(error)
        this.message = "Error with logging in."
        // whatever you want
      })

    }
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

  @media(max-width: 700px) {
    .container {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    input {
      width: 95vw;
      font-size: 2em;
    }

    .button {
      width: 93vw;
    }

    .top-container {
      margin-bottom: 4em;
    }

    input[type='checkbox'] {
      transform: scale(2)
    }
  }
</style>
