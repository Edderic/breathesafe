<template>
  <div class='centered'>
      <CircularButton v-for='leftButton in leftButtons' :text='leftButton.text' @click='send(leftButton.emitSignal, {value: leftButton.text, identifier: identifier})'/>
      <input
        type='number'
        :value='value'
        @change='change'
      >
      <CircularButton v-for='rightButton in rightButtons' :text='rightButton.text' @click='send(rightButton.emitSignal, {value: rightButton.text, identifier: identifier})'/>
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
    value: Number,
    identifier: String
  },
  computed: {

  },
  methods: {
    change(event) {
      this.$emit('update', { value: event.target.value, identifier: this.identifier})
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
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }


  .centered {
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>
