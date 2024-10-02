<template>
  <div class='align-items-center flex-dir-col sticky'>
    <div class='flex align-items-center row'>
      <h2 class='tagline'>Masks</h2>
      <CircularButton text="+" @click="newMask" v-show="currentUser"/>
    </div>

    <div class='row'>
      <input type="text" v-model='search'>
      <SearchIcon height='2em' width='2em'/>

      <button id='search-icon'>
        <svg class='filter-button' xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80"
          width="2em" height="2em"
          @click='setDisplay("filter")' v-if="display != 'filter'">
          <path d='m 20 20 h 40 l -18 30 v 20 l -4 -2  v -18 z' stroke='black' fill='#aaa'/>
        </svg>
      </button>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>




    <div class='main grid'>
      <div class='card flex flex-dir-col align-items-center justify-content-center' v-for='m in displayables' @click='viewMask(m.id)'>
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
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SearchIcon from './search_icon.vue'
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
    PersonIcon,
    SearchIcon,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
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

    perimColorScheme() {
      return perimeterColorScheme()
    },
    displayables() {
      if (this.search == "") {
        return this.masks
      } else {
        let lowerSearch = this.search.toLowerCase()
        return this.masks.filter((mask) => mask.uniqueInternalModelCode.toLowerCase().match(lowerSearch))
      }
    },
    messages() {
      return this.errorMessages;
    },
  },
  async created() {
    // TODO: a parent might input data on behalf of their children.
    // Currently, this.loadStuff() assumes We're loading the profile for the current user
    this.loadStuff()
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
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
</style>
