<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='3em' width='3em' class='round button'>
    <circle cx="40" cy="40" r="40" :fill="computedBackgroundColor" class='circle' @mouseover='hover = true' @mouseleave='hover = false'/>

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
    return {
      hover: false
    }
  },
  props: {
    text: String,
    backgroundColor: {
      type: String,
      default: 'rgb(200, 200, 200)'
    },
    highlight: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    computedBackgroundColor() {
      if (this.highlight || this.hover) {
        return '#eee'
      } else {
        return this.backgroundColor
      }
    }
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

  svg {
    margin-left: 1em;
    margin-right: 1em;
  }

  .circle:hover {
    cursor: pointer;
    background-color: #eee;
  }
</style>
