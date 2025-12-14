<template>
  <Popup v-if='showPopup' @onclose='onClose'>
    <div class='consent-popup-content'>
      <h2>Legal Documents Updated</h2>
      <p>The following legal documents have been updated since you last agreed to them. Please review and accept to continue:</p>

      <ul class='outdated-forms-list'>
        <li v-for='form in outdatedForms' :key='form.name'>
          <router-link :to='form.route' target='_blank'>
            {{ form.displayName }}
          </router-link>
          <span class='version-info'>(Version: {{ form.currentVersion }})</span>
        </li>
      </ul>

      <div class='button-container'>
        <Button class='accept-all' @click='onAcceptAll'>Accept All</Button>
        <Button class='reject' @click='onReject'>Reject</Button>
      </div>
    </div>
  </Popup>

  <Popup v-if='showThanksPopup' @onclose='closeThanks'>
    <p>Thank you for accepting the updated legal documents!</p>
  </Popup>

  <Popup v-if='showRejectInfo' @onclose='closeRejectInfo'>
    <div>
      <h3>Data Management</h3>
      <p>
        If you've saved any data, you can delete it by visiting the
        <router-link :to="{ name: 'RespiratorUsers' }">Respirator Users page</router-link>.
        There you can manage and delete data for yourself and any users you manage.
      </p>
      <p>You may also choose to stop using the app.</p>
    </div>
  </Popup>
</template>

<script>
import Popup from './pop_up.vue'
import Button from './button.vue'
import axios from 'axios'
import { mapState, mapActions } from 'pinia'
import { useMainStore } from './stores/main_store'
import { setupCSRF } from './misc'

export default {
  name: 'LegalFormsConsentPopup',
  components: {
    Popup,
    Button
  },
  data() {
    return {
      showPopup: false,
      showThanksPopup: false,
      showRejectInfo: false,
      outdatedForms: []
    }
  },
  computed: {
    ...mapState(useMainStore, [
      'currentUser',
      'consentFormVersion',
      'disclaimerVersion',
      'termsOfServiceVersion',
      'privacyPolicyVersion',
      'consentDismissedForSession'
    ])
  },
  watch: {
    currentUser: {
      handler() {
        this.checkForOutdatedForms()
      },
      deep: true
    }
  },
  mounted() {
    this.checkForOutdatedForms()
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'setConsentDismissedForSession']),

    checkForOutdatedForms() {
      // Don't show if already dismissed for this session
      if (this.consentDismissedForSession) {
        return
      }

      // Don't show if user is not logged in
      if (!this.currentUser) {
        return
      }

      // Check which forms need to be accepted
      const formConfigs = [
        {
          name: 'consent_form',
          displayName: 'Consent Form',
          route: '/consent_form',
          currentVersion: this.consentFormVersion
        },
        {
          name: 'disclaimer',
          displayName: 'Disclaimer',
          route: '/disclaimer',
          currentVersion: this.disclaimerVersion
        },
        {
          name: 'terms_of_service',
          displayName: 'Terms of Service',
          route: '/terms_of_service',
          currentVersion: this.termsOfServiceVersion
        },
        {
          name: 'privacy_policy',
          displayName: 'Privacy Policy',
          route: '/privacy',
          currentVersion: this.privacyPolicyVersion
        }
      ]

      const outdated = []
      const userForms = this.currentUser.forms || {}

      formConfigs.forEach(config => {
        if (!config.currentVersion) {
          return // Skip if version not configured
        }

        const acceptedVersion = userForms[config.name]?.version_accepted

        if (!acceptedVersion || acceptedVersion !== config.currentVersion) {
          outdated.push(config)
        }
      })

      this.outdatedForms = outdated

      // Show popup if there are outdated forms
      if (outdated.length > 0) {
        this.showPopup = true
      }
    },

    async onAcceptAll() {
      setupCSRF()

      try {
        const formNames = this.outdatedForms.map(f => f.name)
        const response = await axios.post('/users/consent', {
          decision: 'accept',
          forms: formNames
        })

        if (response.status >= 200 && response.status < 300) {
          // Update current user with new forms data
          await this.getCurrentUser()

          this.showPopup = false
          this.showThanksPopup = true
        }
      } catch (e) {
        console.error('Error accepting forms:', e)
      }
    },

    onReject() {
      setupCSRF()

      try {
        axios.post('/users/consent', { decision: 'reject' })
      } catch (e) {
        console.error('Error rejecting forms:', e)
      }

      this.showPopup = false
      this.showRejectInfo = true
    },

    closeThanks() {
      this.showThanksPopup = false
      this.setConsentDismissedForSession(true)
    },

    closeRejectInfo() {
      this.showRejectInfo = false
      this.setConsentDismissedForSession(true)
    },

    onClose() {
      // Allow closing the popup but it will show again on next page load
      // unless they accept or we dismiss for session
      this.showPopup = false
    }
  }
}
</script>

<style scoped>
  .consent-popup-content {
    padding: 1em;
    max-width: 600px;
  }

  .consent-popup-content h2 {
    margin-top: 0;
    color: #333;
  }

  .consent-popup-content p {
    line-height: 1.6;
    color: #555;
  }

  .outdated-forms-list {
    list-style: none;
    padding: 0;
    margin: 1.5em 0;
  }

  .outdated-forms-list li {
    padding: 0.75em;
    margin: 0.5em 0;
    background-color: #f9f9f9;
    border-left: 4px solid #2196F3;
    border-radius: 4px;
  }

  .outdated-forms-list li a {
    font-weight: bold;
    color: #2196F3;
    text-decoration: none;
  }

  .outdated-forms-list li a:hover {
    text-decoration: underline;
  }

  .version-info {
    font-size: 0.9em;
    color: #666;
    margin-left: 0.5em;
  }

  .button-container {
    display: flex;
    gap: 1em;
    justify-content: center;
    margin-top: 1.5em;
  }

  .accept-all {
    background-color: #4CAF50;
    color: white;
    padding: 0.75em 2em;
    font-size: 1.1em;
    font-weight: bold;
  }

  .accept-all:hover {
    background-color: #45a049;
  }

  .reject {
    background-color: #f44336;
    color: white;
    padding: 0.75em 2em;
    font-size: 1.1em;
    font-weight: bold;
  }

  .reject:hover {
    background-color: #da190b;
  }
</style>
