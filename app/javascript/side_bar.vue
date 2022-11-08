<template>
  <div>
    <router-link :to="`/analytics/${this.$route.params.id}#individual-risk`" class='link-h1'>
      Individual Risk
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#overview`" class='link-h1'>
      Overview
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#strengths`" class='link-h2'>
      Strengths
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#room-for-improvement`" class='link-h2'>
      Room for Improvement
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#details`" class='link-h1'>
      Details
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`" class='link-h2'>
      Clean Air Delivery Rate (CADR)
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#air-changes-per-hour`" class='link-h2'>
      Air Changes per Hour (ACH)
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#total-ach`" class='link-h2'>
      Total ACH
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#behaviors`" class='link-h2'>
      Behaviors
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#inhalation`" class='link-h2'>
      Inhalation
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#exhalation`" class='link-h2'>
      Exhalation
    </router-link>

    <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2'>
      Masking
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#interventions`" class='link-h1'>
      Interventions
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#computational-details`" class='link-h1'>
      Computational Details
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#details-ventilation-ach`" class='link-h2'>
      Ventilation ACH
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#details-upper-room-germicidal-uv-ach`" class='link-h2'>
      Upper-Room Germicidal UV ACH
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#details-portable-air-cleaner-ach`" class='link-h2'>
      Portable Air Cleaner ACH
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'SideBar'
}
</script>

<style scoped>
  .link-h1 {
    margin-left: 2em;
    margin-top: 1em;
  }

  .link-h2 {
    margin-left: 3em;
    margin-top: 1em;
  }

</style>
