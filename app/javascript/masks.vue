<template>
  <div class='align-items-center flex-dir-col sticky'>
    <div class='top-controls'>
      <div class='bar'>
        <div class='flex align-items-center row'>
          <h2 class='tagline'>Masks</h2>
          <CircularButton v-if="isAdmin" text="R" @click="retrainModel" />
          <CircularButton text="+" @click="newMask" />
          <CircularButton text="?" @click="showPopup = 'Help'"/>
        </div>

        <div class='row'>
          <input id='search' type="text" :value='search' @change='updateSearch'>
          <SearchIcon height='2em' width='1em'/>

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

        <Pagination
          :current-page="currentPage"
          :per-page="perPage"
          :total-count="totalCount"
          item-name="masks"
          @page-change="onPageChange"
        />
      </div>

      <div class='container chunk'>
        <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
        <br>
      </div>
    </div>

    <div class='container chunk'>
      <RecommendPopup
        v-if="showPopup == 'Recommend'"
        :showPopup='showPopup == "Recommend"'
        :facialMeasurements='facialMeasurements'
        @hidePopUp='showPopup = false'
        @updateFacialMeasurement='triggerRouterForFacialMeasurementUpdate'
      />

      <Popup
        v-if="showPopup == 'Retrain'"
        @onclose='showPopup = false'
      >
        <h3>Training started</h3>
        <p>Job ID: {{ retrainJobId }}</p>
      </Popup>

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
        :filterForMissing='filterForMissing'
        :showMissingFilters='true'
        :filterForTargeted='filterForTargeted'
        :filterForNotTargeted='filterForNotTargeted'
        :sortByField='sortByField'
        :sortByStatus='sortByStatus'
        @hidePopUp='showPopup = false'
        @filterFor='updateQuery'
      />
    </div>

    <div
      v-if="isRecommenderLoading"
      class="recommender-loading-overlay"
    >
      <div class="recommender-loading-content">
        <div class="recommender-spinner" />
        <p class="recommender-loading-message">
          Creating a recommendation sometimes takes up to a minute. Thank you for your patience.
        </p>
      </div>
    </div>

    <MaskCards
      :cards='sortedDisplayables'
      :dataContext='maskDataContext'
      :showUniqueNumFitTesters='true'
      :viewMaskOnClick='true'
      :facialMeasurements='facialMeasurements'
      :showProbaFit='shouldShowProbaFit'
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
import { Respirator } from './masks.js'
import HelpPopup from './help_popup.vue'
import Pagination from './pagination.vue'
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
    Pagination,
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
      retrainJobId: null,
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
      currentPage: 1,
      perPage: 12,
      totalCount: 0,
      maskDataContext: {},
      lastHandledRecommenderPayload: null,
      recommenderWarmupKey: 'mask_recommender_warmup_done',
      isRecommenderLoading: false,
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
          'isAdmin',
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
          'filterForStyle',
          'filterForMissing'
        ]
    ),
    facialMeasurements() {
      return getFacialMeasurements.bind(this)()
    },

    perimColorScheme() {
      return perimeterColorScheme()
    },
    displayables() {
      return this.masks;
    },
    sortedDisplayables() {
      return this.displayables;
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
             this.filterForStyle !== 'none' ||
             this.filterForMissing.length > 0
    },
    shouldShowProbaFit() {
      const hasPayload = !!this.$route.query.recommenderPayload
      const hasProbaFit = this.masks.some((mask) => mask.probaFit !== undefined && mask.probaFit !== null)
      return hasPayload || hasProbaFit || this.sortByField === 'probaFit'
    },
  },

  async created() {
    // TODO: a parent might input data on behalf of their children.
    // Currently, this.loadStuff() assumes We're loading the profile for the current user
    this.maybeWarmupRecommender()
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
    maybeWarmupRecommender() {
      try {
        if (window.sessionStorage.getItem(this.recommenderWarmupKey) === '1') {
          return
        }
      } catch (_error) {
        return
      }

      axios.post('/mask_recommender/warmup.json')
        .then(() => {
          try {
            window.sessionStorage.setItem(this.recommenderWarmupKey, '1')
          } catch (_error) {
            // Ignore browser storage errors and keep UX non-blocking.
          }
        })
        .catch(() => {
          // Warmup is best effort; don't surface errors to the user.
        })
    },
    async load(toQuery, previousQuery) {
      this.setFilterQuery(toQuery, 'search')
      this.setFilterQuery(toQuery, 'sortByStatus')
      this.setFilterQuery(toQuery, 'sortByField')
      this.setFilterQuery(toQuery, 'filterForColor')
      this.setFilterQuery(toQuery, 'filterForStrapType')
      this.setFilterQuery(toQuery, 'filterForStyle')
      this.setFilterQuery(toQuery, 'filterForMissing')

      const page = parseInt(toQuery.page, 10)
      this.currentPage = Number.isNaN(page) || page < 1 ? 1 : page
      if (await this.maybeLoadRecommenderPayload(toQuery)) {
        return
      }

      await this.loadData(toQuery)
    },
    async retrainModel() {
      this.errorMessages = []
      this.setWaiting(true)
      try {
        const response = await axios.post('/mask_recommender/train.json')
        this.retrainJobId = response?.data?.job_id || null
        if (!this.retrainJobId) {
          this.errorMessages = ['Retraining started, but no job id was returned.']
          return
        }
        this.showPopup = 'Retrain'
      } catch (error) {
        const message = error?.response?.data?.error || error?.message || 'Unable to retrain model.'
        this.errorMessages = [message]
      } finally {
        this.setWaiting(false)
      }
    },
    async loadData(toQuery) {
      this.setWaiting(true);
      try {
        await this.loadMasks();
      } finally {
        this.setWaiting(false);
      }
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
        search: event.target.value,
        page: 1
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
      const query = Object.assign({}, this.$route.query, args.query || {}, { page: 1 })
      this.$router.push({ ...args, query })
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
      // Fetch recommender columns from backend to avoid hardcoding
      const colsResp = await axios.get('/mask_recommender/recommender_columns.json')
      const cols = (colsResp.data && colsResp.data.recommender_columns) || []

      // Map snake_case columns to store keys (camelCase + Mm suffix)
      const payload = {}
      for (const col of cols) {
        const camel = col.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
        const key = `${camel}Mm`
        payload[col] = this.getFacialMeasurement(key)
      }
      payload['facial_hair_beard_length_mm'] = this.facialHairBeardLengthMm

      await axios.post(
        `/mask_recommender.json`,
        { facial_measurements: payload }
      )
        .then(response => {
          let data = response.data
          const masks = data && data.masks ? data.masks : data
          if (masks) {
            this.masks = masks.map((m) => new Respirator(m))
            this.totalCount = masks.length
            if (data && data.context) {
              this.maskDataContext = data.context
            }
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load mask recommendations."
          // whatever you want
        })

    },
    async maybeLoadRecommenderPayload(toQuery) {
      const payloadParam = toQuery.recommenderPayload
      if (!payloadParam) {
        this.isRecommenderLoading = false
        return false
      }

      // Never fall back to generic /masks.json while a recommender payload is present.
      // If this payload was already queued/loaded, keep waiting for async results.
      if (payloadParam === this.lastHandledRecommenderPayload) {
        return true
      }

      const facialMeasurements = this.decodeRecommenderPayload(payloadParam)
      if (!facialMeasurements) {
        this.isRecommenderLoading = false
        this.message = "Failed to decode recommendations payload."
        return true
      }

      this.lastHandledRecommenderPayload = payloadParam
      this.isRecommenderLoading = true
      try {
        await this.requestAsyncRecommendations(facialMeasurements)
      } finally {
        this.isRecommenderLoading = false
      }
      return true
    },
    async requestAsyncRecommendations(facialMeasurements) {
      try {
        const startResponse = await axios.post(
          `/mask_recommender/async.json`,
          { facial_measurements: facialMeasurements }
        )
        const jobId = startResponse?.data?.job_id
        if (!jobId) {
          this.message = "Failed to start mask recommendations."
          return
        }
        await this.pollRecommendationStatus(jobId)
      } catch (error) {
        this.message = "Failed to load mask recommendations."
      }
    },
    async pollRecommendationStatus(jobId) {
      while (true) {
        try {
          const response = await axios.get(`/mask_recommender/async/${jobId}.json`)
          const status = response?.data?.status
          if (status === 'complete') {
            const data = response.data?.result
            const masks = data && data.masks ? data.masks : data
            if (masks) {
              this.masks = masks.map((m) => new Respirator(m))
              this.totalCount = masks.length
              if (data && data.context) {
                this.maskDataContext = data.context
              }
            }
            return
          }
          if (status === 'failed') {
            this.message = response?.data?.error || "Failed to load mask recommendations."
            return
          }
        } catch (error) {
          this.message = "Failed to load mask recommendations."
          return
        }

        await new Promise((resolve) => setTimeout(resolve, 1000))
      }
    },
    decodeRecommenderPayload(payload) {
      try {
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
        const padded = base64 + '='.repeat((4 - base64.length % 4) % 4)
        const json = atob(padded)
        return JSON.parse(json)
      } catch (error) {
        return null
      }
    },
    async loadStuff() {
      // TODO: load the profile for the current user
      await this.loadMasks()
    },
    async loadMasks() {
      const params = {
        page: this.currentPage,
        per_page: this.perPage,
        search: this.search,
        sort_by: this.sortByField,
        sort_order: this.sortByStatus,
        filter_color: this.filterForColor,
        filter_style: this.filterForStyle,
        filter_strap_type: this.filterForStrapType,
        filter_missing: this.filterForMissing.length ? this.filterForMissing.join(',') : 'none'
      }

      try {
        const response = await axios.get('/masks.json', { params })
        const data = response.data
        if (data.masks) {
          this.masks = data.masks.map(m => new Respirator(m))
        } else {
          this.masks = []
        }
        this.totalCount = data.total_count || 0
        this.maskDataContext = data.context || {}
      } catch (error) {
        this.message = "Failed to load masks."
      }
    },
    onPageChange(page) {
      if (page === this.currentPage) return
      const newQuery = Object.assign({}, this.$route.query, { page })
      this.$router.push({ name: 'Masks', query: newQuery })
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
    grid-template-columns: 25% 25% 25% 25%;
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

  .top-controls {
    margin: 1em 0;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }

  .bar {
    max-height: 3em;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    padding-top: 1em;
  }

  .recommender-loading-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;
    background: rgba(255, 255, 255, 0.92);
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: all;
  }

  .recommender-loading-content {
    max-width: 32em;
    text-align: center;
    padding: 1.5em;
  }

  .recommender-spinner {
    width: 2.75em;
    height: 2.75em;
    margin: 0 auto 0.9em;
    border-radius: 50%;
    border: 0.35em solid #d9d9d9;
    border-top-color: #2c3e50;
    animation: recommender-spin 0.9s linear infinite;
  }

  .recommender-loading-message {
    margin: 0;
    font-size: 1rem;
    line-height: 1.4;
    color: #222;
  }

  @keyframes recommender-spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media(max-width: 1000px) {
    .top-controls {
      flex-direction: column;
      margin-top: 4em;
    }
    .bar {
      flex-direction: column;
    }
    margin-top: 4em;
  }
  @media(max-width: 768px) {
    .top-controls {
      flex-direction: column;
    }
  }
  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 100%;
    }
    img {
      width: 100vw;
    }


    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }
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
