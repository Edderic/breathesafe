<template>

    <tr>
      <td>
        <div class='row justify-content-center align-items-center'>
          <h3 class='bold'>Infector Activity</h3>
          <CircularButton text='?' @click='show = !show'/>
        </div>
      </td>
      <td>
        <ColoredCell
            :colorScheme="riskiestAerosolGenerationActivityScheme"
            :maxVal=1
            :value='aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])'
            :text='riskiestPotentialInfector["aerosolGenerationActivity"]'
            :style="inlineCellCSS"
        />
      </td>
    </tr>

    <tr v-if='show'>
      <td colspan='2'>
        <div class='explainer'>
          <p>
            The riskiest aerosol generation activity recorded for a person in this measurement is <span class='bold'>{{riskiestPotentialInfector["aerosolGenerationActivity"]}}</span>,
            which corresponds to a factor of <span class='bold'>{{aerosolActivityToFactor(riskiestPotentialInfector["aerosolGenerationActivity"])}}</span>. See Risk Equation section for more details.
          </p>
          <div class='centered'>
            <table>
              <tr>
                <th>Infector Activity</th>
                <th>Factor</th>
              </tr>
              <tr v-for='(value, key) in infectorActivities'>
                <td :class='{"table-td": true, bold: key == riskiestPotentialInfector["aerosolGenerationActivity"]}'>{{key}}</td>
                <td class='table-td'>
                <ColoredCell
                  :colorScheme="riskiestAerosolGenerationActivityScheme"
                  :maxVal=1
                  :value='value'
                  :style="tableColoredCell"
                />
                </td>
              </tr>
            </table>
          </div>
        </div>
      </td>
    </tr>

</template>

<script>
import ColoredCell from './colored_cell.vue';
import CircularButton from './circular_button.vue';
import { infectorActivityTypes } from './misc'

export default {
  name: 'InfectorActivity',
  components: {
    ColoredCell,
    CircularButton
  },
  data() {
    return {
      infectorActivities: infectorActivityTypes,
      show: false
    }
  },
  props: {

    aerosolGenerationActivity: String,
    riskiestAerosolGenerationActivityScheme: Object,
    aerosolActivityToFactor: Object,
    riskiestPotentialInfector: String,
    inlineCellCSS: String,
    tableColoredCell: Object
  },
  computed: {

  },
  methods: {
    inhalationValue(value) {
      if (value && this.worstCaseInhalation["ageGroup"]) {
        return value[this.worstCaseInhalation["ageGroup"]]["mean cubic meters per hour"]
      } else {
        return 0
      }
    },
  }
}
</script>

<style scoped>

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .align-items-center {
    display: flex;
    align-items: center;
  }

  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .bold {
    font-weight: bold;
  }
</style>
