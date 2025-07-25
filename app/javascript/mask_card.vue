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
    <div class='masks' :style='gridTemplateColumns'>

      <div class='card flex flex-dir-col align-items-center justify-content-center' v-for='m in cards' @click='selectMask(m.id)'>

        <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
        <div class='description'>
          <span>
            {{m.uniqueInternalModelCode}}
          </span>
        </div>
        <table v-if='showStats'>
          <tr>
            <th>Proba Fit</th>
            <td rowspan='1'>
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
            <th>Filtration factor</th>
            <td>
              <ColoredCell
               class='risk-score'
               :colorScheme="fitFactorColorScheme"
               :maxVal=1000
               :value='m.avgSealedFitFactor'
                :text="`${Math.round(m.avgSealedFitFactor)} (${m.countSealedFitFactor})`"
               :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black'  }"
               :exception='exceptionMissingObject'
               />
            </td>
          </tr>
          <tr>
            <th>Breathability</th>
            <td>
              <ColoredCell
               class='risk-score'
               :colorScheme="breathabilityColorScheme"
               :maxVal=250
               :value='m.avgBreathabilityPa'
                :text="`${Math.round(m.avgBreathabilityPa)} pa (${m.countBreathability})`"
               :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black'  }"
               :exception='exceptionMissingObject'
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
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import { assignBoundsToColorScheme, colorPaletteFall, convertColorListToCutpoints, generateEvenSpacedBounds } from './colors.js'
import SearchIcon from './search_icon.vue'
import SortingStatus from './sorting_status.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { perimeterColorScheme } from './colors.js'
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
    SurveyQuestion,
    TabSet
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
        gridTemplateColumns = "33% 33% 33%"
      }

      return {
        'grid-template-columns': gridTemplateColumns
      }
    },

    perimColorScheme() {
      return perimeterColorScheme()
    },

    breathabilityColorScheme() {
      const minimum = 50
      const maximum = 400
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      let copyColorPaletteFall = JSON.parse(JSON.stringify(colorPaletteFall)).reverse()

      const scheme = convertColorListToCutpoints(
        copyColorPaletteFall
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
    },

    fitFactorColorScheme() {
      const minimum = 1
      const maximum = 100
      const numObjects = 6
      const evenSpacedBounds = generateEvenSpacedBounds(minimum, maximum, numObjects)

      const scheme = convertColorListToCutpoints(
        JSON.parse(JSON.stringify(colorPaletteFall))
      )

      return assignBoundsToColorScheme(scheme, evenSpacedBounds)
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
      this.toggleMaskCardPopup()
      this.selectedMask = this.masks.filter((m) => m.id == id)[0]
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
    height: 75vh;
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

  .popup {
    top: 3em;
  }

  .button {
    margin: 1em;
  }

  h3 {
    padding-left: 1em;
    padding-right: 1em;
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
    .masks {
      grid-template-columns: 100%;
      overflow: auto;
      height: 65vh;
    }

    #search {
      width: 70vw;
      padding: 1em;
    }

    .icon {
      padding: 1em;
    }

    .thumbnail {
      max-width:70vw;
      max-height:none;
    }

  }

</style>

