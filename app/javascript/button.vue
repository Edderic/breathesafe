<template>
  <div class='button'>{{text}}</div>
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
    text: String
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
  .button {
    font-weight: bold;
    border: 1px solid grey;
    text-align: center;
    padding: 1em;
    font-size: 1.5em;
    background-color: rgb(219, 21, 0);
    color: white;
    margin-top: 1em;
  }

  @media(max-width: 800px) {
  }
</style>
