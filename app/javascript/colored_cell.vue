<template>
  <td
    :style="{ backgroundColor: cellColor }"
  >
    <slot>
      {{ display }}
    </slot>
  </td>
</template>

<script>
  import { getColor, interpolateRgb } from './colors';

  export default {
    computed: {
      display() {
        if (!!this.text) {
          return this.text
        } else {
          return this.ratio
        }
      },
      ratio() {
        return this.value / parseFloat(this.maxVal);
      },
      cellColor() {
        return getColor(this.colorScheme, this.ratio)
      },
    },
    methods: {
    },
    props: [
      'value',
      'text',
      'maxVal',
      'colorScheme'
    ]
  }
</script>

<style scoped>
</style>
