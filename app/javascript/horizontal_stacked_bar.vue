<template>
  <table>
    <tr v-for='(v, key, z) in values'>
      <td class='v-ticks' :style='{ "padding-top": verticalPadding, "padding-bottom": verticalPadding}'>{{key}}</td>
      <td>
      <div class='bar' :style='{"background-color": this.color(z), "width": this.width(v), "padding-top": verticalPadding, "padding-bottom": verticalPadding }'>{{v}}</div>
      </td>
    </tr>
  </table>
</template>

<script>
// Have a VueX store that maintains state across components
import { round } from './misc.js'

export default {
  name: 'HorizontalStackedBar',
  components: {
  },
  computed: {
    normalizer: function() {
      let sum = 0
      for (let v in this.values) {
        sum += parseFloat(this.values[v])
      }
      return sum
    }
  },
  props: {
    'values': Object,
    'colors': Array,
    'verticalPadding': {
      default: '1em'
    }
  },
  methods: {
    width: function(v) {
       return `${round(parseFloat(v) / this.normalizer * 30, 0) + 1}em`
    },
    color: function(i) {
      return this.colors[i]
    }
  }
}

</script>

<style scoped>
  td {
    height: 1em;
  }

  .bar {
    color: white;
    text-shadow: 1px 1px 2px black;
    font-weight: bold;
    padding: 1em;
  }

  .v-ticks {
    font-weight: bold;
    padding: 1em;
  }
</style>
