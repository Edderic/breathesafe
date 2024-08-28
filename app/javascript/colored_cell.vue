<template>
  <td
    :style="{ backgroundColor: cellColor, padding: padding }"
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
        if (this.exception && this.exception.value == this.value) {
          return this.exception.text
        } else if (this.text == "" || !!this.text) {
          return this.text
        } else {
          return this.value
        }
      },
      cellColor() {
        if (this.backgroundColor) {
          return this.backgroundColor
        }

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
      'exception': Object,
      'backgroundColor': String,
      'padding': String
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
