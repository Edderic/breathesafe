<template>
  <div class='align-items-center flex-dir-col'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>Fit Tests</h2>
      <CircularButton text="+" @click="newFitTest"/>
    </div>

    <div class='row'>
      <input type="text" v-model='search'>
      <SearchIcon height='2em' width='2em'/>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>


    <div class='main'>
      <table>
        <thead>
          <th>Image</th>
          <th>Mask</th>
          <th>Created at</th>
          <th>User Seal Check</th>
          <th>QLFT</th>
          <th>QNFT</th>
          <th>Comfort</th>
        </thead>
        <tbody>
          <tr v-for='f in displayables'>
            <td>
              <img :src="f.imageUrls[0]" alt="" class='thumbnail'>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.uniqueInternalModelCode}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Mask"})'>{{f.shortHandCreatedAt}}</td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "User Seal Check"})'>
              <ColoredCell class='status' :text='f.userSealCheckStatus' :backgroundColor='statusColor(f.userSealCheckStatus)'/>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QLFT"})'>
              <ColoredCell class='status' :text='f.qualitativeStatus' :backgroundColor='statusColor(f.qualitativeStatus)'/>
            </td>
            <td class='status' @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "QNFT"})'>
              <ColoredCell class='status' :text='f.quantitativeStatus' :backgroundColor='quantitativeStatusColor(f.quantitativeStatus)'/>
            </td>
            <td @click='setRouteTo("EditFitTest", { id: f.id }, { tabToShow: "Comfort"})'>
              <ColoredCell class='status' :text='f.comfortStatus' :backgroundColor='statusColor(f.comfortStatus)'/>
            </td>
          </tr>
        </tbody>
      </table>

      <h3 class='text-align-center' v-show='fit_tests.length == 0'>No fit tests to show. Use the (+) sign above to add fit testing data.</h3>
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
import { userSealCheckColorMapping, genColorSchemeBounds, getColor, fitFactorColorScheme } from './colors.js'
import ColoredCell from './colored_cell.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SearchIcon from './search_icon.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { FitTest } from './fit_testing.js';

export default {
  name: 'FitTests',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    ColoredCell,
    SearchIcon,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      errorMessages: [],
      masks: [],
      search: "",
      fit_tests: []
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
    displayables() {
      if (this.search == "") {
        return this.fit_tests
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.fit_tests.filter((fit_test) => fit_test.uniqueInternalModelCode.toLowerCase().match(lowerSearch))
      }
    },
    messages() {
      return this.errorMessages;
    },
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      // TODO: a parent might input data on behalf of their children.
      // Currently, this.loadStuff() assumes We're loading the profile for the current user
      this.loadStuff()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    quantitativeStatusColor(status) {
      let hmff;
      if (status.includes("HMFF")) {
        hmff = parseFloat(status.split(' ')[0])
        return getColor(fitFactorColorScheme, hmff)
      }
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
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .card {
    padding: 1em 0;
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
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .thumbnail {
    max-width:10em;
    max-height:10em;
  }

  .text-align-center {
    text-align: center;
  }

  .status {
    padding: 0.5em;
  }
</style>
