<template>
  <div class='align-items-center flex-dir-col'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>Fit Tests</h2>
      <CircularButton text="+" @click="newFitTest"/>
    </div>

    <div class='menu row'>
      <TabSet
        :options='tabToShowOptions'
        @update='setTabTo'
        :tabToShow='tabToShow'
      />
    </div>

    <div class='row'>
      <label >For:</label>
      <select :value="managedId" @change='setManagedUser'>
        <option v-for='m in managedUsers' :value="m.managedId">{{m.firstName + ' ' + m.lastName}}</option>
      </select>
    </div>

    <SortFilterPopup
      :showPopup='showPopup'
      @filterFor='filterFor'
      @sortBy='filterFor'
      @hideSortFilterPopUp='hideSortFilterPopUp'
    />


    <SearchSortFilterSection
      @updateSearch='updateSearch'
      @toggleShowPopup='toggleShowPopup'
    />

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <MaskCards :cards='sortedDisplayables' v-show='tabToShow == "Untested"'/>

    <div class='main scrollable desktopView' v-show='tabToShow == "Tested"'>
      <table>
        <thead>
          <th>Tester</th>
          <th>Image</th>
          <th>Mask</th>
          <th>Created at</th>
          <th>Beard Length</th>
          <th>User Seal Check</th>
          <th>QLFT</th>
          <th>QNFT HMFF</th>
          <th>Comfort</th>
          <th>Has facial measurement data</th>
        </thead>
        <tbody>
          <tr v-for='f in displayables'>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "User"})'>{{f.firstName + ' ' + f.lastName}}</td>
            <td>
              <router-link :to="showMask(f)">
                <img :src="f.imageUrls[0]" alt="" class='thumbnail'>
              </router-link>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.uniqueInternalModelCode}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.shortHandCreatedAt}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Facial Hair"})'>{{f.facialHair.beard_length_mm}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "User Seal Check"})'>
              <ColoredCell class='status' :text='f.userSealCheckStatus' :backgroundColor='statusColor(f.userSealCheckStatus)'/>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QLFT"})'>
              <ColoredCell class='status' :text='f.qualitativeStatus' :backgroundColor='statusColor(f.qualitativeStatus)'/>
            </td>
            <td class='status' @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QNFT"})'>
              <ColoredCell class='status' :text='f.quantitativeStatus' :backgroundColor='quantitativeStatusColor(f.quantitativeStatus)'/>
            </td>
            <td >
              <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Comfort"})' class='status' :text='f.comfortStatus' :backgroundColor='statusColor(f.comfortStatus)'/>
            </td>
              <td >
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Comfort"})' class='status' :text='f.facialMeasurementPresence' :backgroundColor='facialMeasPresenceColorMappingStatus(f.facialMeasurementPresence)'/>
              </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class='main scrollable mobileView' v-show='tabToShow == "Tested"'>
      <div class='grid'>
        <div v-for='f in displayables' class='card'>
          <table>
            <tr>
              <td rowspan='2' colspan='2'>
                <router-link :to="showMask(f)">
                  <img :src="f.imageUrls[0]" alt="" class='thumbnail'>
                </router-link>
              </td>
              <th>Tester</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "User"})'>{{f.firstName + ' ' + f.lastName}}</td>
            </tr>
            <tr>
              <th>Mask</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.uniqueInternalModelCode}}</td>
            </tr>

            <tr>
              <th>Created at</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.shortHandCreatedAt}}</td>
              <th>Beard length</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Facial Hair"})'>{{f.facialHair.beard_length_mm}}</td>
            </tr>

            <tr>
              <th>User Seal Check</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "User Seal Check"})'>
                <ColoredCell class='status' :text='f.userSealCheckStatus' :backgroundColor='statusColor(f.userSealCheckStatus)'/>
              </td>
              <th>QLFT</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QLFT"})'>
                <ColoredCell class='status' :text='f.qualitativeStatus' :backgroundColor='statusColor(f.qualitativeStatus)'/>
              </td>
            </tr>

            <tr>
              <th>QNFT</th>
              <td class='status' @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QNFT"})'>
                <ColoredCell class='status' :text='f.quantitativeStatus' :backgroundColor='quantitativeStatusColor(f.quantitativeStatus)'/>
              </td>

              <th>Comfort</th>
              <td >
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Comfort"})' class='status' :text='f.comfortStatus' :backgroundColor='statusColor(f.comfortStatus)'/>
              </td>
            </tr>

            <tr>
              <th colspan='2'>Facial Measurements</th>
              <td colspan='2'>
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Comfort"})' class='status' :text='f.facialMeasurementPresence' :backgroundColor='facialMeasPresenceColorMappingStatus(f.facialMeasurementPresence)'/>
              </td>
            </tr>
          </table>



        </div>
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
import { facialMeasurementsPresenceColorMapping, userSealCheckColorMapping, genColorSchemeBounds, getColor, fitFactorColorScheme } from './colors.js'
import ColoredCell from './colored_cell.vue'
import MaskCards from './mask_card.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SortFilterPopup from './sort_filter_popup.vue'
import SearchSortFilterSection from './search_sort_filter_section.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { useManagedUserStore } from './stores/managed_users_store.js';
import { FitTest } from './fit_testing.js';
import { displayableMasks, sortedDisplayableMasks } from './masks.js'

export default {
  name: 'FitTests',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    MaskCards,
    SortFilterPopup,
    SearchSortFilterSection,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      tabToShowOptions: [
        {
          text: "Tested",
        },
        {
          text: "Untested",
        }
      ],
      testedAndUntested: [],
      messages: [],
      masks: [],
      search: "",
      fit_tests: [],
      tabToShow: "Tested",
      managedUserId: undefined,
      showPopup: false,
      sortByField: undefined,
      sortByStatus: undefined,
      filterForEarloop: true,
      filterForHeadstrap: true,
      filterForTargeted: true,
      filterForNotTargeted: true,
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
        useManagedUserStore,
        [
          'managedUsers',
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
    managedUser() {
      if (this.managedId && this.managedUsers.length > 0) {
        return this.managedUsers.filter(function(m) {

          return m.managedId == this.managedId
        }.bind(this))[0]
      } else if (this.managedUsers.length > 0) {
        return this.managedUsers[0]
      }

      return {
        managedId: 0
      }

    },
    untestedDisplayables() {
      return displayableMasks.bind(this)(this.untested)
    },
    sortedDisplayables() {
      return sortedDisplayableMasks.bind(this)(this.untestedDisplayables)
    },
    untested() {
      return this.testedAndUntested.filter(
        function(t) {
          let lowerSearch = this.search.toLowerCase()

          let lowerSearchCriteria = true;

          if (lowerSearch != "") {
            lowerSearchCriteria = t.uniqueInternalModelCode.toLowerCase().match(lowerSearch)
          }

          return ((t.managedId == this.managedUser.managedId)
            && (t.count == 0)
            && lowerSearchCriteria
          )
        }.bind(this)
      )
    },
    displayables() {
      let lowerSearch = this.search.toLowerCase()
      return this.fit_tests.filter(
        function(fit_test) {
          let managedUserIdCriteria = true;
          let lowerSearchCriteria = true;

          if (this.managedId) {
            managedUserIdCriteria = fit_test.userId == this.managedId;
          }

          if (lowerSearch != "") {
            lowerSearchCriteria = fit_test.uniqueInternalModelCode.toLowerCase().match(lowerSearch)
          }

          return lowerSearchCriteria && managedUserIdCriteria
        }.bind(this)
      )
    },
  },
  async created() {
    await this.getCurrentUser()

    let toQuery = this.$route.query


    if (!this.currentUser) {
      signIn.call(this)
    } else {
      // TODO: a parent might input data on behalf of their children.
      // Currently, this.loadStuff() assumes We're loading the profile for the current user
      this.loadStuff()
      if (this.$route.name == 'FitTests' ) {
        if (toQuery['tabToShow']) {
          this.tabToShow = toQuery.tabToShow
        }
        if (toQuery['managedId']) {
          this.managedId = parseInt(toQuery.managedId)
        }
      }
    }


    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (!this.currentUser) {
          signIn.call(this)
        } else {
          // TODO: a parent might input data on behalf of their children.
          // Currently, this.loadStuff() assumes We're loading the profile for the current user
          this.loadStuff()
          if (this.$route.name == 'FitTests' ) {
            if (toQuery['tabToShow']) {
              this.tabToShow = toQuery.tabToShow
            }
            if (toQuery['managedId']) {
              this.managedId = parseInt(toQuery.managedId)
            }
          }
        }

      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    toggleShowPopup(showPopup) {
      this.showPopup = showPopup
    },
    hideSortFilterPopUp() {
      this.showPopup = false
    },
    filterFor(args) {
      this.$router.push(
        {
          name: 'FitTests',
          query: args.query
        }
      )
    },
    updateSearch(search) {
      this.search = search.value
    },
    setManagedUser(event) {
      let query = JSON.parse(JSON.stringify(this.$route.query))

      query = Object.assign(query,
        {
          'managedId': parseInt(event.target.value)
        }
      )

      this.setRouteTo(
        'FitTests',
        this.$route.params,
        query
      )


    },
    showMask(f) {
      if (f && f.maskId) {
        return {name: 'ShowMask', params: { id: f.maskId}}
      }
      return ""
    },
    quantitativeStatusColor(status) {
      let hmff;
      if (status.includes("N")) {
        hmff = parseFloat(status.split(' ')[0])
        return getColor(fitFactorColorScheme, hmff)
      }
    },
    facialMeasPresenceColorMappingStatus(status) {
      let color = facialMeasurementsPresenceColorMapping[status]

      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    statusColor(status) {
      let color = userSealCheckColorMapping[status]
      return `rgb(${color.r}, ${color.g}, ${color.b})`
    },
    setTabTo(opt) {
      let query = JSON.parse(JSON.stringify(this.$route.query))

      let someQuery = Object.assign(query,
        {
          tabToShow: opt.name,
        }
      )

      this.$router.push({
        name: this.$route.name,
        query: someQuery
      })
    },
    setRouteTo(name, params, query) {

      this.$router.push(
        {
          name: name,
          params: params,
          query: query
        }
      )
    },
    userSealCheckPassed() {
      return ftUserSealCheckPassed(this.userSealCheck)
    },
    getAbsoluteHref(href) {
      // TODO: make sure this works for all
      return `${href}`
    },
    newFitTest() {
      this.$router.push(
        {
          name: "NewFitTest",
          query: {
            mode: 'Edit'
          }
        }
      )
    },
    viewMask(id) {
      this.$router.push(
        {
          name: "ViewMask",
          params: {
            id: id
          }
        }
      )
    },
    async loadStuff() {
      // TODO: load the profile for the current user
      await this.loadManagedUsers()
      await this.loadFitTests()
    },
    async loadFitTests() {
      // TODO: make this more flexible so parents can load data of their children
      await axios.get(
        `/fit_tests.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.fit_tests) {
            this.fit_tests = data.fit_tests.map((ft) => new FitTest(ft))
          }
          if (response.data.tested_and_untested) {
            this.testedAndUntested = deepSnakeToCamel(data.tested_and_untested)
          }

          // whatever you want
        })
        .catch(error => {
          this.message = "Failed to load fit tests."
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
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .card {
    cursor: pointer;
    padding: 1em 0;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
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

  select, label {
    margin: 1em;
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

  .thumbnail {
    max-width:10em;
    max-height:10em;
  }

  table th{
    position: sticky;
    top: 0;
    background-color: #eee;
  }

  .status {
    padding: 0.5em;
    min-width: 7em;
    text-align: center;
  }

  tbody tr:hover {
    cursor: pointer;
  }

  .grid {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
  }

  .text-align-center {
    text-align: center;
  }

  .scrollable {
    overflow-y: auto;
    height: 75vh;
    width: 100%;
  }

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
  }

  .padded {
    padding: 0.5em;
  }

  .mobileView {
    display: none;
  }

  @media(max-width: 1450px) {
    #search {
      width: 70vw;
      padding: 1em;
    }

    .status {
      min-width: 3em;
    }

    .mobileView {
      display: flex;
    }

    .desktopView {
      display: none;
    }

    table th {
      position: static;
    }
    img {
      width: 50vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }

    .thumbnail {
      max-height: none;
    }
  }
  @media(max-width: 950px) {
    #search {
      width: 70vw;
      padding: 1em;
    }

    .grid {
      grid-template-columns: 100%;
    }

    .status {
      min-width: 3em;
    }

    .mobileView {
      display: flex;
    }

    .desktopView {
      display: none;
    }

    table th {
      position: static;
    }
    img {
      width: 50vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }

    .thumbnail {
      max-width: 50vw;
      max-height: none;
    }
  }
</style>
