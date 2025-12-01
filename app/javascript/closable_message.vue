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
import { Comment } from 'vue'

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
      if (this.messages && this.messages.length > 0) return true
      if (!this.$slots.default) return false
      const nodes = this.$slots.default() || []
      // Consider only non-comment, non-empty nodes as visible content
      const hasVisible = nodes.some(n => {
        if (n.type === Comment) return false
        if (typeof n.children === 'string') {
          return n.children.trim().length > 0
        }
        // For element nodes, treat as visible
        return true
      })
      return hasVisible
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
