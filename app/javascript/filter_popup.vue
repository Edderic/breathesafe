<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>Sort by:</h3>
      <table class='sort-table'>
        <thead>
          <tr>
            <th>field</th>
            <th>status</th>
          </tr>
        </thead>
        <tbody>
          <tr @click='sortBy("probaFit")'>
            <th >Probability of Fit</th>
            <td>
              <SortingStatus :status='sortingStatus("probaFit")'/>
            </td>
          </tr>
          <tr @click='sortBy("uniqueFitTestersCount")' v-if='showUniqueNumberFitTesters'>
            <th ># testers</th>
            <td>
              <SortingStatus :status='sortingStatus("uniqueFitTestersCount")'/>
            </td>
          </tr>
          <tr @click='sortBy("perimeterMm")'>
            <th >Perimeter</th>
            <td>
              <SortingStatus :status='sortingStatus("perimeterMm")'/>
            </td>
          </tr>
        </tbody>
      </table>
      <br>

      <h3>Filter for:</h3>
      <br v-if='showTargetedOptions'>
      <div v-if='showTargetedOptions'>Targeted Masks (for Testers)</div>
      <table v-if='showTargetedOptions'>
        <tr>
          <td><input id='targeted' type="checkbox" :checked='filterForTargeted' @click='filterFor("Targeted")'><label for="targeted">Targeted</label></td>
          <td><input id='not_targeted' type="checkbox" :checked='filterForNotTargeted' @click='filterFor("NotTargeted")'><label for="not_targeted">Not Targeted</label></td>
        </tr>
      </table>

      <br>
      <div>Strap type</div>
      <table>
        <tr class='checkboxes'>
          <td><input id='toggleAdjustableEarloop' type="checkbox" :checked='filterForAdjustableEarloop' @click='filterFor("AdjustableEarloop")'>
            <label for="toggleAdjustableEarloop">Adjustable Earloop</label>
          </td>
          <td><input id='toggleEarloop' type="checkbox" :checked='filterForEarloop' @click='filterFor("Earloop")'>
            <label for="toggleEarloop">Earloop</label>
          </td>
          <td><input id='toggleAdjustableHeadstrap' type="checkbox" :checked='filterForAdjustableHeadstrap' @click='filterFor("AdjustableHeadstrap")'>
            <label for="toggleAdjustableHeadstrap">Adjustable Headstrap</label>
          </td>
          <td><input id='toggleHeadstrap' type="checkbox" :checked='filterForHeadstrap' @click='filterFor("Headstrap")'>
            <label for="toggleHeadstrap">
            Headstrap
            </label>
          </td>
        </tr>
      </table>


    </div>
  </Popup>
  </div>
</template>

<script>
import axios from 'axios';
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel } from './misc.js'
import SortingStatus from './sorting_status.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'


export default {
  name: 'SortFilterPopup',
  components: {
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
    showFitTesting: {
      default: false
    },
    showUniqueNumberFitTesters: {
      default: true
    },
    showTargetedOptions: {
      default: true
    },
    sortByField: {
      default: undefined
    },
    sortByStatus: {
      default: 'ascending'
    },
    showPopup: {
      default: false
    },
    filterForAdjustableHeadstrap: {
      default: true
    },
    filterForAdjustableEarloop: {
      default: true
    },
    filterForEarloop: {
      default: true
    },
    filterForHeadstrap: {
      default: true
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
    hidePopup() {
      this.$emit('hidePopUp')
    },
    updateFacialMeasurement(event, key) {
      this.$emit('updateFacialMeasurement', event, key)
    },
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

      this.$emit('filterFor', {
        query: combinedQuery
      })
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

  tr.checkboxes td {
    display: flex;
    flex-direction: row;
  }

  .sort-table {
    width: 20em;
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
