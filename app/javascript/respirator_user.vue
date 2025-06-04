<template>
  <div>
    <h2 class='tagline'>Respirator User</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>
    <div class='centered align-items-center'>
      <div>
        <span>User: {{managedUser.fullName}}</span>
      </div>
      <div>
        <span>Percent Completed: {{Math.round((1 - managedUser.missingRatio) * 100, 4)}}%</span>
      </div>

    </div>
      <br>

    <div class='menu row'>
      <TabSet
        class='tabToShowNotMobile'
        :options='tabToShowOptions'
        @update='setRouteTo'
        :tabToShow='tabToShow'
      />
    </div>

    <div class='menu row' v-show="tabToShow == 'Facial Measurements'">
      <TabSet
        :options='facialMeasurementParts'
        @update='setSecondaryRouteTo'
        :tabToShow='secondaryTab'
      />
    </div>

    <div class='main justify-items-center' v-if='tabToShow=="Name"'>
      <p class='narrow-p '>
        A user could input data on behalf of other users (e.g. a parent inputting data of their children).
        Adding names could help you distinguish among individuals who you'd be inputting data for.
        This data will not be shared publicly.
      </p>
      <table class='questions'>
        <tbody>
          <tr class='canConvertToColumn'>
            <td>What is first name of the individual you'll be adding data for?</td>
            <td>
              <input
                  type='text'
                  v-model='managedUser.firstName'
                  :disabled='mode == "View"'
              >
            </td>
          </tr>
          <tr class='canConvertToColumn'>
            <td>What is the last name of the individual you'll be adding data for?</td>
            <td>
              <input
                  type='text'
                  v-model='managedUser.lastName'
                  :disabled='mode == "View"'
              >
            </td>
          </tr>
        </tbody>
      </table>

      <br>

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
        :selected="managedUser.raceEthnicity"
        :disabled='mode == "View"'
      />
      <SurveyQuestion
        :question="genderSexQuestion"
        :answer_options="gender_and_sex_options"
        @update="selectGenderAndSex"
        :selected="managedUser.genderAndSex"
        :disabled='mode == "View"'
      />
      <div>
        <input class='text-for-other' type="text" v-model='otherGender'
        :disabled='mode == "View"'
        >
      </div>

      <SurveyQuestion
        :question="yearOfBirthQuestion"
        :value="managedUser.yearOfBirth"
        question_type="number"
        @update="selectYearOfBirth"
        :disabled='mode == "View"'
        placeholder='yyyy'
      />

      <br>
    </div>

    <div class="edit-facial-measurements" v-if='tabToShow=="Facial Measurements"'>

      <div class='left-pane' >
        <p v-if='infoToShow == "straightLineMeasurementsGuide"' >For measuring straight lines (e.g. face width (B), face length (D), etc.), we recommend a digital caliper such as <a href="https://www.amazon.com/gp/product/B00JALAIIE/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1" target='_blank'>this</a>.</p>
        <a href="https://www.amazon.com/gp/product/B00JALAIIE/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1" target='_blank' v-if='infoToShow == "straightLineMeasurementsGuide"' >
          <img class='left-pane-image' src="https://c.media-amazon.com/images/I/6194IWMjJEL._SX522_.jpg" alt='iGaging 6" Digital External Outside Caliper OD for Woodworking' v-if='infoToShow == "straightLineMeasurementsGuide"' >
        </a>

        <p v-show='infoToShow == "curvedMeasurementsGuide"'>For measuring curves (e.g. bitragion subnasale arc (L) and bitragion menton arc (K)), we recommend a tape measure such as <a href="https://www.amazon.com/dp/B0BGHCTL45?ref=ppx_yo2ov_dt_b_fed_asin_title">this</a>.</p>

        <a v-show='infoToShow == "curvedMeasurementsGuide"' href="https://www.amazon.com/dp/B0BGHCTL45?ref=ppx_yo2ov_dt_b_fed_asin_title" target='_blank'>
          <img class='left-pane-image' src="https://c.media-amazon.com/images/I/71Cwjwnqc6L._SL1500_.jpg" alt='Tape Measure, iBayam Soft Ruler Measuring Tape for Body Weight Loss Fabric Sewing Tailor Cloth Vinyl Measurement Craft Supplies, 60-Inch Double Scale Ruler, 2-Pack White, Blue' v-show='infoToShow == "curvedMeasurementsGuide"'>
        </a>

        <div v-for='(value, key, index) in facialMeasurementExplanations'>

          <div v-if='infoToShow == key'>
            <br>
            <br>
            <p>{{value.eng}}</p>
            <img class='left-pane-image' :src="value.image_url" alt='`${value.eng} measurement`' >
            <p>{{value.explanation}}</p>
          </div>

        </div>

        <img class='left-pane-image' :src="imgUrl('face_depth')" alt='face depth measurement' v-if='infoToShow == "faceDepth"'>

        <p v-if='infoToShow == "cheekFullness"' class='left-pane'>Select options below to get an understanding of different types of cheek fullness:</p>
        <TabSet

          :options='cheekFullnessOptions'
          @update='setCheekFullnessExampleToShow'
          :tabToShow="cheekFullnessExample"
          v-if='infoToShow == "cheekFullness"'
        />
        <img class='left-pane-image' v-if='infoToShow == "cheekFullness" && cheekFullnessExample == "Hallow/gaunt"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-hollow.png" alt="hallow/gaunt cheeks">
        <img class='left-pane-image' v-if='infoToShow == "cheekFullness" && cheekFullnessExample == "Medium"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-neutral.png" alt="medium-ful cheeks">
        <img class='left-pane-image' v-if='infoToShow == "cheekFullness" && cheekFullnessExample == "Rounded/full"' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/cheeks-rounded.png" alt="rounded cheeks">
      </div>

      <div class='flex-dir-col' v-show="secondaryTab == 'Part I'">
        <br>
        <table>
          <thead>
            <tr>
              <th colspan='2'><h3>Straight-line Measurements (Part I)</h3></th>
              <td>
                <CircularButton text="?" @click="toggleInfo('straightLineMeasurementsGuide')" :highlight="infoToShow == 'straightLineMeasurementsGuide'"/>
              </td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th colspan="1">
                <label for="faceWidth">Face Width (mm) </label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('faceWidthMm')" :highlight="infoToShow == 'faceWidthMm'"/>
              </td>

              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceWidth"
                    @change='setFacialMeasurement($event, "faceWidth")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>

            <tr>
              <th colspan="1">
                <label for="jawWidth">Jaw Width (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('jawWidthMm')" :highlight="infoToShow == 'jawWidthMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.jawWidth"
                    @change='setFacialMeasurement($event, "jawWidth")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>
            <tr v-show="secondaryTab == 'Part I' || mode == 'View'">
              <th colspan="1">
                <label for="faceDepth">Face Depth (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('faceDepth')" :highlight="infoToShow == 'faceDepth'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceDepth"
                    @change='setFacialMeasurement($event, "faceDepth")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>

            <tr v-show="secondaryTab == 'Part I' || mode == 'View'">
              <th colspan="1">
                <label for="faceLength">Face Length (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('faceLengthMm')" :highlight="infoToShow == 'faceLengthMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.faceLength"
                    @change='setFacialMeasurement($event, "faceLength")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>

            <tr v-show="secondaryTab == 'Part I' || mode == 'View'">
              <th colspan="1">
                <label for="lowerFaceLength">Lower Face Length (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('lowerFaceLengthMm')" :highlight="infoToShow == 'lowerFaceLengthMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.lowerFaceLength"
                    @change='setFacialMeasurement($event, "lowerFaceLength")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>


            </tbody>
          </table>
          </div>
          <div class='flex-dir-col'  v-show="secondaryTab == 'Part II'">
            <br>

            <table>
              <tbody>
              <tr>
                <th colspan='2' ><h3>Straight-line Measurements (Part II)</h3></th>
                <td>
                  <CircularButton text="?" @click="toggleInfo('straightLineMeasurementsGuide')" :highlight="infoToShow == 'straightLineMeasurementsGuide'"/>
                </td>
              </tr>
              <tr v-show="secondaryTab == 'Part II' || mode == 'View'">
                <th colspan="1">
                  <label for="noseProtrusion">Nose Breadth (mm)</label>
                </th>

                <td>
                  <CircularButton text="?" @click="toggleInfo('noseBreadthMm')" :highlight="infoToShow == 'noseBreadthMm'"/>
                </td>
                <td>
                  <input
                      v-if='latestFacialMeasurement'
                      type='number'
                      :value="latestFacialMeasurement.noseBreadth"
                      @change='setFacialMeasurement($event, "noseBreadth")'
                      :disabled="mode == 'View'"
                      >
                </td>
              </tr>

              <tr v-show="secondaryTab == 'Part II' || mode == 'View'">
                <th colspan="1">
                  <label for="noseProtrusion">Nose Protrusion (mm)</label>
                </th>

                <td>
                  <CircularButton text="?" @click="toggleInfo('noseProtrusionMm')" :highlight="infoToShow == 'noseProtrusionMm'"/>
                </td>
                <td>
                  <input
                      v-if='latestFacialMeasurement'
                      type='number'
                      :value="latestFacialMeasurement.noseProtrusion"
                      @change='setFacialMeasurement($event, "noseProtrusion")'
                      :disabled="mode == 'View'"
                      >
                </td>
              </tr>

              <tr v-show="secondaryTab == 'Part II' || mode == 'View'">
                <th colspan="1">
                  <label for="nasalRootBreadth">Nasal Root Breadth (mm)</label>
                </th>

                <td>
                  <CircularButton text="?" @click="toggleInfo('nasalRootBreadthMm')" :highlight="infoToShow == 'nasalRootBreadthMm'"/>
                </td>
                <td>
                  <input
                      v-if='latestFacialMeasurement'
                      type='number'
                      :value="latestFacialMeasurement.nasalRootBreadth"
                      @change='setFacialMeasurement($event, "nasalRootBreadth")'
                      :disabled="mode == 'View'"
                      >
                </td>
              </tr>

              <tr v-show="secondaryTab == 'Part II' || mode == 'View'">
                <th colspan="1">
                  <label for="noseBridgeHeight">Nose Bridge Height (mm)</label>
                </th>
                <td>
                  <CircularButton text="?" @click="toggleInfo('noseBridgeHeightMm')" :highlight="infoToShow == 'noseBridgeHeightMm'"/>
                </td>
                <td>
                  <input
                      v-if='latestFacialMeasurement'
                      type='number'
                      :value="latestFacialMeasurement.noseBridgeHeight"
                      @change='setFacialMeasurement($event, "noseBridgeHeight")'
                      :disabled="mode == 'View'"
                      >
                </td>
              </tr>

              <tr v-show="secondaryTab == 'Part II' || mode == 'View'">
                <th colspan="1">
                  <label for="lipWidth">Lip Width (mm)</label>
                </th>
                <td>
                  <CircularButton text="?" @click="toggleInfo('lipWidthMm')" :highlight="infoToShow == 'lipWidthMm'"/>
                </td>
                <td>
                  <input
                      v-if='latestFacialMeasurement'
                      type='number'
                      :value="latestFacialMeasurement.lipWidth"
                      :disabled="mode == 'View'"
                      @change='setFacialMeasurement($event, "lipWidth")'
                      >
                </td>
              </tr>




            </tbody>
          </table>
        </div>

        <div class='flex-dir-col'>

        <br>

        <table v-show="secondaryTab == 'Part III'" >
          <tbody>

            <tr>
              <th colspan='2'><h3>Curved Measurements</h3></th>
              <td>
                <CircularButton text="?" @click="toggleInfo('curvedMeasurementsGuide')" :highlight="infoToShow == 'curvedMeasurementsGuide'"/>
              </td>
            </tr>

            <tr v-show="secondaryTab == 'Part III' || mode == 'View'">
              <th colspan="1">
                <label for="bitragionMentonArc">Bitragion Menton Arc (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('bitragionMentonArcMm')" :highlight="infoToShow == 'bitragionMentonArcMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.bitragionMentonArc"
                    @change='setFacialMeasurement($event, "bitragionMentonArc")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>

            <tr v-show="secondaryTab == 'Part III' || mode == 'View'">
              <th colspan="1">
                <label for="bitragionSubnasaleArc">Bitragion Subnasale Arc (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('bitragionSubnasaleArcMm')" :highlight="infoToShow == 'bitragionSubnasaleArcMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.bitragionSubnasaleArc"
                    @change='setFacialMeasurement($event, "bitragionSubnasaleArc")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>

            <tr v-show="secondaryTab == 'Part III' || mode == 'View'">
              <th colspan="1">
                <label for="headCircumference">Head Circumference (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('headCircumferenceMm')" :highlight="infoToShow == 'headCircumferenceMm'"/>
              </td>
              <td>
                <input
                    v-if='latestFacialMeasurement'
                    type='number'
                    :value="latestFacialMeasurement.headCircumference"
                    @change='setFacialMeasurement($event, "headCircumference")'
                    :disabled="mode == 'View'"
                    >
              </td>
            </tr>
          </tbody>
        </table>

        <table v-show="secondaryTab == 'Part III'">
          <thead>
            <tr>
              <th colspan='3'><h3>Qualitative Measurements</h3></th>
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
                    :disabled="mode == 'View'"
                    >
                    <option>hollow/gaunt</option>
                    <option>medium</option>
                    <option>rounded/full</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>

      </div>


    </div>

    <br>

    <div class='buttons justify-content-center'>
      <Button :shadow='true' class='button' text="View Mode" @click='mode = "View"' v-show='mode == "Edit"'/>
      <Button :shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-show='mode == "View"'/>
      <Button :shadow='true' text="Save and continue" @click='save()' v-show='mode != "View"'/>
      <Button :shadow='true' text="Delete" @click='deleteUser($route.params.id)' v-show='mode == "Edit"'/>
      <Button :shadow='true' text="Apply Retroactively to Fit Tests" @click='applyFacialMeasurements' v-show='mode == "View" && tabToShow == "Facial Measurements"'/>
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
import { getFacialMeasurements } from './facial_measurements.js'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useManagedUserStore } from './stores/managed_users_store';
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
      facialMeasurementParts: [
        {
          text: "Part I",
        },
        {
          text: "Part II",
        },
        {
          text: "Part III"
        }
      ],
      secondaryTab: 'Part I',

      errorMessages: [],
      mode: 'View',
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
      tabToShow: 'Name',
      tabToShowOptions: [
        {
          text: "Name",
        },
        {
          text: "Demographics",
        },
        {
          text: "Facial Measurements"
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
      infoToShow: "straightLineMeasurementsGuide"
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
          'messages'
        ]
    ),
    ...mapWritableState(
      useManagedUserStore,
      ['managedUser']
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'otherGender'
        ]
    ),

    facialMeasurementExplanations() {
      return getFacialMeasurements.bind(this)()
    },

    genderSexQuestion() {
      return `What is ${this.managedUser.firstName}'s gender?`;
    },
    yearOfBirthQuestion() {
      return `What is ${this.managedUser.firstName}'s year of birth? (Leave blank if ${this.managedUser.firstName} prefers not to disclose)`;
    },
    raceEthnicityQuestion() {
      return `Which race or ethnicity best describes ${this.managedUser.firstName}?`;
    },
    latestFacialMeasurement() {
      return this.facialMeasurements[this.facialMeasurements.length - 1];
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

    if (toQuery['secondaryTab'] && (this.$route.name == "RespiratorUser")) {
      this.secondaryTab = toQuery['secondaryTab']
    }

    // TODO: add param watchers
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && (this.$route.name == "RespiratorUser")) {
          this.tabToShow = toQuery['tabToShow']
        }

        if (toQuery['secondaryTab'] && (this.$route.name == "RespiratorUser")) {
          this.secondaryTab = toQuery['secondaryTab']
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['deleteManagedUser', 'loadManagedUser']),
    imgUrl(part) {
      return `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/${part}.jpg`
    },

    async applyFacialMeasurements() {
      let answer = window.confirm(`This will apply this set of facial measurements to existing fit tests for ${this.managedUser.fullName}, overriding past facial measurements. Are you sure?`);

      if (answer) {
        // post facial measurements to fit test
        await axios.post(
          `/facial_measurements/${this.latestFacialMeasurement.id}/fit_tests`,
        )
          .then(response => {
            let data = response.data
            this.$router.push({
              'name': 'FitTests'
            })

          })
          .catch(error => {
            if (error && error.response && error.response.data && error.response.data.messages) {
              this.addMessages(error.response.data.messages)
            } else {
              this.addMessages([error.message])
            }
          })
      }
    },

    async deleteUser(id) {
      await this.deleteManagedUser(
        id,
        function () {
          this.$router.push(
            {
              name: 'RespiratorUsers'
            }
          )
        }.bind(this),
        function () {
          // do nothing
        }.bind(this)
      )

    },
    setSecondaryRouteTo(opt) {
      this.$router.push({
        name: "RespiratorUser",
        query: {
          tabToShow: 'Facial Measurements',
          secondaryTab: opt.name
        }
      })
    },
    async loadStuff() {
      this.loadManagedUser(this.$route.params.id)
      this.loadFacialMeasurements(this.$route.params.id)
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
            let dictionary = {
              source: 'caliper for straight lines & tape measure for curves'
            }

            for (key of this.getFacialMeasurements) {
              dictionary[key] = undefined
            }

            this.facialMeasurements.push(dictionary)
          }
          // whatever you want
        })
        .catch(error => {
          for(let errorMessage of error.response.data.messages) {
            this.messages.push({
              str: errorMessage
            })
          }
        // whatever you want
        })
    },
    validateYearOfBirth() {
      let messages = [];

      let fullYear = (new Date()).getFullYear()

      if (this.managedUser.yearOfBirth && this.managedUser.yearOfBirth > fullYear) {
        messages.push("Year of birth cannot in the future")
      }

      this.addMessages(messages);
    },
    validateFacialMeasurementsPart(parts) {
      let messages = [];
      parts.forEach((d) => {
        if (this.latestFacialMeasurement[d] == null || this.latestFacialMeasurement[d] == "" || this.latestFacialMeasurement[d] == 0) {
          messages.push(`${d} must be a positive number.`)
        }
      })

      this.addMessages(messages);
    },
    async save() {
      if (this.tabToShow == "Name") {
        await this.saveProfile("Demographics")
      } else if (this.tabToShow == "Demographics") {
        this.validateYearOfBirth()

        if (this.messages.length == 0) {
          await this.saveProfile("Facial Measurements")
        }
      } else {
        if (this.secondaryTab == 'Part I') {
          if (this.messages.length == 0) {
            await this.saveFacialMeasurement(function() {
              this.setSecondaryRouteTo({name: 'Part II'})
            }.bind(this))
          }
        }
        else if (this.secondaryTab == 'Part II') {
          if (this.messages.length == 0) {
            await this.saveFacialMeasurement(function() {
              this.setSecondaryRouteTo({name: 'Part III'})
            }.bind(this))
          }
        }
        else if (this.secondaryTab == 'Part III') {
          if (this.messages.length == 0) {
            await this.saveFacialMeasurement(function() {
              this.mode = 'View'
              this.addMessages(["Successfully saved the last step of facial measurements."])

              this.setSecondaryRouteTo({name: 'Part III'})
            }.bind(this))


          }
        }
      }
        // must be in Facial Measurements
    },
    async saveProfile(tabToShow) {
      await this.updateProfile(this.$route.params.id)
      this.$router.push({
        name: "RespiratorUser",
        params: {
          id: this.$route.params.id,
        },
        query: {
          tabToShow: tabToShow
        }
      })
    },
    async updateProfile(id) {
      setupCSRF();

      if (!id) {
        id = currentUser.id
      }

      let toSave = {
        'profile': {
          'first_name': this.managedUser.firstName,
          'last_name': this.managedUser.lastName,
          'race_ethnicity': this.managedUser.raceEthnicity,
          'gender_and_sex': this.managedUser.genderAndSex,
          'year_of_birth': this.managedUser.yearOfBirth,
        }
      }

      await axios.put(
        `/users/${id}/profile.json`,
        toSave
      )
        .then(response => {
          this.addMessages(response.data.messages)
          this.status = 'saved'
        })
        .catch(error => {
          this.addMessages(error.response.data.messages)
          // whatever you want
        })
    },
    async saveFacialMeasurement(successCallback) {
      await axios.post(
        `/users/${this.$route.params.id}/facial_measurements.json`, {
          facial_measurement: {
            source: this.latestFacialMeasurement.source,
            face_width: this.latestFacialMeasurement.faceWidth,
            nose_bridge_height: this.latestFacialMeasurement.noseBridgeHeight,
            nasal_root_breadth: this.latestFacialMeasurement.nasalRootBreadth,
            nose_breadth: this.latestFacialMeasurement.noseBreadth,
            lip_width: this.latestFacialMeasurement.lipWidth,
            nose_protrusion: this.latestFacialMeasurement.noseProtrusion,
            jaw_width: this.latestFacialMeasurement.jawWidth,
            face_depth: this.latestFacialMeasurement.faceDepth,
            face_length: this.latestFacialMeasurement.faceLength,
            lower_face_length: this.latestFacialMeasurement.lowerFaceLength,
            bitragion_menton_arc: this.latestFacialMeasurement.bitragionMentonArc,
            bitragion_subnasale_arc: this.latestFacialMeasurement.bitragionSubnasaleArc,
            cheek_fullness: this.latestFacialMeasurement.cheekFullness,
            head_circumference: this.latestFacialMeasurement.headCircumference,
            user_id: this.$route.params.id
          }
        }
      )
        .then(response => {
          let data = response.data

          successCallback()
          // whatever you want
          // TODO: when saving we wanna get the latest facial measurement
          // e.g. get updated list of latest facial measurements
        })
        .catch(error => {
          this.addMessages([error.response.data.messages])
          // whatever you want
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
      this.managedUser.raceEthnicity = raceEth
    },
    selectGenderAndSex(genderAndSex) {
      this.managedUser.genderAndSex = genderAndSex
    },
    selectYearOfBirth(event) {
      this.managedUser.yearOfBirth = parseInt(event.target.value)
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
    max-width: 2.5em;
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

  .justify-content-center {
    justify-content: center;
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
    max-width: 24em;
  }
  .left-pane {
    text-align: center;
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
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
    min-width: 53em;
  }

  .buttons {
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
      display: grid;
      grid-template-columns: 100%;
      min-width: auto;
    }

    .buttons {
      flex-direction: column;
    }

    .canConvertToColumn {
      display: flex;
      flex-direction: column;
      margin: 1em 0;
    }

    input {
      width: 90vw;
      padding: 1em;
    }
  }

</style>
