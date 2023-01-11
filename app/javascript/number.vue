<template>
  <div>
      <CircularButton v-for='leftButton in leftButtons' :text='leftButton.text' @click='send(leftButton.emitSignal, leftButton.text)'/>
      <input
        type='number'
        :value='value'
        @change='change'
      >
      <CircularButton v-for='rightButton in rightButtons' :text='rightButton.text' @click='send(rightButton.emitSignal, rightButton.text)'/>
  </div>
</template>

<script>
import CircularButton from './circular_button.vue';

export default {
  name: 'Number',
  components: {
    CircularButton,
  },
  data() {
    return {}
  },
  props: {
    leftButtons: Array,
    rightButtons: Array,
    value: Number
  },
  computed: {

  },
  methods: {
    change(event) {
      this.$emit('update', event.target.value)
    },
    send(method, args) {
      this.$emit(method, args)
    }
  }

}
</script>

<style scoped>
  input {
    height: 2em;
    margin-left: 1em;
    margin-right: 1em;

    width: 3em;
    font-weight: bold;
    font-size: 24px;
    margin-left: 0.5em;
    margin-right: 0.5em;
    text-align: center;
  }

  input[type='number'] {
    width: 2em;
    font-size: 24px;
  }
</style>
