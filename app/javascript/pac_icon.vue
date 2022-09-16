<template>

<svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :height='height' :width='width'>
  <path d='h 80 v 80 h -80 z' stroke='black' fill="#ccc"/>
  <path d="M 30 20 l -5 17 h 25 l 3 -17 z m -5 17 v 23 h 25 v -23 m 0 23 l 3 -17.5 l 0 -19" fill="white" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
  <path d="M 27 43 v 17 m 5 0 v -17 m 5 0 v 17 m 5 0 v -17 m 5 0 v 17 " fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
  <path d="M 25 43 h 24" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>

  <ellipse cx="39" cy="28" rx="10" ry="7" stroke="black" fill="transparent" stroke-width="1"/>
  <ellipse cx="39" cy="28" rx="7" ry="5" stroke="black" fill="transparent" stroke-width="1"/>
  <ellipse cx="39" cy="28" rx="4" ry="3" stroke="black" fill="transparent" stroke-width="1"/>

  <path d="M 34 25 c 0 -5 0 -5 -5 -13 " stroke='green' fill='transparent'/>
  <path d="M 34 25 m -5 -13 l 2 -2 l -5 0 l 1 5 z" stroke='green' fill='green' />

  <path d="M 40 25 l 0 -17 " stroke='green'/>
  <path d="M 40 25 m 0 -17 l 3 0 l -3 -3 l -3 3 z" stroke='green' fill='green'/>


  <path d="M 46 25 c 0 -5 0 -5 5 -13" stroke='green' fill='transparent'/>
  <path d="M 46 25 m 5 -13 l 2.5 2.5 l 0 -5 l -5 1 z" stroke='green' fill='green'/>


  <path d="M 46 55 c 2 7 0 10 6 15" stroke='red' fill='transparent'/>
  <path d="M 46 55 l 3 -1 l -4 -2 l -2 4.5" stroke='red' fill='red'/>

  <path d="M 31 55 c 0 5 0 10 -7 14" stroke='red' fill='transparent'/>
  <path d="M 31 55 l 3 2 l -2 -5 l -3 3 z" stroke='red' fill='red'/>


  <text x="55" y="38">PAC</text>

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
