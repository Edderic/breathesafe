<template>
  <button class='icon' id='search-icon'>
    <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :height='height' :width='width'>
      <circle :cx="cx" :cy="cy" r="25" :fill="strokeColor"/>
      <circle :cx="cx" :cy="cy" r="20" fill="rgb(230, 230, 230)"/>
      <path :d="line" :stroke='strokeColor' stroke-width='10'/>
    </svg>
  </button>
</template>

<script>
export default {
  name: 'SearchIcon',
  components: {
  },
  data() {
    return {
      darkness: 150,
      cy: 30,
      cx: 30
    }
  },
  props: {
    height: Number,
    width: Number,
  },
  computed: {
    strokeColor() {
      return `rgb(${this.darkness}, ${this.darkness}, ${this.darkness})`
    },
    line() {
      return `m 50 50 l 20 20`
    }

  },
  methods: {
  }

}
</script>

<style scoped>

  button {
    display: flex;
    cursor: pointer;
    padding: 0.25em;
  }

  @media(max-width: 700px) {
    .icon {
      padding: 1em;
    }
  }
</style>

