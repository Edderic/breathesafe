<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>Recommend:</h3>
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
            <th>{{value.eng}}</th>
            <td>
              <CircularButton text='?' @click='show(key)'/>
            </td>
            <td>
              <input class='num' type="number" :value='value.value' @change="updateFacialMeasurement($event, key)">
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
        <Button v-if='keyToShow == ""' :shadow='true' @click="recommend">Recommend</Button>
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
import SortingStatus from './sorting_status.vue'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';
import { Respirator, displayableMasks, sortedDisplayableMasks } from './masks.js'


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
    facialMeasurements: {
      default: {
        'bitragionSubnasaleArcMm': {
          'eng': "Bitragion subnasale arc (mm)",
          'value': 220,
          'explanation': "The surface distance between the left and right tragion landmarks across the subnasale landmark at the bottom of the nose",
          'image_url': "https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g30003.jpg"
        },
        'faceWidthMm': {
          'eng': "Face width (mm)",
          'value': 155,
          'explanation': "",
          'image_url': ''
        },
        'noseProtrusionMm': {
          'eng': "Nose protrusion (mm)",
          'value': 27,
          'explanation': "The straight-line distance between the pronasale landmark at the tip of the nose and the subnasale landmark under the nose.",
          'image_url': 'https://nap.nationalacademies.org/openbook/0309103983/xhtml/images/p20012464g33001.jpg'
        },
        'beardLength': {
          'eng': "Beard length (mm)",
          'value': 0
        },
      }
    },
    showPopup: {
      default: false
    },
  },
  computed: {
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
  },
  methods: {
    show(key) {
      this.keyToShow = key
    },
    hidePopup() {
      this.$emit('hidePopUp', true)
    },
    updateFacialMeasurement(event, key) {
      this.$emit('updateFacialMeasurement', event, key)
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


