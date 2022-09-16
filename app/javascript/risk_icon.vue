<template>

<svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :height='height' :width='width'>
  <g>
    <path d='m 4 29 l 20 30 l 30 -20 l -20 -30 z' stroke='black' fill='transparent' stroke-linejoin='round'/>
    <g transform="rotate(-32, 20, 25)">
      <circle cx="23" cy="27" r="5" fill="red" />
      <path d='m 27 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' fill='red'/>
    </g>
  </g>
  <g transform="translate(28, -10) skewX(12) skewY(40) scale(0.6)">
    <path d='m 4 29 l 20 30 l 30 -20 l -20 -30 z' stroke='black' fill='transparent' stroke-linejoin='round'/>
    <g transform="rotate(-32, 20, 25)">
      <circle cx="23" cy="27" r="5" fill="green" />
      <path d='m 27 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' fill='green'/>
    </g>
  </g>

  <g transform="translate(83, 24) skewX(-63) skewY(33) scale(0.47)">
    <path d='M 6 29 l 20 30 l 30 -20 l -20 -30 z' stroke='black' fill='transparent' stroke-linejoin='round'/>
    <g transform="rotate(-32, 20, 25)">
      <circle cx="23" cy="27" r="5" fill="green" />
      <path d='m 27 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' fill='green'/>
    </g>
  </g>

  <text x="25" y="64">RISK</text>
</svg>

</template>

<script>
export default {
  name: 'PacIcon',
  components: {
  },
  props: {
    height: {
      default: '5em'
    },

    width: {
      default: '5em'
    }
  }
}
</script>

<style scoped>
text {
  dominant-baseline: hanging;
  font: 10px Verdana, Helvetica, Arial, sans-serif;
  font-weight: bold;
}
</style>
