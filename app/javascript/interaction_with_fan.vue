<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" :viewBox="`0 0 ${heightAndWidth} ${heightAndWidth}`" height='20em' width='20em'>

    <path :d='`m 0 0 h ${heightAndWidth} v ${heightAndWidth} h -${heightAndWidth} z`' :fill='colorScheme[0]' :stroke='colorScheme[0]'/>

    <g class='everything' :transform='transformEverything'>
      <path d='m 50 99 l 10 -20 l -5 -15 l -3 -5 l -15 -15 l 3 -10 l 4 -10 l 6 -10 l 8 -8 l 13 -3 l 20 0 l 20 20 l 10 20 l -2 20 l -10 10' :stroke='colorScheme[1]' :fill='colorScheme[1]'/>
      <path d='m 50 99 l 10 -20 l -5 -15 l -3 -5 l -15 -15 l 3 -10 l 4 -10 l 6 -10 l 8 -8 l 13 -3 l 20 0 l 20 20 l 10 20 l -2 20 l -10 10' :stroke='colorScheme[2]' :fill='colorScheme[2]' transform='translate(19,12) scale(0.8, 0.8) '/>
      <path d='m 50 99 l 10 -20 l -5 -15 l -3 -5 l -15 -15 l 3 -10 l 4 -10 l 6 -10 l 8 -8 l 13 -3 l 20 0 l 20 20 l 10 20 l -2 20 l -10 10' :stroke='colorScheme[3]' :fill='colorScheme[3]' transform='translate(35,25) scale(0.6, 0.6) '/>

      <g class='head' transform='translate(20, 50)'>
        <path d="m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z" stroke='black' fill='#ccc'/>
        <path d="m 20 30 l 5 -3" stroke='black' fill='transparent'/>

        <circle cx="23" cy="30" r="1" fill="black"/>
      </g>

      <g class='fan-and-wind' :transform='fanTransform'>
        <g class='left-wind'>
          <path d='m 80 140 c 0 -10 -2 -8 -5 -20' fill='transparent' stroke='black'/>
          <path d='m 75 120 l 5 3 M 75 120 l -3 5' fill='transparent' stroke='black'/>
        </g>

        <g class='middle-wind' transform='scale(-1, 1) translate(-170, 0) rotate(20, 75, 120)'>
          <path d='m 80 140 c 0 -10 -2 -8 -5 -20' fill='transparent' stroke='black'/>
          <path d='m 75 120 l 5 3 M 75 120 l -3 5' fill='transparent' stroke='black'/>
        </g>

        <g class='right-wind' transform='scale(-1, 1) translate(-190, 0)'>
          <path d='m 80 140 c 0 -10 -2 -8 -5 -20' fill='transparent' stroke='black'/>
          <path d='m 75 120 l 5 3 M 75 120 l -3 5' fill='transparent' stroke='black'/>
        </g>

        <g class='fan'>
          <path d='m 70 150 h 50 v 5 h -50 z' stroke='black' fill='white'/>
          <path d='m 75 155 c 0 10 15 20 20 20 v -20' stroke='black' fill='white'/>
          <path d='m 75 155 c 0 10 15 20 20 20 v -20' stroke='black' fill='white' transform=' scale(-1, 1) translate(-190, 0)'/>


          <path d='m 95 157.5 c -10 0 -8 10 -8 10 l -2 20 h 10' stroke='black' fill='white' />
          <path d='m 95 157.5 c -10 0 -8 10 -8 10 l -2 20 h 10' stroke='black' fill='white' transform='scale(-1, 1) translate(-190, 0)'/>

          <circle cx='95' cy='165' r='5' stroke='black' fill='white'/>
        </g>
      </g>

      <g class='air-cleaner' transform='translate(90, 130)' v-if='airCleaner'>
        <path d='h 80 v 80 h -80 z' stroke='black' fill="#ccc"/>


        <path d='M 30 20 l -5 -10 l -7 -20 l -10 -10 l 5 -10 l 10 -8 l 10 0 l 10 8 l 10 3 l 5 10 l 0 6 l -5 10 -3 10 -2 10 z' stroke='green' fill='green'/>

        <path d='M 30 20 l -5 -10 l -7 -20 l -10 -10 l 5 -10 l 10 -8 l 10 0 l 10 8 l 10 3 l 5 10 l 0 6 l -5 10 -3 10 -2 10 z' stroke='#006400' fill='#006400' transform='scale(0.8, 0.8) translate(10, 0)'/>

        <path d="M 30 20 l -5 17 h 25 l 3 -17 z m -5 17 v 23 h 25 v -23 m 0 23 l 3 -17.5 l 0 -19" fill="white" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
        <path d="M 27 43 v 17 m 5 0 v -17 m 5 0 v 17 m 5 0 v -17 m 5 0 v 17 " fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>
        <path d="M 25 43 h 24" fill="transparent" stroke='black' stroke-linecap='round' stroke-linejoin='round'/>

        <ellipse cx="39" cy="28" rx="10" ry="7" stroke="black" fill="transparent" stroke-width="1"/>
        <ellipse cx="39" cy="28" rx="7" ry="5" stroke="black" fill="transparent" stroke-width="1"/>
        <ellipse cx="39" cy="28" rx="4" ry="3" stroke="black" fill="transparent" stroke-width="1"/>

        <path d="M 46 55 c 2 7 0 10 6 15" stroke='red' fill='transparent'/>
        <path d="M 46 55 l 3 -1 l -4 -2 l -2 4.5" stroke='red' fill='red'/>

        <path d="M 31 55 c 0 5 0 10 -7 14" stroke='red' fill='transparent'/>
        <path d="M 31 55 l 3 2 l -2 -5 l -3 3 z" stroke='red' fill='red'/>


        <text x="55" y="38">PAC</text>

      </g>

      <g class='other-head' transform='translate(20, 50) scale(-1, 1) translate(-150, 0)'>
        <path d="m 5 40 c 0 -10 10 -20 15 -20 c 5 0 10 0 6 10 c 4 4 4 4 4 12 l -5 0 l 3 4 l -8 1 l 8 7 c -2 10 -16 6 -16 5 z" stroke='black' fill='#ccc'/>
        <path d="m 20 30 l 5 -3" stroke='black' fill='transparent'/>

        <circle cx="23" cy="30" r="1" fill="black"/>
      </g>

    </g>
  </svg>
</template>

<script>
export default {
  name: 'InteractionWithFan',
  components: {
  },
  data() {
    return {
    }
  },
  props: {
    early: {
      type: String,
      default: true
    },
    airCleaner: {
      type: String,
      default: false
    },
    largerVolume: {
      type: String,
      default: false
    },

  },
  computed: {
    fanTransform() {
      if (this.airCleaner) {
        return 'translate(-20, 0)'
      }

      return 'translate(0, 0)'
    },
    transformEverything() {
      if (this.largerVolume) {
        return 'translate(50, 50)'
      } else {
        return 'translate(0, 0)'
      }
    },
    heightAndWidth() {
      if (this.largerVolume) {
        return '300'
      } else {
        return '200'
      }
    },
    colorScheme() {
      if (this.early && !this.largerVolume) {
        return this.colorSchemeEarly
      } else if (this.early && this.largerVolume){
        return this.colorSchemeEarlyAndLargerVolume
      } else if (this.airCleaner) {
        return this.colorSchemeEarlyAndLargerVolume
      }
      else {
        return this.colorSchemeLate
      }
    },
    colorSchemeEarly() {
      return [
        'yellow',
        'orange',
        'red',
        'rgb(174, 17, 0)'
      ]
    },
    colorSchemeEarlyAndLargerVolume() {
      return [
        '#9ACD32',
        'yellow',
        'orange',
        'rgb(174, 17, 0)'
      ]
    },
    colorSchemeLate() {
      return [
        'red',
        'red',
        'red',
        'rgb(174, 17, 0)'
    ]
    },
  }, methods: {
  }

}
</script>

<style scoped>
</style>
