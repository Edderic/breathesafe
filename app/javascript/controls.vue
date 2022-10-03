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
      <tr>
        <th>Individual risk given 1 infector</th>

        <td>
          <ColoredCell
            :colorScheme="riskColorScheme"
            :maxVal=1
            :value='roundOut(this.risk, 6)'
            :style="styleProps"
            />
        </td>
      </tr>

    </table>
  </div>
</template>

<script>
import { mapWritableState, mapState, mapActions } from 'pinia';
import { useAnalyticsStore } from './stores/analytics_store'
import {
  round
} from  './misc';

export default {
  name: 'Controls',
  data() {
    return {
      selectedHour: 1,
      hoursToSelect: [
        '1 hour',
        '4 hours',
        '8 hours',
        '40 hours',
      ],
    }
  },
  computed: {
    ...mapWritableState(
      useAnalyticsStore,
      [
        'numInfectors',
        'numSusceptibles',
        'selectedAirCleaner',
        'selectedInfectorMask',
        'selectedSusceptibleMask'
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
      ]
    ),
    setDuration(event) {
      this.selectedHour = this.hoursToSelect[event.target.value].split(' ')[0]
    },
    roundOut(someValue, numRound) {
      return round(someValue, numRound)
    },
  },
  props: {
    maskInstances: Array,
    airCleanerInstances: Array
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
</style>