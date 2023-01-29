<template>
  <div :class='{button: true, major: major, selected: selected, shadow: sidePadded, "side-padded": sidePadded}'>
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
    padding-left: 1em;
    padding-right: 1em;
    padding-top: 1em;
    padding-bottom: 1em;
  }
  .button {
    margin-top: 1em;
    margin-bottom: 1em;
    font-weight: bold;
    border: none;
    text-align: center;
    font-size: 1.5em;
    color: white;
    background-color: #eee;
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
