<template>
  <div class='centered parameters column'>
    <h3>Duration (hours)</h3>
    <Number
      class='continuous'
      :leftButtons="[{text: '-1', emitSignal: 'incrementDuration'}]"
      :rightButtons="[{text: '+1', emitSignal: 'incrementDuration'}]"
      :value='selectedHour'
      @incrementDuration='incrementDuration'
      @update='setDuration'
    />
    <h3>Masking</h3>
    <table>
      <tr>
        <td>
        </td>
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
    </table>
    <h3>Air Cleaning</h3>
    <table>
      <tr>
        <th>
          Amount
        </th>
        <td>
          <Number
            class='continuous'
            :leftButtons="[{text: '-1', emitSignal: 'incrementNumPAC'}]"
            :rightButtons="[{text: '+1', emitSignal: 'incrementNumPAC'}]"
            :value='numPACs'
            @incrementNumPAC='incrementNumPACs'
            @update='setNumPortableAirCleaners'
          />
        </td>
      </tr>
      <tr>
        <th>Protection
        </th>
        <td>
          <select class='centered' :value='selectedAirCleaner.name()' @change='selectPAC'>
            <option :value="cleaner.singular" v-for='cleaner in airCleanerInstances'>{{cleaner.singular}}</option>
          </select>
        </td>
      </tr>
      <tr>
        <th>Image
        </th>
        <td>
          <a :href="selectedAirCleaner.website()">
            <img :src="selectedAirCleaner.imgLink()" alt="">
          </a>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import ColoredCell from './colored_cell.vue';
import Number from './number.vue';
import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store'
import {
  round
} from  './misc';

export default {
  name: 'Controls',
  components: {
    ColoredCell,
    Number
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
    incrementDuration(event) {
      this.copyQuery({'duration': parseInt(event.value) + this.selectedHour})
    },
    setDuration(event) {
      this.copyQuery({'duration': event.value})
    },
    incrementNumPACs(event) {
      this.copyQuery({'numPACs': parseInt(this.numPACs) + parseInt(event.value)})
    },
    setNumPortableAirCleaners(event) {
      this.copyQuery({'numPACs': event.value})
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
