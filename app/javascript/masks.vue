<template>
  <div class='align-items-center'>
    <h2 class='tagline'>Masks</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <CircularButton text="+" @click="newMask"/>

    <div class='main'>
      <table>
        <thead>
          <tr >
            <th>Image</th>
            <th>Unique Model Code</th>
            <th>Filter Type</th>
            <th>Elastomeric</th>
            <th>Purchasing URLs</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for='m in masks' @click='viewMask(m.id)'>
            <td>
              <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
            </td>
            <td>{{m.uniqueInternalModelCode}}</td>
            <td>{{m.filterType}}</td>
            <td>{{m.elastomeric}}</td>
            <td>
              <ul>
                <li v-for='w in m.whereToBuyUrls'>
                  <a :href="getAbsoluteHref(w)" target='_blank'>{{w}}</a>
                </li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel } from './misc.js'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'Masks',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      errorMessages: [],
      masks: []
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
    getAbsoluteHref(href) {
      return `//${href}`
    },
    newMask() {
      this.$router.push(
        {
          name: "AddMask"
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
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
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

  .row button {
    width: 100%;
    padding-top: 1em;
    padding-bottom: 1em;
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
    flex-direction: column;
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

  .centered {
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
</style>
