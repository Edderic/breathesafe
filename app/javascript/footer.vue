<template>
  <div class='footer row'>
    <router-link class='link' :to="{'name': 'TermsOfService'}">Terms of Service</router-link>
    <a class='link' href="https://app.termly.io/notify/da32d236-6da0-4eac-b420-b983a26320f4">Data Subject Access Request (DSAR) Form</a>
    <router-link class='link' :to="{'name': 'PrivacyPolicy'}">Privacy Policy</router-link>
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
  }

  .link {
    padding: 1em;
  }
</style>
