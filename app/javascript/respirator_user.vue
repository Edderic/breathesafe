<template>
  <div>
    <h2 class='tagline'>Respirator User</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>
    <div class='centered'>
      <span>Percent Completed:</span>
      <span>&nbsp;
      {{readyToAddFitTestingDataPercentage}}
      </span>

    </div>
      <br>

    <div class='menu row'>
      <TabSet
        :options='tabToShowOptions'
        @update='setRouteTo'
        :tabToShow='tabToShow'
      />
    </div>

    <div class='main justify-items-center' v-if='tabToShow=="Name"'>
      <p class='narrow-p '>
        A user could input data on behalf of other users (e.g. a parent inputting data of their children).
        Adding names could help you distinguish among individuals who you'd be inputting data for.
        This data will not be shared publicly.
      </p>
      <table>
        <tbody>
          <tr>
            <td>What is first name of the individual you'll be adding data for?</td>
            <td>
              <input
                  type='text'
                  v-model='firstName'
              >
            </td>
          </tr>
          <tr>
            <td>What is the last name of the individual you'll be adding data for?</td>
            <td>
              <input
                  type='text'
                  v-model='lastName'
              >
            </td>
          </tr>
        </tbody>
      </table>

      <br>

      <Button text="Save and continue" @click='saveProfile("Demographics")'/>
    </div>

    <div class='main' v-if='tabToShow=="Demographics"'>
      <p class='narrow-p'>
        Demographic data will be used to assess sampling bias and this data will only
        be reported in aggregate. If a category has less than 5 types of
        people, individuals will be grouped in a "not enough data/prefer not to
        disclose" group to preserve privacy.
      </p>
      <SurveyQuestion
        :question="raceEthnicityQuestion"
        :answer_options="race_ethnicity_options"
        @update="selectRaceEthnicity"
        :selected="raceEthnicity"
      />
      <SurveyQuestion
        :question="genderSexQuestion"
        :answer_options="gender_and_sex_options"
        @update="selectGenderAndSex"
        :selected="genderAndSex"
      />
      <div>
        <input class='text-for-other' type="text" v-model='otherGender'>
      </div>

      <br>

      <Button text="Save and continue" @click='saveProfile("FacialMeasurements")'/>
    </div>

    <div class="edit-facial-measurements" v-if='tabToShow=="FacialMeasurements"'>



      <img v-if='infoToShow == "quantitativeGuide"' class="adaptive-wide" src="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8587533/bin/bmjgh-2021-005537f01.jpg" alt="Depiction of different measurements">

      <div v-show='infoToShow == "cheekFullness"' class='align-items-center'>
        <p class='left-pane'>Select options below to get an understanding of different types of cheek fullness:</p>
        <TabSet
          :options='cheekFullnessOptions'
          @update='setCheekFullnessExampleToShow'
          :tabToShow="cheekFullnessExample"
        />
        <img class='left-pane-image' v-if='cheekFullnessExample == "Hallow/gaunt"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-hollow.png" alt="hallow/gaunt cheeks">
        <img class='left-pane-image' v-if='cheekFullnessExample == "Medium"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-neutral.png" alt="medium-ful cheeks">
        <img class='left-pane-image' v-if='cheekFullnessExample == "Rounded/full"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-rounded.png" alt="rounded cheeks">
      </div>
      <br>

      <div class='flex-dir-col'>
        <br>
        <table>
          <thead>
            <tr>
              <th colspan='1'>Quantitative Measurements</th>
              <th>
                <CircularButton text="?" @click="toggleInfo('quantitativeGuide')" :highlight="infoToShow == 'quantitativeGuide'"/>
              </th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>
                <label for="source">Source</label>
              </th>
              <td>
                <select
                    v-if='latestFacialMeasurement'
                    :value="latestFacialMeasurement.source"
                    >
                    <option>caliper/tape</option>
                </select>
              </td>
            </tr>
            <tr>
              <th>
                <label for="faceWidth">Face Width <b>(B)</b> (mm) </label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceWidth"
                    @change='setFacialMeasurement($event, "faceWidth")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="jawWidth">Jaw Width <b>(C)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.jawWidth"
                    @change='setFacialMeasurement($event, "jawWidth")'
                    >
              </td>
            </tr>
            <tr>
              <th>
                <label for="faceDepth">Face Depth <b>(P)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceDepth"
                    @change='setFacialMeasurement($event, "faceDepth")'
                    >
              </td>
            </tr>
            <tr>
              <th>
                <label for="faceLength">Face Length <b>(D)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceLength"
                    @change='setFacialMeasurement($event, "faceLength")'
                    >
              </td>
            </tr>
            <tr>
              <th>
                <label for="bitragionMentonArc">Bitragion Menton Arc <b>(K)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.bitragionMentonArc"
                    @change='setFacialMeasurement($event, "bitragionMentonArc")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="bitragionSubnasaleArc">Bitragion Subnasale Arc <b>(L)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.bitragionSubnasaleArc"
                    @change='setFacialMeasurement($event, "bitragionSubnasaleArc")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="noseProtrusion">Nose Protrusion <b>(M)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.noseProtrusion"
                    @change='setFacialMeasurement($event, "noseProtrusion")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="nasalRootBreadth">Nasal Root Breadth <b>(H)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.nasalRootBreadth"
                    @change='setFacialMeasurement($event, "nasalRootBreadth")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="noseBridgeHeight">Nose Bridge Height <b>(H)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.noseBridgeHeight"
                    @change='setFacialMeasurement($event, "noseBridgeHeight")'
                    >
              </td>
            </tr>

            <tr>
              <th>
                <label for="lipWidth">Lip Width <b>(J)</b> (mm)</label>
              </th>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.lipWidth"
                    @change='setFacialMeasurement($event, "lipWidth")'
                    >
              </td>
            </tr>

          </tbody>
        </table>

        <br>

        <table>
          <thead>
            <tr>
              <th colspan='3'>Qualitative Measurements</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>
                <label for="cheekFullness">Cheek Fullness</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('cheekFullness')" :highlight="infoToShow == 'cheekFullness'"/>
              </td>
              <td>
                <select
                    v-if='latestFacialMeasurement'
                    :value="latestFacialMeasurement.cheekFullness"
                    @change='setFacialMeasurement($event, "cheekFullness")'
                    >
                    <option>hollow/gaunt</option>
                    <option>medium</option>
                    <option>rounded/full</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>

        <Button text="Save" @click='saveFacialMeasurement'/>
      </div>


    </div>
    <br>
    <br>
    <br>

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
  name: 'RespiratorUser',
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
      cheekFullnessExample: 'Hallow/gaunt',
      noseBridgeHeightExample: 'Low',
      noseBridgeHeightOptions: [
        {
          text: 'Low'
        },
        {
          text: 'Medium'
        },
        {
          text: 'High'
        }
      ],
      cheekFullnessOptions: [
        {
          text: 'Hallow/gaunt'
        },
        {
          text: 'Medium'
        },
        {
          text: 'Rounded/full'
        }
      ],
      tabToShow: 'Demographics',
      tabToShowOptions: [
        {
          text: "Name",
        },
        {
          text: "Demographics",
        },
        {
          text: "FacialMeasurements"
        }
      ],
      race_ethnicity_question: "Which race or ethnicity best describes you?",
      race_ethnicity_options: [
        "American Indian or Alaskan Native",
        "Asian / Pacific Islander",
        "Black or African American",
        "Hispanic",
        "White / Caucasian",
        "Multiple ethnicity / Other",
        "Prefer not to disclose",
      ],
      sex_assigned_at_birth_question: "What is your sex assigned at birth?",
      gender_and_sex_options: [
        "Cisgender male",
        "Cisgender female",
        "MTF transgender",
        "FTM transgender",
        "Intersex",
        "Prefer not to disclose",
        "Other"
      ],
      facialMeasurements: [],
      infoToShow: "quantitativeGuide"
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
          'readyToAddFitTestingDataPercentage'
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'message'
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity',
          'genderAndSex',
          'otherGender'
        ]
    ),

    genderSexQuestion() {
      return `Which is ${this.firstName}'s gender?`;
    },
    raceEthnicityQuestion() {
      return `Which race or ethnicity best describes ${this.firstName}?`;
    },
    latestFacialMeasurement() {
      return this.facialMeasurements[this.facialMeasurements.length - 1];
    },
    messages() {
      return this.errorMessages;
    },
    readyToAddFitTestingData() {
      let numerator = !this.nameIncomplete
        + !this.raceEthnicityIncomplete
        + !this.genderAndSexIncomplete
        + !this.facialMeasurementsIncomplete

      let rounded = Math.round(
        numerator / 4 * 100
      )

      return `${rounded}%`
    },
    sortedFacialMeasurements() {
      return this.facialMeasurements.sort((a, b) => {
        return new Date(a.createdAt) > new Date(b.createdAt)
      })
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

    let toQuery = this.$route.query

    if (toQuery['tabToShow'] && (this.$route.name == "RespiratorUser")) {
      this.tabToShow = toQuery['tabToShow']
    }

    // TODO: add param watchers
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && (this.$route.name == "RespiratorUser")) {
          this.tabToShow = toQuery['tabToShow']
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    addFacialMeasurement() {
      this.facialMeasurements.push(
        {
          source: 'caliper/tape',
          faceWidth: 0,
          noseBridgeHeight: 0,
          nasalRootBreadth: 0,
          jawWidth: 0,
          faceDepth: 0,
          faceLength: 0,
          lowerFaceLength: 0,
          bitragionMentonArc: 0,
          bitragionSubnasaleArc: 0,
          cheekFullness: 'medium',

        }
      )
    },
    async loadStuff() {
      // TODO: load the profile for the current user
      this.loadProfile()
      this.loadFacialMeasurements(this.currentUser.id)
    },
    async loadFacialMeasurements(userId) {
      // TODO: make this more flexible so parents can load data of their children
      await axios.get(
        `/users/${userId}/facial_measurements.json`,
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
