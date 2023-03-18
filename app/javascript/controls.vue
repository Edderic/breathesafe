<template>
  <div class='centered parameters column'>
    <h2>Dilute the Air</h2>
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
        <input class='centered' :value='numInfectors' @change='setNumInfs'/>
      </td>
      <td>
        <select class='centered' :value='selectedInfectorMask.name()' @change='selectInfMask'>
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
        <input class='centered' :value='numSusceptibles' @change='setNumSus'/>
      </td>

      <td>
        <select class='centered' :value='selectedSusceptibleMask.name()' @change='selectSusMask'>
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
        <input class='centered' :value='numPACs' @change='setNumPortableAirCleaners'/>
      </td>

      <td>
        <select class='centered' :value='selectedAirCleaner.name()' @change='selectPAC'>
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
        <th>Duration (hours)</th>
        <td>
          <input type="number" :value='selectedHour' @change='setDuration'>
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
        'selectedInfMask',
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
    copyQuery(arg) {
      let query = JSON.parse(JSON.stringify(this.$route.query))
      Object.assign(query, arg)

      this.$router.push({
        name: 'Analytics',
        params: this.$route.params,
        query: query
      })
    },
    setNumInfs(event) {
      this.copyQuery({'numInfectors': event.target.value})
    },
    setNumSus(event) {
      this.copyQuery({'numSusceptibles': event.target.value})
    },
    selectInfMask(event) {
      this.copyQuery({'infectorMask': event.target.value})
    },
    selectSusMask(event) {
      this.copyQuery({'susceptibleMask': event.target.value})
    },
    setDuration(event) {
      this.copyQuery({'duration': event.target.value})
    },
    setNumPortableAirCleaners(event) {
      this.copyQuery({'numPACs': event.target.value})
    },
    selectPAC(event) {
      this.copyQuery({'pacName': event.target.value})
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
