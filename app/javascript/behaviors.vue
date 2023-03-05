<template>
  <DrillDownSection
    title='Behaviors'
    icon="<svg xmlns='http://www.w3.org/2000/svg' fill='#000000' viewBox='0 0 80 80' height='3em' width='3em'> <path d='m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z' stroke='black' fill='#eee'/> <path d='m 20 30 l 5 -3' stroke='black' fill='transparent'/> <circle cx='23' cy='30' r='1' fill='black'/> <path d='m 25 50 c 10 0 25 0 25 -3' stroke='red' fill='transparent'/> <path d='m 50 47 l 1 3 l 3 -3 l -4.5 -2 z' stroke='red' fill='red'/> <path d='m 25 50 c 10 -5 18 0 21 -12' stroke='red' fill='transparent'/> <path d='m 47 38 l 2 1 l -1 -6 l -5 2 z' stroke='red' fill='red'/> <g transform='rotate(-30, 30, 22.5) scale(0.75) translate(-8, 30)'> <circle cx='40' cy='30' r='2' fill='black'/> <path d='m 41 30 v -10 h 5 v 10' stroke='black' fill='transparent'/> <circle cx='44.5' cy='30' r='2' fill='black'/> </g> <g transform='translate(10, 0) rotate(20, 40, 30)'> <circle cx='40' cy='30' r='2' fill='black'/> <path d='m 41 30 v -10 h 5 v 10' stroke='black' fill='transparent'/> <circle cx='44.5' cy='30' r='2' fill='black'/> </g> <g transform='translate(8, 5) rotate(30, 40, 30) scale(1.5)'> <circle cx='40' cy='30' r='2' fill='black'/> <path d='m 41 30 v -10 h 5 v 10' stroke='black' fill='transparent'/> <circle cx='44.5' cy='30' r='2' fill='black'/> </g> </svg> "
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
