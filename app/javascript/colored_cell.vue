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
  import { interpolateColor } from './misc';

  export default {
    computed: {
      ratio() {
        return this.value / this.maxVal;
      },
      cellColor() {
        return interpolateColor(this.colorInterpolationScheme, this.ratio);
      },
    },
    methods: {
    },
    props: [
      'value',
      'colorInterpolationScheme',
      'maxVal'
    ]
  }
</script>

<style scoped>
</style>
