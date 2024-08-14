<template>
  <div class='align-items-center flex-dir-col'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>{{pageTitle}}</h2>
    </div>


    <div class='menu row'>
      <TabSet
        :options='tabToShowOptions'
        @update='setRouteTo'
        :tabToShow='tabToShow'
      />
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <div v-show='tabToShow == "Mask"'>
      <h3 class='text-align-center'>Search for and pick a mask</h3>

      <div class='row justify-content-center'>
        <input type="text" @change='updateSearch'>
        <SearchIcon height='2em' width='2em'/>
      </div>


      <div :class='{main: true, grid: true, selectedMask: maskHasBeenSelected}'>
        <div class='card flex flex-dir-col align-items-center justify-content-center' v-for='m in selectDisplayables' @click='selectMask(m.id)'>
          <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
          <div class='description'>
            <span>
              {{m.uniqueInternalModelCode}}
            </span>
          </div>
        </div>
      </div>

      <table>
        <tbody>
          <tr>
            <th>Selected Mask</th>
            <td>{{selectedMask.uniqueInternalModelCode}}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-show='tabToShow == "Comfort"' class='justify-content-center flex-dir-col'>
      <table>
        <tbody>
          <tr>
            <th>Selected Mask</th>
            <td>{{selectedMask.uniqueInternalModelCode}}</td>
          </tr>
        </tbody>
      </table>

      <SurveyQuestion
        question="How comfortable is the position of the mask on the nose?"
        :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
        @update="selectComfortNose"
        :selected="comfort['How comfortable is the position of the mask on the nose?']"
      />

      <SurveyQuestion
        question="Is there adequate room for eye protection?"
        :answer_options="['Inadequate', 'Adequate', 'Not applicable']"
        @update="selectComfortEyeProtection"
        :selected="comfort['Is there adequate room for eye protection?']"
      />

      <SurveyQuestion
        question="Is there enough room to talk?"
        :answer_options="['Not enough', 'Unsure', 'Enough']"
        @update="selectComfortEnoughRoomToTalk"
        :selected="comfort['Is there enough room to talk?']"
      />

      <SurveyQuestion
        question="How comfortable is the position of the mask on face and cheeks?"
        :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
        @update="selectComfortFaceAndCheeks"
        :selected="comfort['How comfortable is the position of the mask on face and cheeks?']"
      />
    </div>


    <div v-show='tabToShow == "User Seal Check"' class='justify-content-center flex-dir-col align-content-center'>
      <table>
        <tbody>
          <tr>
            <th>Selected Mask</th>
            <td>{{selectedMask.uniqueInternalModelCode}}</td>
          </tr>
        </tbody>
      </table>

      <a class='text-align-center' href="//cdc.gov/niosh/docs/2018-130/pdfs/2018-130.pdf" target='_blank'>What are user seal checks?</a>
      <div v-show="showPositiveUserSealCheck">
        <h4>While performing a *positive-pressure* user seal check, </h4>

        <SurveyQuestion
            question="...how much air movement on your face along the seal of the mask did you feel?"
            :answer_options="['A lot of air movement', 'Some air movement', 'No air movement']"
            @update="selectPositivePressureAirMovement"
            :selected="userSealCheck['positive']['...how much air movement on your face along the seal of the mask did you feel?']"
            />

        <SurveyQuestion
            question="...how much did your glasses fog up?"
            :answer_options="['A lot', 'A little', 'Not at all', 'Not applicable']"
            @update="selectPositivePressureGlassesFoggingUp"
            :selected="userSealCheck['positive']['...how much did your glasses fog up?']"
            />

        <SurveyQuestion
            question="...how much pressure build up was there?"
            :answer_options="['Substantial', 'Only a little', 'No pressure build up']"
            @update="selectPositivePressureBuildUp"
            :selected="userSealCheck['positive']['...how much pressure build up was there?']"
            />
      </div>

      <div v-show="!showPositiveUserSealCheck">
        <h4>While performing a *negative-pressure* user seal check, </h4>
        <SurveyQuestion
            question="...how much air passed between your face and the mask?"
            :answer_options="['A lot of air', 'Some air', 'Unnoticeable']"
            @update="selectNegativePressureAirMovement"
            :selected="userSealCheck['negative']['...how much air passed between your face and the mask?']"
            />
      </div>
    </div>

    <div v-show='tabToShow == "QLFT"' class='justify-content-center flex-dir-col align-content-center'>
      <div class='grid qlft'>
        <table>
          <tbody>
            <tr>
              <th>Selected Mask</th>
              <td>{{selectedMask.uniqueInternalModelCode}}</td>
            </tr>

            <tr>
              <th>Procedure</th>
              <td>
                <select v-model='results.qualitative.procedure'>
                  <option>Skipping</option>
                  <option>Full OSHA</option>
                </select>
              </td>
            </tr>

            <tr>
              <th>Solution</th>
              <td>
                <select v-model='results.qualitative.aerosol.type'>
                  <option>Not applicable</option>
                  <option>Isoamyl Acetate</option>
                  <option>Saccharin</option>
                  <option>Bitrex</option>
                  <option>Irritant Smoke</option>
                </select>
              </td>
            </tr>

            <tr>
              <th>Notes</th>
              <td>
                <textarea id="" name="" cols="30" rows="10" v-model='results.qualitative.aerosol.notes'></textarea>
              </td>
            </tr>
          </tbody>
        </table>

        <div class='Instructions' v-show='results.qualitative.aerosol.type == "Saccharin"'>
          <p v-for='text in saccharinInstructions'>
            {{text}}
          </p>
        </div>



        <table>
          <tbody>
            <tr v-for='ex in results.qualitative.exercises'>
              <th>{{ex.name}}</th>
              <td>
                <CircularButton text="?" @click="showDescription(ex.name)"/>
              </td>
              <td>
                <select v-model='ex.result'>
                  <option>Pass</option>
                  <option>Fail</option>
                  <option>Not applicable</option>
                </select>
              </td>
            </tr>

          </tbody>
        </table>
      </div>
    </div>

    <div v-show='tabToShow == "QNFT"' class='justify-content-center flex-dir-col align-content-center'>
      <div class='grid qlft'>
        <table>
          <tbody>
            <tr>
              <th>Selected Mask</th>
              <td>{{selectedMask.uniqueInternalModelCode}}</td>
            </tr>
            <tr>
              <th>Aerosol</th>
              <td>
                <select v-model='results.quantitative.aerosol.type'>
                  <option>Ambient</option>
                  <option>Salt</option>
                  <option>Smoke</option>
                </select>
              </td>
            </tr>

            <tr>
              <th>Initial count (particles / cm3)</th>
              <td>
                <input type='number' v-model='results.quantitative.aerosol.initial_count'>
              </td>
            </tr>

            <tr>
              <th>Procedure</th>
              <td>
                <select v-model='results.quantitative.procedure'>
                  <option>Skipping</option>
                  <option>Full OSHA</option>
                </select>
              </td>
            </tr>
            <tr>
              <th>Notes</th>
              <td>
                <textarea id="" name="" cols="30" rows="10" v-model='results.quantitative.aerosol.notes'></textarea>
              </td>
            </tr>
          </tbody>
        </table>

        <table>
          <thead>
            <th>Exercise</th>
            <td></td>
            <th>Fit Factor</th>
          </thead>

          <tbody>
            <tr v-for='ex in results.quantitative.exercises'>
              <th>{{ex.name}}</th>
              <td>
                <CircularButton text="?" @click="showDescription(ex.name)"/>
              </td>
              <td>
                <input type="number" v-model='ex.fit_factor'>
              </td>
            </tr>

          </tbody>
        </table>
      </div>



    </div>

    <br>

    <div class='row'>
      <Button class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
    </div>

    <br>
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
import SearchIcon from './search_icon.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'FitTest',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SearchIcon,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      id: 0,
      mode: 'Create',
      selectedPressureCheckOption: 'Positive',
      pressureCheckOptions: [
        {
          'text': 'Positive',
        },
        {
          'text': 'Negative',
        }
      ],
      tabToShow: 'Mask',
      secondaryTabToShow: 'Choose Procedure',
      secondaryTabToShowOptions: [
        {
          text: 'Choose Procedure'
        },
        {
          text: 'Instructions'
        },
        {
          text: 'Results'
        },
      ],
      tabToShowOptions: [
        {
          text: "Mask",
        },
        {
          text: "User Seal Check"
        },
        {
          text: "QLFT"
        },
        {
          text: "QNFT"
        },
        {
          text: "Comfort",
        },
      ],
      oshaExercises: {
        'Normal breathing': {
          'description': 'In a normal standing position, without talking, the subject shall breathe normally.'
        },
        'Deep breathing': {
          'description': 'In a normal standing position, the subject shall breathe slowly and deeply, taking caution so as not to hyperventilate.'
        },
        'Turning head side to side': {
          'description': 'Standing in place, the subject shall slowly turn his/her head from side to side between the extreme positions on each side. The head shall be held at each extreme momentarily so the subject can inhale at each side.'
        },

        'Moving head up and down': {
          'description': 'Standing in place, the subject shall slowly move his/her head up and down. The subject shall be instructed to inhale in the up position (i.e., when looking toward the ceiling).'
        },
        'Talking': {
          'description': 'The subject shall talk out loud slowly and loud enough so as to be heard clearly by the test conductor. The subject can read from a prepared text such as the Rainbow Passage, count backward from 100, or recite a memorized poem or song.  Rainbow Passage: When the sunlight strikes raindrops in the air, they act like a prism and form a rainbow. The rainbow is a division of white light into many beautiful colors. These take the shape of a long round arch, with its path high above, and its two ends apparently beyond the horizon. There is, according to legend, a boiling pot of gold at one end. People look, but no one ever finds it. When a man looks for something beyond reach, his friends say he is looking for the pot of gold at the end of the rainbow.'
        },
        'Grimace': {
          'description': 'The test subject shall grimace by smiling or frowning. (This applies only to QNFT testing; it is not performed for QLFT)',
        },
        'Bending over': {
          'description': 'The test subject shall bend at the waist as if he/she were to touch his/her toes. Jogging in place shall be substituted for this exercise in those test environments such as shroud type QNFT or QLFT units that do not permit bending over at the waist.'
        }
      },
      saccharinInstructions: [
'The entire screening and testing procedure shall be explained to the test subject prior to the conduct of the screening test.',

'(a) Taste threshold screening. The saccharin taste threshold screening, performed without wearing a respirator, is intended to determine whether the individual being tested can detect the taste of saccharin.',

'(1) During threshold screening as well as during fit testing, subjects shall wear an enclosure about the head and shoulders that is approximately 12 inches in diameter by 14 inches tall with at least the front portion clear and that allows free movements of the head when a respirator is worn. An enclosure substantially similar to the 3M hood assembly, parts # FT 14 and # FT 15 combined, is adequate.',

"(2) The test enclosure shall have a 3⁄4 -inch (1.9 cm) hole in front of the test subject's nose and mouth area to accommodate the nebulizer nozzle.",

'(3) The test subject shall don the test enclosure. Throughout the threshold screening test, the test subject shall breathe through his/her slightly open mouth with tongue extended. The subject is instructed to report when he/she detects a sweet taste.',

'(4) Using a DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent, the test conductor shall spray the threshold check solution into the enclosure. The nozzle is directed away from the nose and mouth of the person. This nebulizer shall be clearly marked to distinguish it from the fit test solution nebulizer.',

'(5) The threshold check solution is prepared by dissolving 0.83 gram of sodium saccharin USP in 100 ml of warm water. It can be prepared by putting 1 ml of the fit test solution (see (b)(5) below) in 100 ml of distilled water.',

'(6) To produce the aerosol, the nebulizer bulb is firmly squeezed so that it collapses completely, then released and allowed to fully expand.',

'(7) Ten squeezes are repeated rapidly and then the test subject is asked whether the saccharin can be tasted. If the test subject reports tasting the sweet taste during the ten squeezes, the screening test is completed. The taste threshold is noted as ten regardless of the number of squeezes actually completed.',

'(8) If the first response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the saccharin is tasted. If the test subject reports tasting the sweet taste during the second ten squeezes, the screening test is completed. The taste threshold is noted as twenty regardless of the number of squeezes actually completed.',

'(9) If the second response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the saccharin is tasted. If the test subject reports tasting the sweet taste during the third set of ten squeezes, the screening test is completed. The taste threshold is noted as thirty regardless of the number of squeezes actually completed.',

'(10) The test conductor will take note of the number of squeezes required to solicit a taste response.',

'(11) If the saccharin is not tasted after 30 squeezes (step 10), the test subject is unable to taste saccharin and may not perform the saccharin fit test.',

'Note to paragraph 3(a): If the test subject eats or drinks something sweet before the screening test, he/she may be unable to taste the weak saccharin solution.',

'(12) If a taste response is elicited, the test subject shall be asked to take note of the taste for reference in the fit test.',

'(13) Correct use of the nebulizer means that approximately 1 ml of liquid is used at a time in the nebulizer body.',

'(14) The nebulizer shall be thoroughly rinsed in water, shaken dry, and refilled at least each morning and afternoon or at least every four hours.',

'(b) Saccharin solution aerosol fit test procedure.',

'(1) The test subject may not eat, drink (except plain water), smoke, or chew gum for 15 minutes before the test.',

'(2) The fit test uses the same enclosure described in 3. (a) above.',

'(3) The test subject shall don the enclosure while wearing the respirator selected in section I. A. of this appendix. The respirator shall be properly adjusted and equipped with a particulate filter(s).',

'(4) A second DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent is used to spray the fit test solution into the enclosure. This nebulizer shall be clearly marked to distinguish it from the screening test solution nebulizer.',

'(5) The fit test solution is prepared by adding 83 grams of sodium saccharin to 100 ml of warm water.',

'(6) As before, the test subject shall breathe through the slightly open mouth with tongue extended, and report if he/she tastes the sweet taste of saccharin.',

'(7) The nebulizer is inserted into the hole in the front of the enclosure and an initial concentration of saccharin fit test solution is sprayed into the enclosure using the same number of squeezes (either 10, 20 or 30 squeezes) based on the number of squeezes required to elicit a taste response as noted during the screening test. A minimum of 10 squeezes is required.',

'(8) After generating the aerosol, the test subject shall be instructed to perform the exercises in section I. A. 14. of this appendix.',

'(9) Every 30 seconds the aerosol concentration shall be replenished using one half the original number of squeezes used initially (e.g., 5, 10 or 15).',

'(10) The test subject shall indicate to the test conductor if at any time during the fit test the taste of saccharin is detected. If the test subject does not report tasting the saccharin, the test is passed.',

'(11) If the taste of saccharin is detected, the fit is deemed unsatisfactory and the test is failed. A different respirator shall be tried and the entire test procedure is repeated (taste threshold screening and fit testing).',

'(12) Since the nebulizer has a tendency to clog during use, the test operator must make periodic checks of the nebulizer to ensure that it is not clogged. If clogging is found at the end of the test session, the test is invalid.',
      ],
      errorMessages: [],
      masks: [],
      results: {
        'qualitative': {
          procedure: null,
          aerosol: {
            type: 'Not applicable',
            notes: ''
          },
          exercises: [
            {
              name: 'Normal breathing',
              result: null
            },
            {
              name: 'Deep breathing',
              result: null
            },
            {
              name: 'Turning head side to side',
              result: null
            },
            {
              name: 'Moving head up and down',
              result: null
            },
            {
              name: 'Talking',
              result: null
            },
            {
              name: 'Rainbow passage',
              result: null
            },
            {
              name: 'Bending over',
              result: null
            },
            {
              name: 'Normal breathing',
              result: null
            }
          ]
        },
        'quantitative': {
          procedure: 'Full OSHA',
          aerosol: {
            type: 'Ambient',
            initial_count: 0,
            notes: ''
          },
          exercises: [
            {
              name: 'Normal breathing',
              fit_factor: null
            },
            {
              name: 'Deep breathing',
              fit_factor: null
            },
            {
              name: 'Turning head side to side',
              fit_factor: null
            },
            {
              name: 'Moving head up and down',
              fit_factor: null
            },
            {
              name: 'Talking',
              fit_factor: null
            },
            {
              name: 'Rainbow passage',
              fit_factor: null
            },
            {
              name: 'Grimace',
              fit_factor: null
            },
            {
              name: 'Bending over',
              fit_factor: null
            },
            {
              name: 'Normal breathing',
              fit_factor: null
            }
          ]
        }
      },
      selectedMask: {
        id: 0,
        uniqueInternalModelCode: '',
        hasExhalationValve: false
      },
      comfort: {
        "How comfortable is the position of the mask on the nose?": null,
        "Is there adequate room for eye protection?": null,
        "Is there enough room to talk?": null,
        "How comfortable is the position of the mask on face and cheeks?": null
      },
      userSealCheck: {
        'positive': {
          "...how much air movement on your face along the seal of the mask did you feel?": null,
          '...how much did your glasses fog up?': null,
          '...how much pressure build up was there?': null
        },
        'negative': {
          '...how much air passed between your face and the mask?': null
        }
      },
      search: ""
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
    toSave() {
      return {
        comfort: this.comfort,
        mask_id: this.selectedMask.id,
        user_seal_check: this.userSealCheck,
      }
    },
    createOrEdit() {
      return (this.mode == 'Create' || this.mode == 'Edit')
    },
    showPositiveUserSealCheck() {
      return this.selectedMask &&
        'hasExhalationValve' in this.selectedMask &&
        this.selectedMask['hasExhalationValve'] == false
    },
    maskHasBeenSelected() {
      return 'id' in this.selectedMask
    },
    pageTitle() {
      if (this.$route.name == 'NewFitTest') {
        return "Add New Fit Testing"
      }
    },
    displayables() {
      if (this.search == "") {
        return this.masks
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.masks.filter((mask) => mask.uniqueInternalModelCode.toLowerCase().match(lowerSearch))
      }
    },
    selectDisplayables() {
      let lengthToDisplay = 6
      if (this.displayables.length < 6) {
        lengthToDisplay = this.displayables.length
      }

      return this.displayables.slice(0, lengthToDisplay)
    },
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

    let toQuery = this.$route.query

    if ((this.$route.name == "NewFitTest" || this.$route.name == "EditFitTest") && 'id' in this.$route.params) {
      this.id = this.$route.params.id
    }


    if (toQuery['tabToShow'] && (this.$route.name == "NewFitTest")) {
      this.tabToShow = toQuery['tabToShow']
    }

    // TODO: add param watchers
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && ((this.$route.name == "NewFitTest") || (this.$route.name == "EditFitTest"))) {
          this.tabToShow = toQuery['tabToShow']
        }
      }
    )

    this.$watch(
      () => this.$route.params,
      (toParams, fromParams) => {
        if (toParams['id'] && ((this.$route.name == "NewFitTest") || (this.$route.name == "EditFitTest"))) {
          this.id = toParams['id']
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    updateSearch(event) {
      this.selectedMask = {}
      this.search = event.target.value
    },
    getAbsoluteHref(href) {
      // TODO: make sure this works for all
      return `${href}`
    },
    newFitTest() {
      this.$router.push(
        {
          name: "AddFitTest"
        }
      )
    },
    selectMask(id) {
      this.selectedMask = this.masks.filter((m) => m.id == id)[0]
      this.search = this.selectedMask.uniqueInternalModelCode
    },
    async loadStuff() {
      // TODO: load the profile for the current user
      await this.loadMasks()
    },
    async loadMasks() {
      // TODO: make this more flexible so parents can load data of their children
      await axios.get(
        `/masks.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.masks) {
            this.masks = deepSnakeToCamel(data.masks)
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load masks."
          // whatever you want
        })
    },

    validateComfort() {
      let missingValue = []

      for (const [key, value] of Object.entries(this.comfort)) {
        if (value == null) {
          this.errorMessages.push(
            {
              str: `Please fill out: "${key}"`
            }
          )
        }
      }
    },
    validateMask() {
      if (!('id' in this.selectedMask)) {
        this.errorMessages.push(
          {
            str: "Please select a mask."
          }
        )
      }
    },

    async saveFitTest(targetTabToShow) {
      if (this.id) {

        await axios.put(
          `/fit_tests/${this.id}.json`, {
            fit_test: this.toSave
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            // this.mode = 'View'
            this.$router.push({
              path: `/fit_tests/${this.id}`,
              query: {
                tabToShow: targetTabToShow
              },
              force: true
            })
          })
          .catch(error => {
            //  TODO: actually use the error message
            this.errorMessages.push({
              str: "Failed to update fit test."
            })
          })
      } else {

        // create
        await axios.post(
          `/fit_tests.json`, {
            fit_test: this.toSave
          }
        )
          .then(response => {
            let data = response.data

            // TODO: could get the id from data
            // We could save it
            // whatever you want

            this.id = response.data.fit_test.id

            this.$router.push({
              name: 'EditFitTest',
              params: {
                id: this.id
              },
              query: this.$route.query,
              force: true
            })
          })
          .catch(error => {
            //  TODO: actually use the error message
            this.errorMessages.push({
              str: "Failed to create fit test."
            })
          })
      }
    },
    async validateAndSaveFitTest() {
      // this.runValidations()

      this.errorMessages = []

      if (this.errorMessages.length > 0) {
        return;
      }

      if (this.tabToShow == 'Mask') {
        this.validateMask()

        if (this.errorMessages.length == 0) {
          await this.saveFitTest('Comfort')
        } else {
          return
        }

        return
      }

      else if (this.tabToShow == 'Comfort') {
        this.validateMask()
        this.validateComfort()

        if (this.errorMessages.length == 0) {
          await this.saveFitTest('User Seal Check')
        } else {
          return
        }
      }

    },

    selectPositivePressureAirMovement(value) {
      this['userSealCheck']['positive']['...how much air movement on your face along the seal of the mask did you feel?'] = value
    },
    selectNegativePressureAirMovement(value) {
      this['userSealCheck']['negative']['...how much air passed between your face and the mask?'] = value
    },
    selectPositivePressureGlassesFoggingUp(value) {
      this['userSealCheck']['positive']['...how much did your glasses fog up?'] = value
    },
    selectPositivePressureBuildUp(value) {
      this['userSealCheck']['positive']['...how much pressure build up was there?'] = value
    },
    selectNegativePressure(value) {
      this['userSealCheck']['While performing a negative user seal check, did you notice any leakage?'] = value
    },
    selectComfortNose(value) {
      this['comfort']['How comfortable is the position of the mask on the nose?'] = value
    },
    selectComfortEyeProtection(value) {
      this['comfort']['Is there adequate room for eye protection?'] = value
    },
    selectComfortEnoughRoomToTalk(value) {
      this['comfort']['Is there enough room to talk?'] = value
    },
    selectComfortFaceAndCheeks(value) {
      this['comfort']['How comfortable is the position of the mask on face and cheeks?'] = value
    },
    selectGeneralComfort(value) {
      this['comfort']['How comfortable is this mask/respirator?'] = value
    },
    setRouteTo(opt) {
      this.$router.push({
        name: "NewFitTest",
        query: {
          tabToShow: opt.name
        }
      })
    },
  }
}
</script>

<style scoped>
  .flex {
    display: flex;
  }
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .card {
    padding: 1em 0;
  }

  .card:hover {
    cursor: pointer;
  }

  .card .description {
    padding: 1em 0;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }
  .thumbnail {
    max-width:10em;
    max-height:10em;
  }

  td,th {
    padding: 1em;
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

  .main, .grid.selectedMask {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .align-content-center {
    display: flex;
    align-content: center;
  }

  .justify-content-center {
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
  tbody tr:hover {
    cursor: pointer;
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .text-align-center {
    text-align: center;
  }

  p {
    max-width: 50em;
  }
</style>
