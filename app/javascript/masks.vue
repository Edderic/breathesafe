<template>
  <div>
    <h2 class='tagline'>Masks</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <CircularButton text="+" @click="newMask"/>

    <div class='main'>
      <p class='narrow-p'>
        Demographic data will be used to assess sampling bias and this data will only
        be reported in aggregate. If a category has less than 5 types of
        people, individuals will be grouped in a "not enough data/prefer not to
        disclose" group to preserve privacy.
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'Masks',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      errorMessages: [],
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
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'message'
        ]
    ),
    messages() {
      return this.errorMessages;
    },
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      // TODO: a parent might input data on behalf of their children.
      // Currently, this.loadStuff() assumes We're loading the profile for the current user
      this.loadStuff()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    newMask() {
      this.$router.push(
        {
          name: "AddMask"
        }
      )
    },
    async loadStuff() {
      // TODO: load the profile for the current user
      this.loadProfile()
      this.loadFacialMeasurements()
    },
    async loadFacialMeasurements() {
      // TODO: make this more flexible so parents can load data of their children
      await axios.get(
        `/users/${this.currentUser.id}/facial_measurements.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.facial_measurements) {
            this.facialMeasurements = deepSnakeToCamel(data.facial_measurements)
          }

          if (this.facialMeasurements.length == 0) {
            this.facialMeasurements.push({
              source: 'caliper/tape',
                faceWidth: 0,
                noseBridgeHeight: 0,
                nasalRootBreadth: 0,
                noseProtrusion: 0,
                lipWidth: 0,
                jawWidth: 0,
                faceDepth: 0,
                faceLength: 0,
                lowerFaceLength: 0,
                bitragionMentonArc: 0,
                bitragionSubnasaleArc: 0,
                cheekFullness: 'medium',
            })
          }
          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load profile."
          // whatever you want
        })
    },
    async saveProfile(tabToShow) {
      await this.updateProfile()
      this.$router.push({
        name: "RespiratorUser",
        params: {
          id: this.currentUser.id,
        },
        query: {
          tabToShow: tabToShow
        }
      })
    },
    runFacialMeasurementValidations() {
      let quantitativeMeasurements = [
        'faceWidth', 'noseBridgeHeight', 'nasalRootBreadth', 'lipWidth',
        'noseProtrusion', 'jawWidth', 'faceDepth', 'faceLength',
        'lowerFaceLength', 'bitragionSubnasaleArc', 'bitragionMentonArc'
      ]

      let negativeOrZero = [];

      for(let q of quantitativeMeasurements) {
        if (this.latestFacialMeasurement[q] <= 0) {
          this.errorMessages.push({
            str: `${q} cannot be zero or negative.`,
          })
        }
      }
    },
    async saveFacialMeasurement() {
      this.runFacialMeasurementValidations()

      if (this.errorMessages.length > 0) {
        return;
      }

      await axios.post(
        `/users/${this.currentUser.id}/facial_measurements.json`, {
          source: this.latestFacialMeasurement.source,
          face_width: this.latestFacialMeasurement.faceWidth,
          nose_bridge_height: this.latestFacialMeasurement.noseBridgeHeight,
          nasal_root_breadth: this.latestFacialMeasurement.nasalRootBreadth,
          lip_width: this.latestFacialMeasurement.lipWidth,
          nose_protrusion: this.latestFacialMeasurement.noseProtrusion,
          jaw_width: this.latestFacialMeasurement.jawWidth,
          face_depth: this.latestFacialMeasurement.faceDepth,
          face_length: this.latestFacialMeasurement.faceLength,
          lower_face_length: this.latestFacialMeasurement.lowerFaceLength,
          bitragion_menton_arc: this.latestFacialMeasurement.bitragionMentonArc,
          bitragion_subnasale_arc: this.latestFacialMeasurement.bitragionSubnasaleArc,
          cheek_fullness: this.latestFacialMeasurement.cheekFullness,
          user_id: this.currentUser.id
        }
      )
        .then(response => {
          let data = response.data
          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to create facial measurement."
          // whatever you want
        })
      this.$router.push({
        name: 'RespiratorUsers',
      })
    },
    setRouteTo(opt) {
      this.$router.push({
        name: "RespiratorUser",
        query: {
          tabToShow: opt.name
        }
      })
    },
    selectRaceEthnicity(raceEth) {
      this.raceEthnicity = raceEth
    },
    selectGenderAndSex(genderAndSex) {
      this.genderAndSex = genderAndSex
    },
    setFacialMeasurement(event, whatToSet) {
      this.latestFacialMeasurement[whatToSet] = event.target.value
    },
    setNoseBridgeHeightExampleToShow(opt) {
      this.noseBridgeHeightExample = opt.name
    },
    setCheekFullnessExampleToShow(opt) {
      this.cheekFullnessExample = opt.name
    },
    toggleInfo(infoToShow) {
      this.infoToShow = infoToShow;
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }
  .text-for-other {
    margin: 0 1.25em;
  }

  .justify-items-center {
    justify-items: center;
  }

  .menu {
    justify-content:center;
    min-width: 500px;
    background-color: #eee;
    margin-top: 0;
    margin-bottom: 0;
  }
  .row {
    display: flex;
    flex-direction: row;
  }

  .row button {
    width: 100%;
    padding-top: 1em;
    padding-bottom: 1em;
  }


  .flex-dir-col {
    display: flex;
    flex-direction: column;
  }
  p {

    margin: 1em;
  }

  select {
    padding: 0.25em;
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

  .align-items-center {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .left-pane-image {

  }
  p.left-pane {
    max-width: 50%;
  }

  p.narrow-p {
    max-width: 40em;
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
  .label-input {
    align-items:center;
    justify-content:space-between;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  .adaptive-wide img {
    width: 100%;
  }
  img {
    max-width: 30em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }
  }
</style>
