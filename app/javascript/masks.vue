<template>
  <div class='align-items-center flex-dir-col sticky'>
    <div class='top-controls'>
      <div class='bar'>
        <div class='flex align-items-center row'>
          <h2 class='tagline'>Masks</h2>
          <CircularButton v-if="isAdmin" text="R" @click="retrainModel" />
          <CircularButton text="+" @click="newMask" />
          <CircularButton :text="resultsViewToggleText" @click="toggleResultsView" />
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
          v-if="!hasRecommenderPayload"
          :current-page="currentPage"
          :per-page="perPage"
          :total-count="totalCount"
          item-name="masks"
          @page-change="onPageChange"
        />
      </div>

      <div v-if="activeFilterPills.length" class="active-filter-pills">
        <FilterPill
          v-for="pill in activeFilterPills"
          :key="pill.id"
          :label="pill.label"
          @remove="removeFilterPill(pill)"
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
        :recommenderModelTimestamp="recommenderModelTimestamp"
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
        :filterForAvailable='filterForAvailable'
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
      v-if="!showTableView"
      :cards='sortedDisplayables'
      :dataContext='maskDataContext'
      :showUniqueNumFitTesters='true'
      :viewMaskOnClick='true'
      :facialMeasurements='facialMeasurements'
    />

    <div v-else class="mask-metrics-table-wrapper">
      <table class="mask-metrics-table">
        <thead>
          <tr>
            <th class="sticky-column sticky-image-column">Image</th>
            <th class="sticky-column sticky-mask-column desktop">Mask</th>
            <th
              v-for="row in tableMetricRows"
              :key="`feature-column-${row.key}`"
              class="metric-label"
            >
              {{ row.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="m in sortedDisplayables"
            :key="`mask-row-${m.id}`"
          >
            <td class="sticky-column sticky-image-column image-cell">
              <img
                v-if="m.imageUrls && m.imageUrls.length > 0"
                :src="m.imageUrls[0]"
                :alt="m.uniqueInternalModelCode"
                class="table-mask-image"
              >
              <div v-else class="table-mask-image-placeholder">No image</div>
              <button
                class="mobile-mask-name-button"
                @click="viewMask(m)"
              >
                {{ m.uniqueInternalModelCode }}
              </button>
            </td>
            <th class="sticky-column sticky-mask-column desktop">
              <button
                class="mask-row-button"
                @click="viewMask(m)"
              >
                {{ m.uniqueInternalModelCode }}
              </button>
            </th>
            <td
              v-for="row in tableMetricRows"
              :key="`metric-cell-${m.id}-${row.key}`"
            >
              <div
                v-if="row.key === 'strap_type'"
                class="table-text-cell"
                :style="tableTextCellStyle"
              >
                {{ metricCellText(row.key, m) }}
              </div>
              <ColoredCell
                v-else
                :value="metricCellScore(row.key, m)"
                :text="metricCellText(row.key, m)"
                :colorScheme="tableCellColorScheme"
                :exception="missingMetricCell"
                :style="coloredCellStyle"
                padding="0.55em"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
import FilterPill from './filter_pill.vue'
import SortPopup from './sort_popup.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { getFacialMeasurements } from './facial_measurements.js'
import { colorPaletteFall, genColorSchemeBounds, perimeterColorScheme } from './colors.js'
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
    FilterPill,
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
      recommenderModelTimestamp: null,
      viewportWidth: typeof window !== 'undefined' ? window.innerWidth : 1024,
      showTableView: false,
      missingMetricCell: {
        color: {
          r: '200',
          g: '200',
          b: '200',
        },
        value: -1,
        text: 'Missing',
      },
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
          'filterForMissing',
          'filterForAvailable'
        ]
    ),
    facialMeasurements() {
      return getFacialMeasurements.bind(this)()
    },

    hasRecommenderPayload() {
      return !!this.$route.query.recommenderPayload
    },
    perimColorScheme() {
      return perimeterColorScheme()
    },
    resultsViewToggleText() {
      return this.showTableView ? 'C' : 'T'
    },
    isNarrowTableViewport() {
      return this.viewportWidth < 1000
    },
    showStrapTypeColumn() {
      return this.viewportWidth >= 1072
    },
    tableMetricRows() {
      if (this.isNarrowTableViewport) {
        const rows = [
          { key: 'proba_fit', label: 'Fit' },
          { key: 'filtration', label: 'Filter' },
          { key: 'breathability', label: 'Breath' },
          { key: 'affordability', label: 'Cost' },
        ]
        if (this.showStrapTypeColumn) {
          rows.push({ key: 'strap_type', label: 'Strap' })
        }
        return rows
      }

      const rows = [
        { key: 'proba_fit', label: 'Probability of Fit' },
        { key: 'filtration', label: 'Filtration Factor' },
        { key: 'breathability', label: 'Breathability (pa)' },
        { key: 'affordability', label: 'Affordability (USD)' },
      ]
      if (this.showStrapTypeColumn) {
        rows.push({ key: 'strap_type', label: 'Strap type' })
      }
      return rows
    },
    tableCellColorScheme() {
      return genColorSchemeBounds(0, 1, 5, [...colorPaletteFall].reverse())
    },
    coloredCellStyle() {
      const baseStyle = {
        color: '#fff',
        textShadow: '0 1px 4px rgba(0, 0, 0, 0.65)',
        fontWeight: '600',
      }
      if (this.viewportWidth <= 768) {
        return Object.assign({ height: '8em' }, baseStyle)
      }
      return Object.assign({ height: '4em' }, baseStyle)
    },
    tableTextCellStyle() {
      if (this.viewportWidth <= 768) {
        return { height: '6em' }
      }
      return { height: '4em' }
    },
    displayables() {
      const masks = [...this.masks]
      if (!this.hasRecommenderPayload) {
        return masks
      }

      const searchValue = (this.search || '').toLowerCase().trim()
      const colorFilter = this.filterForColor
      const styleFilter = this.filterForStyle
      const strapFilter = this.filterForStrapType
      const missingFilters = this.filterForMissing || []

      return masks.filter((mask) => {
        const textBlob = [
          mask.uniqueInternalModelCode,
          mask.style,
          mask.strapType,
          mask.filterType,
          mask.color,
          ...(mask.colors || []),
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        if (searchValue && !textBlob.includes(searchValue)) {
          return false
        }

        if (this.filterForAvailable !== 'false' && mask.available === false) {
          return false
        }

        if (colorFilter && colorFilter !== 'none') {
          const maskColors = [mask.color, ...(mask.colors || [])]
            .filter(Boolean)
            .map((c) => String(c).toLowerCase())
          if (!maskColors.includes(String(colorFilter).toLowerCase())) {
            return false
          }
        }

        if (styleFilter && styleFilter !== 'none') {
          if (String(mask.style || '').toLowerCase() !== String(styleFilter).toLowerCase()) {
            return false
          }
        }

        if (strapFilter && strapFilter !== 'none') {
          if (String(mask.strapType || '').toLowerCase() !== String(strapFilter).toLowerCase()) {
            return false
          }
        }

        if (missingFilters.length > 0) {
          const matchesAllMissingFilters = missingFilters.every((missingFilter) => this.matchesMissingFilter(mask, missingFilter))
          if (!matchesAllMissingFilters) {
            return false
          }
        }

        return true
      })
    },
    effectiveSortField() {
      if (!this.sortByField || this.sortByField === 'none') {
        return this.hasRecommenderPayload ? 'probaFit' : null
      }
      return this.sortByField
    },
    effectiveSortStatus() {
      if (!this.sortByStatus || this.sortByStatus === 'none') {
        return this.effectiveSortField === 'probaFit' ? 'descending' : 'ascending'
      }
      return this.sortByStatus
    },
    sortedDisplayables() {
      const displayables = [...this.displayables]
      if (!this.hasRecommenderPayload) {
        return displayables
      }

      const field = this.effectiveSortField
      if (!field) {
        return displayables
      }

      const status = this.effectiveSortStatus
      const factor = status === 'ascending' ? 1 : -1

      return displayables.sort((a, b) => {
        const aRaw = a[field]
        const bRaw = b[field]
        const aNum = Number(aRaw)
        const bNum = Number(bRaw)

        if (Number.isFinite(aNum) && Number.isFinite(bNum)) {
          return (aNum - bNum) * factor
        }

        const aStr = String(aRaw || '').toLowerCase()
        const bStr = String(bRaw || '').toLowerCase()
        if (aStr < bStr) return -1 * factor
        if (aStr > bStr) return 1 * factor
        return 0
      })
    },
    activeFilterPills() {
      const pills = []

      if (this.filterForColor && this.filterForColor !== 'none') {
        pills.push({ id: `color-${this.filterForColor}`, type: 'color', value: this.filterForColor, label: `Color: ${this.filterForColor}` })
      }
      if (this.filterForStyle && this.filterForStyle !== 'none') {
        pills.push({ id: `style-${this.filterForStyle}`, type: 'style', value: this.filterForStyle, label: `Style: ${this.filterForStyle}` })
      }
      if (this.filterForStrapType && this.filterForStrapType !== 'none') {
        pills.push({ id: `strap-${this.filterForStrapType}`, type: 'strap_type', value: this.filterForStrapType, label: `Strap: ${this.filterForStrapType}` })
      }
      if (this.filterForAvailable === 'false') {
        pills.push({ id: 'available-false', type: 'available', value: 'false', label: 'Including unavailable masks' })
      }

      const missingLabelByValue = {
        strap_type: 'Strap type missing',
        style: 'Style missing',
        perimeter: 'Perimeter missing',
        filtration_factor: 'Filtration factor missing',
        breathability: 'Breathability missing',
      }
      for (const value of this.filterForMissing || []) {
        pills.push({
          id: `missing-${value}`,
          type: 'missing',
          value,
          label: missingLabelByValue[value] || `Missing: ${value}`,
        })
      }

      return pills
    },
    messages() {
      return this.errorMessages;
    },
    filterButtonColor() {
      return '#aaa'
    },
    hasActiveFilters() {
      return this.filterForColor !== 'none' ||
             this.filterForStrapType !== 'none' ||
             this.filterForStyle !== 'none' ||
             this.filterForMissing.length > 0 ||
             this.filterForAvailable === 'false'
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
  mounted() {
    this.handleWindowResize()
    window.addEventListener('resize', this.handleWindowResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleWindowResize)
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
    matchesMissingFilter(mask, filterMissing) {
      if (filterMissing === 'strap_type') {
        const value = mask.strapType
        return value === null || value === undefined || String(value).trim() === ''
      }
      if (filterMissing === 'style') {
        const value = mask.style
        return value === null || value === undefined || String(value).trim() === ''
      }
      if (filterMissing === 'perimeter') {
        const value = Number(mask.perimeterMm)
        return !Number.isFinite(value) || value === 0
      }
      if (filterMissing === 'filtration_factor') {
        const value = Number(mask.avgSealedFitFactor)
        return !Number.isFinite(value) || value <= 0
      }
      if (filterMissing === 'breathability') {
        const value = Number(mask.avgBreathabilityPa)
        return !Number.isFinite(value) || value <= 0
      }
      return false
    },
    handleWindowResize() {
      this.viewportWidth = window.innerWidth
      this.updateTableViewportHeight()
    },
    updateTableViewportHeight() {
      const wrapper = this.$el?.querySelector('.mask-metrics-table-wrapper')
      if (!wrapper) {
        return
      }

      const footerCandidates = [
        document.querySelector('footer'),
        document.querySelector('.footer'),
        document.querySelector('[class*=\"footer\"]'),
      ].filter(Boolean)
      const measuredFooterHeight = footerCandidates.reduce((maxHeight, node) => {
        const h = node.getBoundingClientRect().height || 0
        return h > maxHeight ? h : maxHeight
      }, 0)

      const footerHeight = Math.max(measuredFooterHeight, this.viewportWidth <= 900 ? 56 : 0)
      const top = wrapper.getBoundingClientRect().top
      const bottomBuffer = this.viewportWidth <= 900 ? 36 : 14
      const available = Math.max(200, window.innerHeight - top - footerHeight - bottomBuffer)

      wrapper.style.setProperty('--footer-height', `${footerHeight}px`)
      wrapper.style.setProperty('--table-viewport-height', `${available}px`)
    },
    toggleResultsView() {
      this.showTableView = !this.showTableView
      this.$nextTick(() => this.updateTableViewportHeight())
    },
    metricCellScore(metricKey, mask) {
      if (metricKey === 'proba_fit') {
        const value = Number(mask.probaFit)
        if (this.metricIsMissing(metricKey, mask)) {
          return -1
        }
        return this.clampPercent(value)
      }

      if (metricKey === 'filtration') {
        const value = Number(mask.avgSealedFitFactor)
        if (this.metricIsMissing(metricKey, mask)) {
          return -1
        }
        const logValue = Math.log10(value)
        return this.clampPercent(logValue / 3)
      }

      if (metricKey === 'breathability') {
        if (this.metricIsMissing(metricKey, mask)) {
          return -1
        }
        const bounds = this.breathabilityBounds()
        if (bounds.min === null || bounds.max === null) {
          return -1
        }
        const scaled = this.minMaxScale(Number(mask.avgBreathabilityPa), bounds.min, bounds.max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (metricKey === 'affordability') {
        if (this.metricIsMissing(metricKey, mask)) {
          return -1
        }
        const bounds = this.costBounds()
        if (bounds.min === null || bounds.max === null) {
          return -1
        }
        const scaled = this.minMaxScale(Number(mask.initialCostUsDollars), bounds.min, bounds.max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (metricKey === 'strap_type') {
        return -1
      }

      return -1
    },
    metricCellText(metricKey, mask) {
      if (this.metricIsMissing(metricKey, mask)) {
        return 'Missing'
      }

      if (metricKey === 'proba_fit') {
        return `${Math.round(Number(mask.probaFit) * 100)}%`
      }
      if (metricKey === 'filtration') {
        return `${Math.round(Number(mask.avgSealedFitFactor))}`
      }
      if (metricKey === 'breathability') {
        return `${Math.round(Number(mask.avgBreathabilityPa))} pa`
      }
      if (metricKey === 'affordability') {
        return `$${Number(mask.initialCostUsDollars).toFixed(2)}`
      }
      if (metricKey === 'strap_type') {
        return mask.strapType || 'Missing'
      }
      return 'Missing'
    },
    metricIsMissing(metricKey, mask) {
      if (metricKey === 'proba_fit') {
        const hasRecommenderPayload = !!this.$route.query.recommenderPayload
        const value = Number(mask.probaFit)
        return !hasRecommenderPayload || !Number.isFinite(value)
      }
      if (metricKey === 'filtration') {
        const value = Number(mask.avgSealedFitFactor)
        return !Number.isFinite(value) || value <= 0
      }
      if (metricKey === 'breathability') {
        const value = Number(mask.avgBreathabilityPa)
        return !Number.isFinite(value) || value <= 0
      }
      if (metricKey === 'affordability') {
        const value = Number(mask.initialCostUsDollars)
        return !Number.isFinite(value) || value <= 0
      }
      if (metricKey === 'strap_type') {
        return !mask.strapType || String(mask.strapType).trim() === ''
      }
      return true
    },
    clampPercent(value) {
      if (!Number.isFinite(value)) {
        return 0
      }
      return Math.max(0, Math.min(1, value))
    },
    minMaxScale(value, min, max, { zeroRangeValue }) {
      if (!Number.isFinite(value) || min === null || max === null) {
        return zeroRangeValue
      }
      const range = max - min
      if (range <= 0) {
        return zeroRangeValue
      }
      return (value - min) / range
    },
    breathabilityBounds() {
      const contextMin = this.maskDataContext.breathability_min
      const contextMax = this.maskDataContext.breathability_max
      if (contextMin !== null && contextMin !== undefined && contextMax !== null && contextMax !== undefined) {
        return { min: Number(contextMin), max: Number(contextMax) }
      }

      const values = (this.sortedDisplayables || [])
        .map((m) => Number(m.avgBreathabilityPa))
        .filter((v) => Number.isFinite(v) && v > 0)

      if (values.length === 0) {
        return { min: null, max: null }
      }
      return { min: Math.min(...values), max: Math.max(...values) }
    },
    costBounds() {
      const contextMin = this.maskDataContext.initial_cost_min
      const contextMax = this.maskDataContext.initial_cost_max
      if (contextMin !== null && contextMin !== undefined && contextMax !== null && contextMax !== undefined) {
        return { min: 0, max: Math.max(Number(contextMax), 5) }
      }

      const values = (this.sortedDisplayables || [])
        .map((m) => Number(m.initialCostUsDollars))
        .filter((v) => Number.isFinite(v) && v > 0)

      if (values.length === 0) {
        return { min: null, max: null }
      }
      return { min: 0, max: Math.max(...values, 5) }
    },

    async load(toQuery, previousQuery) {
      if (this.$route.name !== 'Masks') {
        return
      }
      const needsAvailableFilter = !Object.prototype.hasOwnProperty.call(toQuery, 'filterForAvailable') || !toQuery.filterForAvailable
      if (needsAvailableFilter) {
        const normalizedQuery = Object.assign({}, toQuery, { filterForAvailable: 'true' })
        await this.$router.replace({ name: 'Masks', query: normalizedQuery })
        return
      }
      if (toQuery.recommenderPayload) {
        const needsSortField = !toQuery.sortByField || toQuery.sortByField === 'none'
        const needsSortStatus = !toQuery.sortByStatus || toQuery.sortByStatus === 'none'

        if (needsSortField || needsSortStatus) {
          const normalizedQuery = Object.assign({}, toQuery, {
            sortByField: needsSortField ? 'probaFit' : toQuery.sortByField,
            sortByStatus: needsSortStatus ? 'descending' : toQuery.sortByStatus,
          })
          await this.$router.replace({ name: 'Masks', query: normalizedQuery })
          return
        }
      }

      this.setFilterQuery(toQuery, 'search')
      this.setFilterQuery(toQuery, 'sortByStatus')
      this.setFilterQuery(toQuery, 'sortByField')
      this.setFilterQuery(toQuery, 'filterForColor')
      this.setFilterQuery(toQuery, 'filterForStrapType')
      this.setFilterQuery(toQuery, 'filterForStyle')
      this.setFilterQuery(toQuery, 'filterForMissing')
      this.setFilterQuery(toQuery, 'filterForAvailable')

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
    viewMask(idOrMask) {
      const id = typeof idOrMask === 'object' ? (idOrMask.id || idOrMask.maskId) : idOrMask
      if (!id) {
        console.warn('Masks: unable to navigate to mask details, missing id', idOrMask)
        return
      }

      const targetPath = `/masks/${id}`
      this.$router.push({ path: targetPath }).catch(() => {})
      setTimeout(() => {
        if (this.$route.path !== targetPath) {
          window.location.hash = `#${targetPath}`
        }
      }, 0)
    },
    removeFilterPill(pill) {
      const query = Object.assign({}, this.$route.query)

      if (pill.type === 'color') {
        query.filterForColor = 'none'
      } else if (pill.type === 'style') {
        query.filterForStyle = 'none'
      } else if (pill.type === 'strap_type') {
        query.filterForStrapType = 'none'
      } else if (pill.type === 'missing') {
        const nextValues = (this.filterForMissing || []).filter((value) => value !== pill.value)
        query.filterForMissing = nextValues.length ? nextValues.join(',') : 'none'
      } else if (pill.type === 'available') {
        query.filterForAvailable = 'true'
      }

      query.page = 1
      this.$router.push({ name: 'Masks', query })
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
        this.recommenderModelTimestamp = null
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
        this.recommenderModelTimestamp = null
        this.message = "Failed to decode recommendations payload."
        return true
      }

      this.lastHandledRecommenderPayload = payloadParam
      this.isRecommenderLoading = true
      this.recommenderModelTimestamp = null
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
            const modelTimestamp = response?.data?.model?.timestamp
            this.recommenderModelTimestamp = modelTimestamp || null
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
        filter_missing: this.filterForMissing.length ? this.filterForMissing.join(',') : 'none',
        filter_available: this.filterForAvailable
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
    position: relative;
    z-index: 30;
  }

  .bar {
    max-height: none;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }

  .active-filter-pills {
    padding: 0 1em;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.45em;
    max-width: 95vw;
    position: relative;
    z-index: 31;
    margin-top: 0.45em;
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

  .mask-metrics-table-wrapper {
    width: 100%;
    overflow-x: auto;
    overflow-y: auto;
    padding: 0 1em calc(var(--footer-height, 0px) + 0.75em);
    box-sizing: border-box;
    height: var(--table-viewport-height, 70vh);
  }

  .mask-metrics-table {
    border-collapse: collapse;
    width: max-content;
    min-width: 100%;
    background-color: #fff;
  }

  .mask-metrics-table th,
  .mask-metrics-table td {
    border: 1px solid #ddd;
    text-align: center;
    vertical-align: middle;
  }

  .mask-metrics-table thead th {
    position: sticky;
    top: 0;
    z-index: 4;
    background-color: #f4f4f4;
  }

  .mask-metrics-table th.sticky-column,
  .mask-metrics-table td.sticky-column {
    position: sticky;
    z-index: 3;
    background-color: #f4f4f4;
  }

  .mask-metrics-table .sticky-image-column {
    left: 0;
    min-width: 7em;
    width: 7em;
  }

  .mask-metrics-table .sticky-mask-column {
    left: 7em;

  }

  .mask-metrics-table thead th.sticky-column {
    z-index: 5;
  }

  .mask-metrics-table thead .sticky-mask-column {
    z-index: 6;
  }

  .mask-metrics-table .metric-label {
    font-weight: 700;
    padding: 1em;
  }

  .image-cell {
    padding: 0.25em;
  }

  .table-mask-image {
    display: block;
    max-height: 4.5em;
    max-width: 6.5em;
    width: auto;
    height: auto;
    object-fit: contain;
    margin: 0 auto;
  }

  .table-mask-image-placeholder {
    color: #777;
    font-size: 0.75em;
    line-height: 1.2;
    min-height: 4.5em;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-mask-name-button {
    display: none;
    background: transparent;
    border: none;
    margin: 0.35em auto 0;
    padding: 0;
    font-size: 0.7em;
    line-height: 1.2;
    max-width: 8.5em;
    white-space: normal;
    word-break: break-word;
    text-align: center;
    color: #222;
  }

  .table-text-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    line-height: 1.2;
    padding: 0.4em;
    word-break: break-word;
    color: #222;
    text-shadow: none;
    font-weight: 500;
  }

  .mask-row-button {
    background: transparent;
    border: none;
    font-size: 1em;
    line-height: 1.25;
    padding: 0.4em;
    white-space: normal;
    text-align: center;
    max-width: 23em;
    min-height: 3.5em;
  }

  @media(max-width: 1400px) {
    .sticky-column {
      max-width: 10em;
    }
    .mask-row-button {
      text-align: center;
    }
  }

  @media(max-width: 1127px) {
    .table-text-cell {
      width: 6em;
    }
  }

  @media(max-width: 1072px) {
    .table-text-cell {
      display: none;
    }
  }

  @media(max-width: 1020px) {
    .mask-metrics-table th,
    .mask-metrics-table td {
      min-width: 6em;
    }

    .top-controls {
      flex-direction: column;
      margin-top: 3em;
      margin-bottom: 0.75em;
    }

    .bar {
      flex-direction: column;
    }

    .active-filter-pills {
      margin-top: 0.65em;
      margin-bottom: 0.35em;
    }

    margin-top: 4em;
  }
  @media(max-width: 768px) {
    .top-controls {
      flex-direction: column;
    }

    .sticky-mask-column.desktop {
      display: none;
    }

    .mask-metrics-table .sticky-image-column {
      width: 8.5em;
      min-width: 8.5em;
    }

    .mobile-mask-name-button {
      display: block;
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

    .mask-metrics-table-wrapper {
      padding-bottom: calc(var(--footer-height, 56px) + 2.25em);
    }

    .mask-metrics-table th,
    .mask-metrics-table td {
      min-width: 5em;
    }
  }

  @media(max-width: 600px) {
    .mask-metrics-table td,
    .mask-metrics-table th {
      min-width: 4em;
    }
    .mask-metrics-table td div {
      padding: 2em;
    }
  }

</style>
