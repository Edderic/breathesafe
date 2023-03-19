<template>
  <div class='container row centered menu'>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: '',
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
  .menu {
    min-width: 500px;
    background-color: #eee;
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
