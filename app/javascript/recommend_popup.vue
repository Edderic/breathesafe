<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>{{title}}:</h3>
      <p>{{explanation}}</p>
      <table>
        <thead>
          <tr>
            <th></th>
            <th></th>
            <th></th>
          </tr>
        </thead>
        <tbody v-if='explanationToShow == ""'>
          <tr v-for='(value, key, index) in facialMeasurements'>
            <th  v-if='value.use_for_recommender'>{{value.eng}}</th>
            <td v-if='value.use_for_recommender'>
              <CircularButton text='?' @click='show(key)'/>
            </td>
            <td v-if='value.use_for_recommender'>
              <input class='num' type="number" :value='getFacialMeasurement(key)' @change="update($event, key)">
            </td>
          </tr>
        </tbody>
      </table>
      <br>

      <div class='explanation justify-content-center' v-if='explanationToShow != ""'>
        <h2>
          {{engToShow}}
        </h2>
        <div>
          <img :src="imageToShow" alt="">
        </div>
        <p>
            {{explanationToShow}}
        </p>
      </div>

      <div class='justify-content-center'>
        <Button v-if='!hideButton && keyToShow == ""' :shadow='true' @click="recommend">{{title}}</Button>
        <Button v-if='keyToShow != ""' :shadow='true' @click="keyToShow = ''">Back</Button>
      </div>
    </div>
  </Popup>
  </div>
</template>

<script>
import axios from 'axios';
import CircularButton from './circular_button.vue'
import Button from './button.vue'
import PersonIcon from './person_icon.vue'
import Popup from './pop_up.vue'
import { deepSnakeToCamel } from './misc.js'
import { getFacialMeasurements } from './facial_measurements.js'
import SortingStatus from './sorting_status.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'
import { useFacialMeasurementStore } from './stores/facial_measurement_store'


export default {
  name: 'RecommendPopup',
  components: {
    Button,
    CircularButton,
    Popup,
    PersonIcon,
    SortingStatus
  },
  data() {
    return {
      search: "",
      keyToShow: ""
    }
  },
  props: {
    hideButton: {
      default: false
    },
    title: {
      default: 'Recommend'
    },

    explanation: {
      default: ''
    },
    showPopup: {
      default: false
    },
  },
  computed: {
    facialMeasurements() {
      return getFacialMeasurements()
    },
    explanationToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['explanation']
    },
    imageToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['image_url']
    },
    engToShow() {
      if (!this.keyToShow) {
        return ""
      }
      return this.facialMeasurements[this.keyToShow]['eng']
    }
  },
  async created() {
    this.load(this.$route.query, {})
    this.$watch(
      () => this.$route.query,
      (toQuery, fromQuery) => {
          this.load.bind(this)
      }
    )
  },
  methods: {
    ...mapActions(useFacialMeasurementStore, ['getFacialMeasurement', 'updateFacialMeasurement']),
    load(toQuery, fromQuery) {
      for (let facialMeasurement in this.facialMeasurements) {
        if (toQuery[facialMeasurement]) {
          this.updateFacialMeasurement(facialMeasurement, toQuery[facialMeasurement])
        }
      }
    },
    show(key) {
      this.keyToShow = key
    },
    hidePopup() {
      this.$emit('hidePopUp', true)
    },
    update(event, key) {
      this.$emit('updateFacialMeasurement', event, key)
      this.updateFacialMeasurement(key, event.target.value)
    },
    recommend() {
      let event = {
        target: {
          value: this.facialMeasurements.bitragionSubnasaleArcMm.value
        }
      }

      this.$emit(
        'updateFacialMeasurement',
        event,
        'bitragionSubnasaleArcMm'
      )
    }
  }
}
</script>

<style scoped>
  button {
    display: flex;
    cursor: pointer;
    padding: 0.25em;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }

  .explanation {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  p {
    margin: 1em;
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

  tbody tr:hover {
    cursor: pointer;
    background-color: rgb(230,230,230);
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

  @media(max-width: 700px) {
    #search {
      width: 70vw;
      padding: 1em;
    }
  }

</style>


