<template>
  <DrillDownSection

    title='Probability that at least one infector is present'
    :value='probabilityOneInfectorIsPresent'
    :text='drillDownText'
    :colorScheme='riskColorScheme'
  >
    <tr>
      <td colspan=2>
        <div class='explainer'>
          <span>On average, assuming {{ numInfectors }} COVID infector(s) in
          the room, and that everyone stays there for {{selectedHour}} hour(s), the
          number of people that would be infected is <span
          class='bold'>{{roundOut(numSusceptibles * risk, 1)}}</span>:

          </span>
          <div class='people-icons people '>
            <PersonIcon
              backgroundColor='red'
              :amount='roundOut(numInfected, 0)'
            />
            <PersonIcon
              backgroundColor='green'
              :amount='numSusceptibles - roundOut(numInfected, 0)'
            />
          </div>

          <p>If the average number of new infections is less than 1 everywhere,
          COVID-19 will become extinct. Business owners can do their part by making their
          environments less conducive to spread, for example, by adopting higher indoor
          air quality standards and masking. <span class='bold'>At the very least,
          aim for a combination of interventions to keep the average new infections below 1</span>.
          </p>
        </div>
      </td>
    </tr>
  </DrillDownSection>
</template>

<script>
import { round, oneInFormat } from './misc.js'
import { assignBoundsToColorScheme, infectedPeopleColorBounds, riskColorInterpolationScheme } from './colors.js'
import DrillDownSection from './drill_down_section.vue'
import { useAnalyticsStore } from './stores/analytics_store.js'
import { mapWritableState, mapState, mapActions } from 'pinia';

export default {
  name: 'ProbaAtLeastOneInfectorPresent',
  components: {
    DrillDownSection
  },
  data() {
    return {}
  },
  props: {
  },
  computed: {
    ...mapWritableState(
        useAnalyticsStore,
        [
          'possibleInfectorGroups',
          'probabilityOneInfectorIsPresent',
        ]
    ),
    riskColorScheme() {
      return riskColorInterpolationScheme
    },

    drillDownText() {
      return `1 in ${oneInFormat(this.probabilityOneInfectorIsPresent)}`
    }
  },

  methods: {
    roundOut(x, y) {
      return round(x, y)
    }
  }

}
</script>

<style scoped>
</style>
