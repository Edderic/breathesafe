<template>
  <div class='align-items-center'>
    <h2 class='tagline'>{{tagline}}</h2>
    <div class='container chunk'>
      <ClosableMessage @onclose='errorMessages = []' :messages='messages'/>
      <br>
    </div>

    <TabSet
      :options='tabToShowOptions'
      @update='setRouteTo'
      :tabToShow='tabToShow'
    />

    <div class='main'>
      <table v-if='tabToShow == "Basic Info"'>
        <tbody>
          <tr>
            <th>Unique Internal Model Code</th>
            <td colspan=2>
              <input class='full-width has-minimal-width' type="text" v-model='uniqueInternalModelCode' v-show="createOrEdit">
              <span class='full-width has-minimal-width ' v-show="!createOrEdit">
                {{uniqueInternalModelCode }}
              </span>
            </td>
          </tr>
          <tr v-if='createOrEdit'>
            <th>image URLs</th>
            <td class='justify-content-center' colspan=2>
              <CircularButton text="+" @click="addImageUrl"/>
            </td>
          </tr>
          <tr v-show='createOrEdit'>
            <th>Image URL</th>
            <th>Image</th>
            <th v-if='userCanEdit && editMode'>Delete</th>
          </tr>

          <tr v-show='!createOrEdit' v-for="(imageUrl, index) in imageUrls">
            <td :colspan='3' class='text-align-center'>
              <img class='preview' :src="imageUrl" :alt="maskImageAlt(index)">
            </td>
          </tr>

          <tr v-show='createOrEdit' v-for="(imageUrl, index) in imageUrls">
            <td colspan='1'>
              <input class='input-list' type="text" :value='imageUrl' @change="update($event, 'imageUrls', index)"
                  :disabled="!createOrEdit"
              >
            </td>
            <td :colspan='imagePrevColspan' class='text-align-center'>
              <img class='preview' :src="imageUrl" :alt="maskImageAlt(index)">
            </td>
            <td class='text-align-center' v-if='createOrEdit'>
              <CircularButton text="x" @click="deleteImageUrl(index)" />
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
            <th v-if='userCanEdit && editMode'>Delete</th>
          </tr>
          <tr v-for="(purchasingUrl, index) in whereToBuyUrls" class='text-align-center'>
            <td :colspan='whereToBuyUrlsColspan' >
              <input class='input-list almost-full-width' type="text" :value='purchasingUrl' @change="update($event, 'whereToBuyUrls', index)"
                  v-if="createOrEdit"
              >
              <a :href="purchasingUrl" v-if="!createOrEdit">{{purchasingUrl}}</a>
            </td>
            <td>
              <CircularButton text="x" @click="deletePurchasingUrl(index)" v-if='userCanEdit && editMode'/>
            </td>
          </tr>
          <tr>
            <th>Initial cost (US Dollars)</th>
            <td colspan=1 class='text-align-center'>

              <input type="number"
                v-model='initialCostUsDollars'
                :disabled="!createOrEdit"
              >
            </td>
          </tr>
          <tr>
            <th>Filter change cost (US Dollars)</th>
            <td colspan=1 class='text-align-center'>

              <input type="number"
                v-model='filterChangeCostUsDollars'
                :disabled="!createOrEdit"
              >
            </td>
          </tr>
          <tr>
            <th>Notes</th>
            <td><textarea id="notes" name="notes" cols="30" rows="5" v-model='notes' :disabled=!createOrEdit></textarea></td>
          </tr>

        </tbody>
      </table>

      <table v-if='tabToShow == "Effectiveness"'>
        <tbody>
          <tr>
            <td colspan=3>
              <h3>Filter Media</h3>
            </td>
          </tr>
          <tr>
            <th colspan=2>Filter type</th>
            <td colspan=1 class='text-align-center'>
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

          <tr v-if='createOrEdit'>
            <th>Filtration Efficiencies</th>
            <td class='justify-content-center' colspan=2>
              <CircularButton text="+" @click="addFiltrationEfficiency" v-if='createOrEdit'/>
            </td>
          </tr>
          <tr>
            <th colspan='1'>Filtration Efficiency (Percent)</th>
            <th colspan='1'>Source</th>
            <th class='notes' colspan='1'>Notes</th>
            <th v-if='userCanEdit && editMode'>Delete</th>
          </tr>
          <tr v-for="(f, index) in filtrationEfficiencies" class='text-align-center'>
            <td colspan=1>
              <input type="number" :value='f.filtrationEfficiencyPercent' @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencyPercent')"
                  :disabled="mode != 'Create' && mode != 'Edit'"
              >
            </td>
            <td>
              <input type='text' class='input-list'
                     :value='f.filtrationEfficiencySource'
                     @change="updateArrayOfObj($event, 'filtrationEfficiencies', index, 'filtrationEfficiencySource')"

                     v-show="createOrEdit"
              >
              <a :href="f.filtrationEfficiencySource">link</a>
            </td>
              <td class='notes'>{{f.filtrationEfficiencyNotes}}</td>
            <td>
              <CircularButton text="x" @click="deleteArrayOfObj($event, 'filtrationEfficiencies', index)" v-if='userCanEdit && editMode'/>
            </td>
          </tr>
        </tbody>
      </table>

    <table v-if='tabToShow == "Effectiveness"'>
      <tbody>
        <tr>
          <td colspan='3'>
            <h3>Factors that affect fit</h3>
          </td>
        </tr>
        <tr>
          <th colspan='2'>Style</th>
          <td :colspan='1' class='text-align-center'>
            <select
                v-model="style"
                :disabled="!createOrEdit"
                >
                <option>Bifold</option>
                <option>Bifold &amp; Gasket</option>
                <option>Boat</option>
                <option>Cotton + High Filtration Efficiency Material</option>
                <option>Cup</option>
                <option>Duckbill</option>
                <option>Elastomeric</option>
            </select>
          </td>
        </tr>

        <tr>
          <th colspan='2'>Strap type</th>
          <td colspan='1' class='text-align-center'>
            <select
                v-model="strapType"
                :disabled="!createOrEdit"
                >
                <option>ear loop</option>
                <option>headband</option>
            </select>
          </td>
        </tr>

        </tbody>
      </table>


      <table v-if='tabToShow == "Breatheability"'>
        <tbody>
          <tr v-if='createOrEdit'>
            <th>Pressure drops</th>
            <td class='justify-content-center' colspan=2>
              <CircularButton text="+" @click="addBreathability" v-if='createOrEdit'/>
            </td>
          </tr>
          <tr>
            <th colspan='1'>Pressure Drop (Pascal) under 85 Liters per minute (LPM)</th>
            <th colspan='1'>Source (e.g. URL)</th>
            <th class='notes' colspan='1'>Notes</th>
            <th v-if='userCanEdit && editMode'>Delete</th>
          </tr>
          <tr v-for="(p, index) in breathability" class='text-align-center'>
            <td colspan=1>
              <input type="number" :value='p.breathabilityPascals' @change="updateArrayOfObj($event, 'breathability', index, 'breathabilityPascals')"
                  :disabled="mode != 'Create' && mode != 'Edit'"
              >
            </td>
            <td>
              <input type='text' class='input-list'
                     :value='p.breathabilityPascalsSource'
                     @change="updateArrayOfObj($event, 'breathability', index, 'breathabilitySource')"

                     :disabled="mode != 'Create' && mode != 'Edit'"
              >
            </td>
            <td class='notes'>{{p.breathabilityPascalsNotes}}</td>
            <td>
              <CircularButton text="x" @click="deleteArrayOfObj($event, 'breathability', index)" v-if='userCanEdit && editMode'/>
            </td>
          </tr>
        </tbody>
      </table>

      <table v-if='tabToShow == "Dimensions"'>
        <tbody>
          <tr>
            <th>Mass (grams)</th>
            <td>
              <input type="number" v-model="massGrams" :disabled="!createOrEdit">
            </td>
          </tr>
          <tr>
            <th>Height (mm)</th>
            <td>
              <input type="number" v-model="heightMm" :disabled="!createOrEdit">

            </td>
          </tr>
          <tr>
            <th>Width (mm)</th>
            <td>
              <input type="number" v-model="widthMm" :disabled="!createOrEdit">

            </td>
          </tr>
          <tr>
            <th>Depth (mm)</th>
            <td>
              <input type="number" v-model="depthMm" :disabled="!createOrEdit">
            </td>
          </tr>
        </tbody>
      </table>

      <br>

      <div class="row">
        <Button class='button' text="Edit" @click='editMode = true' v-if='!editMode && userCanEdit'/>
        <Button class='button' text="Delete" @click='deleteMask' v-if='deletable && editMode'/>
        <Button class='button' text="Save" @click='saveMask' v-if='createOrEdit && editMode'/>
        <Button class='button' text="Cancel" @click='handleCancel' v-if='createOrEdit && editMode'/>
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
      notes: '',
      massGrams: 0,
      widthMm: 0,
      heightMm: 0,
      depthMm: 0,
      tabToShow: "Basic Info",
      tabToShowOptions: [
        {
          text: "Basic Info",
        },
        {
          text: "Effectiveness",
        },
        {
          text: "Breatheability",
        },
        {
          text: "Dimensions",
        },
      ],
      initialCostUsDollars: 0,
      hasGasket: false,
      editMode: false,
      id: null,
      uniqueInternalModelCode: '',
      modifications: {},
      filterType: 'N95',
      filtrationEfficiencies: [],
      breathability: [],
      filterChangeCostUsDollars: 0,
      strapType: 'headband',
      style: '',
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
    filtrationEfficienciesRuby() {
      let collection = []
      for(let f of this.filtrationEfficiencies) {
        collection.push({
          'filtration_efficiency_notes': f.filtrationEfficiencyNotes,
          'filtration_efficiency_source': f.filtrationEfficiencySource,
          'filtration_efficiency_percent': f.filtrationEfficiencyPercent
        })

      }

      return collection
    },
    breathabilityRuby() {
      let collection = []
      for(let f of this.breathability) {
        collection.push({
          'breathability_pascals_notes': f.breathabilityPascalsNotes,
          'breathability_pascals_source': f.breathabilityPascalsSource,
          'breathability_pascals': parseFloat(f.breathabilityPascals)
        })

      }

      return collection
    },
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
    sealColspan() {
      if (this.editMode) {
        return 2
      }
     return 1
    },
    imagePrevColspan() {
      if (this.editMode) {
        return 1
      }
     return 2
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
    toSave() {
      return {
        notes: this.notes,
        mass_grams: this.massGrams,
        width_mm: this.widthMm,
        height_mm: this.heightMm,
        depth_mm: this.depthMm,
        unique_internal_model_code: this.uniqueInternalModelCode,
        modifications: this.modifications,
        filter_type: this.filterType,
        filtration_efficiencies: this.filtrationEfficienciesRuby,
        breathability: this.breathabilityRuby,
        filter_change_cost_us_dollars: this.filterChangeCostUsDollars,
        style: this.style,
        image_urls: this.imageUrls,
        where_to_buy_urls: this.whereToBuyUrls,
        author_ids: [this.currentUser.id],
        initial_cost_us_dollars: this.initialCostUsDollars
      }
    }
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    }
    if (this.$route.params.id) {
      this.loadMask()
    } else {
      // must be in creation mode
      this.editMode = true
    }

    // TODO: this should only be done when created
    this.authorIds = [this.currentUser.id]


    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
        if (toQuery['tabToShow'] && (["AddMask", "ViewMask"].includes(this.$route.name))) {
          this.tabToShow = toQuery['tabToShow']
        }
      }
    )

  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    maskImageAlt(index) {
      return `Image #${index} for ${this.uniqueInternalModelCode}`
    },
    addFiltrationEfficiency() {
      this.filtrationEfficiencies.push({
        'filtrationEfficiencyPercent': 1,
        'filtrationEfficiencySource': ''
      })

    },
    addBreathability() {
      this.breathability.push({
        'breathabilityPascals': 0,
        'breathabilitySource': ''
      })

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
    handleCancel() {
      if (this.mode == 'Create') {
        this.$router.push(
          {
            name: "Masks"
          }
        )
      } else {
        this.editMode = false
      }
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
            'massGrams',
            'modifications',
            'filterType',
            'filtrationEfficiencies',
            'breathability',
            'initialCostUsDollars',
            'filterChangeCostUsDollars',
            'elastomeric',
            'notes',
            'imageUrls',
            'whereToBuyUrls',
            'authorIds',
            'strapType',
            'style',
            'widthMm',
            'heightMm',
            'depthMm',
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
            mask: this.toSave
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
            mask: this.toSave
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
    setRouteTo(opt) {
      this.$router.push({
        name: this.$route.name,
        query: {
          tabToShow: opt.name
        }
      })
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
    },
    deleteArrayOfObj(event, property, index) {
      if (index !== null) {
        this[property].splice(index, 1)
      }
    },
    updateArrayOfObj(event, property, index, nestedProp) {
      if (index !== null) {
        this[property][index][nestedProp] = event.target.value
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

  .notes {
    max-width: 20em;
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
    max-width:20em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  th, td {
    padding: 0.5em;
    text-align: center;
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
