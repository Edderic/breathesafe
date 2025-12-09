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
        <p v-if='infoToShow == "straightLineMeasurementsGuide"' >
An iOS app is currently in development to make the facial measurement collection seamless. Please reach out to info@breathesafe.xyz to get some information about how to get access to this app. After following instructions in the app, you'll be asked to upload data. If successful, you'll see the data here, in JSON format.
</p>

        <!-- iOS App Data (ARKit) -->
        <div v-if='infoToShow == "straightLineMeasurementsGuide"' style="margin: 1em 0;">
          <h4>iOS App Data<span v-if='latestFacialMeasurement && latestFacialMeasurement.arkit && latestFacialMeasurement.updatedAt'> (updated: {{ formatTimestamp(latestFacialMeasurement.updatedAt) }})</span></h4>
          <div v-if='mode == "View"'>
            <pre v-if='latestFacialMeasurement && latestFacialMeasurement.arkit' style="background-color: #f5f5f5; padding: 1em; border-radius: 4px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; overflow-y: auto; max-height: 40vh;">{{ formattedArkit }}</pre>
            <p v-else style="color: #666; font-style: italic;">No iOS app data available.</p>
          </div>
          <div v-else>
            <textarea
              v-if='latestFacialMeasurement'
              v-model='arkitTextareaValue'
              @input='updateArkitFromTextarea'
              style="width: 100%; min-height: 200px; font-family: monospace; padding: 1em; border: 1px solid #ccc; border-radius: 4px;"
              placeholder='Enter JSON data here...'
            ></textarea>
            <p v-else style="color: #666; font-style: italic;">No facial measurement available.</p>
          </div>
        </div>

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
                <label>Nose (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('noseArkit')" :highlight="infoToShow == 'noseArkit'"/>
              </td>
              <td>
                <span v-if="aggregatedArkitMeasurements.nose != null && typeof aggregatedArkitMeasurements.nose === 'number'">
                  {{ aggregatedArkitMeasurements.nose.toFixed(1) }}
                </span>
                <span v-else style="color: #666; font-style: italic;">Incomplete</span>
              </td>
            </tr>

            <tr>
              <th colspan="1">
                <label>Strap (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('strapArkit')" :highlight="infoToShow == 'strapArkit'"/>
              </td>
              <td>
                <span v-if="aggregatedArkitMeasurements.strap != null && typeof aggregatedArkitMeasurements.strap === 'number'">
                  {{ aggregatedArkitMeasurements.strap.toFixed(1) }}
                </span>
                <span v-else style="color: #666; font-style: italic;">Incomplete</span>
              </td>
            </tr>

            <tr>
              <th colspan="1">
                <label>Top Cheek (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('topCheekArkit')" :highlight="infoToShow == 'topCheekArkit'"/>
              </td>
              <td>
                <span v-if="aggregatedArkitMeasurements.topCheek != null && typeof aggregatedArkitMeasurements.topCheek === 'number'">
                  {{ aggregatedArkitMeasurements.topCheek.toFixed(1) }}
                </span>
                <span v-else style="color: #666; font-style: italic;">Incomplete</span>
              </td>
            </tr>

            <tr>
              <th colspan="1">
                <label>Mid Cheek (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('midCheekArkit')" :highlight="infoToShow == 'midCheekArkit'"/>
              </td>
              <td>
                <span v-if="aggregatedArkitMeasurements.midCheek != null && typeof aggregatedArkitMeasurements.midCheek === 'number'">
                  {{ aggregatedArkitMeasurements.midCheek.toFixed(1) }}
                </span>
                <span v-else style="color: #666; font-style: italic;">Incomplete</span>
              </td>
            </tr>

            <tr>
              <th colspan="1">
                <label>Chin (mm)</label>
              </th>
              <td>
                <CircularButton text="?" @click="toggleInfo('chinArkit')" :highlight="infoToShow == 'chinArkit'"/>
              </td>
              <td>
                <span v-if="aggregatedArkitMeasurements.chin != null && typeof aggregatedArkitMeasurements.chin === 'number'">
                  {{ aggregatedArkitMeasurements.chin.toFixed(1) }}
                </span>
                <span v-else style="color: #666; font-style: italic;">Incomplete</span>
              </td>
            </tr>
            </tbody>
          </table>
          </div>

        <div class='flex-dir-col'>

        <br>
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
import { deepSnakeToCamel, deepCamelToSnake, setupCSRF } from './misc.js'
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
      infoToShow: "straightLineMeasurementsGuide",
      arkitTextareaValue: '',
      aggregateArkitTimeout: null
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
      if (!this.facialMeasurements || this.facialMeasurements.length === 0) {
        return null;
      }
      // Find the measurement with the most recent updatedAt timestamp
      return this.facialMeasurements.reduce((latest, current) => {
        if (!latest) return current;
        if (!current || !current.updatedAt) return latest;
        if (!latest.updatedAt) return current;
        return new Date(current.updatedAt) > new Date(latest.updatedAt) ? current : latest;
      }, null);
    },
    sortedFacialMeasurements() {
      return this.facialMeasurements.sort((a, b) => {
        return new Date(a.createdAt) > new Date(b.createdAt)
      })
    },
    formattedArkit() {
      if (!this.latestFacialMeasurement || !this.latestFacialMeasurement.arkit) {
        return '';
      }
      try {
        return JSON.stringify(this.latestFacialMeasurement.arkit, null, 2);
      } catch (e) {
        return String(this.latestFacialMeasurement.arkit);
      }
    },
    aggregatedArkitMeasurements() {
      // Use aggregated values from Ruby backend (computed in FacialMeasurement model)
      if (!this.latestFacialMeasurement || !this.latestFacialMeasurement.aggregated) {
        return {
          nose: null,
          strap: null,
          topCheek: null,
          midCheek: null,
          chin: null
        };
      }

      const aggregated = this.latestFacialMeasurement.aggregated;

      // Convert snake_case keys from Ruby to camelCase for JavaScript
      return {
        nose: aggregated.noseMm !== undefined ? aggregated.noseMm : null,
        strap: aggregated.strapMm !== undefined ? aggregated.strapMm : null,
        topCheek: aggregated.topCheekMm !== undefined ? aggregated.topCheekMm : null,
        midCheek: aggregated.midCheekMm !== undefined ? aggregated.midCheekMm : null,
        chin: aggregated.chinMm !== undefined ? aggregated.chinMm : null
      };
    },
  },
  watch: {
    mode(newMode) {
      // Sync textarea when switching to edit mode
      if (newMode === 'Edit') {
        this.syncArkitTextarea();
      }
    },
    latestFacialMeasurement: {
      handler() {
        // Sync textarea when facial measurement changes
        this.syncArkitTextarea();
      },
      deep: true
    }
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
  beforeUnmount() {
    // Clean up timeout when component is destroyed
    if (this.aggregateArkitTimeout) {
      clearTimeout(this.aggregateArkitTimeout);
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),
    ...mapActions(useManagedUserStore, ['deleteManagedUser', 'loadManagedUser']),
    imgUrl(part) {
      return `https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/${part}.jpg`
    },
    formatTimestamp(timestamp) {
      if (!timestamp) {
        return '';
      }
      // Format as YYYY-MM-DD HH:MM:SS
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return '';
      }
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
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
            // Initialize an empty measurement object so the UI can bind safely
            this.facialMeasurements.push({
              source: 'caliper for straight lines & tape measure for curves'
            })
          }

          // Sync arkit textarea value when measurements are loaded
          this.syncArkitTextarea()
          // whatever you want
        })
        .catch(error => {
          const msgs = error && error.response && error.response.data && error.response.data.messages
          if (Array.isArray(msgs)) {
            this.addMessages(msgs)
          } else {
            this.addMessages([error && error.message ? error.message : 'Something went wrong while loading facial measurements.'])
          }
        // whatever you want
        })
    },
    syncArkitTextarea() {
      if (this.latestFacialMeasurement && this.latestFacialMeasurement.arkit) {
        try {
          this.arkitTextareaValue = JSON.stringify(this.latestFacialMeasurement.arkit, null, 2);
        } catch (e) {
          this.arkitTextareaValue = String(this.latestFacialMeasurement.arkit);
        }
      } else {
        this.arkitTextareaValue = '';
      }
    },
    updateArkitFromTextarea() {
      if (!this.latestFacialMeasurement) {
        return;
      }

      const text = this.arkitTextareaValue.trim();

      if (!text) {
        // Empty textarea means no arkit data
        this.latestFacialMeasurement.arkit = null;
        // Clear aggregated data
        if (this.latestFacialMeasurement.aggregated) {
          this.latestFacialMeasurement.aggregated = {
            noseMm: null,
            strapMm: null,
            topCheekMm: null,
            midCheekMm: null,
            chinMm: null
          };
        }
        return;
      }

      try {
        // Try to parse as JSON
        const parsed = JSON.parse(text);
        this.latestFacialMeasurement.arkit = parsed;

        // Debounce the aggregation API call (wait 500ms after user stops typing)
        if (this.aggregateArkitTimeout) {
          clearTimeout(this.aggregateArkitTimeout);
        }

        this.aggregateArkitTimeout = setTimeout(() => {
          this.computeAggregations(parsed);
        }, 500);
      } catch (e) {
        // Invalid JSON - keep the text but don't update the object yet
        // Validation will happen on save
        // Clear aggregated data on invalid JSON
        if (this.latestFacialMeasurement.aggregated) {
          this.latestFacialMeasurement.aggregated = {
            noseMm: null,
            strapMm: null,
            topCheekMm: null,
            midCheekMm: null,
            chinMm: null
          };
        }
      }
    },
    async computeAggregations(arkitData) {
      // Only compute aggregations in Edit mode
      if (this.mode === 'View') {
        return;
      }

      if (!this.latestFacialMeasurement) {
        return;
      }

      try {
        setupCSRF();

        // Convert camelCase to snake_case before sending to Ruby
        const arkitDataSnakeCase = deepCamelToSnake(arkitData);

        const response = await axios.post(
          `/users/${this.$route.params.id}/facial_measurements/aggregate_arkit.json`,
          { arkit: arkitDataSnakeCase }
        );

        if (response.data && response.data.aggregated) {
          // Convert snake_case keys from Ruby to camelCase for JavaScript
          const aggregated = deepSnakeToCamel(response.data.aggregated);

          // Update the aggregated data
          if (!this.latestFacialMeasurement.aggregated) {
            this.latestFacialMeasurement.aggregated = {};
          }

          this.latestFacialMeasurement.aggregated = {
            noseMm: aggregated.noseMm !== undefined ? aggregated.noseMm : null,
            strapMm: aggregated.strapMm !== undefined ? aggregated.strapMm : null,
            topCheekMm: aggregated.topCheekMm !== undefined ? aggregated.topCheekMm : null,
            midCheekMm: aggregated.midCheekMm !== undefined ? aggregated.midCheekMm : null,
            chinMm: aggregated.chinMm !== undefined ? aggregated.chinMm : null
          };
        }
      } catch (error) {
        // Silently fail - don't show error messages while user is typing
        // Aggregations will be computed on save anyway
        console.warn('Failed to compute aggregations:', error);
      }
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
        // Facial Measurements tab - route to Respirator Users after save
        if (this.messages.length == 0) {
          await this.saveFacialMeasurement(function() {
            this.$router.push({
              name: 'RespiratorUsers'
            })
          }.bind(this))
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
          const msgs = error && error.response && error.response.data && error.response.data.messages
          if (Array.isArray(msgs)) {
            this.addMessages(msgs)
          } else {
            this.addMessages([error && error.message ? error.message : 'Something went wrong while updating profile.'])
          }
          // whatever you want
        })
    },
    async saveFacialMeasurement(successCallback) {
      // Parse arkit from textarea if in edit mode
      if (this.mode !== 'View' && this.arkitTextareaValue.trim()) {
        try {
          this.latestFacialMeasurement.arkit = JSON.parse(this.arkitTextareaValue.trim());
        } catch (e) {
          this.addMessages([`Invalid JSON in iOS App Data: ${e.message}`]);
          return; // Don't save if JSON is invalid
        }
      } else if (this.mode !== 'View' && !this.arkitTextareaValue.trim()) {
        // Empty textarea means no arkit data
        this.latestFacialMeasurement.arkit = null;
      }

      // Convert ARKit data from camelCase to snake_case before sending to Ruby
      let arkitData = null;
      if (this.latestFacialMeasurement.arkit) {
        arkitData = deepCamelToSnake(this.latestFacialMeasurement.arkit);
      }

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
            arkit: arkitData,
            user_id: this.$route.params.id
          }
        }
      )
        .then(response => {
          let data = response.data

          // Reload facial measurements to get the updated data
          this.loadFacialMeasurements(this.$route.params.id);

          successCallback()
          // whatever you want
          // TODO: when saving we wanna get the latest facial measurement
          // e.g. get updated list of latest facial measurements
        })
        .catch(error => {
          const msgs = error && error.response && error.response.data && error.response.data.messages
          if (Array.isArray(msgs)) {
            this.addMessages(msgs)
          } else {
            // Check for validation errors in the response
            const errorData = error.response?.data;
            if (errorData && typeof errorData === 'object') {
              // Handle Rails validation errors
              if (errorData.errors && typeof errorData.errors === 'object') {
                Object.keys(errorData.errors).forEach(key => {
                  const fieldErrors = Array.isArray(errorData.errors[key])
                    ? errorData.errors[key]
                    : [errorData.errors[key]];
                  fieldErrors.forEach(err => {
                    this.addMessages([`${key}: ${err}`]);
                  });
                });
              } else if (errorData.error) {
                this.addMessages([errorData.error]);
              } else {
                this.addMessages([error && error.message ? error.message : 'Something went wrong while saving facial measurements.']);
              }
            } else {
              this.addMessages([error && error.message ? error.message : 'Something went wrong while saving facial measurements.']);
            }
          }
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
