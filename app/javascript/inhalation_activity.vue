<template>

    <tr>
      <td>
        <div class='row justify-content-center align-items-center'>
          <h3 class='bold'>Inhalation Activity</h3>
          <CircularButton text='?' @click='show = !show'/>
        </div>
      </td>
      <td>
        <ColoredCell
            :colorScheme="inhalationActivityScheme"
            :maxVal=1
            :value='worstCaseInhalation["inhalationFactor"]'
            :text='worstCaseInhalation["inhalationActivity"]'
            :style="inlineCellCSS"
        />
      </td>
    </tr>

    <tr v-if='show'>
      <td colspan='2'>
        <div class='explainer'>
          <p> The worst case inhalation activity was <ColoredCell
                                :colorScheme="inhalationActivityScheme"
                                :maxVal=1
                                :value='worstCaseInhalation["inhalationFactor"]'
                                :text='worstCaseInhalation["inhalationActivity"]'
                                :style="inlineCellCSS"
                            />, which corresponds to a factor of
                <ColoredCell
                    :colorScheme="inhalationActivityScheme"
                    :maxVal=1
                    :value='worstCaseInhalation["inhalationFactor"]'
                    :style="inlineCellCSS"
                />. To better contextualize how good this is, let's look at the
                table of inhalation activities and factors:
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

</template>

<script>
import ColoredCell from './colored_cell.vue';
import CircularButton from './circular_button.vue';

export default {
  name: 'InhalationActivity',
  components: {
    ColoredCell,
    CircularButton
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
</style>
