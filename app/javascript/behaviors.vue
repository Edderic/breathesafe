<template>
  <div class='item-span-wide' id='section-behaviors'>
    <br id='risk-assessment-summary'>
    <div class='row centered'>
      <h2 class='centered'>Behaviors</h2>
      <CircularButton text='?' @click='show = !show'/>
    </div>
  </div>

  <div class='explainer' id='section-behaviors' v-if='show'>
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
  </div>
</template>

<script>
import CircularButton from './circular_button.vue'

export default {
  name: '',
  components: {
    CircularButton,
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
</style>
