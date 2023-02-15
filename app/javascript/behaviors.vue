<template>
  <DrillDownSection
    title='Behaviors'
    :showStat='false'
  >
    <p>
      Activities that people partake in can affect the probability of
      transmission of COVID and other respiratory viruses. Activities
      where the infector is doing lots of exhalation and vocalization (e.g. loudly
      talking during heavy exercise) could drastically increase the
      risk of transmission. Likewise, doing activities where
      susceptibles are inhaling more air in shorter time increases their risk of
      getting COVID.

    </p>
    <p>

    </p>
    <p>
      Choosing activities where an infector is quiet and at rest, along
      with susceptibles being at rest, could decrease the risk of
      airborne transmission.
    </p>
  </DrillDownSection>
</template>

<script>
import CircularButton from './circular_button.vue'
import DrillDownSection from './drill_down_section.vue'

export default {
  name: '',
  components: {
    CircularButton,
    DrillDownSection
  },
  data() {
    return { show: false }
  },
  props: {
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .row {
    margin: 1em 0;
    display: flex;
    flex-direction: row;
  }


  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .title {
    max-width: 12em;
    margin-left: 1em;
  }

  .showHideButton {
    margin-left: 1em;
    margin-right: 1em;
  }
</style>
