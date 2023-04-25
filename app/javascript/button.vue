<template>
  <div :class='{button: true, major: major, selected: selected, shadow: sidePadded, "side-padded": true}' :style='{"background-color": backgroundColor}'>
{{text}}
  <slot></slot>
</div>
</template>

<script>
export default {
  name: 'Button',
  components: {
  },
  data() {
    return {}
  },
  props: {
    disabled: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      default: ''
    },
    major: Boolean,
    shadow: {
      type: Boolean,
      default: false
    },
    selected: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    backgroundColor() {
      if (this.disabled) {
        return '#eee'
      } else if (this.major) {
        return 'rgb(219, 21, 0)'

      } else if (this.selected) {
        return '#e6e6e6'
      }
      else {
        return 'rgb(200,200,200)'
      }
    },
    sidePadded() {
      return this.text.length > 0
    }
  }, methods: {
  }

}
</script>

<style scoped>
  .side-padded {
    padding-left: 0.5em;
    padding-right: 0.5em;
    padding-top: 0.5em;
    padding-bottom: 0.5em;
  }
  .button {
    font-weight: bold;
    border: none;
    text-align: center;
    font-size: 1.5em;
    color: white;
    background-color: ;
  }
  .button:hover {
    cursor: pointer;
  }

  .selected {
    border-bottom: 4px solid black;
  }


  .shadow {
    text-shadow: 1px 1px 2px black;
  }

  @media(max-width: 800px) {
  }
</style>
