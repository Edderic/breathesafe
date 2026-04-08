<template>
  <div class="auth-page">
    <form class="auth-card auth-card--wide" action="">
      <div class="auth-header">
        <p class="auth-eyebrow">Breathesafe account</p>
        <h1 class="auth-title">Sign up or sign in</h1>
        <p class="auth-subtitle" v-if="!registered">
          Use your account email and password to sign in, or create a new account below.
        </p>
        <p class="auth-subtitle" v-else>
          {{ message }}
        </p>
      </div>

      <div class="auth-message" v-if="message && !registered">
        {{ message }}
      </div>

      <template v-if="!registered">
        <div class="auth-form">
          <div class="auth-field">
            <label for="sign-in-email">Email</label>
            <input
              id="sign-in-email"
              class="auth-input"
              :value="email"
              autocomplete="email"
              placeholder="name@example.com"
              @change="setEmail"
            >
          </div>

          <div class="auth-field">
            <label for="sign-in-password">Password</label>
            <input
              id="sign-in-password"
              class="auth-input"
              :value="password"
              type="password"
              autocomplete="current-password"
              @change="setPassword"
              @keyup.enter.stop="signIn"
            >
          </div>

          <div class="auth-actions auth-actions--stacked">
            <button class="auth-submit" type="button" @click="signIn">Sign in</button>
            <button
              class="auth-submit auth-submit--secondary"
              type="button"
              @click="signUp"
              :disabled="!agreeTOSMedicalDisclaimerPrivacyPolicy"
            >
              Sign up
            </button>
          </div>
        </div>

        <div class="auth-links auth-links--inline auth-links--no-border auth-help">
          <p>Forgot your password? <a href="/users/password/new">Reset it by email</a></p>
        </div>

        <div class="auth-checkbox">
          <input
            v-model="agreeTOSMedicalDisclaimerPrivacyPolicy"
            type="checkbox"
            id="agreePolicies"
          >

          <label for="agreePolicies">
            By signing up, you agree to our <router-link :to="{ name: 'TermsOfService' }">Terms of Service</router-link>, <router-link :to="{ name: 'ConsentForm' }">Consent form</router-link>, <router-link :to="{ name: 'Disclaimer' }">Disclaimer</router-link>, and <router-link :to="{ name: 'PrivacyPolicy' }">Privacy Policy</router-link>.
          </label>
        </div>
      </template>

      <div class="auth-links" v-if="!registered">
        <p><a href="/users/confirmation/new">Need a new confirmation email?</a></p>
        <p><a href="/users/unlock/new">Need unlock instructions?</a></p>
      </div>
    </form>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { mapActions, mapWritableState } from 'pinia';
import { setupCSRF } from './misc.js';
import axios from 'axios';

export default {
  name: 'SignIn',
  computed: {
    ...mapWritableState(useMainStore, ['message', 'currentUser'])
  },
  created() {
   if (this.currentUser) {
      this.redirectToAttemptTarget();
    }
    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        let attemptName = toQuery['attempt-name']
        if (attemptName && !!this.currentUser) {
          this.redirectToAttemptTarget();
        }
      }
    )
  },
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
    buildRouteFromAttemptQuery() {
      const attemptName = this.$route.query['attempt-name'];
      if (!attemptName || attemptName === 'SignIn') {
        return null;
      }

      const query = JSON.parse(JSON.stringify(this.$route.query));
      delete query['attempt-name'];

      const params = {};
      for (const key in this.$route.query) {
        if (key.startsWith('params-')) {
          const paramKey = key.substring('params-'.length);
          params[paramKey] = this.$route.query[key];
        }
      }

      Object.keys(query).forEach((key) => {
        if (key.startsWith('params-')) delete query[key];
      });

      return { name: attemptName, params, query };
    },
    redirectToAttemptTarget() {
      const target = this.buildRouteFromAttemptQuery();
      if (target) {
        this.$router.replace(target);
      }
    },
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
          password: this.password,
          accept_consent: this.agreeTOSMedicalDisclaimerPrivacyPolicy
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
      setupCSRF();

      let success = false
      await axios.post('/users/log_in', {
        user: {
          email: this.email,
          password: this.password
        }
      })
      .then(async response => {
        if (response.status == 201) {
          success = true
        }

        this.currentUser = response.data
        // Refresh CSRF token after successful sign-in
        await setupCSRF()
        // whatever you want
        this.loadProfile()

        const obj = this.buildRouteFromAttemptQuery();
        if (obj) {
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
  .auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px 16px;
    background:
      radial-gradient(circle at top left, rgba(232, 241, 250, 0.95), transparent 38%),
      linear-gradient(180deg, #f7fafc 0%, #eef2f7 100%);
  }

  .auth-card {
    box-sizing: border-box;
    width: min(100%, 460px);
    padding: 36px 32px;
    border: 1px solid rgba(25, 38, 56, 0.1);
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 22px 60px rgba(31, 41, 55, 0.14);
  }

  .auth-card--wide {
    width: min(100%, 520px);
  }

  .auth-header {
    margin-bottom: 28px;
  }

  .auth-eyebrow {
    margin: 0 0 10px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4b6b8a;
  }

  .auth-title {
    margin: 0;
    font-size: clamp(1.9rem, 4vw, 2.4rem);
    line-height: 1.1;
    color: #162132;
  }

  .auth-subtitle {
    margin: 12px 0 0;
    font-size: 1rem;
    line-height: 1.6;
    color: #546375;
  }

  .auth-message {
    margin-bottom: 18px;
    padding: 14px 16px;
    border: 1px solid #bfd3ec;
    border-radius: 14px;
    background: #eef5ff;
    color: #1f3d66;
    line-height: 1.5;
  }

  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .auth-field label {
    display: block;
    margin-bottom: 8px;
    font-size: 0.96rem;
    font-weight: 600;
    color: #223249;
  }

  .auth-input {
    box-sizing: border-box;
    width: 100%;
    padding: 14px 16px;
    border: 1px solid #c8d2de;
    border-radius: 14px;
    background: #fbfdff;
    font-family: inherit;
    font-size: 1rem;
    color: #162132;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  }

  .auth-input:focus {
    outline: none;
    border-color: #2f6fed;
    box-shadow: 0 0 0 4px rgba(47, 111, 237, 0.16);
    background: #fff;
  }

  .auth-actions {
    margin-top: 6px;
  }

  .auth-actions--stacked {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .auth-submit {
    width: 100%;
    padding: 15px 18px;
    border: 0;
    border-radius: 14px;
    background: linear-gradient(135deg, #1e5bd7 0%, #3c7af2 100%);
    color: #fff;
    font-family: inherit;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    cursor: pointer;
    box-shadow: 0 12px 24px rgba(47, 111, 237, 0.22);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease, opacity 0.15s ease;
  }

  .auth-submit:hover,
  .auth-submit:focus {
    transform: translateY(-1px);
    box-shadow: 0 16px 28px rgba(47, 111, 237, 0.28);
    filter: brightness(1.02);
  }

  .auth-submit:focus {
    outline: 3px solid rgba(47, 111, 237, 0.18);
    outline-offset: 2px;
  }

  .auth-submit:disabled {
    cursor: not-allowed;
    opacity: 0.55;
    transform: none;
    box-shadow: none;
    filter: none;
  }

  .auth-submit--secondary {
    background: linear-gradient(135deg, #5b6778 0%, #7d8b9f 100%);
    box-shadow: 0 12px 24px rgba(86, 98, 116, 0.2);
  }

  .auth-links {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid rgba(34, 50, 73, 0.1);
  }

  .auth-links p {
    margin: 0;
  }

  .auth-links p + p {
    margin-top: 10px;
  }

  .auth-links a {
    color: #1e5bd7;
    font-weight: 600;
  }

  .auth-links a:hover,
  .auth-links a:focus {
    color: #1748ab;
  }

  .auth-links--inline p {
    color: #546375;
  }

  .auth-links--no-border {
    margin-top: 18px;
    padding-top: 0;
    border-top: 0;
  }

  .auth-checkbox {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-top: 22px;
    padding: 16px;
    border-radius: 16px;
    background: #f7f9fc;
    color: #4c5b6e;
    line-height: 1.6;
  }

  .auth-checkbox input[type='checkbox'] {
    width: 1.15em;
    height: 1.15em;
    min-width: 1.15em;
    margin-top: 0.2em;
  }

  .auth-checkbox label {
    font-size: 0.94rem;
  }

  .auth-checkbox a {
    color: #1e5bd7;
    font-weight: 600;
  }

  @media(max-width: 700px) {
    .auth-page {
      padding: 18px 12px;
      align-items: flex-start;
    }

    .auth-card {
      width: 100%;
      padding: 28px 20px;
      border-radius: 18px;
    }
  }
</style>
