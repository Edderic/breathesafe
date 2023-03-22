<template>
  <div :class='{container: true, row: true, centered: true, menu: true, "background-color": backgroundColor}'>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'Menu',
  components: {
  },
  data() {
    return {}
  },
  props: {
    backgroundColor: {
      type: String,
      default: '#eee'
    }
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
  .menu {
    min-width: 500px;
    margin-top: 0;
    margin-bottom: 0;
  }

  .menu button {
    border: 0;
    background-color: #eee;
  }

  .menu .tab-item {
    border-top: 4px solid #eee;
  }

  .menu button.selected, .menu .button.selected {
    background-color: #cacaca;
  }

</style>
