<template>
  <td
    :style="{ backgroundColor: cellColor }"
  >
    <slot>
      {{ value / maxVal }}
    </slot>
  </td>
</template>

<script>
  import { interpolateRgb } from './misc';

  export default {
    computed: {
      ratio() {
        return this.value / parseFloat(this.maxVal);
      },
      cellColor() {
        for (let obj of this.colorScheme) {
          if (obj['lowerBound'] <= this.ratio && this.ratio < obj['upperBound']) {
            return interpolateRgb(
              obj['lowerColor'],
              obj['upperColor'],
              obj['lowerBound'],
              this.ratio,
              obj['upperBound']
            )
          }
        }

        let obj = this.colorScheme[this.colorScheme.length-1]
        return interpolateRgb(
          obj['lowerColor'],
          obj['upperColor'],
          obj['lowerBound'],
          obj['upperBound'],
          obj['upperBound']
        )
      },
    },
    methods: {
    },
    props: [
      'value',
      'maxVal',
      'colorScheme'
    ]
  }
</script>

<style scoped>
</style>
