<template>

    <div class='row align-items-center justify-content-center' v-if='!showStat'>
      <h2 class='title row align-items-center justify-content-center'>
        <div v-html='icon' class='icon'></div>
        {{title}}
      </h2>
      <CircularButton class='showHideButton' text='?' @click='show = !show'/>
    </div>

    <div class='explainer' v-if='!showStat && show'>
      <slot></slot>
    </div>

    <tr v-if='showStat'>
      <td class='bold'>

        <div class='row align-items-center justify-content-center'>
          <h3 class='title'>{{title}}</h3>
          <CircularButton class='showHideButton' text='?' @click='show = !show'/>
        </div>
      </td>

      <td class='second-td' v-if='showStat'>
        <ColoredCell
            :colorScheme="colorScheme"
            :maxVal=1
            :value='value'
            :text='text'
            :style="styleProps"
        />
      </td>
    </tr>
    <tr v-if='show && showStat'>
      <td colspan='2'>
        <div class='explainer'>
          <slot></slot>
        </div>
      </td>
    </tr>
</template>

<script>
import { round } from './misc.js'
import { co2ColorScheme } from './colors.js'
import ColoredCell from './colored_cell.vue'
import CircularButton from './circular_button.vue'

export default {
  name: 'DrillDownSection',
  components: {
    ColoredCell,
    CircularButton,
  },
  data() {
    return { show: false}
  },
  props: {
    icon: String,
    title: String,
    value: Number,
    text: {
      type: String
    },
    colorScheme: {
      default: {},
      type: Object
    },
    showStat: {
      default: true,
      type: Boolean
    }
  },
  computed: {
    styleProps() {
      return {
          'font-weight': 'bold',
          'color': 'white',
          'text-shadow': '1px 1px 2px black',
          'padding': '1em'
        }
    },
  }, methods: {
  }

}
</script>

<style scoped>
  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .align-items-center {
    display: flex;
    align-items: center;
  }


  .explainer {
    max-width: 25em;
    margin: 0 auto;
  }

  .second-td {
    width: 8em;
  }

  .title {
    max-width: 12em;
    margin-left: 1em;
  }

  .showHideButton {
    margin-left: 1em;
    margin-right: 1em;
  }

  .icon {
    padding-right: 0.5em;
  }

  .row {
    display: flex;
    flex-direction: row;
  }
</style>
