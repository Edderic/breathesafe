<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Sign In</h2>
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
        @change="setPassword">
    </div>

    <div class='container'>
      <button @click="signin">Sign in</button>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useMainStore } from './stores/main_store';
import { mapActions } from 'pinia';
import axios from 'axios';

export default {
  name: 'SignIn',
  components: {
  },
  computed: {

  },
  created() { },
  data() {
    return {
      name: "",
      password: ""
    }
  },
  methods: {
    ...mapActions(useMainStore, ['setFocusTab']),
    setEmail(event) {
      this.email = event.target.value;
    },
    setPassword(event) {
      this.password = event.target.value;
    },
    signin() {
      let token = document.getElementsByName('csrf-token')[0].getAttribute('content')
      axios.defaults.headers.common['X-CSRF-Token'] = token
      axios.defaults.headers.common['Accept'] = 'application/json'
      axios.post('/users/log_in', {
        user: {
          email: this.email,
          password: this.password
        }
      })
      .then(response => {
        console.log(response)
        if (response.status == 201) {
          this.setFocusTab('events');
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
