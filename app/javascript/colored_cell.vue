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
  div {
    margin: 0 auto;
    vertical-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>
