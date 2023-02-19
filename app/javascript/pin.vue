<template>
  <button id='whereabouts'>
    <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :height='height' :width='width'>
      <circle cx="40" cy="40" r="40" fill="rgb(200, 200, 200)"/>
      <circle cx="40" cy="25" r="20" fill="white"/>

      <path d='m 21 28 c 0 15 10 22 19 40 c 10 -18 19 -28 19 -40' stroke='white' fill='white'/>

      <circle cx="40" cy="25" r="10" fill="rgb(150, 29, 2)"/>
    </svg>
  </button>
</template>

<script>
export default {
  name: 'Pin',
  components: {
  },
  data() {
    return {}
  },
  props: {
    height: Number,
    width: Number,
  },
  computed: {

  },
  methods: {
  }

}
</script>

<style scoped>

  button {
    display: flex;
    cursor: pointer;
  }

</style>
