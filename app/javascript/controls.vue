<template>
  <div class='centered parameters column'>
    <h2>Interventions</h2>
    <table>
    <tr>
      <td>
      </td>
      <th>
        Amount
      </th>
      <th>Protection
      </th>
      <th>Image
      </th>
    </tr>
    <tr>
      <th>
         Infector
      </th>
      <td>
        <input class='centered' :value='numInfectors' @change='setNumInfectors'/>
      </td>
      <td>
        <select class='centered' @change='selectInfectorMask'>
          <option :value="mask.maskName" v-for='mask in maskInstances'>{{mask.maskName}}</option>
        </select>
      </td>
      <td>
        <a :href="selectedInfectorMask.website()">
          <img :src="selectedInfectorMask.imgLink()" alt="">
        </a>
      </td>
    </tr>
    <tr>
      <th>
         Susceptible
      </th>

      <td>
        <input class='centered' :value='numSusceptibles' @change='setNumSusceptibles'/>
      </td>

      <td>
        <select class='centered' @change='selectSusceptibleMask'>
          <option :value="mask.maskName" v-for='mask in maskInstances'>{{mask.maskName}}</option>
        </select>
      </td>
      <td>
        <a :href="selectedSusceptibleMask.website()">
          <img :src="selectedSusceptibleMask.imgLink()" alt="">
        </a>
      </td>
    </tr>
    <tr>
      <th>
         Portable Air Cleaner
      </th>

      <td>
        <input class='centered' :value='numPACs' @change='setNumPACs'/>
      </td>

      <td>
        <select class='centered' @change='selectAirCleaner'>
          <option :value="cleaner.singular" v-for='cleaner in airCleanerInstances'>{{cleaner.singular}}</option>
        </select>
      </td>
      <td>
        <a :href="selectedAirCleaner.website()">
          <img :src="selectedAirCleaner.imgLink()" alt="">
        </a>
      </td>
    </tr>
    </table>
    <table>

      <tr>
        <th>Duration</th>
        <td>
          <select @change='setDuration'>
            <option :value="i" v-for='(v, i) in hoursToSelect'>{{v}}</option>
          </select>
        </td>
      </tr>

    </table>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue';
import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store'
import {
  round
} from  './misc';

export default {
  name: 'Controls',
  components: {
    ColoredCell
  },
  data() {
    return {
      hoursToSelect: [
        '1 hour',
        '4 hours',
        '8 hours',
        '40 hours',
      ],
    }
  },
  computed: {
    ...mapState(
      useAnalyticsStore,
      [
        'risk',
        'styleProps'
      ]
    ),
    ...mapWritableState(
      useAnalyticsStore,
      [
        'numInfectors',
        'numSusceptibles',
        'selectedAirCleaner',
        'selectedInfectorMask',
        'selectedHour',
        'selectedSusceptibleMask',
        'setNumSusceptibles',
        'numPACs'
      ]
    ),
  },
  methods: {
    ...mapActions(
      useAnalyticsStore,
      [
        'selectAirCleaner',
        'selectSusceptibleMask',
        'selectInfectorMask',
        'setNumInfectors',
        'setNumPACs',
      ]
    ),
    setDuration(event) {
      this.selectedHour = parseInt(this.hoursToSelect[event.target.value].split(' ')[0])
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  },
  props: {
    maskInstances: Array,
    airCleanerInstances: Array,
    riskColorScheme: Array,
  }
}
</script>

<style scoped>

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .column {
    display: flex;
    flex-direction: column;
  }

  img {
    height: 3em;
  }

  input {
    width: 4em;
  }
  @media (max-width: 750px) {
    .parameters {
      font-size: 0.5em;
    }
  }
</style>
