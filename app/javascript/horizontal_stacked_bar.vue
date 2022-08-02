<template>
  <table>
    <tr v-for='(v, key, z) in values'>
      <td class='v-ticks'>{{key}}</td>
      <td>
      <div class='bar' :style='{"background-color": this.color(z), "width": this.width(v)}'>{{v}}</div>
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
      console.log("this.values", this.values);
      return sum
    }
  },
  props: {
    'values': Object,
    'colors': Array
  },
  methods: {
    width: function(v) {
       console.log(`${round(parseFloat(v) / this.normalizer * 50, 0) + 1}em`)
       return `${round(parseFloat(v) / this.normalizer * 50, 0) + 1}em`
    },
    color: function(i) {
       console.log(this.colors[i])
      return this.colors[i]
    }
  }
}

</script>

<style scoped>
  td {
    height: 2em;
  }

  .bar {
    color: white;
    padding: 1em;
    text-shadow: '1px 1px 2px black';
    font-weight: bold;
  }

  .v-ticks {
    font-weight: bold;
    padding: 1em;
  }
</style>
