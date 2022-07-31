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

        let obj = this.colorScheme[this.closestColorIndex]
        return interpolateRgb(
          obj['lowerColor'],
          obj['upperColor'],
          obj['lowerBound'],
          obj['upperBound'],
          obj['upperBound']
        )
      },
      closestColorIndex() {
        let closestIndex = 0
        let bestValue = 0
        let index = 0

        for (let obj of this.colorScheme) {
          if (Math.abs(obj['upperBound'] - this.ratio) < Math.abs(bestValue - this.ratio)) {
            bestValue = obj['upperBound']
            closestIndex = index
          }

          index += 1
        }

        return closestIndex
      }
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
