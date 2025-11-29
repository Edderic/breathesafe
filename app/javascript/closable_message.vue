<template>
  <Popup v-if='shouldShow' @onclose='close'>
    <div class='message-content'>
      <p v-for='message in messages' :key='message.str'>
        <router-link v-if='!!message.to' :to='message.to' @click='close'>
          {{message.str}}
        </router-link>
        <span v-else>
          {{message.str}}
        </span>
      </p>
      <slot></slot>
    </div>
  </Popup>
</template>

<script>
import Popup from './pop_up.vue'

export default {
  name: 'ClosableMessage',
  components: {
    Popup
  },
  props: {
    messages: {
      type: Array,
      default: [],
    }
  },
  computed: {
    shouldShow() {
      return this.messages.length > 0 || (this.$slots.default && this.$slots.default().length > 0)
    }
  },
  methods: {
    close() {
      this.$emit('onclose')
    }
  }
}
</script>

<style scoped>
  .message-content {
    font-weight: bold;
  }

  .message-content p {
    padding: 0.5em 0;
    margin: 0;
  }

  .message-content p:first-child {
    padding-top: 0;
  }

  .message-content p:last-child {
    padding-bottom: 0;
  }

  tr td {
    padding-left: 0.5em;
    padding-right: 0.5em;
  }
</style>
