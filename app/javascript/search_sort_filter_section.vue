<template>
  <div class='row'>
    <input id='search' type="text" @change='updateSearch'>
    <SearchIcon height='2em' width='2em'/>

    <button class='icon' @click='toggleShowPopup'>
      <svg class='filter-button' xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="8 10 70 70"
                                                                                   width="2em" height="2em"
                                                                                               >
                                                                                               <path d='m 20 20 h 40 l -18 30 v 20 l -4 -2  v -18 z' stroke='black' fill='#aaa'/>
      </svg>

    </button>
  </div>
</template>

<script>
import axios from 'axios';
import Popup from './pop_up.vue'
import { deepSnakeToCamel } from './misc.js'
import SearchIcon from './search_icon.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';


export default {
  name: 'Masks',
  components: {
    Popup,
    SearchIcon,
  },
  data() {
    return {
      filterForEarloop: true,
      filterForHeadstrap: true,
      filterForTargeted: true,
      filterForNotTargeted: true,
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
      search: "",
      sortByField: undefined,
      sortByStatus: 'ascending'
    }
  },
  props: {
    showPopup: {
      default: false
    },
  },
  computed: {
  },
  methods: {
    toggleShowPopup() {
      this.$emit('toggleShowPopup', !this.showPopup)
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

      this.$router.push(
        {
          name: 'Masks',
          query: combinedQuery
        }
      )
    },
    sortingStatus(field) {
      if (this.sortByField == field) {
        return this.sortByStatus
      } else {
        return ''
      }
    },
    updateSearch(event) {
      let newQuery = {
        search: event.target.value
      }

      let combinedQuery = Object.assign(
        JSON.parse(
          JSON.stringify(this.$route.query)
        ),
        newQuery
      )

      this.$emit('updateSearch', { query: combinedQuery })
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

