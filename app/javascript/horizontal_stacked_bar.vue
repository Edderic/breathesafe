<template>

    <tbody>
    <tr v-for='(v, key, z) in values'>
      <td class='v-ticks' :style='{ "padding-top": verticalPadding, "padding-bottom": verticalPadding}'>{{key}}</td>
      <td>{{v}}</td>
      <td>
        <div class='bar' :style='{"background-color": this.colorScheme[z], "width": this.width(v), "padding-top": verticalPadding, "padding-bottom": verticalPadding }'></div>
      </td>
    </tr>
    </tbody>
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
    },
    colorScheme: function() {
      let dict = this.values

      let dictLength = Object.keys(dict).length
      let collection = []

      for(var i = 0; i < dictLength; i++) {
        collection.push(this.colors[i % this.colors.length])
      }

      return collection
    },
  },
  props: {
    'values': Object,
    'maxBarWidth': {
      type: Number,
      default: 5
    },
    'colors': {
      type: Array,
      default: ['red', 'orange', 'yellow', 'green', 'blue', 'purple']

    },
    'verticalPadding': {
      default: '0em'
    }
  },
  methods: {

    width: function(v) {
       return `${round(parseFloat(v) / this.normalizer, 2) * this.maxBarWidth}em`
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
    display: inline-block;
    height: 1.5em;
    min-width: 1px;
  }

  .v-ticks {
    font-weight: bold;
    padding: 1em;
    text-align: end;
  }
</style>
