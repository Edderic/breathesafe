<template>
  <div>
    <div class='container scroll'>
      <router-link :to="`/analytics/${this.$route.params.id}#interventions`" class='link-h1' id='link-interventions'>
        Interventions
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#risk-assessment-summary`" class='link-h1' id='link-risk-assessment-summary'>
        Risk Assessment Summary
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#average-new-infections`" class='link-h2' id='link-average-new-infections'>
        Average New Infections
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#individual-risk`" class='link-h2' id='link-individual-risk'>
        Individual Risk
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#lost-labor-and-wages`" class='link-h2' id='link-lost-labor-and-wages'>
        Lost Labor &#38; Wages
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#risk-equation`" class='link-h1' id='link-risk-equation'>
        Risk Equation
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#strengths`" class='link-h2' id='link-strengths'>
        Strengths
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#room-for-improvement`" class='link-h2' id='link-room-for-improvement'>
        Room for Improvement
      </router-link>

      <router-link :to="`/analytics/${this.$route.params.id}#risk-assessment-details`" class='link-h1' id='link-risk-assessment-details'>
        Risk Assessment Details
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#clean-air-delivery-rate`" class='link-h2' id='link-clean-air-delivery-rate'>
        Clean Air Delivery Rate (CADR)
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#total-ach`" class='link-h2' id='link-total-ach'>
        Total ACH
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#behaviors`" class='link-h2' id='link-behaviors'>
        Behaviors
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#inhalation-activity`" class='link-h2' id='link-inhalation-activity'>
        Inhalation Activity
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#infector-activity`" class='link-h2' id='link-infector-activity'>
        Infector Activity
      </router-link>

      <router-link :to="`/analytics/${this.$route.params.id}#masking`" class='link-h2' id='link-masking'>
        Masking
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#computational-details`" class='link-h1' id='link-computational-details'>
        Computational Details
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-ventilation-ach`" class='link-h2' id='link-details-ventilation-ach'>
        Ventilation ACH
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-upper-room-germicidal-uv-ach`" class='link-h2' id='link-details-upper-room-germicidal-uv-ach'>
        Upper-Room Germicidal UV ACH
      </router-link>
      <router-link :to="`/analytics/${this.$route.params.id}#details-portable-air-cleaner-ach`" class='link-h2' id='link-details-portable-air-cleaner-ach'>
        Portable Air Cleaner ACH
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SideBar',
  mounted() {
    var observer = new IntersectionObserver(function(entries) {
      // isIntersecting is true when element and viewport are overlapping
      // isIntersecting is false when element and viewport don't overlap
      for (let entry of entries) {
        let id = entry.target.id;
        let selection = document.querySelector(`#link-${id.substring(8)}`)

        if(entry.isIntersecting === true) {
          selection.classList.add("active")
          console.log('Element has just become visible in screen');
        }
        else {
          selection.classList.remove("active")
        }
      }
    }, { threshold: [0.20] });

    for (let j of document.querySelectorAll(".link-h2")) {
      console.log(j.id.substring(5))
      observer.observe(document.querySelector(`#section-${j.id.substring(5)}`));
    }
    for (let j of document.querySelectorAll(".link-h1")) {
      console.log(j.id.substring(5))
      observer.observe(document.querySelector(`#section-${j.id.substring(5)}`));
    }
  }
}
</script>

<style scoped>
  .link-h1 {
    margin-top: 1em;
  }

  .link-h2 {
    margin-left: 0.5em;
    margin-top: 1em;
  }

  .container {
    display: flex;
    flex-direction: column;
  }

  .scroll {
    overflow-y: auto;
  }

  .active {
    background-color: #d9d9d9;
  }

  #link-interventions {
    display: none;
  }

  @media (max-width: 1400px) {
    #link-interventions {
      display: inline-block;
    }
    .link-h1, .link-h2 {
      font-size: 0.75em;
    }
  }
</style>
