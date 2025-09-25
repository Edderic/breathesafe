<template>
  <CircularButton
    :text="expanded ? 'v' : '>'"
    v-bind="$attrs"
    @click="$emit('click')"
  />
</template>

<script>
import CircularButton from './circular_button.vue'

export default {
  name: 'ExpandableButton',
  components: {
    CircularButton
  },
  props: {
    expanded: {
      type: Boolean,
      required: true
    }
  },
  emits: ['click']
}
</script>
