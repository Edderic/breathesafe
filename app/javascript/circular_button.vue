<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='3em' width='3em' class='round'>
    <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>

    <slot v-if='!text'></slot>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" class='tilted-header'>{{text}}</text>
  </svg>
</template>

<script>
export default {
  name: 'CircularButton',
  components: {
  },
  data() {
    return {}
  },
  props: {
    text: String
  },
  computed: {
  },
  methods: {
  }
}
</script>

<style scoped>
  .round text {
    font: 32px Verdana, Helvetica, Arial, sans-serif;
  }

  .round {
  }
</style>
