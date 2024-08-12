<template>
  <div class='align-items-center flex-dir-col'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>{{pageTitle}}</h2>
    </div>


    <div class='menu row'>
      <TabSet
        :options='tabToShowOptions'
        @update='setRouteTo'
        :tabToShow='tabToShow'
      />
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <div v-show='tabToShow == "Mask"'>
      <h3 class='text-align-center'>Search for and pick a mask</h3>

      <div class='row justify-content-center'>
        <input type="text" @change='updateSearch'>
        <SearchIcon height='2em' width='2em'/>
      </div>


      <div :class='{main: true, grid: true, selectedMask: maskHasBeenSelected}'>
        <div class='card flex flex-dir-col align-items-center justify-content-center' v-for='m in selectDisplayables' @click='selectMask(m.id)'>
          <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
          <div class='description'>
            <span>
              {{m.uniqueInternalModelCode}}
            </span>
          </div>
        </div>
      </div>

      <table>
        <tbody>
          <tr>
            <th>Selected Mask</th>
            <td>{{selectedMask.uniqueInternalModelCode}}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-show='tabToShow == "Comfort"' class='justify-content-center flex-dir-col'>
      <table>
        <tbody>
          <tr>
            <th>Selected Mask</th>
            <td>{{selectedMask.uniqueInternalModelCode}}</td>
          </tr>
        </tbody>
      </table>

      <SurveyQuestion
        question="How comfortable is the position of the mask on the nose?"
        :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
        @update="selectComfortNose"
        :selected="comfort['How comfortable is the position of the mask on the nose?']"
      />

      <SurveyQuestion
        question="Is there adequate room for eye protection?"
        :answer_options="['Inadequate', 'Adequate', 'Not applicable']"
        @update="selectComfortEyeProtection"
        :selected="comfort['Is there adequate room for eye protection?']"
      />

      <SurveyQuestion
        question="Is there enough room to talk?"
        :answer_options="['Not enough', 'Unsure', 'Enough']"
        @update="selectComfortEnoughRoomToTalk"
        :selected="comfort['Is there enough room to talk?']"
      />

      <SurveyQuestion
        question="How comfortable is the position of the mask on face and cheeks?"
        :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
        @update="selectComfortFaceAndCheeks"
        :selected="comfort['How comfortable is the position of the mask on face and cheeks?']"
      />
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
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SearchIcon from './search_icon.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'FitTest',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SearchIcon,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      tabToShow: 'Mask',
      tabToShowOptions: [
        {
          text: "Mask",
        },
        {
          text: "Comfort",
        },
        {
          text: "User Seal Checks"
        },
        {
          text: "Fit Testing"
        }
      ],
      errorMessages: [],
      masks: [],
      selectedMask: {},
      comfort: {
        "How comfortable is the position of the mask on the nose?": null,
        "Is there adequate room for eye protection?": null,
        "Is there enough room to talk?": null,
        "How comfortable is the position of the mask on face and cheeks?": null
      },
      search: ""
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
    maskHasBeenSelected() {
      return 'id' in this.selectedMask
    },
    pageTitle() {
      if (this.$route.name == 'NewFitTest') {
        return "Add New Fit Testing"
      }
    },
    displayables() {
      if (this.search == "") {
        return this.masks
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.masks.filter((mask) => mask.uniqueInternalModelCode.toLowerCase().match(lowerSearch))
      }
    },
    selectDisplayables() {
      let lengthToDisplay = 6
      if (this.displayables.length < 6) {
        lengthToDisplay = this.displayables.length
      }

      return this.displayables.slice(0, lengthToDisplay)
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

    let toQuery = this.$route.query

    if (toQuery['tabToShow'] && (this.$route.name == "NewFitTest")) {
      this.tabToShow = toQuery['tabToShow']
    }

    // TODO: add param watchers
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && (this.$route.name == "NewFitTest")) {
          this.tabToShow = toQuery['tabToShow']
        }
      }
    )
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    updateSearch(event) {
      this.selectedMask = {}
      this.search = event.target.value
    },
    getAbsoluteHref(href) {
      // TODO: make sure this works for all
      return `${href}`
    },
    newFitTest() {
      this.$router.push(
        {
          name: "AddFitTest"
        }
      )
    },
    selectMask(id) {
      this.selectedMask = this.masks.filter((m) => m.id == id)[0]
      this.search = this.selectedMask.uniqueInternalModelCode
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

    selectComfortNose(value) {
      this['comfort']['How comfortable is the position of the mask on the nose?'] = value
    },
    selectComfortEyeProtection(value) {
      this['comfort']['Is there adequate room for eye protection?'] = value
    },
    selectComfortEnoughRoomToTalk(value) {
      this['comfort']['Is there enough room to talk?'] = value
    },
    selectComfortFaceAndCheeks(value) {
      this['comfort']['How comfortable is the position of the mask on face and cheeks?'] = value
    },
    selectGeneralComfort(value) {
      this['comfort']['How comfortable is this mask/respirator?'] = value
    },
    setRouteTo(opt) {
      this.$router.push({
        name: "NewFitTest",
        query: {
          tabToShow: opt.name
        }
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

  .card:hover {
    cursor: pointer;
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

  .main, .grid.selectedMask {
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

  .text-align-center {
    text-align: center;
  }
</style>
