<template>
  <div class='align-items-center'>
    <h2 class='tagline'>{{tagline}}</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <div class='main'>
      <table>
        <tbody>
          <tr>
            <th>Unique Internal Model Code</th>
            <td colspan=2><input class='full-width has-minimal-width' type="text" v-model='uniqueInternalModelCode' :disabled="!createOrEdit"></td>
          </tr>
          <tr>
            <th>Filter type</th>
            <td colspan=2>
              <select
                  v-model="filterType"
                  :disabled="!createOrEdit"
                  >
                  <option>cloth</option>
                  <option>surgical</option>
                  <option>KN95</option>
                  <option>N95</option>
                  <option>N99</option>
                  <option>P100</option>
              </select>
            </td>
          </tr>

          <tr>
            <th>Elastomeric</th>
            <td colspan='2'>
              <select
                  v-model="elastomeric"
                  :disabled="!createOrEdit"
                  >
                  <option>true</option>
                  <option>false</option>
              </select>
            </td>
          </tr>
          <tr v-if='createOrEdit'>
            <th>image URLs</th>
            <td class='justify-content-center' colspan=2>
              <CircularButton text="+" @click="addImageUrl"/>
            </td>
          </tr>
          <tr>
            <th>Image URL</th>
            <th>Image</th>
            <th v-if='userCanEdit'>Delete</th>
          </tr>
          <tr v-for="(imageUrl, index) in imageUrls">

            <td colspan='1'>
              <input class='input-list' type="text" :value='imageUrl' @change="update($event, 'imageUrls', index)"
                  :disabled="!createOrEdit"
              >
            </td>
            <td>
              <img class='preview' :src="imageUrl" :alt="maskImageAlt(index)">
            </td>
            <td class='text-align-center'>
              <CircularButton text="x" @click="deleteImageUrl(index)" v-if='createOrEdit'/>
            </td>
          </tr>
          <tr v-if='createOrEdit'>
            <th>Purchasing URLs</th>
            <td class='justify-content-center' colspan=2>
              <CircularButton text="+" @click="addPurchasingUrl" v-if='createOrEdit'/>
            </td>
          </tr>
          <tr>
            <th colspan='2'>Purchasing URL</th>
            <th v-if='userCanEdit'>Delete</th>
          </tr>
          <tr v-for="(purchasingUrl, index) in whereToBuyUrls" class='text-align-center'>
            <td :colspan='whereToBuyUrlsColspan' >
              <input class='input-list almost-full-width' type="text" :value='purchasingUrl' @change="update($event, 'whereToBuyUrls', index)"
                  v-if="createOrEdit"
              >
              <a :href="purchasingUrl" v-if="!createOrEdit">{{purchasingUrl}}</a>
            </td>
            <td>
              <CircularButton text="x" @click="deletePurchasingUrl(index)" v-if='userCanEdit'/>
            </td>
          </tr>
        </tbody>
      </table>
      <br>

      <div class="row">
        <Button class='button' text="Edit" @click='editMode = true' v-if='!editMode && userCanEdit'/>
        <Button class='button' text="Delete" @click='deleteMask' v-if='deletable && editMode'/>
        <Button class='button' text="Save" @click='saveMask' v-if='createOrEdit && editMode'/>
        <Button class='button' text="Cancel" @click='editMode = false' v-if='createOrEdit && editMode'/>
      </div>
      <br>
      <br>

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
  name: 'AddMask',
  components: {
    Button,
    CircularButton,
    ClosableMessage,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      editMode: false,
      id: null,
      uniqueInternalModelCode: '',
      modifications: {},
      filterType: 'N95',
      elastomeric: false,
      imageUrls: [],
      authorIds: [],
      whereToBuyUrls: [],
      errorMessages: [],
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
    currentUserIsAuthor() {
      return this.authorIds.includes(this.currentUser.id)
    },
    deletable() {
      return !!this.id && this.currentUserIsAuthor
    },
    whereToBuyUrlsColspan() {
      if (this.userCanEdit) {
        return 2
      }
     return 3
    },
    userCanEdit() {
      if (!this.currentUser) {
        return false
      }

      return this.authorIds.includes(this.currentUser.id)
    },
    mode() {
      if (this.$route.params.id) {
        if (this.userCanEdit && this.editMode) {
          return 'Edit'
        } else {
          return 'View'
        }
      } else {
        return 'Create'
      }
    },
    createOrEdit() {
      return (this.mode == 'Create' || this.mode == 'Edit') && this.editMode
    },
    tagline() {
      return `${this.mode} Mask`
    },
    messages() {
      return this.errorMessages;
    },
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    }
    if (this.$route.params.id) {
      this.loadMask()
    }

    this.authorIds = [this.currentUser.id]
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    maskImageAlt(index) {
      return `Image #${index} for ${this.uniqueInternalModelCode}`
    },
    addImageUrl() {
      if (!this.userCanEdit) {
        return
      }
      this.imageUrls.push('')
    },
    addPurchasingUrl() {
      this.whereToBuyUrls.push('')
    },
    deleteImageUrl(index) {
      this.imageUrls.splice(index, 1);
    },
    deletePurchasingUrl(index) {
      this.whereToBuyUrls.splice(index, 1);
    },
    newMask() {
      this.$router.push(
        {
          name: "AddMask"
        }
      )
      this.masks.push(
        {
          unique_internal_model_code: '',
          modifications: {},
          type: '',
          image_urls: [],
          author_ids: [],
          where_to_buy_urls: [],
        }
      )
    },
    async loadStuff() {
      // TODO: load the profile for the current user

    },
    runValidations() {
      if (this.imageUrls.length <= 0) {
        this.errorMessages.push({
          str: "Please provide an image URL so one image can be displayed."
        })
      }
    },
    async loadMask() {
      await axios.get(
        `/masks/${this.$route.params.id}.json`
      )
        .then(response => {
          let data = response.data
          // whatever you want
          let mask = deepSnakeToCamel(data.mask)
          let items = [
            'id',
            'uniqueInternalModelCode',
            'modifications',
            'filterType',
            'elastomeric',
            'imageUrls',
            'whereToBuyUrls',
            'authorIds'
          ]

          for(let item of items) {
            this[item] = mask[item]
          }

        })
        .catch(error => {
          this.messages.push({
            str: "Failed to load mask."
          })
          // whatever you want
        })
    },
    async deleteMask() {
      if (this.$route.params.id) {
        await axios.delete(
          `/masks/${this.$route.params.id}.json`
        )
          .then(response => {
            let data = response.data

            this.$router.push({
              name: 'Masks',
            })
          })
          .catch(error => {
            this.messages.push({
              str: "Failed to delete mask."
            })
          })
      }
    },
    async saveMask() {
      this.runValidations()

      if (this.errorMessages.length > 0) {
        return;
      }

      if (this.$route.params.id) {
        await axios.put(
          `/masks/${this.$route.params.id}.json`, {
            mask: {
              unique_internal_model_code: this.uniqueInternalModelCode,
              modifications: this.modifications,
              filter_type: this.filterType,
              elastomeric: this.elastomeric,
              image_urls: this.imageUrls,
              where_to_buy_urls: this.whereToBuyUrls,
              author_ids: [this.currentUser.id],
            }
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            this.$router.push({
              name: 'Masks',
            })
          })
          .catch(error => {
            this.messages.push({
              str: "Failed to update mask."
            })
          })
      } else {
        // create
        await axios.post(
          `/masks.json`, {
            mask: {
              unique_internal_model_code: this.uniqueInternalModelCode,
              modifications: this.modifications,
              filter_type: this.filterType,
              elastomeric: this.elastomeric,
              image_urls: this.imageUrls,
              where_to_buy_urls: this.whereToBuyUrls,
              author_ids: [this.currentUser.id],
            }
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            this.$router.push({
              name: 'Masks',
            })
          })
          .catch(error => {
            this.messages.push({
              str: "Failed to create mask."
            })
          })
      }
    },
    visitMasks() {
      this.$router.push({
        name: 'Masks',
      })
    },
    update(event, property, index) {
      if (index !== null) {
        this[property][index] = event.target.value
      } else {
        this[property] = event.target.value
      }
    }
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

  .has-minimal-width {
    min-width: 25em;
  }
  .text-for-other {
    margin: 0 1.25em;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .justify-items-center {
    display: flex;
    justify-items: center;
  }

  .almost-full-width {
    width: 90%;
  }
  .full-width {
    width: 100%;
  }
  .input-list {
    margin-left: 6em;
    min-width: 20em;
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

  .row .button {
    width: 100%;
    margin: 1em;
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

  .text-align-center {
    text-align: center;
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

  img.preview {
    max-width:10em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  th, td {
    padding: 0.5em;
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
</style>
