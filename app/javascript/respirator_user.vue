<template>
  <div>
    <h2 class='tagline'>Respirator User</h2>
    <div class='menu row'>
      <Button :class="{ tab: true }" @click='setRouteTo("Demographics")' shadow='true' text='Demographics' :selected="tabToShow=='Demographics'"/>
      <Button :class="{ tab: true }" @click='setRouteTo("FacialMeasurements")' shadow='true' text='Facial Measurements' :selected="tabToShow=='FacialMeasurements'"/>
    </div>

    <div class='main' v-if='tabToShow=="Demographics"'>
      <SurveyQuestion
        question="Which race or ethnicity best describes you?"
        :answer_options="race_ethnicity_options"
        @update="selectRaceEthnicity"
        :selected="raceEthnicity"
      />
      <SurveyQuestion
        question="What is your gender?"
        :answer_options="gender_and_sex_options"
        @update="selectGenderAndSex"
        :selected="genderAndSex"
      />
      <div>
        <input class='text-for-other' type="text" v-model='otherGender'>
      </div>

      <br>

      <Button text="Save" @click='saveProfile()'/>
    </div>

    <div class="edit-facial-measurements" v-if='tabToShow=="FacialMeasurements"'>



      <img v-if='infoToShow == "quantitativeGuide"' class="adaptive-wide" src="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8587533/bin/bmjgh-2021-005537f01.jpg" alt="Depiction of different measurements">

      <div v-if='infoToShow == "noseBridgeHeight"' class='align-items-center'>
        <p class='left-pane'>Select options below to get an understanding of what "Low", "Medium", and "High" nose bridges are.</p>
        <TabSet
          :options='noseBridgeHeightOptions'
          @update='setNoseBridgeHeightExampleToShow'
        />
        <img class='left-pane-image' v-if='noseBridgeHeightExample == "Low"' src="https://qph.cf2.quoracdn.net/main-qimg-4a76e688296db52b1e13b73a03f56242.webp" alt="low nose bridge">
        <img class='left-pane-image' v-if='noseBridgeHeightExample == "Medium"' src="https://qph.cf2.quoracdn.net/main-qimg-688959ce2f1936ceb9fd523e8bc60094.webp" alt="medium nose bridge">
        <img class='left-pane-image' v-if='noseBridgeHeightExample == "High"' src="https://qph.cf2.quoracdn.net/main-qimg-855fbe23110d6998624e7af03ccf642e.webp" alt="high nose bridge">
      </div>

      <div class='align-items-center' v-if='infoToShow == "noseBridgeBreadth"' >
        <p class='left-pane'>Wide vs. Medium nose bridge</p>
        <img class='left-pane-image' src="https://amitismedtour.com/wp-content/uploads/2021/11/Wide-Nose-Rhinoplasty-1-1200x800.jpg" alt="before and after rhinoplasty. Wide vs. Narrow nose bridge">
      </div>


      <br>

      <div class='flex-dir-col'>
        <br>
        <table>
          <thead>
            <tr>
              <th colspan='2'>Quantitative Measurements</th>
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
                <label for="noseBridgeHeight">Nose Bridge Height</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('noseBridgeHeight')"/>
              </td>
              <td>
                <select
                    v-if='latestFacialMeasurement'
                    :value="latestFacialMeasurement.noseBridgeHeight"
                    @change='setFacialMeasurement($event, "noseBridgeHeight")'
                    >
                    <option>low</option>
                    <option>medium</option>
                    <option>high</option>
                </select>
              </td>
            </tr>
            <tr>
              <th>
                <label for="noseBridgeBreadth">Nose Bridge Breadth</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('noseBridgeBreadth')"/>
              </td>
              <td>
                <select
                    v-if='latestFacialMeasurement'
                    :value="latestFacialMeasurement.noseBridgeBreadth"
                    @change='setFacialMeasurement($event, "noseBridgeBreadth")'
                    >
                    <option>narrow</option>
                    <option>medium</option>
                    <option>broad</option>
                </select>
              </td>
            </tr>
            <tr>
              <th>
                <label for="cheekFullness">Cheek Fullness</label>
              </th>
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
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
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
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
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
      tabToShow: 'Demographics',
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
    latestFacialMeasurement() {
      return this.facialMeasurements[this.facialMeasurements.length - 1]
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
          noseBridgeHeight: 'medium',
          noseBridgeBreadth: 'medium',
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
                noseBridgeHeight: 'medium',
                noseBridgeBreadth: 'medium',
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
    async saveProfile() {
      await this.updateProfile()
      this.$router.push({
        name: "RespiratorUser",
        params: {
          id: this.currentUser.id,
        },
        query: {
          tabToShow: 'FacialMeasurements'
        }
      })
    },
    async saveFacialMeasurement() {
      await axios.post(
        `/users/${this.currentUser.id}/facial_measurements.json`, {
          source: this.latestFacialMeasurement.source,
          face_width: this.latestFacialMeasurement.faceWidth,
          nose_bridge_height: this.latestFacialMeasurement.noseBridgeHeight,
          nose_bridge_breadth: this.latestFacialMeasurement.noseBridgeBreadth,
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
    setRouteTo(tabToShow) {
      this.$router.push({
        name: "RespiratorUser",
        query: {
          tabToShow: tabToShow
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
    justify-content: space-around;
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
