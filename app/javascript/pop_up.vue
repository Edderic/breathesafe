<template>
  <div class='popup' @click='close'>
    <div class='content' @click.stop>
      <CircularButton @click='close' class='close' text='x'/>
      <div class='slot-wrapper'>
        <slot></slot>
      </div>
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
      return `0`
    }

  }, methods: {
    close() {
      this.$emit('onclose')
    }
  }

}
</script>

<style scoped>
  .popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .content {
    background-color: white;
    padding: 2em;
    border-radius: 8px;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    margin: 2em;
    position: relative;
  }

  .close {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1001;
    margin-left: 0;
    margin-right: 0;
  }

  .slot-wrapper {
    position: relative;
  }

  p {
    padding: 1em;

  }
</style>
