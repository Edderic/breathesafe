<template>
  <DrillDownSection
    title='Inhalation Activity'
    :value='worstCaseInhalation["inhalationFactor"]'
    :text='worstCaseInhalation["inhalationActivity"]'
    :colorScheme='inhalationActivityScheme'
  >
    <tr>
      <td colspan='2'>
        <div class='explainer'>
          <p> The worst case inhalation activity was <span
          class='bold'>{{worstCaseInhalation["inhalationActivity"]}}</span>, which
          corresponds to a factor of <span
          class='bold'>{{worstCaseInhalation["inhalationFactor"]}}</span>. To better
          contextualize how good this is, let's look at the
          table of inhalation activities and factors. See Risk Equation section
          for more details.

          </p>

          <div class='centered'>
            <table>
              <tr>
                <th>Inhalation Activity</th>
                <th>Factor</th>
              </tr>
              <tr v-for='(value, key, index) in susceptibleBreathingActivityFactorMappings'>
                <td style='padding: 0.25em 1em;' :class="{ bold: key == worstCaseInhalation['inhalationActivity']}">{{ ['Sleep or Nap', 'Sedentary / Passive', 'Light Intensity', 'Moderate Intensity', 'High Intensity'][index] }}</td>
                <td style='padding: 0;'>
                  <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='inhalationValue(value)'
                    :style="tableColoredCellWithHorizPadding"
                    />
                </td>
              </tr>
            </table>
          </div>
        </div>
      </td>
    </tr>
  </DrillDownSection>

</template>

<script>
import ColoredCell from './colored_cell.vue';
import CircularButton from './circular_button.vue';
import DrillDownSection from './drill_down_section.vue'

export default {
  name: 'InhalationActivity',
  components: {
    ColoredCell,
    CircularButton,
    DrillDownSection
  },
  data() {
    return {
      show: false
    }
  },
  props: {
    worstCaseInhalation: Object,
    inhalationActivityScheme: Array,
    susceptibleBreathingActivityFactorMappings: Array,
    inlineCellCSS: Object,
    tableColoredCellWithHorizPadding: Object,
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
