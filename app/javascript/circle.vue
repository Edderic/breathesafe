<template>
  <div class='pair'>
    <div class='circle' :style='{"background-color": color}'>&nbsp;</div>
    <div class='text'>{{color}}</div>
  </div>
</template>

<script>
  export default {
    name: 'Circle',
    components: {
    },
    data() {
      return {
        colorOptions: {
          'White': {
            color: '#FFF',
          },
          'Black': {
            color: '#000'
          },
          'Blue': {
            color: '#00F'
          },
          'Grey': {
            color: '#aaa'
          },
          'Graphics': {
            color: '#aaa'
          },
          'Orange': {
            color: '#aaa'
          },
          'Green': {
            color: '#0F0'
          },
          'Purple': {
            color: '#F0F'
          },
          'Pink': {
            color: '#FFC0CB'
          },
          'Multicolored': {
            color: '#FFC0CB'
          }
        }
      }
    },
    props: {
      color: {
        default: 'White'
      }
    },
    computed: {

    },
    methods: {
    }
  }
</script>

<style scoped>
  .circle {
    border-radius: 100%;
    width: 1em;
    height: 1em;
    border: 1px solid black;
  }
  .pair {
    display: flex;
    flex-direction: row;
    align-items: center;
  }

  .text {
    margin-left: 1em;
  }
</style>
