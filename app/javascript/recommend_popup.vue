<template>
  <div>
  <Popup @onclose='hidePopup' v-if='showPopup'>
    <div  style='padding: 1em;'>
      <h3>Recommend:</h3>
      <table>
        <thead>
          <tr>
            <th>Measurement</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for='(value, key, index) in facialMeasurements'>
            <th>{{value.eng}}</th>
            <td>
              <input class='num' type="number" :value='value.value' @change="updateFacialMeasurement($event, key)">
            </td>
          </tr>
        </tbody>
      </table>
      <br>

      <div class='justify-content-center'>
        <Button :shadow='true' @click="recommend">Recommend</Button>
      </div>
    </div>
  </Popup>
  </div>
</template>

<script>
import axios from 'axios';
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
    facialMeasurements: {
      default: {
        'bitragionSubnasaleArc': {
          'eng': "Bitragion subnasale arc (mm)",
          'value': 230
        },
        'faceWidth': {
          'eng': "Face width (mm)",
          'value': 155
        },
        'noseProtrusion': {
          'eng': "Nose protrusion (mm)",
          'value': 25
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
  },
  async created() {
  },
  methods: {
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


