<template>
  <span class='pair' :class='{ selected: selected }'>
    <div class='circle' :style='{"background-color": color, "border": border }'>&nbsp;</div>
    <div class='text'>{{color}}</div>
  </span>
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
      },
      selected: {
        default: false
      }
    },
    computed: {
      border() {
        if (this.selected) {
          return '2px solid black';
        }
        else {
          return `2px solid ${this.color}`;
        }
      }

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
  .pair:hover {
    cursor:pointer;
  }

  .text {
    color: #aaa;
    margin-left: 1em;
  }

  .selected {
  }
  .selected .text {
    color: black;
  }
</style>
