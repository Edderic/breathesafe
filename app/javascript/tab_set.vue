<template>
    <div class='menu row' id='tabToShow'>
      <Button v-for="o in options" :class="{ tab: true }" @click='setTabThenTrigger(o)' shadow='true' :text='o.text' :selected="tabToShow==o.text"/>
    </div>

    <select id='tabToShowMobile' name="tabToShowSelect" @change='setTabThenTrigger'>
      <option v-for='option in options' :value="option.text">{{option.text}}</option>
    </select>
</template>

<script>
import Button from './button.vue'
import CircularButton from './circular_button.vue'

export default {
  name: 'TabSet',
  components: {
    Button,
    CircularButton,
  },
  data() {
  },
  props: {
    options: Array,
    tabToShow: String

  },
  computed: {
  },
  async created() {
  },
  methods: {
    setTabThenTrigger(option) {
      let val = option.text
      if (option['target'] && option['target']['value']) {
        val = option['target']['value']
      }

      this.$emit('update', {
        'name': val
      })
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }
  .text-for-other {
    margin: 0 1.25em;
  }

  .menu {
    justify-content:center;
    min-width: 500px;
    background-color: #eee;
    margin-top: 0;
    margin-bottom: 0;
  }
  .row {
    display: flex;
    flex-direction: row;
  }

  .row button {
    width: 100%;
    padding-top: 1em;
    padding-bottom: 1em;
  }


  .flex-dir-col {
    display: flex;
    flex-direction: column;
  }
  p {

    margin: 1em;
  }

  select {
    padding: 0.25em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }
  .label-input {
    align-items:center;
    justify-content:space-between;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  .adaptive-wide img {
    width: 100%;
  }
  img {
    width: 30em;
  }
  #tabToShowMobile {
    font-size: 1.5em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  @media(min-width: 700px) {
    #tabToShowMobile {
      display: none;
    }
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }

    #tabToShow {
      display: none;
    }
  }
</style>

