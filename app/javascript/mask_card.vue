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

    <div>
      <p v-show='cards.length == 0'>
        This page displays untested masks that have been shipped to the pod that the individual belongs to. This list can be empty when:
      </p>

      <ul v-show='cards.length == 0'>
        <li>the pod for this given individual <strong>was not</strong> sent a mask kit from Breathesafe LLC</li>
        <li>the pod for this individual did receive masks sent by Breathesafe LLC, and the individual provided data by:
          <ul>
            <li>Marking the masks as being too big or too small</li>
            <li>Marking the mask as not having been received by the pod.</li>
            <li>Testing the mask by going through the qualitative fit testing procedure</li>
          </ul>
        </li>
      </ul>

      <p v-show='cards.length == 0'>
        If this individual did not receive a mask kit but are expecting to have received one, please contact <a href="mailto:info@breathesafe.xyz">info@breathesafe.xyz</a>. If the individual does have access to masks that were not shipped by Breathesafe LLC, said individual can still add user seal check and fit test data by clicking on the plus button above.
      </p>
    </div>
    <div class='masks'>

      <div class='card flex align-items-center justify-content-center' v-for='m in cards' @click='selectMask(m.id)'>

        <table v-if='showStats'>
          <tr >
            <td colspan='2'>
              <div class='image-and-name'>
                <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
              </div>
            </td>

            <th colspan='1'>Probability of Fit</th>
            <td colspan="1">
              <ColoredCell
               class='risk-score'
               :colorScheme="fitColorScheme"
               :maxVal=1
               :value='m.probaFit'
               :text="`${Math.round(m.probaFit * 100, 3)}% (${m.uniqueFitTestersCount})`"
               :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black'  }"
               :exception='exceptionMissingObject'
               />
            </td>
          </tr>
          <tr>
            <td colspan='4'>
              <div class='description'>
                <span>
                  {{m.uniqueInternalModelCode}}
                </span>
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
                <div v-else class='stat-bar-wrapper'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('filtration', m), 'filtration')"></div>
                  <div class='stat-bar-label'>{{ statLabel('filtration', m) }}</div>
                  <div v-if="statAxisLabel('filtration', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('filtration', 'min') }}</div>
                  <div v-if="statAxisLabel('filtration', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('filtration', 'max') }}</div>
                </div>
              </div>
            </td>
            <th># Fit Tests</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('fit_tests', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('fit_tests') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('fit_tests', m), 'fit_tests')"></div>
                  <div class='stat-bar-label'>{{ statLabel('fit_tests', m) }}</div>
                  <div v-if="statAxisLabel('fit_tests', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('fit_tests', 'min') }}</div>
                  <div v-if="statAxisLabel('fit_tests', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('fit_tests', 'max') }}</div>
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
                <div v-else class='stat-bar-wrapper'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('breathability', m), 'breathability')"></div>
                  <div class='stat-bar-label'>{{ statLabel('breathability', m) }}</div>
                  <div v-if="statAxisLabel('breathability', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('breathability', 'min') }}</div>
                  <div v-if="statAxisLabel('breathability', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('breathability', 'max') }}</div>
                </div>
              </div>
            </td>
            <th>Style</th>
            <td>{{ formatText(m.style, 'Missing') }}</td>
          </tr>
          <tr>
            <th>Perimeter (mm)</th>
            <td>
              <div class='stat-cell'>
                <div v-if="statIsMissing('perimeter', m)" class='stat-bar-wrapper stat-bar-missing'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar stat-bar-missing-fill'></div>
                  <div class='stat-bar-label'>{{ statMissingText('perimeter') }}</div>
                </div>
                <div v-else class='stat-bar-wrapper'>
                  <div class='stat-bar-axis'></div>
                  <div class='stat-bar' :style="statBarStyle(statPercent('perimeter', m), 'perimeter')"></div>
                  <div class='stat-bar-label'>{{ statLabel('perimeter', m) }}</div>
                  <div v-if="statAxisLabel('perimeter', 'min')" class='stat-bar-tick stat-bar-tick-left'>{{ statAxisLabel('perimeter', 'min') }}</div>
                  <div v-if="statAxisLabel('perimeter', 'max')" class='stat-bar-tick stat-bar-tick-right'>{{ statAxisLabel('perimeter', 'max') }}</div>
                </div>
              </div>
            </td>
            <th>Strap Type</th>
            <td>{{ formatText(m.strapType, 'Missing') }}</td>
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
      sortByStatus: 'ascending'
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
    showProbaFit: {
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

    this.loadStuff()
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
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
    selectMask(id) {
      const mask = this.cards.find((m) => m.id === id)
      if (!mask) {
        return
      }

      this.selectedMask = mask

      // query: this.facialMeasurements
      let query = { }
      for (let facialMeasurement in this.facialMeasurements) {
        query[facialMeasurement] = this.facialMeasurements[facialMeasurement]['value']
      }

      if (this.viewMaskOnClick) {
        this.$router.push({
          name: 'ShowMask',
          params: {
            id: this.selectedMask.id
          },
          query: query
        })
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
    formatText(value, missingText = 'N/A') {
      if (!value) {
        return missingText
      }

      return value
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
        const min = this.dataContext.breathability_min
        const max = this.dataContext.breathability_max
        if (this.statIsMissing(type, mask) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(value, min, max, { zeroRangeValue: 0 })
        return this.clampPercent(1 - scaled)
      }

      if (type === 'perimeter') {
        const value = mask.perimeterMm
        const min = this.dataContext.perimeter_min
        const max = this.dataContext.perimeter_max
        if (this.statIsMissing(type, mask) || min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        const scaled = this.minMaxScale(value, min, max, { zeroRangeValue: 1 })
        return this.clampPercent(scaled)
      }

      if (type === 'fit_tests') {
        const value = mask.fitTestCount
        const max = this.dataContext.fit_test_count_max
        if (this.statIsMissing(type, mask) || max === null || max === undefined) {
          return null
        }
        if (max <= 0) {
          return 0
        }
        return this.clampPercent(value / max)
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
      if (type === 'fit_tests') {
        return this.formatCount(mask.fitTestCount)
      }
      return 'N/A'
    },
    statBarStyle(percent, type) {
      return {
        width: `${Math.round(percent * 100)}%`,
        backgroundColor: this.statRowColors()[type]
      }
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
      if (type === 'fit_tests') {
        return mask.fitTestCount === null || mask.fitTestCount === undefined || isNaN(mask.fitTestCount)
      }
      return true
    },
    statAxisLabel(type, position) {
      if (type === 'filtration') {
        return position === 'min' ? '10^0' : '10^3'
      }
      if (type === 'breathability') {
        const min = this.dataContext.breathability_min
        const max = this.dataContext.breathability_max
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
        const min = this.dataContext.perimeter_min
        const max = this.dataContext.perimeter_max
        if (min === null || max === null || min === undefined || max === undefined) {
          return null
        }
        return position === 'min' ? this.formatValue(min) : this.formatValue(max)
      }
      if (type === 'fit_tests') {
        const max = this.dataContext.fit_test_count_max
        if (max === null || max === undefined) {
          return null
        }
        return position === 'min' ? '0' : this.formatCount(max)
      }
      return null
    },
    statMissingText(type) {
      return 'Missing'
    },
    statRowColors() {
      return {
        filtration: '#c0392b',
        breathability: '#e67e22',
        perimeter: '#16a085',
        fit_tests: '#2980b9'
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
    grid-template-columns: 33% 33% 33%;
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
  }
  .stat-bar {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    border-radius: 0.4em;
    opacity: 0.9;
  }
  .stat-bar-label {
    position: relative;
    z-index: 1;
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
      grid-template-columns: 50% 50%;
    }
  }
  @media(max-width: 1250px) {
    .masks {
      grid-template-columns: 100%;

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
      grid-template-columns: 100%;
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
      max-height: 7em;
    }

  }

  @media(max-width: 600px) {
    .image-and-name {
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
  }

</style>
