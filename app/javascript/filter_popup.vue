<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>Filter for:</h3>
      <div class='wide'>
        <div>
          <div>Color</div>
          <span v-for='opt in colorOptions' class='filterCheckbox' >
            <Circle :color='opt' :selected='["none", opt].includes(filterForColor)' :for='`color${opt}`' @click='filterFor("Color", opt)'/>
          </span>
          <br>
        </div>

        <div>
          <div>Strap type</div>
          <table>
            <tr class='options'>
              <td v-for='opt in strapTypes'>
                <input :id='`toggle${opt}`' type="radio" :checked='filterForStrapType == opt' @click='filterFor("StrapType", opt)'>
                <label :for='`toggle${opt}`'>{{opt}}</label>
              </td>
            </tr>
          </table>
          <br v-if='showTargetedOptions'>
        </div>
      </div>
      <div v-if='showTargetedOptions'>Targeted Masks (for Testers)</div>
      <table v-if='showTargetedOptions'>
        <tr>
          <td><input id='targeted' type="checkbox" :checked='filterForTargeted' @click='filterFor("Targeted")'><label for="targeted">Targeted</label></td>
          <td><input id='not_targeted' type="checkbox" :checked='filterForNotTargeted' @click='filterFor("NotTargeted")'><label for="not_targeted">Not Targeted</label></td>
        </tr>
      </table>

      <br>


    </div>
  </Popup>
  </div>
</template>

<script>
import axios from 'axios';
import Circle from './circle.vue'
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel } from './misc.js'
import SortingStatus from './sorting_status.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'


export default {
  name: 'FilterPopup',
  components: {
    Circle,
    Popup,
    PersonIcon,
    SortingStatus
  },
  data() {
    return {
      search: "",
    }
  },
  props: {
    colorOptions: {
      default: []
    },
    strapTypes: {
      default: []
    },
    showFitTesting: {
      default: false
    },
    showUniqueNumberFitTesters: {
      default: true
    },
    showTargetedOptions: {
      default: true
    },
    showPopup: {
      default: false
    },
    filterForColor: {
      default: "none"
    },
    filterForStrapType: {
      default: "none"
    },
    filterForTargeted: {
      default: true
    },
    filterForNotTargeted: {
      default: true
    },
  },
  computed: {
  },
  async created() {
  },
  methods: {
    isChecked(namespace, opt) {
      return this['filterFor' + namespace] == opt
    },
    hidePopup() {
      this.$emit('hidePopUp')
    },
    updateFacialMeasurement(event, key) {
      this.$emit('updateFacialMeasurement', event, key)
    },
    filterFor(namespace, string) {
      let filterForString = ('filterFor' + namespace)
      let newQuery = {}
      if (this[filterForString] == string) {
        // remove the filtering
        // if array
        newQuery[filterForString] = 'none'
      } else {
        newQuery[filterForString] = string
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      this.$emit('filterFor', {
        query: combinedQuery
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

  ul li {
    list-style-type: none;
  }

  .colorLabel {
    margin-left: 1em;
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

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
    overflow-y: auto;
    height: 75vh;
  }

  .targeted {
    padding-left: 5em;
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
  }
  .sticky {
    position: fixed;
    top: 3em;
  }

  th, td {
    text-align: center;
  }

  .num {
    width: 3em;
  }

  tr.options td, .filterCheckbox {
    display: flex;
    flex-direction: row;
  }

  .options:hover {
    cursor: pointer;
  }

  .sort-table {
    width: 20em;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 50% 50%;
    }
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
    .grid {
      grid-template-columns: 100%;
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

    .targeted {
      padding-left: 50vw;
    }

    .main {
      overflow: auto;
      height: 65vh;
    }
  }

</style>
