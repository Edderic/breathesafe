<template>
  <div class='align-items-center flex-dir-col'>

    <div class='header-section'>
      <div class='flex align-items-center row'>
        <h2 class='tagline'>Fit Tests</h2>
        <CircularButton text="+" @click="newFitTest"/>
        <CircularButton text="⬆" @click="importFitTests" class="import-button"/>
      </div>


      <div class='row'>
        <label >By:</label>
        <select :value="managedId" @change='setManagedUser'>
          <option v-for='m in uniqueManagedUsers' :key="m.managedId" :value="m.managedId">{{m.firstName + ' ' + m.lastName}}</option>
        </select>
      </div>

      <SearchSortFilterSection
          @updateSearch='filterFor'
          @toggleShowPopup='toggleShowPopup'
          @filterFor='filterFor'
          :filterForColor='filterForColor'
          :filterForStrapType='filterForStrapType'
          :filterForStyle='filterForStyle'
          />
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <!-- Actions menu for fit test -->
    <div v-if='selectedFitTestForActions' :key='actionsMenuKey' class='actions-menu-container' @click.self='closeActionsMenu'>
      <div class='actions-menu-wrapper' @click.stop>
        <CircularButton @click='closeActionsMenu' class='close-actions' text='x'/>
        <div class='actions-menu-content'>
          <table class='actions-table' v-if='selectedFitTestForActions'>
            <tr>
              <th>Tester</th>
              <td>{{selectedFitTestForActions.firstName + ' ' + selectedFitTestForActions.lastName}}</td>
            </tr>
            <tr>
              <th>Image</th>
              <td>
                <img v-if='selectedFitTestForActions.imageUrls && selectedFitTestForActions.imageUrls[0]'
                     :src="selectedFitTestForActions.imageUrls[0]"
                     alt=""
                     class='thumbnail-small'>
                <span v-else>No image</span>
              </td>
            </tr>
            <tr>
              <th>Mask</th>
              <td>{{selectedFitTestForActions.uniqueInternalModelCode}}</td>
            </tr>
            <tr>
              <th>Created at</th>
              <td>{{selectedFitTestForActions.shortHandCreatedAt}}</td>
            </tr>
          </table>
          <div class='actions-buttons'>
            <Button text='Clone' @click='cloneFitTest'/>
            <Button text='Delete' @click='confirmDelete'/>
          </div>
          <div v-if='deleteConfirmation' class='delete-confirmation'>
            <p>Are you sure you want to delete this fit test?</p>
            <div class='confirmation-buttons'>
              <Button text='Delete' @click='deleteFitTest'/>
              <Button text='Cancel' @click='cancelDelete'/>
            </div>
          </div>
          <ClosableMessage v-if='actionMenuMessages && actionMenuMessages.length > 0' @onclose='actionMenuMessages = []' :messages='actionMenuMessages'/>
        </div>
      </div>
    </div>

    <div class='main scrollable desktopView'>
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
          <th>Actions</th>
        </thead>
        <tbody>
          <tr v-for='f in sortedFitTests' :key='f.id'>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.firstName + ' ' + f.lastName}}</td>
            <td>
              <router-link :to="showMask(f)">
                <img :src="f.imageUrls[0]" alt="" class='thumbnail'>
              </router-link>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.uniqueInternalModelCode}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.shortHandCreatedAt}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{getBeardLength(f)}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
              <ColoredCell class='status' :text='f.userSealCheckStatus' :backgroundColor='statusColor(f.userSealCheckStatus)'/>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
              <ColoredCell class='status' :text='f.qualitativeStatus' :backgroundColor='statusColor(f.qualitativeStatus)'/>
            </td>
            <td class='status' @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
              <ColoredCell class='status' :text='f.quantitativeStatus' :backgroundColor='quantitativeStatusColor(f.quantitativeStatus)'/>
            </td>
            <td >
              <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, {})' class='status' :text='f.comfortStatus' :backgroundColor='statusColor(f.comfortStatus)'/>
            </td>
              <td >
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, {})' class='status' :text='f.facialMeasurementPresence' :backgroundColor='facialMeasPresenceColorMappingStatus(f.facialMeasurementPresence)'/>
              </td>
            <td @click.stop>
              <CircularButton @click.stop='showActions(f.id)' class='gear-button'>

              <svg
                viewBox="0 0 100 100"
                xmlns="http://www.w3.org/2000/svg"
                role="img"
                aria-label="Gear icon"
                class='gear'
              >
                <!-- Gear body & teeth use currentColor so you can tint via CSS -->
                <g fill="currentColor">
                  <!-- Main gear body -->
                  <circle cx="50" cy="50" r="30" />

                  <!-- Six teeth -->
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2" />
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
                        transform="rotate(60 50 50)" />
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
                        transform="rotate(120 50 50)" />
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
                        transform="rotate(180 50 50)" />
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
                        transform="rotate(240 50 50)" />
                  <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
                        transform="rotate(300 50 50)" />

                  <!-- Inner ring -->
                  <circle cx="50" cy="50" r="14" fill="none" stroke="currentColor" stroke-width="6" />
                </g>
              </svg>
              </CircularButton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class='main scrollable mobileView'>
      <div class='grid'>
        <div v-for='f in sortedFitTests' class='card'>
          <table>
            <tr>
              <td rowspan='2' colspan='2'>
                <router-link :to="showMask(f)">
                  <img :src="f.imageUrls[0]" alt="" class='thumbnail'>
                </router-link>
              </td>
              <th>Tester</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.firstName + ' ' + f.lastName}}</td>
            </tr>
            <tr>
              <th>Mask</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.uniqueInternalModelCode}}</td>
            </tr>

            <tr>
              <th>Created at</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{f.shortHandCreatedAt}}</td>
              <th>Beard length</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>{{getBeardLength(f)}}</td>
            </tr>

            <tr>
              <th>User Seal Check</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
                <ColoredCell class='status' :text='f.userSealCheckStatus' :backgroundColor='statusColor(f.userSealCheckStatus)'/>
              </td>
              <th>QLFT</th>
              <td @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
                <ColoredCell class='status' :text='f.qualitativeStatus' :backgroundColor='statusColor(f.qualitativeStatus)'/>
              </td>
            </tr>

            <tr>
              <th>QNFT</th>
              <td class='status' @click='setRouteTo("EditFitTest", { id: f.id }, {})'>
                <ColoredCell class='status' :text='f.quantitativeStatus' :backgroundColor='quantitativeStatusColor(f.quantitativeStatus)'/>
              </td>

              <th>Comfort</th>
              <td >
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, {})' class='status' :text='f.comfortStatus' :backgroundColor='statusColor(f.comfortStatus)'/>
              </td>
            </tr>

            <tr>
              <th colspan='2'>Facial Measurements</th>
              <td colspan='2'>
                <ColoredCell @click='setRouteTo("EditFitTest", { id: f.id }, {})' class='status' :text='f.facialMeasurementPresence' :backgroundColor='facialMeasPresenceColorMappingStatus(f.facialMeasurementPresence)'/>
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
import { deepSnakeToCamel, setupCSRF } from './misc.js'
// import SortFilterPopup from './sort_filter_popup.vue'
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
    // SortFilterPopup,
    SearchSortFilterSection,
    SurveyQuestion,
  },
  data() {
    return {
      managedId: 0,
      messages: [],
      masks: [],
      search: "",
      fit_tests: [],
      showPopup: false,
      sortByField: undefined,
      sortByStatus: undefined,
      filterForColor: "none",
      filterForStrapType: "none",
      filterForStyle: "none",
      filterForTargeted: true,
      filterForNotTargeted: true,
      selectedFitTestForActions: null,
      deleteConfirmation: false,
      actionMenuMessages: [],
      actionsMenuKey: 0
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
        useManagedUserStore,
        [
          'managedUsers',
        ]
    ),
    uniqueManagedUsers() {
      const seen = new Set()
      return this.managedUsers.filter(m => {
        if (seen.has(m.managedId)) {
          return false
        }
        seen.add(m.managedId)
        return true
      })
    },
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
    displayables() {
      let lowerSearch = this.search.toLowerCase()


      let displayable_fit_tests = displayableMasks.bind(this)(this.fit_tests)

      let results = displayable_fit_tests.filter(
        function(fit_test) {
          let managedUserIdCriteria = true;
          let lowerSearchCriteria = true;

          if (this.managedId) {
            managedUserIdCriteria = (fit_test.userId == this.managedId);
          }

          if (lowerSearch != "") {
            lowerSearchCriteria = fit_test.uniqueInternalModelCode.toLowerCase().match(lowerSearch)
          }

          return lowerSearchCriteria && managedUserIdCriteria
        }.bind(this)
      )

      return results

    },
    sortedFitTests() {
      return sortedDisplayableMasks.bind(this)(this.displayables)
    }
  },
  async created() {
    await this.getCurrentUser()

    let toQuery = this.$route.query

    await this.loadWatch(toQuery, {})

    this.$watch(
      () => this.$route.query,
      this.loadWatch
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'setWaiting']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    getBeardLength(fitTest) {
      if (!fitTest || !fitTest.facialHair || Object.keys(fitTest.facialHair).length === 0) {
        return 'N/A'
      }
      // Check both camelCase (after deepSnakeToCamel) and snake_case (original) versions
      const facialHair = fitTest.facialHair
      const beardLength = facialHair.beardLengthMm || facialHair.beard_length_mm
      return beardLength || 'N/A'
    },
    showActions(fitTestId) {
      const fitTest = this.fit_tests.find(f => f.id === fitTestId)
      if (fitTest) {
        this.deleteConfirmation = false
        this.actionMenuMessages = []
        // Create a new object reference to ensure Vue detects the change
        // Copy all properties to a new object
        this.selectedFitTestForActions = Object.assign({}, fitTest)
        // Increment key to force re-render
        this.actionsMenuKey += 1
      }
    },
    closeActionsMenu() {
      this.selectedFitTestForActions = null
      this.deleteConfirmation = false
      this.actionMenuMessages = []
    },
    async cloneFitTest() {
      if (!this.selectedFitTestForActions) return

      try {
        const response = await axios.post(
          `/fit_tests/${this.selectedFitTestForActions.id}/clone`,
          {},
          { headers: { 'Content-Type': 'application/json' } }
        )

        if (response.status === 201) {
          this.actionMenuMessages = [{ str: 'Fit test cloned successfully!' }]
          this.closeActionsMenu()
          // Refresh the table
          await this.loadFitTests()
        } else {
          this.actionMenuMessages = [{ str: 'Failed to clone fit test.' }]
        }
      } catch (error) {
        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to clone fit test.'
        this.actionMenuMessages = [{ str: errorMsg }]
      }
    },
    confirmDelete() {
      this.deleteConfirmation = true
      this.actionMenuMessages = []
    },
    cancelDelete() {
      this.deleteConfirmation = false
      this.actionMenuMessages = []
    },
    async deleteFitTest() {
      if (!this.selectedFitTestForActions) return

      try {
        const response = await axios.delete(
          `/fit_tests/${this.selectedFitTestForActions.id}`
        )

        if (response.status === 200) {
          this.actionMenuMessages = [{ str: 'Fit test deleted successfully!' }]
          this.closeActionsMenu()
          // Refresh the table
          await this.loadFitTests()
        } else {
          this.actionMenuMessages = [{ str: 'Failed to delete fit test.' }]
        }
      } catch (error) {
        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to delete fit test.'
        this.actionMenuMessages = [{ str: errorMsg }]
      }
    },
    async loadWatch(toQuery, fromQuery) {
      if (this.$route.name == 'FitTests' ) {
        if (!this.currentUser) {
          signIn.call(this)
        } else {
          await this.loadStuff()
          if (toQuery['managedId']) {
            this.managedId = parseInt(toQuery.managedId)
          }

          // setup search, filtering, sorting variables
          // TODO: might be better off that this is in some function for reusability purposes
          this.search = this.$route.query.search || ''
          this.sortByStatus = this.$route.query.sortByStatus

          this.sortByField = this.$route.query.sortByField

          this.filterForColor = toQuery['filterForColor'] || 'none'
          this.filterForStrapType = toQuery['filterForStrapType'] || 'none'
          this.filterForStyle = toQuery['filterForStyle'] || 'none'
        }
      }
    },
    newFitTestForUser(args) {
      this.$router.push(
        {
          name: "NewFitTest",
          query: args
        }
      )
    },
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
    importFitTests() {
      this.$router.push(
        {
          name: "NewBulkFitTestsImport"
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

  .flex-dir-row {
    display: flex;
    flex-direction: row;
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
    height: 80vh;
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

  .header-section {
    display: flex;
    flex-direction: row;
    align-items: center;
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

  @media(max-width: 700px) {
    .header-section {
      flex-direction: column;
    }

    .search-section {
      width: 90vw;
    }
  }

  .actions-menu-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .actions-menu-wrapper {
    position: relative;
    background-color: #ffffd6;
    border-radius: 8px;
    padding: 1em;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }

  .close-actions {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 10;
  }

  .actions-menu-content {
    padding: 1em;
  }

  .actions-table {
    width: 100%;
    margin-bottom: 1em;
  }

  .actions-table th {
    text-align: left;
    padding-right: 1em;
    font-weight: bold;
  }

  .actions-table td {
    padding: 0.5em;
  }

  .thumbnail-small {
    max-width: 100px;
    max-height: 100px;
    object-fit: contain;
  }

  .actions-buttons {
    display: flex;
    gap: 1em;
    margin-top: 1em;
  }

  .actions-buttons .button {
    display: flex;
    width:45%;
    align-items: center;
    justify-content: center;
  }

  .delete-confirmation {
    margin-top: 1em;
    padding: 1em;
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 4px;
  }

  .delete-confirmation p {
    margin-bottom: 1em;
  }

  .confirmation-buttons {
    display: flex;
    gap: 1em;
  }

  .gear-button svg {
    display: block;
    margin: 0 auto;
    color: #80808080;
  }

  .import-button {
    margin-left: 0.5em;
    margin-right: 0.5em;
  }

</style>
