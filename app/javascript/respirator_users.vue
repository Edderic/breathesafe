<template>
  <div>
    <h2 class='tagline'>Respirator Users</h2>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <div class='main'>
      <div class='centered'>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Race &amp; Ethnicity filled out</th>
              <th>Gender filled out</th>
              <th>Has Facial Measurements</th>
              <th>Ready to add Fit Testing Data</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                {{firstName}} {{lastName}}
              </td>
              <td>
                {{raceEthnicityComplete}}
              </td>
              <td>
                {{genderAndSexComplete}}
              </td>
              <td>
                {{facialMeasurementsComplete}}
              </td>
              <td>
                {{readyToAddFitTestingDataPercentage}}
              </td>
              <td>
                <Button @click="edit(profileId)" text='Edit' />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'RespiratorUsers',
  components: {
    Button,
    ClosableMessage
  },
  data() {
    return {
      messages: [],
      facialMeasurementsLength: 0
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
          'readyToAddFitTestingDataPercentage',
          'nameComplete',
          'genderAndSexComplete',
          'raceEthnicityComplete',
          'facialMeasurementsComplete',
          'loadFacialMeasurements',
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity',
          'genderAndSex',
        ]
    ),
    facialMeasurementsIncomplete() {
      return this.facialMeasurementsLength == 0
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadStuff()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile']),
    async loadStuff() {
      this.loadProfile()
      this.loadFacialMeasurements(this.currentUser.id)
    },
    edit(profileId) {
      this.$router.push({
        name: 'RespiratorUser',
        params: {
          id: profileId
        }
      })
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  p {
    margin: 1em;
  }

  th, td {
    padding: 0.5em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  img {
    width: 30em;
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
  }
</style>
