<template>
    <Popup class='popup' v-show='!!selectedMask.id && showMaskCardPopup && !viewMaskOnClick' @onclose='toggleMaskCardPopup'>
      <div class='align-items-center justify-content-center'>
        <h3>{{selectedMask.uniqueInternalModelCode}}</h3>
      </div>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='viewMask'>See details about Mask</Button>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='newFitTestWithSize("Too small")'>Mark Too Small</Button>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='newFitTestWithSize("Too big")'>Mark Too Big</Button>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='markNotIncludedInMaskKit()'>Mark Not Included in Kit</Button>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='newFitTestForUser'>Add Fit Testing Data</Button>
      <Button shadow='true' :class="{ tab: true }"  class='button' @click='toggleMaskCardPopup'>Cancel</Button>
    </Popup>

    <div class='masks' :style='masksGridStyle'>

      <div class='card flex align-items-center justify-content-center' v-for='m in cards' @click='selectMask(m)'>

        <table v-if='showStats'>
          <tr class="mobile-only">
            <td class="mobile-image-cell">
              <div class='image-and-name'>
                <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
              </div>
            </td>
            <td class="mobile-title-cell">
              <div class='description'>
                <span>
                  {{m.uniqueInternalModelCode}}
                </span>
              </div>
            </td>
          </tr>
          <tr class="mobile-only">
            <th>Probability of Fit</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('proba_fit', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('proba_fit') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('proba_fit')">
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('proba_fit', m), 'proba_fit')"></div>
                  <div
                    v-if="statNeedsMarker('proba_fit')"
                    class='stat-bar-marker'
                    :style="statMarkerStyle(statPercent('proba_fit', m), 'proba_fit')"
                  ></div>
                  <div
                    v-if="statNeedsMarker('proba_fit')"
                    class='stat-bar-cover'
                    :style="statCoverStyle(statPercent('proba_fit', m), 'proba_fit')"
                  ></div>
                  <div class='stat-bar-label'>{{ statLabel('proba_fit', m) }}</div>
                  <div v-if="statAxisLabel('proba_fit', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('proba_fit', 'min') }}</div>
                  <div v-if="statAxisLabel('proba_fit', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('proba_fit', 'max') }}</div>
                </div>
              </div>
            </td>
          </tr>
          <tr class="desktop-only">
            <td colspan="1">
              <div class='image-and-name'>
                <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
              </div>
            </td>

            <td colspan='1'>
              <div class='description'>
                <span>
                  {{m.uniqueInternalModelCode}}
                </span>
              </div>
            </td>
          </tr>
          <tr>
            <th>Probability of Fit</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('proba_fit', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('proba_fit') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('proba_fit')">
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('proba_fit', m), 'proba_fit')"></div>
                  <div
                    v-if="statNeedsMarker('proba_fit')"
                    class='stat-bar-marker'
                    :style="statMarkerStyle(statPercent('proba_fit', m), 'proba_fit')"
                  ></div>
                  <div
                    v-if="statNeedsMarker('proba_fit')"
                    class='stat-bar-cover'
                    :style="statCoverStyle(statPercent('proba_fit', m), 'proba_fit')"
                  ></div>
                  <div class='stat-bar-label'>{{ statLabel('proba_fit', m) }}</div>
                  <div v-if="statAxisLabel('proba_fit', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('proba_fit', 'min') }}</div>
                  <div v-if="statAxisLabel('proba_fit', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('proba_fit', 'max') }}</div>
                </div>
              </div>
            </td>
          </tr>
            <tr>
            <th>Filtration Factor</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('filtration', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('filtration') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('filtration')">
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('filtration', m), 'filtration')"></div>
                  <div
                    v-if="statNeedsMarker('filtration')"
                    class='stat-bar-marker'
                    :style="statMarkerStyle(statPercent('filtration', m), 'filtration')"
                  ></div>
                  <div
                    v-if="statNeedsMarker('filtration')"
                    class='stat-bar-cover'
                    :style="statCoverStyle(statPercent('filtration', m), 'filtration')"
                  ></div>
                  <div class='stat-bar-label'>{{ statLabel('filtration', m) }}</div>
                  <div v-if="statAxisLabel('filtration', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('filtration', 'min') }}</div>
                  <div v-if="statAxisLabel('filtration', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('filtration', 'max') }}</div>
                </div>
              </div>
            </td>
          </tr>
          <tr>
            <th>Breathability</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('breathability', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('breathability') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('breathability')">
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('breathability', m), 'breathability')"></div>
                  <div
                    v-if="statNeedsMarker('breathability')"
                    class='stat-bar-marker'
                    :style="statMarkerStyle(statPercent('breathability', m), 'breathability')"
                  ></div>
                  <div
                    v-if="statNeedsMarker('breathability')"
                    class='stat-bar-cover'
                    :style="statCoverStyle(statPercent('breathability', m), 'breathability')"
                  ></div>
                  <div class='stat-bar-label'>{{ statLabel('breathability', m) }}</div>
                  <div v-if="statAxisLabel('breathability', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('breathability', 'min') }}</div>
                  <div v-if="statAxisLabel('breathability', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('breathability', 'max') }}</div>
                </div>
              </div>
            </td>
          </tr>
          <tr>
              <th>Affordability (USD)</th>
              <td>
                <div class='stat-cell'>
                  <div v-if="statIsMissing('cost', m)" class='stat-bar-wrapper stat-bar-missing'>
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar stat-bar-missing-fill'></div>
                    <div class='stat-bar-label'>{{ statMissingText('cost') }}</div>
                  </div>
                  <div v-else class='stat-bar-wrapper' :style="statBarWrapperStyle('cost')">
                    <div class='stat-bar-axis'></div>
                    <div class='stat-bar' :style="statBarStyle(statPercent('cost', m), 'cost')"></div>
                    <div
                      v-if="statNeedsMarker('cost')"
                      class='stat-bar-marker'
                      :style="statMarkerStyle(statPercent('cost', m), 'cost')"
                    ></div>
                    <div
                      v-if="statNeedsMarker('cost')"
                      class='stat-bar-cover'
                      :style="statCoverStyle(statPercent('cost', m), 'cost')"
                    ></div>
                    <div class='stat-bar-label'>{{ statLabel('cost', m) }}</div>
                    <div v-if="statAxisLabel('cost', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('cost', 'min') }}</div>
                    <div v-if="statAxisLabel('cost', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('cost', 'max') }}</div>
                  </div>
                </div>
              </td>
          </tr>

          <tr>
            <th>Strap Type</th>
            <td>{{ formatText(m.strapType, 'Missing') }}</td>
          </tr>
          <tr>
            <th>Colors</th>
            <td>
              <MaskColorChips
                :colors='maskColorValues(m)'
                :showLabels='false'
              />
            </td>
          </tr>
        </table>
      </div>
    </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import ColoredCell from './colored_cell.vue'
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import MaskColorChips from './mask_color_chips.vue'
import { deepSnakeToCamel } from './misc.js'
import { assignBoundsToColorScheme, colorPaletteFall, convertColorListToCutpoints, generateEvenSpacedBounds } from './colors.js'
import SearchIcon from './search_icon.vue'
import SortingStatus from './sorting_status.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { Respirator } from './masks.js'


export default {
  name: 'MaskCards',
  components: {
    Button,
    CircularButton,
    ColoredCell,
    ClosableMessage,
    Popup,
    MaskColorChips,
    PersonIcon,
    SearchIcon,
    SortingStatus,
    SurveyQuestion
  },
  data() {
    return {
      selectedMaskId: undefined,
      selectedMask: { uniqueInternalModelCode: ''},
      filterForEarloop: true,
      filterForHeadstrap: true,
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
      search: "",
      sortByField: undefined,
      sortByStatus: 'ascending',
      viewportWidth: typeof window !== 'undefined' ? window.innerWidth : 1920
    }
  },
  props: {
    facialMeasurements: {
      default: {}
    },
    viewMaskOnClick: {
      default: true
    },
    managedUser: {
      default: {
        managedId: 0
      }
    },
    cards: {
      default: []
    },
    showUniqueNumFitTesters: {
      default: false
    },
    showMaskCardPopup: {
      default: false
    },
    showStats: {
      default: true
    },
    dataContext: {
      default: () => ({})
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
          'message'
        ]
    ),

    gridTemplateColumns() {
      let gridTemplateColumns = ""

      if (this.cards.length <=1) {
        gridTemplateColumns = "100%"
      }
      else if (this.cards.length ==2) {
        gridTemplateColumns = "50% 50%"
      }
      else {
        gridTemplateColumns = "16.66% 16.66% 16.66% 16.66% 16.66% 16.66%"
      }

      return {
        'grid-template-columns': gridTemplateColumns
      }
    },

    fitColorScheme() {
      const minimum = 0
      const maximum = 1
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall))
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },
    messages() {
      return this.errorMessages;
    },
    hasRecommenderPayload() {
      return !!(this.$route && this.$route.query && this.$route.query.recommenderPayload)
    },
    expectedMaskColumns() {
      if (this.viewportWidth <= 800) {
        return 1
      }
      if (this.viewportWidth <= 1250) {
        return 2
      }
      if (this.viewportWidth <= 1580) {
        return 3
      }
      return 4
    },
    forceSingleMaskColumn() {
      if (this.cards.length === 0) {
        return false
      }
      return this.cards.length < this.expectedMaskColumns
    },
    masksGridStyle() {
      if (!this.forceSingleMaskColumn) {
        return {}
      }
      return { 'grid-template-columns': '100%' }
    },
  },
  async created() {
    // TODO: a parent might input data on behalf of their children.
    // Currently, this.loadStuff() assumes We're loading the profile for the current user
    this.search = this.$route.query.search || ''
    this.sortByStatus = this.$route.query.sortByStatus
    this.sortByField = this.$route.query.sortByField

    let filterCriteria = ["Earloop", "Headstrap", "Targeted", "NotTargeted"];
    for(let filt of filterCriteria) {
      let specificFilt = 'filterFor' + filt
      if (this.$route.query[specificFilt] == undefined) {
        this[specificFilt] = true
      } else {
        this[specificFilt] = this.$route.query[specificFilt] == 'true'
      }
    }

    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        this.search = toQuery.search || ''
        this.sortByStatus = toQuery.sortByStatus
        this.sortByField = toQuery.sortByField
        // react to route changes...
        for(let filt of filterCriteria) {
          let specificFilt = 'filterFor' + filt
          if (this.$route.query[specificFilt] == undefined) {
            this[specificFilt] = true
          } else {
            this[specificFilt] = this.$route.query[specificFilt] == 'true'
          }
        }
      }
    )

    window.addEventListener('resize', this.updateViewportWidth)

    this.loadStuff()
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateViewportWidth)
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    updateViewportWidth() {
      this.viewportWidth = window.innerWidth
    },
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    toggleMaskCardPopup() {
      this.$emit('toggleMaskCardPopup')
    },
    newFitTestWithSize(size) {
      this.$emit('newFitTestWithSize', {size: size, maskId: this.selectedMask.id, userId: this.managedUser.managedId})
    },
    markNotIncludedInMaskKit() {
      this.$emit('markNotIncludedInMaskKit', {maskId: this.selectedMask.id, managedId: this.managedUser.managedId})
    },
    newFitTestForUser() {
      this.$emit('newFitTestForUser', {
        maskId: this.selectedMask.id,
        userId: this.managedUser.managedId,
        tabToShow: 'Facial Hair'
      })
    },
    selectMask(maskOrId) {
      const mask = typeof maskOrId === 'object'
        ? maskOrId
        : this.cards.find((m) => (m.id || m.maskId) === maskOrId)

      if (!mask) {
        return
      }

      this.selectedMask = mask
      if (this.viewMaskOnClick) {
        const targetId = this.selectedMask.id || this.selectedMask.maskId
        if (!targetId) {
          console.warn('MaskCards: unable to navigate to mask details, missing id', this.selectedMask)
          return
        }

        const targetPath = `/masks/${targetId}`
        this.$router.push({ path: targetPath }).catch(() => {})
        setTimeout(() => {
          if (this.$route.path !== targetPath) {
            window.location.hash = `#${targetPath}`
          }
        }, 0)
      } else {
        this.toggleMaskCardPopup()
      }
    },
    filterFor(string) {
      let filterForString = ('filterFor' + string)
      let newQuery = {}
      newQuery[filterForString] = !this['filterFor' + string]

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      this.$router.push(
        {
          name: 'Masks',
          query: combinedQuery
        }
      )
    },
    formatValue(value, suffix = '') {
      if (value === null || value === undefined || isNaN(value)) {
        return 'N/A'
      }

      return `${Math.round(value)}${suffix}`
    },
    formatCount(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return 'N/A'
      }

      return `${Math.round(value)}`
    },
    formatCurrency(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return 'Missing'
      }

      return `$${Number(value).toFixed(2)}`
    },
    formatText(value, missingText = 'N/A') {
      if (!value) {
        return missingText
      }

      return value
    },
    maskColorValues(mask) {
      if (!mask || !Array.isArray(mask.colors)) {
        return []
      }
      return mask.colors
        .map((value) => String(value || '').trim())
        .filter((value, index, arr) => value && arr.indexOf(value) === index)
    },
    statPercent(type, mask) {
      if (type === 'filtration') {
        const value = mask.avgSealedFitFactor
        if (this.statIsMissing(type, mask)) {
          return null
        }
        const logValue = Math.log10(value)
        return this.clampPercent(logValue / 3)
      }

      if (type === 'breathability') {
        const value = mask.avgBreathabilityPa
        const bounds = this.breathabilityBounds()
        const min = bounds.min
        const max = bounds.max
        if (this.statIsMissing(type, mask) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(value, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (type === 'perimeter') {
        const value = mask.perimeterMm
        const bounds = this.perimeterBounds()
        const min = bounds.min
        const max = bounds.max
        if (this.statIsMissing(type, mask) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(value, min, max, { zeroRangeValue: 1 })
        return this.clampPercent(scaled)
      }
      if (type === 'cost') {
        const value = mask.initialCostUsDollars
        const bounds = this.costBounds()
        const min = bounds.min
        const max = bounds.max
        if (this.statIsMissing(type, mask) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(value, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (type === 'fit_tests') {
        const value = mask.fitTestCount
        const max = this.fitTestCountMax()
        if (this.statIsMissing(type, mask) || max === null || max === undefined) {
          return null
        }
        if (max <= 0) {
          return 0
        }
        return this.clampPercent(value / max)
      }

      if (type === 'proba_fit') {
        const value = mask.probaFit
        if (this.statIsMissing(type, mask)) {
          return null
        }
        return this.clampPercent(value)
      }

      return null
    },
    statLabel(type, mask) {
      if (type === 'filtration') {
        return this.formatValue(mask.avgSealedFitFactor)
      }
      if (type === 'breathability') {
        if (this.statIsMissing(type, mask)) {
          return this.statMissingText(type)
        }
        return this.formatValue(mask.avgBreathabilityPa, ' pa')
      }
      if (type === 'perimeter') {
        return this.formatValue(mask.perimeterMm)
      }
      if (type === 'cost') {
        return this.formatCurrency(mask.initialCostUsDollars)
      }
      if (type === 'fit_tests') {
        return this.formatCount(mask.fitTestCount)
      }
      if (type === 'proba_fit') {
        if (this.statIsMissing(type, mask)) {
          return this.statMissingText(type)
        }
        const percent = Math.round(mask.probaFit * 100)
        return `${percent}%`
      }
      return 'N/A'
    },
    statBarStyle(percent, type) {
      const clamped = this.clampPercent(percent)
      const width = clamped === null ? '0%' : `${Math.round(clamped * 100)}%`

      if (type === 'filtration') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }
      if (type === 'breathability') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }
      if (type === 'proba_fit') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }
      if (type === 'fit_tests') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }
      if (type === 'cost') {
        return {
          width: '100%',
          backgroundColor: 'transparent'
        }
      }
      if (type === 'perimeter') {
        return {
          width: width,
          backgroundColor: '#a3a8ad'
        }
      }
      return {
        width: width,
        backgroundColor: this.statRowColors()[type]
      }
    },
    statBarWrapperStyle(type) {
      if (type === 'filtration') {
        return { background: this.filtrationGradient() }
      }
      if (type === 'breathability') {
        const gradient = this.breathabilityGradient()
        if (!gradient) {
          return {}
        }
        return { background: gradient }
      }
      if (type === 'fit_tests') {
        return { background: this.fitTestsGradient() }
      }
      if (type === 'proba_fit') {
        return { background: this.probaFitGradient() }
      }
      if (type === 'cost') {
        return { background: this.costGradient() }
      }
      return {}
    },
    statNeedsMarker(type) {
      return ['filtration', 'breathability', 'proba_fit', 'fit_tests', 'cost'].includes(type)
    },
    statMarkerStyle(percent, type) {
      const clamped = this.clampPercent(percent)
      if (clamped === null) {
        return {}
      }
      const position = Math.round(clamped * 10000) / 100
      return {
        left: `calc(${position}% - 1px)`
      }
    },
    statCoverStyle(percent, type) {
      const clamped = this.clampPercent(percent)
      if (clamped === null) {
        return {}
      }
      const position = Math.round(clamped * 10000) / 100
      return {
        left: `calc(${position}% + 1px)`,
        backgroundColor: '#f1f1f1'
      }
    },
    gradientForType(type) {
      if (type === 'filtration') {
        return this.filtrationGradient()
      }
      if (type === 'breathability') {
        return this.breathabilityGradient()
      }
      if (type === 'proba_fit') {
        return this.probaFitGradient()
      }
      if (type === 'fit_tests') {
        return this.fitTestsGradient()
      }
      if (type === 'cost') {
        return this.costGradient()
      }
      return null
    },
    filtrationGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33.333%, ${green} 100%)`
    },
    breathabilityGradient() {
      const bounds = this.breathabilityBounds()
      const min = bounds.min
      const max = bounds.max
      if (min === null || max === null || min === undefined || max === undefined) {
        return null
      }
      const orderedMin = Math.min(min, max)
      const orderedMax = Math.max(min, max)
      if (orderedMax <= orderedMin) {
        return null
      }
      const p33 = orderedMin + (orderedMax - orderedMin) * 0.3333333333333333
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      const scalePosition = (value) => ((value - orderedMin) / (orderedMax - orderedMin)) * 100
      const axisStop33 = scalePosition(p33)
      return `linear-gradient(90deg, ${red} 0%, ${yellow} ${axisStop33}%, ${green} 100%)`
    },
    probaFitGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33.333%, ${green} 100%)`
    },
    fitTestsGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33.333%, ${green} 100%)`
    },
    costGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33.333%, ${green} 100%)`
    },
    statIsMissing(type, mask) {
      if (type === 'filtration') {
        return mask.avgSealedFitFactor === null || mask.avgSealedFitFactor === undefined || isNaN(mask.avgSealedFitFactor) || mask.avgSealedFitFactor <= 0
      }
      if (type === 'breathability') {
        return mask.avgBreathabilityPa === null || mask.avgBreathabilityPa === undefined || isNaN(mask.avgBreathabilityPa) || mask.avgBreathabilityPa <= 0
      }
      if (type === 'perimeter') {
        return mask.perimeterMm === null || mask.perimeterMm === undefined || isNaN(mask.perimeterMm) || mask.perimeterMm <= 0
      }
      if (type === 'cost') {
        return mask.initialCostUsDollars === null || mask.initialCostUsDollars === undefined || isNaN(mask.initialCostUsDollars) || mask.initialCostUsDollars <= 0
      }
      if (type === 'fit_tests') {
        return mask.fitTestCount === null || mask.fitTestCount === undefined || isNaN(mask.fitTestCount)
      }
      if (type === 'proba_fit') {
        if (!this.hasRecommenderPayload) {
          return true
        }
        return mask.probaFit === null || mask.probaFit === undefined || isNaN(mask.probaFit)
      }
      return true
    },
    statAxisLabel(type, position) {
      if (type === 'filtration') {
        return position === 'min' ? '10^0' : '10^3'
      }
      if (type === 'breathability') {
        const bounds = this.breathabilityBounds()
        const min = bounds.min
        const max = bounds.max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const orderedMin = Math.min(min, max)
        const orderedMax = Math.max(min, max)
        const labelValue = position === 'min' ? orderedMax : orderedMin
        if (labelValue <= 0) {
          return 'Missing'
        }
        return this.formatValue(labelValue, ' pa')
      }
      if (type === 'perimeter') {
        const bounds = this.perimeterBounds()
        const min = bounds.min
        const max = bounds.max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatValue(min) : this.formatValue(max)
      }
      if (type === 'cost') {
        const bounds = this.costBounds()
        const min = bounds.min
        const max = bounds.max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatCurrency(max) : this.formatCurrency(0)
      }
      if (type === 'fit_tests') {
        const max = this.fitTestCountMax()
        if (max === null || max === undefined) {
          return null
        }
        return position === 'min' ? '0' : this.formatCount(max)
      }
      if (type === 'proba_fit') {
        return position === 'min' ? '0%' : '100%'
      }
      return null
    },
    statMissingText(type) {
      return 'Missing'
    },
    breathabilityBounds() {
      const contextMin = this.dataContext.breathability_min
      const contextMax = this.dataContext.breathability_max
      if (contextMin !== null && contextMin !== undefined && contextMax !== null && contextMax !== undefined) {
        return { min: contextMin, max: contextMax }
      }

      const values = (this.cards || [])
        .map((m) => m.avgBreathabilityPa)
        .filter((v) => v !== null && v !== undefined && !isNaN(v) && Number(v) > 0)
        .map((v) => Number(v))

      if (values.length === 0) {
        return { min: null, max: null }
      }

      return { min: Math.min(...values), max: Math.max(...values) }
    },
    perimeterBounds() {
      const contextMin = this.dataContext.perimeter_min
      const contextMax = this.dataContext.perimeter_max
      if (contextMin !== null && contextMin !== undefined && contextMax !== null && contextMax !== undefined) {
        return { min: contextMin, max: contextMax }
      }

      const values = (this.cards || [])
        .map((m) => m.perimeterMm)
        .filter((v) => v !== null && v !== undefined && !isNaN(v) && Number(v) > 0)
        .map((v) => Number(v))

      if (values.length === 0) {
        return { min: null, max: null }
      }

      return { min: Math.min(...values), max: Math.max(...values) }
    },
    fitTestCountMax() {
      const contextMax = this.dataContext.fit_test_count_max
      if (contextMax !== null && contextMax !== undefined) {
        return contextMax
      }

      const values = (this.cards || [])
        .map((m) => m.fitTestCount)
        .filter((v) => v !== null && v !== undefined && !isNaN(v))
        .map((v) => Number(v))

      if (values.length === 0) {
        return null
      }

      return Math.max(...values)
    },
    costBounds() {
      const contextMin = this.dataContext.initial_cost_min
      const contextMax = this.dataContext.initial_cost_max
      if (contextMin !== null && contextMin !== undefined && contextMax !== null && contextMax !== undefined) {
        return { min: 0, max: Math.max(contextMax, 5) }
      }

      const values = (this.cards || [])
        .map((m) => m.initialCostUsDollars)
        .filter((v) => v !== null && v !== undefined && !isNaN(v) && Number(v) > 0)
        .map((v) => Number(v))

      if (values.length === 0) {
        return { min: null, max: null }
      }

      return { min: 0, max: Math.max(...values, 5) }
    },
    statRowColors() {
      return {
        filtration: '#c0392b',
        breathability: '#e67e22',
        perimeter: '#16a085',
        cost: 'rgb(188, 163, 255)',
        fit_tests: '#2980b9',
        proba_fit: '#8e44ad'
      }
    },
    clampPercent(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return null
      }
      return Math.max(0, Math.min(1, value))
    },
    minMaxScale(value, min, max, { zeroRangeValue }) {
      const range = max - min
      if (range <= 0) {
        return zeroRangeValue
      }
      return (value - min) / range
    },
    sortingStatus(field) {
      if (this.sortByField == field) {
        return this.sortByStatus
      } else {
        return ''
      }
    },
    sortBy(field) {
      let query = {
        sortByField: field
      }

      if (this.sortByField != field) {
        query['sortByStatus'] = 'ascending'
      } else {
        if (this.sortByStatus == 'ascending') {
          query['sortByStatus'] = 'descending'
        } else if (this.sortByStatus == 'descending') {
          query['sortByStatus'] = 'ascending'
        }
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        query
      )

      this.$router.push(
        {
          name: 'Masks',
          query: combinedQuery
        }
      )
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
    viewMask() {
      this.$router.push(
        {
          name: "ShowMask",
          params: {
            id: this.selectedMask.id
          },
        }
      )

    },
    viewMaskOrAddFitTest(id) {
      // if () {
      // }
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
    async loadStuff() {
      // TODO: load the profile for the current user
      // TODO: take in managed_id from props
      // Conditionally load here, if no managed_id, just load masks as is?
      // If managed id exists, only load the masks that have been shipped to this user?

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
  }
}
</script>

<style scoped>
  .flex {
    display: flex;
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
    flex-direction: column;
    padding: 1em;
  }

  .card:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  .card .description {
    width: 8em;
    padding: 1em;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }

  .thumbnail {
    max-width:11em;
    max-height:11em;
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

  .masks {
    display: grid;
    grid-template-columns: 25% 25% 25% 25%;
    grid-template-rows: auto;
    overflow-y: auto;
    height: 77vh;
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
    padding-left: 0.5em;
    padding-right: 0.5em;
  }
  .sticky {
    position: fixed;
    top: 3em;
  }

  th, td {
    padding-left: 0.5em;
    padding-right: 0.5em;
    text-align: center;
  }
  .stat-cell {
    min-width: 9em;
    max-width: 10em;
  }
  .stat-bar-wrapper {
    position: relative;
    height: 2.25em;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.4em;
    background-color: #f1f1f1;
    overflow: hidden;
  }
  .stat-bar-axis {
    position: absolute;
    left: 0.5em;
    right: 0.5em;
    bottom: 0.35em;
    height: 2px;
    background-color: rgba(0, 0, 0, 0.2);
    z-index: 1;
  }
  .stat-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 0.4em;
    opacity: 0.9;
  }
  .stat-bar-marker {
    position: absolute;
    width: 2px;
    top: 0;
    bottom: 0;
    background-color: #ffffff;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.6);
    z-index: 2;
  }
  .stat-bar-cover {
    position: absolute;
    top: 0;
    bottom: 0;
    right: 0;
    background-color: #f1f1f1;
    z-index: 1;
  }
  .stat-bar-label {
    position: relative;
    z-index: 3;
    font-weight: bold;
    color: #111;
    text-shadow: 1px 1px 2px #fff;
  }
  .stat-bar-tick {
    position: absolute;
    bottom: 0.15em;
    font-size: 0.7em;
    color: #333;
    opacity: 0.75;
    z-index: 1;
  }
  .stat-bar-tick-left {
    left: 0.4em;
  }
  .stat-bar-tick-right {
    right: 0.4em;
  }
  .stat-bar-missing {
    background-color: #e0e0e0;
  }
  .stat-bar-missing-fill {
    width: 100%;
    background-color: #b5b5b5;
  }
  .stat-na {
    font-weight: bold;
    color: #444;
  }

  @media (max-width: 500px) {
    table {
      width: 100%;
    }

    tr {
      display: grid;
      grid-template-columns: 1fr 1fr;
      align-items: center;
    }

    th,
    td {
      width: 100%;
    }

    .desktop-only {
      display: none;
    }

    .mobile-only {
      display: grid;
    }

    .mobile-title-cell .description {
      text-align: left;
    }
  }

  @media (min-width: 501px) {
    .mobile-only {
      display: none;
    }
  }

  .popup {
    top: 3em;
  }

  .button {
    margin: 1em;
  }

  .image-and-name {
    display: flex;
    justify-content: center;
    height: 10em;
    align-items: center;
  }

  h3 {
    padding-left: 1em;
    padding-right: 1em;
  }

  @media(max-width: 1580px) {
    .masks {
      grid-template-columns: 33% 33% 33%;
    }
  }
  @media(max-width: 1250px) {
    .masks {
      grid-template-columns: 50% 50%;

      position: relative;
      top: 2em;
    }
  }
  @media(max-width: 930px) {
    img {
      width: 100vw;
    }


    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }
    .masks {
      grid-template-columns: 50% 50%;
      overflow: auto;

      position: relative;
      top: 2em;
      height: 66vh;
    }

    #search {
      width: 70vw;
      padding: 1em;
    }

    .icon {
      padding: 1em;
    }

    .thumbnail {
      max-height: 15em;
    }

  }

  @media(max-width: 800px) {
    .image-and-name {
      height: 12em;
      width: 45vw;
      flex-direction: column;
    }

    img {
      max-height: 50em;
    }
    .masks {
      grid-template-columns: 100%;
      overflow: auto;

      position: relative;
      top: 2em;
    }
    .card {
      padding: 1em 0;
      display: grid;
      grid-template-columns: 100%;

    }

    th, td {
      padding-left: 0;
      padding-right: 0;
      text-align: center;
    }

    .stat-cell {
      width: 45vw;
      max-width: 45vw;
    }

    .card .description {
      width: 45vw;
    }
  }

</style>

