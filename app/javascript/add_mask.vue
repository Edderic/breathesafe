<template>
  <div class='align-items-center'>
    <h2 class='tagline'>{{tagline}}</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <TabSet
      :options='tabToShowOptions'
      @update='setDisplay'
      :tabToShow='displayTab'
      v-if='mode == "Show"'
    />

    <TabSet
      class='hide-when-mobile'
      :options='tabEditOptions'
      @update='setRouteTo'
      :tabToShow='tabToShow'
        v-if='newOrEdit && displayTab != "Fit Testing"'
    />
    <br>

    <div class='main' v-show="displayTab == 'Misc. Info'">
      <div :class='{ grid: true, view: mode == "Show", edit: mode != "Show", triple: columnCount == 3, quad: columnCount == 4}'>
        <table v-if='tabToShow == "Image & Purchasing" || mode=="Show"'>
          <tbody>
            <tr>
            </tr>
            <tr v-show='newOrEdit' v-for='(imageUrl, index) in imageUrls'>
              <th>Image URL</th>
              <td>
                <input class='input-list' type="text" :value='imageUrl' @change="update($event, 'imageUrls', index)"
                                          v-show="newOrEdit" placeholder="e.g. https://examplemask.com/mask1.jpg"
                                                             >
              </td>
            </tr>

            <tr v-for="(imageUrl, index) in imageUrls">
              <td :colspan='3' class='text-align-center'>
                <img class='preview' :src="imageUrl" :alt="maskImageAlt(index)">
              </td>
            </tr>


            <tr v-if='newOrEdit'>
              <th>Purchasing URLs</th>
              <td class='justify-content-center' colspan=2>
                <CircularButton text="+" @click="addPurchasingUrl" v-if='newOrEdit'/>
              </td>
            </tr>
            <tr>
              <th colspan='2'>Purchasing URL</th>
              <th v-if='userCanEdit && editMode'>Delete</th>
            </tr>
            <tr v-for="(purchasingUrl, index) in whereToBuyUrls" class='text-align-center'>
              <td :colspan='whereToBuyUrlsColspan' >
                <input class='input-list almost-full-width' type="text" :value='purchasingUrl' @change="update($event, 'whereToBuyUrls', index)"
                                                            v-if="newOrEdit"
                                                            >
                                                            <a :href="purchasingUrl" v-if="!newOrEdit">{{shortHand(purchasingUrl)}}</a>
              </td>
                <td>
                  <CircularButton text="x" @click="deletePurchasingUrl(index)" v-show='["New", "Edit"].includes(this.mode) && userCanEdit'/>
                </td>
                <td>
                </td>
            </tr>
          </tbody>

        </table>
        <table v-if='tabToShow == "Basic Info" || mode=="Show"'>

          <thead>
             <tr>
               <th colspan=2><h3>Basic Info</h3></th>
             </tr>
          </thead>
          <tbody>
            <tr>
              <th>Unique Internal Model Code</th>
              <td colspan='1'>
                <input class='full-width has-minimal-width' type="text" v-model='uniqueInternalModelCode' v-show="newOrEdit" placeholder="e.g. Flo Mask Adults S/M Nose with Pro filter">
                <span class='full-width has-minimal-width ' v-show="!newOrEdit">
                  {{uniqueInternalModelCode }}
                </span>
              </td>
            </tr>

            <tr>
              <th>Initial cost (US Dollars)</th>
              <td colspan='1' class='text-align-center'>
                <input type="number"
                       v-model='initialCostUsDollars'
                       v-show="newOrEdit"
                       >

                       <ColoredCell
                           v-show='!newOrEdit'
                           class='risk-score'
                           :colorScheme="costColorScheme"
                           :maxVal=1
                           :value='initialCostUsDollars'
                           :exception='exceptionDollarObject'
                           :text='dollarText(initialCostUsDollars)'
                           :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                           :title='dollarText(initialCostUsDollars)'
                           />
              </td>
            </tr>

            <tr>
              <th>Colors</th>
              <td colspan='1' class='text-align-center'>

              <span v-for='opt in colorOptions' class='filterCheckbox' >
                <Circle :color='opt' :selected='colors.includes(opt)' :for='`color${opt}`' @click='filterFor("Color", opt)' v-if='newOrEdit || colors.includes(opt)'/>
              </span>

              </td>
            </tr>

            <tr>
              <th >Filter type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="filterType"
                    v-show="newOrEdit"
                    >
                    <option>cloth</option>
                    <option>surgical</option>
                    <option>ASTM Lvl 3</option>
                    <option>ASTM</option>
                    <option>CE</option>
                    <option>E100</option>
                    <option>FFP2 Rated</option>
                    <option>KF80</option>
                    <option>KF94</option>
                    <option>KN95</option>
                    <option>KN100</option>
                    <option>N95</option>
                    <option>N99</option>
                    <option>N100</option>
                    <option>Non-Rated</option>
                    <option>P95</option>
                    <option>P99</option>
                    <option>P100</option>
                    <option>PM2.5</option>
                </select>

                <span v-show='!newOrEdit'>{{filterType}}</span>
              </td>
            </tr>
            <tr>
              <th >Style</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="style"
                    v-show="newOrEdit"
                    >
                    <option>Bifold</option>
                    <option>Bifold &amp; Gasket</option>
                    <option>Boat</option>
                    <option>Cotton + High Filtration Efficiency Material</option>
                    <option>Cup</option>
                    <option>Duckbill</option>
                    <option>Elastomeric</option>
                </select>
                <span v-show='!newOrEdit'>{{style}}</span>
              </td>
            </tr>

            <tr>
              <th colspan='1'>Strap type</th>
              <td colspan='1' class='text-align-center'>
                <select
                    v-model="strapType"
                    v-show="newOrEdit"
                    >
                    <option>Earloop</option>
                    <option>Adjustable Earloop</option>
                    <option>Headstrap</option>
                    <option>Adjustable Headstrap</option>
                </select>
                <span v-show='!newOrEdit'>{{strapType}}</span>
              </td>
            </tr>

            <tr>
              <th>Has exhalation valve</th>
              <td v-show='!newOrEdit'>{{hasExhalationValve}}</td>
              <td v-show="newOrEdit">
                <input type="text" v-model='hasExhalationValve'>
              </td>
            </tr>

          </tbody>
        </table>

        <table v-if='tabToShow == "Dimensions" || mode=="Show"'>
          <thead>
             <tr>
               <th colspan=2><h3>Dimensions</h3></th>
             </tr>
          </thead>
          <tbody>
            <tr>
              <th>Mass (grams)</th>
              <td>
                <input type="number" v-model="massGrams" v-show="newOrEdit">

                <ColoredCell
                    v-show='!newOrEdit'
                    class='risk-score'
                    :colorScheme="massColorScheme"
                    :maxVal=1
                    :value='massGrams'
                    :exception='exceptionObjectBlank'
                    :text='massText(massGrams)'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                    :title='massText(massGrams)'
                    />
              </td>
            </tr>
            <tr>
              <th>Perimeter (mm)</th>
              <td>
                <input type="number" v-model="perimeterMm" v-show="newOrEdit">
                <ColoredCell
                    v-show='!newOrEdit'
                    class='risk-score'
                    :colorScheme="perimColorScheme"
                    :maxVal=1
                    :value='perimeterMm'
                    :exception='exceptionObjectBlank'
                    :text='distanceText(perimeterMm, "mm")'
                    :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                    :title='distanceText(perimeterMm, "mm")'
                    />
              </td>
            </tr>
          </tbody>
        </table>
        <table v-if='tabToShow == "Filtration & Breathability" || mode=="Show"'>
          <tbody>
            <tr v-if='newOrEdit'>
              <td colspan='2'>
                <CircularButton text="+" @click="addFiltEffAndBreathability" v-if='newOrEdit'/>
              </td>
            </tr>
          </tbody>

          <tbody v-for="(f, index) in filtrationEfficiencies" class='text-align-center'>
            <tr>
              <td colspan='2'>
                <h3>Filtration & Breathability</h3>
              </td>
            </tr>

            <tr>
              <th v-show='newOrEdit'>Filtration Efficiency (Percent)</th>
              <th v-show='!newOrEdit'>Filtration Efficiency</th>

              <td colspan='1'>
                <input type="number" :value='f.filtrationEfficiencyPercent' @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencyPercent')"
                       v-show="newOrEdit"
                       >
                       <ColoredCell
                           v-show='!newOrEdit'
                           class='risk-score'
                           :colorScheme="colorInterpolationScheme"
                           :maxVal=1
                           :value='filtrationEfficiencyValue(f.filtrationEfficiencyPercent)'
                           :text='percentText(f.filtrationEfficiencyPercent)'
                           :exception='exceptionObject'
                           :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%', }"
                           :title='f.filtrationEfficiencyPercent'
                           />
              </td>
            </tr>

            <tr>
              <th v-show='newOrEdit'>Breathability (Pa)</th>
              <th v-show='!newOrEdit'>Breathability</th>
              <td colspan='1'>
                <input type="number" :value='breathability[index].breathabilityPascals' @change="updateArrayOfObj($event, 'breathability', index, 'breathabilityPascals')"
                       v-show="newOrEdit"
                       >
                       <ColoredCell
                           class='risk-score'
                           v-show='!newOrEdit'
                           :colorScheme="breathabilityInterpolationScheme"
                           :maxVal=1
                           :value='breathability[index].breathabilityPascals'
                           :text='breathabilityText(breathability[index].breathabilityPascals)'
                           :exception='exceptionObjectBlank'
                           :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black',  'border-radius': '100%' }"
                           :title='breathabilityText(breathability[index].breathabilityPascals)'
                           />
              </td>
            </tr>

            <tr>
              <th colspan='2'>Source</th>
            </tr>

            <tr>
              <td colspan='2'>
                <input type='text' class='input-list'
                       :value='f.filtrationEfficiencySource'
                       @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencySource')"

                       v-show="newOrEdit"
                       >
                       <a v-show='!newOrEdit' :href="f.filtrationEfficiencySource">link</a>
              </td>

            </tr>

            <tr>
              <th class='notes' colspan='2'>Notes</th>
            </tr>

            <tr>
              <td colspan='2' class='notes' v-show='!newOrEdit'>{{f.filtrationEfficiencyNotes}}</td>
              <td colspan='2' v-show='newOrEdit'>
                <textarea cols="30" rows="10" @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencyNotes')"></textarea>
              </td>
            </tr>

            <tr class='text-align-center'>
              <td colspan='2'>
                <CircularButton text="x" @click="deleteArrayOfObj($event, 'filtrationEfficiencies', index)" v-if='this.mode == "New" || userCanEdit && mode == "Edit"'/>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <table v-if='tabToShow == "Basic Info"'>
        <tbody>

        </tbody>
      </table>
      <br>

      <div class="buttons justify-content-center">
        <Button shadow='true' class='button' text="Edit" @click='mode = "Edit"' v-if='mode == "Show" && canUpdate'/>
        <Button shadow='true' class='button' text="Delete" @click='deleteMask' v-if='deletable && (mode != "Show") && canUpdate'/>
        <Button shadow='true' class='button' text="Cancel" @click='handleCancel' v-if='(mode == "New") || ((mode == "Edit") && canUpdate)'/>
        <Button shadow='true' class='button' text="Save" @click='saveMask' v-if='(mode == "New") || ((mode == "Edit") && canUpdate)'/>
      </div>

      <br>
      <br>
      <br>

    </div>
    <div class='grid bar-charts' v-show='displayTab == "Fit Testing"'>
      <div class='card'>
        <h3 class='title'>Counts</h3>
        <HorizontalStackedBar
            :values="basicAggregates"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Race &amp; Ethnicity Counts</h3>
        <HorizontalStackedBar
            :values="raceEthnicityAggregates"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Gender Counts</h3>
        <HorizontalStackedBar
            :values="genderSexAggregates"
        />
      </div>
      <div class='card'>
        <h3 class='title'>Age Counts</h3>
        <HorizontalStackedBar
            :values="ageAggregates"
        />
      </div>
    </div>
    <br>
    <br>

  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import Circle from './circle.vue'
import { assignBoundsToColorScheme, binValue, colorPaletteFall, genColorSchemeBounds, riskColorInterpolationScheme, perimeterColorScheme } from './colors';
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import ColoredCell from './colored_cell.vue'
import HorizontalStackedBar from './horizontal_stacked_bar.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel, shortHandHref, round } from './misc.js'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'Mask',
  components: {
    Button,
    Circle,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    HorizontalStackedBar,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      basicAggregates: {},
      basicOptions: [
        'fit_test_count',
        'unique_fit_testers_count'
      ],
      raceEthnicityAggregates: {},
      raceEthnicityOptions: [
        'american_indian_or_alaskan_native_count',
        'asian_pacific_islander_count',
        'black_african_american_count',
        'hispanic_count',
        'white_caucasian_count',
        'multiple_ethnicity_other_count',
        'prefer_not_to_disclose_race_ethnicity_count'
      ],
      ageAggregates: {},
      ageOptions: [
        'age_between_2_and_4',
        'age_between_4_and_6',
        'age_between_6_and_8',
        'age_between_8_and_10',
        'age_between_10_and_12',
        'age_between_12_and_14',
        'age_between_14_and_18',
        'age_adult',
        'prefer_not_to_disclose_age_count'
      ],
      genderSexAggregates: {},
      genderSexOptions: [
        'cisgender_male_count',
        'cisgender_female_count',
        'mtf_transgender_count',
        'ftm_transgender_count',
        'intersex_count',
        'other_gender_sex_count',
        'prefer_not_to_disclose_gender_sex_count'

      ],
      hasExhalationValve: false,
      exceptionObjectBlank: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: '',
        text: '?'
      },
      exceptionObject: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: undefined,
        text: '?'
      },
      exceptionDollarObject: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: 0,
        text: '?'
      },
      mode: 'New',
      notes: '',
      authorId: 0,
      massGrams: null,
      widthMm: null,
      heightMm: null,
      depthMm: null,
      perimeterMm: null,
      tabToShow: "Basic Info",
      displayTab: "Misc. Info",
      tabToShowOptions: [
        {
          text: "Misc. Info",
        },
        {
          text: "Fit Testing",
        },
      ],
      tabEditOptions: [
        {
          text: "Basic Info",
        },
        {
          text: "Image & Purchasing",
        },
        {
          text: "Dimensions",
        },
        {
          text: "Filtration & Breathability",
        },
      ],
      initialCostUsDollars: 0,
      hasGasket: false,
      editMode: false,
      id: null,
      uniqueInternalModelCode: '',
      modifications: {},
      color: '',
      colors: [],
      filterType: 'N95',
      filtrationEfficiencies: [],
      breathability: [],
      filterChangeCostUsDollars: 0,
      strapType: 'Headstrap',
      style: '',
      imageUrls: [''],
      authorIds: [],
      whereToBuyUrls: [],
      errorMessages: [],
    }
  },
  props: {
    colorOptions: {
      default: [
        'White',
        'Black',
        'Blue',
        'Grey',
        'Graphics',
        'Orange',
        'Green',
        'Purple',
        'Pink',
        'Multicolored',
      ],

    }
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
    columnCount() {
      if (this.filtrationEfficiencies.length > 0) {
        return 4
      }
      return 3
    },
    canUpdate() {
      return !!this.currentUser && ((this.authorId == this.currentUser.id) || this.currentUser.admin)
    },
    perimColorScheme() {
      return perimeterColorScheme();
    },

    costColorScheme() {
      const minimum = 0.5
      const maximum = 90 // flo mask
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },

    widthColorScheme() {
      const minimum = 67
      const maximum = 184
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    depthColorScheme() {
      const minimum = 8
      const maximum = 50
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    heightColorScheme() {
      const minimum = 55
      const maximum = 145
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    massColorScheme() {
      const minimum = 10
      const maximum = 200
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    breathabilityInterpolationScheme() {
      const minimum = 46
      const maximum = 468
      const numObjects = 6

      return genColorSchemeBounds(minimum, maximum, numObjects)
    },
    massGramsScaled() {
      // scale to between 0 and 1
      return this.massGrams / 209
    },
    colorInterpolationScheme() {
      return riskColorInterpolationScheme
    },
    dollarCost() {
      if (this.initialCostUsDollars != 0) {
        return this.initialCostUsDollars / 1000
      }
    },
    riskColorScheme() {
      return riskColorInterpolationScheme
    },
    filtrationEfficienciesRuby() {
      let collection = []
      for(let f of this.filtrationEfficiencies) {
        collection.push({
          'filtration_efficiency_notes': f.filtrationEfficiencyNotes,
          'filtration_efficiency_source': f.filtrationEfficiencySource,
          'filtration_efficiency_percent': f.filtrationEfficiencyPercent
        })

      }

      return collection
    },
    breathabilityRuby() {
      let collection = []
      for(let f of this.breathability) {
        collection.push({
          'breathability_pascals_notes': f.breathabilityPascalsNotes,
          'breathability_pascals_source': f.breathabilityPascalsSource,
          'breathability_pascals': parseFloat(f.breathabilityPascals)
        })

      }

      return collection
    },
    currentUserIsAuthor() {
      return this.authorId == this.currentUser.id
    },
    deletable() {
      return !!this.id && this.userCanEdit
    },
    whereToBuyUrlsColspan() {
      if (this.userCanEdit) {
        return 2
      }
     return 3
    },
    sealColspan() {
      if (this.editMode) {
        return 2
      }
     return 1
    },
    imagePrevColspan() {
      if (this.editMode) {
        return 1
      }
     return 2
    },
    userCanEdit() {
      if (!this.currentUser) {
        return false
      }

      return this.currentUserIsAuthor && this.basicAggregates.fit_test_count == 0
    },
    newOrEdit() {
      return (this.mode == 'New' || this.mode == 'Edit')
    },
    tagline() {
      return `${this.mode} Mask`
    },
    toSave() {
      return {
        colors: this.colors,
        notes: this.notes,
        mass_grams: this.massGrams,
        width_mm: this.widthMm,
        perimeter_mm: this.perimeterMm,
        height_mm: this.heightMm,
        depth_mm: this.depthMm,
        unique_internal_model_code: this.uniqueInternalModelCode,
        modifications: this.modifications,
        filter_type: this.filterType,
        filtration_efficiencies: this.filtrationEfficienciesRuby,
        has_exhalation_valve: this.hasExhalationValve,
        breathability: this.breathabilityRuby,
        filter_change_cost_us_dollars: this.filterChangeCostUsDollars,
        style: this.style,
        image_urls: this.imageUrls,
        where_to_buy_urls: this.whereToBuyUrls,
        author_id: this.currentUser.id,
        initial_cost_us_dollars: this.initialCostUsDollars,
        strap_type: this.strapType
      }
    }
  },
  async created() {
    this.getCurrentUser();

    if (this.$route.name == 'NewMask' && this.currentUser) {
      this.mode = 'New'
    } else if (this.$route.name == 'NewMask' && !this.currentUser) {
      // visit the URL
      this.$router.push({
        name: 'SignIn',
        query: {
          'attempt-name': 'NewMask'
        }
      })
    } else if (this.$route.name == 'ShowMask') {
      this.mode = 'Show'
    } else if (this.$route.name == 'EditMask')
      this.mode = 'Edit'

    if (['Edit', 'Show'].includes(this.mode)) {
      this.loadMask()
    }

    let toQuery = this.$route.query

    if (toQuery['tabToShow'] && (["NewMask", "ShowMask", "EditMask"].includes(this.$route.name))) {
      this.tabToShow = toQuery['tabToShow']
    }

    if (toQuery['displayTab'] && (["NewMask", "ShowMask", "EditMask"].includes(this.$route.name))) {
      this.displayTab = toQuery['displayTab']
    }

    this.$watch(
      () => this.$route.name,
      (toName, fromName) => {
        if (toName == "NewMask") {
          this.mode = 'New'
        } else if (toName == "ShowMask") {
          this.mode = 'Show'
          this.loadMask()
        } else if (toName == 'EditMask') {
          this.mode = 'Edit'
          this.loadMask()
        }
      }

    )
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && (["NewMask", "ShowMask", "EditMask"].includes(this.$route.name))) {
          this.tabToShow = toQuery['tabToShow']
        }

        if (toQuery['displayTab'] && (["NewMask", "ShowMask", "EditMask"].includes(this.$route.name))) {
          this.displayTab = toQuery['displayTab']
        }
      }
    )

  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'addMessages']),

    circleStyling(opt ) {
      if (this.colors.includes(opt)) {
        return "{'border': '2px solid black'}"
      } else {
        return "{'border': '0px solid black'}"
      }
    },
    filterFor(namespace, opt) {
      if (this.colors.includes(opt)) {
        this.colors = this.colors.filter(item => item !== opt)
      } else {
        this.colors.push(opt)
      }
    },
    shortHand(href) {
      return shortHandHref(href)
    },
    filtrationEfficiencyValue(percent) {
      if (percent) {
        return 1 - percent / 100
      }

      return undefined
    },
    dollarText(num) {
      if (num) {
        return `$${num}`
      }

      return '?'
    },
    distanceText(num, unitAbbrev) {
      if (!!unitAbbrev) {
        unitAbbrev = 'mm'
      }
      if (num) {
        return `${round(num, 0)} ${unitAbbrev}`
      }

      return '?'
    },
    massText(num) {
      if (num) {
        return `${num} g`
      }

      return '?'
    },
    breathabilityText(num) {
      if (num) {
        return `${num} pa`
      }

      return "?"
    },
    percentText(num) {
      if (num) {
        return `${num}%`
      }

      return "?"
    },
    maskImageAlt(index) {
      return `Image #${index} for ${this.uniqueInternalModelCode}`
    },
    addFiltEffAndBreathability() {
      this.addFiltrationEfficiency()
      this.addBreathability()
    },
    addFiltrationEfficiency() {
      this.filtrationEfficiencies.push({
        'filtrationEfficiencyPercent': 1,
        'filtrationEfficiencySource': ''
      })

    },
    addBreathability() {
      this.breathability.push({
        'breathabilityPascals': 0,
        'breathabilitySource': ''
      })

    },
    addImageUrl() {
      if (!this.userCanEdit) {
        return
      }
      this.imageUrls.push('')
    },
    addPurchasingUrl() {
      this.whereToBuyUrls.push('')
    },
    deleteImageUrl(index) {
      this.imageUrls.splice(index, 1);
    },
    deletePurchasingUrl(index) {
      this.whereToBuyUrls.splice(index, 1);
    },
    handleCancel() {
      if (this.mode == 'New') {
        this.$router.push(
          {
            name: "Masks"
          }
        )
      } else {
        this.mode = 'Show'
      }
    },
    newMask() {
      this.$router.push(
        {
          name: "NewMask"
        }
      )

      this.masks.push(
        {
          unique_internal_model_code: '',
          modifications: {},
          type: '',
          image_urls: [''],
          author_id: null,
          where_to_buy_urls: [],
        }
      )
    },
    async loadStuff() {
      // TODO: load the profile for the current user

    },
    runValidations() {
      if (this.imageUrls.length <= 0) {
        this.messages.push({
          str: "Please provide an image URL so one image can be displayed."
        })
      }

      if (!this.uniqueInternalModelCode) {
        this.messages.push({
          str: "Please provide a Unique Internal Model Code"
        })
      }
    },
    async loadMask() {
      await axios.get(
        `/masks/${this.$route.params.id}.json`
      )
        .then(response => {
          let data = response.data
          // whatever you want
          let mask = deepSnakeToCamel(data.mask)

          for(let k in mask) {
            this[k] = mask[k]
          }

          this.basicAggregates = {}

          for(let k of this.basicOptions) {
            this.basicAggregates[k] = data.mask[k]
          }

          this.raceEthnicityAggregates = {}

          for(let k of this.raceEthnicityOptions) {
            this.raceEthnicityAggregates[k] = data.mask[k]
          }

          this.genderSexAggregates = {}

          for(let k of this.genderSexOptions) {
            this.genderSexAggregates[k] = data.mask[k]
          }

          this.ageAggregates = {}

          for(let k of this.ageOptions) {
            this.ageAggregates[k] = data.mask[k]
          }


        })
        .catch(error => {
          if (error.message) {
            this.addMessages([error.message])
          } else {
            this.addMessages(error.response.data.messages)
          }
        })
    },
    async deleteMask() {
      let answer = window.confirm("Are you sure you want to delete data?");

      if (answer && this.$route.params.id) {
        await axios.delete(
          `/masks/${this.$route.params.id}.json`
        )
          .then(response => {
            let data = response.data

            this.$router.push({
              name: 'Masks',
            })
          })
          .catch(error => {
            if (error.message) {
              this.addMessages([error.message])
            }
              this.addMessages(error.response.data.messages)
          })
      }
    },
    async saveMask() {
      this.runValidations()

      if (this.messages.length > 0) {
        return;
      }

      let maskId = this.$route.params.id;

      if (maskId) {

        await axios.put(
          `/masks/${this.$route.params.id}.json`, {
            mask: this.toSave
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            this.$router.push({
              name: 'ShowMask',
              params: {
                id: maskId
              }
            })

            this.mode = 'Show'
          })
          .catch(error => {
            for(let errorMessage of error.response.data.messages) {
              this.messages.push({
                str: errorMessage
              })
            }
          })
      } else {

        // create
        await axios.post(
          `/masks.json`, {
            mask: this.toSave
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want
            this.$router.push(
              {
                name: 'ShowMask',
                params: {
                  id: data.mask.id
                }
              }
            )

            this.id = data.mask.id
            this.authorId = data.mask.author_id
            this.mode = 'Show'
          })
          .catch(error => {
            if (error.message) {
              this.addMessages([error.message])
            } else {
              this.addMessages(error.response.data.messages)
            }
          })
      }
    },
    setDisplay(opt) {
      this.$router.push({
        name: this.$route.name,
        query: {
          displayTab: opt.name
        }
      })
    },
    setRouteTo(opt) {
      let tabToShow = '';
      if ('target' in opt && 'value' in opt.target) {
        tabToShow = opt.target.value
      } else {
        tabToShow = opt.name
      }

      this.$router.push({
        name: this.$route.name,
        query: {
          tabToShow: tabToShow
        }
      })
    },
    visitMasks() {
      this.$router.push({
        name: 'Masks',
      })
    },
    update(event, property, index) {
      if (index !== null) {
        this[property][index] = event.target.value
      } else {
        this[property] = event.target.value
      }
    },
    deleteArrayOfObj(event, property, index) {
      if (index !== null) {
        this[property].splice(index, 1)
      }
    },
    updateArrayOfObj(event, property, index, nestedProp) {
      if (index !== null) {
        this[property][index][nestedProp] = event.target.value
      }
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

  .has-minimal-width {
    min-width: 25em;
  }
  .text-for-other {
    margin: 0 1.25em;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .justify-items-center {
    display: flex;
    justify-items: center;
  }

  .almost-full-width {
    width: 90%;
  }
  .input-list {
    min-width: 20em;
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

  .row .button {
    width: 100%;
    margin: 1em;
    max-width: 10em;
  }

  .risk-score {
    border-radius: 100%;
    width: 5em;
    height: 5em;
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

  .text-align-center {
    text-align: center;
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

  .notes {
    max-width: 20em;
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

  .grid.edit {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .grid.view.quad {
    grid-template-columns: 25% 25% 25% 25%;
  }

  .grid.view.triple {
    grid-template-columns: 33% 33% 33%;
  }

  .grid.view.dual {
    grid-template-columns: 50% 50%;
  }

  .grid.view.single {
    grid-template-columns: 33% 33%;
  }

  .grid.dual {
    grid-template-columns: 50% 50%;
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

  img.preview {
    max-width:20em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  th, td {
    padding: 0.5em;
    text-align: center;
  }

  .navigator {
    font-size: 1.5em;
  }

  .bar-charts {
    grid-template-columns: 50% 50%;
  }

  @media(max-width: 1300px) {
    .grid.view, .grid.view.quad {
      grid-template-columns: 50% 50%;
    }

    .grid.bar-charts {
      grid-template-columns: 100%;
    }

  }
  @media(max-width: 1000px) {
    .grid.triple, .grid.view.triple, .grid.view.quad {
      grid-template-columns: 100%;
    }
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

    .grid.view {
      grid-template-columns: 100%;
    }

    .hide-when-mobile {
      display: none;
    }

    .buttons, .edit tr {
      display:flex;
      flex-direction: column;
      align-items: center;
    }

    .button, input {
      width: 95vw;
    }

    select {
      width: 97vw;
    }

    .navigator {
      width: 98vw;
    }
  }

  @media(min-width: 700px) {
    .hide-when-not-mobile {
      display: none;
    }

    .buttons {
      flex-direction: row;
    }
  }

  .title {
    text-align: center;
  }
  .card {
    padding: 1em;
  }
</style>
