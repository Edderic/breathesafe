<template>

  <div class='closable-container' v-if='messages.length > 0'>
    <CircularButton @click='close' class='close' :style='{bottom: bottom, left: left}' text='x'/>
    <div class='slot-wrapper'>
      <p v-for='message in messages'>{{message}}</p>
    </div>
  </div>
</template>

<script>
import CircularButton from './circular_button.vue'

export default {
  name: 'ClosableMessage',
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
