<template>
  <div class='footer row'>
    <router-link class='link' :to='{ name: "ConsentForm"}' @click='toggleShowSubNavBar("ConsentForm")'>Consent Form</router-link>
    <router-link class='link' :to="{'name': 'TermsOfService'}">Terms of Service</router-link>
    <router-link class='link' :to="{'name': 'PrivacyPolicy'}">Privacy Policy</router-link>
    <router-link class='link' :to="{'name': 'Disclaimer'}">Disclaimer</router-link>
  </div>
</template>

<script>
export default {
  name: 'Footer',
  components: {
  },
  data() {
    return {}
  },
  props: {
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>

  .footer {
    position: fixed;
    bottom: 0;
    background-color: white;
    width: 100vw;
    display: flex;
    flex-direction: row;
    vertical-align: center;

    border-top: 1px solid grey;
    justify-content: end;
  }

  .link {
    padding: 1em;
  }
</style>
