<template>

<svg
  xmlns="http://www.w3.org/2000/svg"
  fill="#000000"
  viewBox="13 22 13 33"
  height='2em'
  width='1em'
  v-for="index in amount"
  :key="index"
>
  <g>
    <circle cx="19" cy="27" r="5" :fill="backgroundColor" />
    <path d='m 23 29 c 3 0 -5 -2 -12 5 v 8 c 0 3 3 5 4 4 v 8 h 4 v -8 h 1 v 8 h 4 v -8 c 2 -1 3 -2 4 -3 v -8 c 0 -3 -3 -3 -5 -5 z' :fill='backgroundColor'/>
  </g>
</svg>
</template>

<script>
export default {
  name: 'PersonIcon',
  props: {
    amount: {
    },
    backgroundColor: {
      'default': 'green'
    }
  }
}
</script>
