<template>
  <div
    :style="{ backgroundColor: cellColor }"
  >
    <slot>
      {{ display }}
    </slot>
  </div>
</template>

<script>
  import { getColor, interpolateRgb } from './colors';

  export default {
    computed: {
      display() {
        if (this.text == "" || !!this.text) {
          return this.text
        } else {
          return this.value
        }
      },
      cellColor() {
        return getColor(this.colorScheme, this.value)
      },
    },
    methods: {
    },
    props: [
      'value',
      'text',
      'colorScheme'
    ]
  }
</script>

<style scoped>
  div {
    margin: 0 auto;
    vertical-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>
