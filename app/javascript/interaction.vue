<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 200 200" height='20em' width='20em'>
    <path d='m 0 0 h 200 v 200 h -200 z' fill='green' stroke='black'/>

    <path d='m 50 99 l 40 -30 l 20 -40 l -6 -28 l 95 0 v 100 z' stroke='rgb(87, 195, 40)' fill='rgb(87, 195, 40)'/>
    <path d='m 50 99 l 40 -30 l 20 -40 l -6 -28 l 95 0 v 100 z' stroke='rgb(87, 195, 40)' fill='rgb(87, 195, 40)' transform='translate(0, 199) scale(1, -1)'/>

    <path d='m 50 99 l 50 -30 l 30 -40 l -10 -28 l 95 0 v 100 z' stroke='yellow' fill='yellow'/>
    <path d='m 50 99 l 50 -30 l 30 -40 l -10 -28 l 95 0 v 100 z' stroke='yellow' fill='yellow' transform='translate(0, 199) scale(1, -1)'/>

    <path d='m 50 99 l 60 -30 l 30 -40 l 2 -10 l 5 -8 l 3 -5 l 5 0 l 20 5 l 15 5 l 10 20 v 66' stroke='orange' fill='orange'/>
    <path d='m 50 99 l 60 -30 l 30 -40 l 2 -10 l 5 -8 l 3 -5 l 5 0 l 20 5 l 15 5 l 10 20 v 66' stroke='orange' fill='orange' transform='translate(0, 199) scale(1, -1)'/>

    <path d='m 50 99 l 80 -30 l 35 -40 l 10 0 l 10 18 l 3 20 l 2 32 z' stroke='red' fill='red'/>
    <path d='m 50 99 l 80 -30 l 35 -40 l 10 0 l 10 18 l 3 20 l 2 32 z' stroke='red' fill='red' transform='translate(0, 199) scale(1, -1)'/>

    <path d='m 50 99 l 100 -20 l 15 -10 l 10 0 l 5 18 l 1 14 z' stroke='rgb(174, 17, 0)' fill='rgb(174, 17, 0)'/>
    <path d='m 50 99 l 100 -20 l 15 -10 l 10 0 l 5 18 l 1 14 z' stroke='rgb(174, 17, 0)' fill='rgb(174, 17, 0)' transform='translate(0, 199) scale(1, -1)'/>

    <g class='head' transform='translate(20, 50)'>
      <path d="m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z" stroke='black' fill='#ccc'/>
      <path d="m 20 30 l 5 -3" stroke='black' fill='transparent'/>

      <circle cx="23" cy="30" r="1" fill="black"/>
    </g>

    <g class='other-head' transform='translate(20, 50) scale(-1, 1) translate(-150, 0)'>
      <path d="m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z" stroke='black' fill='#ccc'/>
      <path d="m 20 30 l 5 -3" stroke='black' fill='transparent'/>

      <circle cx="23" cy="30" r="1" fill="black"/>
    </g>
  </svg>
</template>

<script>
export default {
  name: 'Interaction',
  components: {
  },
  data() {
    return {}
  },
  props: {
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
</style>
