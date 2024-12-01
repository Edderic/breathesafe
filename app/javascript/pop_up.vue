<template>
  <div class='closable-container'>
    <CircularButton @click='close' class='close' :style='{bottom: bottom, left: left}' text='x'/>
    <div class='slot-wrapper'>
      <slot></slot>
    </div>
  </div>
</template>

<script>
import CircularButton from './circular_button.vue'

export default {
  name: 'Popup',
  components: {
    CircularButton
  },
  data() {
    return {
    }
  },
  props: {
    messages: {
      type: Array,
      default: [],
    }
  },
  computed: {
    bottom() {
      return `15px`

    },

    left() {
      return `${400 - 40}px`
    }

  }, methods: {
    close() {
      this.$emit('onclose')
    }
  }

}
</script>

<style scoped>
  .closable-container {
    width: 400px;
    font-weight: bold;
    background-color: #ffffd6;

    position: absolute;
    margin-left: auto;
    margin-right: auto;
    left: 0;
    right: 0;
    z-index:999;
  }

  .close {
    position: relative;
  }

  .slot-wrapper {
    position: relative;
    top: -30px;
  }

  p {
    padding: 1em;

  }
</style>
