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
        if (this.exception && this.exception.value == this.value) {
          return this.exception.text
        } else if (this.text == "" || !!this.text) {
          return this.text
        } else {
          return this.value
        }
      },
      cellColor() {
        if (this.exception && this.exception.value == this.value) {
          const color = this.exception.color
          return `rgb(${color.r}, ${color.g}, ${color.b})`
        }
        return getColor(this.colorScheme, this.value)
      },
    },
    methods: {
    },
    props: {
      'value': Number,
      'text': String,
      'colorScheme': Object,
      'exception': Object
    }
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
