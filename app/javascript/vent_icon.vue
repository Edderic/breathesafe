<template>

  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :height='height' :width='width'>
    <path d='h 80 v 80 h -80 z' stroke='black' fill="#ccc"/>
    <path d="m 20 30 h 40 l -20 -20 z" stroke='black' fill='#ccc'/>
    <path d="m 20 30 h 40 v 30 h -40 z" stroke='black' fill='#eee'/>

    <path d="m 20 30 m 4 4 v 15 h 10 v -15 z" stroke='black' fill='#ddd'/>
    <path d="m 20 30 m 25 4 v 15 h 10 v -15 z" stroke='black' fill='#ddd'/>

    <path d='m 20 30 m -10 1 c 3 4 5 5 21 8' stroke='green' fill='transparent'/>
    <path d='m 20 30 m -10 1 m 21 8 l -2 2 l 3 -2 l -2 -2 l -0.5 4' stroke='green' fill='green'/>

    <path d='m 20 30 m -13 12 h 19' stroke='green' fill='transparent'/>
    <path d='m 20 30 m -13 12 m 19 0 l 0 2 l 2 -2 l -2 -2 z' stroke='green' fill='green'/>

    <path d='m 20 30 m -10 23 c 4 -3 5 -4 19 -7' stroke='green' fill='transparent'/>
    <path d='m 20 30 m -10 23 m 19 -7 l 1 2 l 2 -3 l -3.5 -1 z' stroke='green' fill='green'/>


    <path d='m 20 30 m 29 8 c 4 0 15 -3 19 -7' stroke='red' fill='transparent'/>
    <path d='m 20 30 m 29 8 m 19 -7 l 1 2 l 2 -3 l -3.5 -0.8 z' stroke='red' fill='red'/>

    <path d='m 20 30 m 29 12 h 20' stroke='red' fill='transparent'/>
    <path d='m 20 30 m 29 12 m 20 0 l 0 2 l 2.5 -2 l -2.5 -2 z' stroke='red' fill='red'/>

    <path d='m 20 30 m 29 16 c 4 0 17 2 20 5' stroke='red' fill='transparent'/>
    <path d='m 20 30 m 29 16 m 20 5 l -2 1.5 l 3 0 l 0 -3 z' stroke='red' fill='red'/>

    <text x="25" y="65" v-if='showText'>VENT</text>
  </svg>


</template>

<script>
export default {
  name: 'VentIcon',
  components: {
  },
  props: {
    height: {
      default: '5em'
    },

    width: {
      default: '5em'
    },
    showText: {
      default: true
    },
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
