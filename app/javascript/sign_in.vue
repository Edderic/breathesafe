<template>
  <form class='wide border-showing' action="">
    <div class='container centered'>
      <h2>Sign in</h2>
    </div>

    <div class='container centered'>
      <h3>{{ message }}</h3>
    </div>

    <div class='container'>
      <label>Email</label>

      <input
        :value="email"
        @change="setEmail">
    </div>

    <div class='container'>
      <label>Password</label>

      <input
        :value="password"
        type="password"
        @change="setPassword"
        @keyup.enter.stop="signIn"
      >
    </div>

    <div class='container'>
      <button @click="signIn">Sign In</button>
    </div>
  </form>
</template>

<script>
// Have a VueX store that maintains state across components
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { mapActions, mapWritableState } from 'pinia';
import axios from 'axios';

export default {
  name: 'SignIn',
  components: {
  },
  computed: {
    ...mapWritableState(useMainStore, ['message'])
  },
  created() { },
  data() {
    return {
      name: "",
      email: "",
      password: "",
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

        // whatever you want
      })
      .catch(error => {
        console.log(error)
        this.message = "Error with logging in."
        // whatever you want
      })

      await this.getCurrentUser();
      await this.loadProfile()

      this.$router.push({
        name: 'MapEvents'
      });
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
</style>
