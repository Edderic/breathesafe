<template>
  <div :class='{button: true, major: major}'>{{text}}</div>
</template>

<script>
export default {
  name: 'Button',
  components: {
  },
  data() {
    return {}
  },
  props: {
    text: String,
    major: Boolean
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
  .button {
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    border: none;
    text-align: center;
    padding: 1em;
    font-size: 1.5em;
    background-color: rgb(200, 200, 200);
    color: white;
  }

  .major {
    background-color: rgb(219, 21, 0);
  }

  @media(max-width: 800px) {
  }
</style>
