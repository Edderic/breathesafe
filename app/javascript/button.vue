<template>
  <div :class='{button: true, major: major, selected: selected, shadow: sidePadded, "side-padded": true}'>
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
    background-color: rgb(200,200,200);
  }
  .button:hover {
    cursor: pointer;
  }

  .selected {
    background-color: #e6e6e6;
    border-bottom: 4px solid black;
  }

  .major {
    background-color: rgb(219, 21, 0);
  }

  .shadow {
    text-shadow: 1px 1px 2px black;
  }

  @media(max-width: 800px) {
  }
</style>
