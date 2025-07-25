<template>
  <div class='align-items-center flex-dir-col sticky'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>Masks</h2>
      <CircularButton text="+" @click="newMask" />
      <CircularButton text="?" @click="showPopup = 'Help'"/>
    </div>

    <div class='row'>
      <input id='search' type="text" :value='search' @change='updateSearch'>
      <SearchIcon height='2em' width='1em'/>

      <button class='icon' @click='showPopup = "Recommend"'>
        R
      </button>

      <button class='icon' @click='showPopup = "Sort"'>
        ⇵
      </button>

      <button class='icon' @click='showPopup = "Filter"'>
        <svg class='filter-button' xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="8 10 70 70"
          width="2em" height="2em"
          >
          <path d='m 20 20 h 40 l -18 30 v 20 l -4 -2  v -18 z' stroke='black' :fill='filterButtonColor'/>
        </svg>
      </button>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <div class='container chunk'>
      <RecommendPopup
        :showPopup='showPopup == "Recommend"'
        :facialMeasurements='facialMeasurements'
        @hidePopUp='showPopup = false'
        @updateFacialMeasurement='triggerRouterForFacialMeasurementUpdate'
      />

      <HelpPopup
        :showPopup='showPopup == "Help"'
        @hidePopUp='showPopup = false'
      />

      <SortPopup
        :masks='masks'
        :showPopup='showPopup == "Sort"'
        :showUniqueNumberFitTesters='true'
        :sortByField='sortByField'
        :sortByStatus='sortByStatus'
        @hidePopUp='showPopup = false'
        @sortBy='updateQuery'
      />

      <FilterPopup
        :showPopup='showPopup == "Filter"'
        :showTargetedOptions='true'
        :showUniqueNumberFitTesters='true'
        :showFitTesting='false'
        :colorOptions='colorOptions'
        :strapTypes='strapTypes'
        :styleTypes='styleTypes'
        :filterForColor='filterForColor'
        :filterForStyle='filterForStyle'
        :filterForStrapType='filterForStrapType'
        :filterForTargeted='filterForTargeted'
        :filterForNotTargeted='filterForNotTargeted'
        :sortByField='sortByField'
        :sortByStatus='sortByStatus'
        @hidePopUp='showPopup = false'
        @filterFor='updateQuery'
      />
    </div>

    <MaskCards
      :cards='sortedDisplayables'
      :showUniqueNumFitTesters='true'
      :viewMaskOnClick='true'
      :facialMeasurements='facialMeasurements'
    />

    <br>
    <br>

  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import ColoredCell from './colored_cell.vue'
import MaskCards from './mask_card.vue'
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import RecommendPopup from './recommend_popup.vue'
import SearchIcon from './search_icon.vue'
import SortingStatus from './sorting_status.vue'
import FilterPopup from './filter_popup.vue'
import SortPopup from './sort_popup.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { getFacialMeasurements } from './facial_measurements.js'
import { perimeterColorScheme } from './colors.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useFacialMeasurementStore } from './stores/facial_measurement_store.js';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'
import HelpPopup from './help_popup.vue'
import { useMasksStore } from './stores/masks_store'


export default {
  name: 'Masks',
  components: {
    Button,
    CircularButton,
    ColoredCell,
    ClosableMessage,
    FilterPopup,
    HelpPopup,
    MaskCards,
    Popup,
    PersonIcon,
    RecommendPopup,
    SearchIcon,
    SortPopup,
    SortingStatus,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      colorOptions: [
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
      styleTypes: [
       "Boat",
       "Bifold",
       "Elastomeric",
       "Duckbill",
       "Cup",
       "Bifold & Gasket",
      ],
      strapTypes: [
        'Adjustable Earloop',
        'Adjustable Headstrap',
        'Earloop',
        'Headstrap',
      ],
      filterForTargeted: true,
      filterForNotTargeted: true,
      showPopup: false,
      exceptionMissingObject: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: '',
        text: '?'
      },
      errorMessages: [],
      masks: [],
      facialHairBeardLengthMm: 0,
      waiting: false,
      masks: [],
      messages: [],
      tagline: 'Masks',
      strapTypeOptions: [
        'Earloop',
        'Adjustable Earloop',
        'Headstrap',
        'Adjustable Headstrap',
      ],
      styleOptions: [
        'Bifold',
        'Bifold & Gasket',
        'Boat',
        'Cotton + High Filtration Efficiency Material',
        'Cup',
        'Duckbill',
        'Elastomeric',
      ],
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
          'isWaiting'
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
    ...mapState(
        useMasksStore,
        [
          'search',
          'sortByStatus',
          'sortByField',
          'filterForColor',
          'filterForStrapType',
          'filterForStyle'
        ]
    ),
    facialMeasurements() {
      return getFacialMeasurements.bind(this)()
    },

    perimColorScheme() {
      return perimeterColorScheme()
    },
    displayables() {
      return displayableMasks.bind(this)(this.masks)
    },
    sortedDisplayables() {
      return sortedDisplayableMasks.bind(this)(this.displayables)
    },
    messages() {
      return this.errorMessages;
    },
    filterButtonColor() {
      return this.hasActiveFilters ? 'red' : '#aaa'
    },
    hasActiveFilters() {
      return this.filterForColor !== 'none' ||
             this.filterForStrapType !== 'none' ||
             this.filterForStyle !== 'none'
    },
  },

  async created() {
    // TODO: a parent might input data on behalf of their children.
    // Currently, this.loadStuff() assumes We're loading the profile for the current user
    await this.load.bind(this)(this.$route.query, undefined)

    this.$watch(
      () => this.$route.query,
      this.load.bind(this)
    )

  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'setWaiting']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    ...mapActions(useFacialMeasurementStore, ['updateFacialMeasurements', 'getFacialMeasurement']),
    ...mapActions(useMasksStore, [
      'setFilterQuery'
    ]),
    async load(toQuery, previousQuery) {
      this.setFilterQuery(toQuery, 'search')
      this.setFilterQuery(toQuery, 'sortByStatus')
      this.setFilterQuery(toQuery, 'sortByField')
      this.setFilterQuery(toQuery, 'filterForColor')
      this.setFilterQuery(toQuery, 'filterForStrapType')
      this.setFilterQuery(toQuery, 'filterForStyle')

      await this.loadData(toQuery)
    },
    async loadData(toQuery) {
      this.setWaiting(true);

      this.updateFacialMeasurements(toQuery)
      await this.updateFacialMeasurement()

      this.setWaiting(false);
    },
    hideSortFilterPopUp() {
      this.showPopup = false
    },
    resetFilters() {
      this.resetFilters()
    },
    getAbsoluteHref(href) {
      // TODO: make sure this works for all
      return `${href}`
    },
    newMask() {
      this.$router.push(
        {
          name: "NewMask"
        }
      )
    },
    viewMask(id) {
      this.$router.push(
        {
          name: "ShowMask",
          params: {
            id: id
          }
        }
      )
    },
    updateSearch(event) {
      let newQuery = {
        search: event.target.value
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )
      this.$router.push({
        name: 'Masks',
        query: combinedQuery
      })
    },
    updateQuery(args) {
      args['name'] = 'Masks'
      this.$router.push(args)
    },

    triggerRouterForFacialMeasurementUpdate(event, key) {
      let newQuery = {}

      newQuery[key] = event.target.value
      newQuery['sortByField'] = 'probaFit'
      newQuery['sortByStatus'] = 'descending'

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )
      this.$router.push({
        name: 'Masks',
        query: combinedQuery
      })
    },
    async updateFacialMeasurement() {
      await axios.post(
        `/mask_recommender.json`,
        {
          'facial_measurements': {
            'bitragion_subnasale_arc': this.getFacialMeasurement('bitragionSubnasaleArcMm'),
            'face_width': this.getFacialMeasurement('faceWidthMm'),
            'nose_protrusion': this.getFacialMeasurement('noseProtrusionMm'),
            'facial_hair_beard_length_mm': this.facialHairBeardLengthMm,
          }
        }
      )
        .then(response => {
          let data = response.data
          if (data) {
            this.masks = []

            for (let m of data) {
              this.masks.push(new Respirator(m))
            }
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load mask recommendations."
          // whatever you want
        })

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
            this.masks = []

            for (let m of data.masks) {
              this.masks.push(new Respirator(m))
            }
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load masks."
          // whatever you want
        })
    },
    sortBy(field) {
      if (this.sortByField == field) {
        this.setSortByStatus(this.sortByStatus == 'ascending' ? 'descending' : 'ascending')
      } else {
        this.setSortByField(field)
        this.setSortByStatus('ascending')
      }
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

  button {
    display: flex;
    cursor: pointer;
    padding: 0.25em;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .card {
    padding: 1em 0;
  }

  .card:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  .card .description {
    padding: 1em;
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
    margin-left: 0.5em;
    margin-right: 0.5em;
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

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
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

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
    overflow-y: auto;
    height: 75vh;
  }

  .targeted {
    padding-left: 5em;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  .tape-measure {
    margin-right: 0.5em;
    max-width: 1.5em;
  }

  .risk-score {
    width: 5em;
    height: 3em;
    font-size: 1em;
  }
  .sticky {
    position: fixed;
    top: 3em;
  }

  th, td {
    text-align: center;
  }

  .icon {
      justify-content: center;
      align-items: center;
      min-width: 3em;
  }

  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 50% 50%;
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
  }
  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 100%;
    }

    #search {
      width: 53vw;
      padding: 1em;
    }

    .icon {
      padding: 1em;
    }

    .thumbnail {
      max-width:70vw;
      max-height:none;
    }

    .targeted {
      padding-left: 50vw;
    }

    .main {
      overflow: auto;
      height: 65vh;
    }
  }

</style>
