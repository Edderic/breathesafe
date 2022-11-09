<template>
  <div>
    <router-link :to="`/analytics/${this.$route.params.id}#risk-assessment`" class='link-h1'>
      Risk Assessment
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#average-new-infections`" class='link-h2'>
      Average New Infections
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#individual-risk`" class='link-h2'>
      Individual Risk
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#strengths`" class='link-h2'>
      Strengths
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#room-for-improvement`" class='link-h2'>
      Room for Improvement
    </router-link>

    <router-link :to="`/analytics/${this.$route.params.id}#economics`" class='link-h1'>
      Economics
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#lost-labor-and-wages`" class='link-h2'>
      Lost Labor &#38; Wages
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#implementation-cost`" class='link-h2'>
      Implementation Cost
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#total-cost`" class='link-h2'>
      Total Cost
    </router-link>
    <router-link :to="`/analytics/${this.$route.params.id}#savings`" class='link-h2'>
      Savings
    </router-link>

    <router-link :to="`/analytics/${this.$route.params.id}#air-cleaner-cost-details`" class='link-h2'>
      Air Cleaner Cost Details
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
