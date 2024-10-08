<template>
  <div class='align-items-center flex-dir-col sticky'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>Masks</h2>
      <CircularButton text="+" @click="newMask" v-show="currentUser"/>
    </div>

    <div class='row'>
      <input type="text" @change='updateSearch'>
      <SearchIcon height='2em' width='2em'/>

      <button class='icon' @click='showPopup = true'>
        <svg class='filter-button' xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="8 10 70 70"
          width="2em" height="2em"
          >
          <path d='m 20 20 h 40 l -18 30 v 20 l -4 -2  v -18 z' stroke='black' fill='#aaa'/>
        </svg>

      </button>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <div class='container chunk'>
      <Popup v-show='showPopup' @onclose='showPopup = false'>
        <div  style='padding: 1em;'>
          <h3>Sort by:</h3>
          <table>
            <thead>
              <tr>
                <th>icon</th>
                <th>field</th>
                <th>status</th>
              </tr>
            </thead>
            <tbody>
              <tr @click='sortBy("perimeterMm")'>
                <td>
                  <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/tape-measure.png" alt="tape measure" class='tape-measure' title="Perimeter of the mask, measured in millimeters, defined as the distance that covers the face">
                </td>
                <td >Perimeter</td>
                <td>
                  <SortingStatus :status='sortingStatus("perimeterMm")'/>
                </td>
              </tr>
              <tr @click='sortBy("uniqueFitTestersCount")'>
                <td>
                  <PersonIcon
                    backgroundColor='rgb(150,150,150)'
                    amount='1'
                  />
                </td>
                <td >Unique number of fit testers</td>
                <td>
                  <SortingStatus :status='sortingStatus("uniqueFitTestersCount")'/>
                </td>
              </tr>
            </tbody>
          </table>
          <br>

          <h3>Filter for:</h3>
          <br>
          <div>Strap type</div>
          <table>
            <tr>
              <td><input type="checkbox" :checked='filterForEarloop' @click='filterFor("Earloop")'>Earloop</td>
              <td><input type="checkbox" :checked='filterForHeadstrap' @click='filterFor("Headstrap")'>Headstrap</td>
            </tr>
          </table>


        </div>
      </Popup>
    </div>




    <div class='main grid'>
      <div class='card flex flex-dir-col align-items-center justify-content-center' v-for='m in sortedDisplayables' @click='viewMask(m.id)'>
        <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
        <div class='description'>
          <span>
            {{m.uniqueInternalModelCode}}
          </span>
        </div>
        <table>
          <tr>
            <td>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/tape-measure.png" alt="tape measure" class='tape-measure' title="Perimeter of the mask, measured in millimeters, defined as the distance that covers the face">
            </td>
            <td>
              <ColoredCell
               class='risk-score'
               :colorScheme="perimColorScheme"
               :maxVal=450
               :value='m.perimeterMm'
               :text="`${m.perimeterMm} mm`"
               :style="{'font-weight': 'bold', color: 'white', 'text-shadow': '1px 1px 2px black'  }"
               :exception='exceptionMissingObject'
               />
            </td>
          </tr>
          <tr>
            <td title="Unique number of fit testers" >
              <PersonIcon
                backgroundColor='rgb(150,150,150)'
                amount='1'
              />
            </td>
            <td>
              <span>
                {{m.uniqueFitTestersCount}}
              </span>
            </td>
          </tr>
        </table>
      </div>
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
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SearchIcon from './search_icon.vue'
import SortingStatus from './sorting_status.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { perimeterColorScheme } from './colors.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'Masks',
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
      filterForEarloop: true,
      filterForHeadstrap: true,
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

    perimColorScheme() {
      return perimeterColorScheme()
    },
    displayables() {
      if (this.search == "" || this.search == undefined) {
        return this.masks
      } else {
        let lowerSearch = this.search.toLowerCase()
        let filterForHeadstrap = this.filterForHeadstrap
        let filterForEarloop = this.filterForEarloop

        return this.masks.filter(
          function(mask) {
            return mask.uniqueInternalModelCode.toLowerCase().match(lowerSearch)
              && (
                (filterForHeadstrap && mask.strapType == 'Headstrap')
                || (filterForEarloop && mask.strapType == 'Earloop')
              )
          }
        )
      }
    },
    sortedDisplayables() {
      if (this.sortByStatus == 'ascending') {
        return this.displayables.sort(function(a, b) {
          return parseInt(a[this.sortByField] || 0)  - parseInt(b[this.sortByField] || 0)
        }.bind(this))
      } else if (this.sortByStatus == 'descending') {
        return this.displayables.sort(function(a, b) {
          return parseInt(b[this.sortByField] || 0) - parseInt(a[this.sortByField] || 0)
        }.bind(this))
      } else {
        return this.displayables
      }
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
    if (this.$route.query.filterForEarloop == undefined) {
      this.filterForEarloop = true
    } else {
      this.filterForEarloop = this.$route.query.filterForEarloop == 'true'
    }

    if (this.$route.query.filterForHeadstrap == undefined) {
      this.filterForHeadstrap = true
    } else {
      this.filterForHeadstrap = this.$route.query.filterForHeadstrap == 'true'
    }

    this.$watch(
      () => this.$route.query,
      (toQuery, previousQuery) => {
        this.search = toQuery.search || ''
        this.sortByStatus = toQuery.sortByStatus
        this.sortByField = toQuery.sortByField
        // react to route changes...
        if (this.$route.query.filterForEarloop == undefined) {
          this.filterForEarloop = true
        } else {
          this.filterForEarloop = this.$route.query.filterForEarloop == 'true'
        }

        if (this.$route.query.filterForHeadstrap == undefined) {
          this.filterForHeadstrap = true
        } else {
          this.filterForHeadstrap = this.$route.query.filterForHeadstrap == 'true'
        }
      }
    )

    this.loadStuff()
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
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
    background-color: rgb(230,230,230);
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
    overflow-y: auto;
    height: 75vh;
  }

  .tape-measure {
    margin-right: 0.5em;
    max-width: 1.5em;
  }

  .risk-score {
    width: 5em;
    height: 2em;
    font-size: 0.75em;
  }
  .sticky {
    position: fixed;
    top: 3em;
  }

  th, td {
    text-align: center;
  }

</style>
