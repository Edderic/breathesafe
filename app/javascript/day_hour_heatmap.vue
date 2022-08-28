<template>
  <table v-if='showable'>
    <tr>
      <th></th>
      <th v-for='hour in hours'>{{ hour }}</th>
    </tr>
    <tr v-for="day in ['Mondays', 'Tuesdays', 'Wednesdays', 'Thursdays', 'Fridays', 'Saturdays', 'Sundays']">
      <td>{{day}}</td>
      <td v-for='hour in hours'>
        <ColoredCell
          :key='day + "-" + hour'
          :value="val(day, hour)"
          :colorScheme="colorInterpolationScheme"
          :maxVal=100
        />
      </td>
    </tr>
  </table>
</template>

<script scoped>
// Have a VueX store that maintains state across components
import ColoredCell from './colored_cell.vue';
import { mapWritableState, mapState, mapActions } from 'pinia';
import {
  hourToIndex,
} from  './misc';

export default {
  name: 'DayHourHeatmap',
  components: {
    ColoredCell,
    Event
  },
  computed: {
    showable() {
      return !!this.dayHours['Mondays']
    },
    hours() {
      let minimumHour;
      let minimumIndex = 23;
      let maximumHour = '11 PM';
      let maximumIndex = 0;

      if (!this.dayHours['Mondays']) {
        return []
      }

      let maxHours = '11 PM'

      for (let day in this.dayHours) {

        let hs = this.dayHours[day]

        for (let h in hs) {
          if (minimumIndex >= hourToIndex[h]) {
            minimumIndex = hourToIndex[h]
            minimumHour = h
          }

          if (maximumIndex <= hourToIndex[h]) {
            maximumIndex = hourToIndex[h]
            maximumHour = h
          }
        }
      }

      let collect = false
      let collection = []

      for (let hour in hourToIndex) {
        if (hour == minimumHour) {
          collect = true
        }

        if (collect) {
          let maybePrefixedWithBlankSpace = hour
          if (hour.length == 4) {
            maybePrefixedWithBlankSpace = "0"  + hour
          }
          collection.push(maybePrefixedWithBlankSpace)
        }

        if (hour == maximumHour) {
          collect = false
        }
      }

      return collection
    },
  },
  async created() {
  },
  data() {
    return {
      colorInterpolationScheme: [
        {
          'lowerBound': -0.00001,
          'upperBound': 1 / 6,
          'lowerColor': {
            name: 'dark green',
            r: 11,
            g: 161,
            b: 3
          },
          'upperColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
        },
        {
          'lowerBound': 1 / 6,
          'upperBound': 2 / 6,
          'lowerColor': {
            name: 'green',
            r: 87,
            g: 195,
            b: 40
          },
          'upperColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
        },
        {
          'lowerBound': 2 / 6,
          'upperBound': 3 / 6,
          'lowerColor': {
            name: 'yellow',
            r: 255,
            g: 233,
            b: 56
          },
          'upperColor': {
            name: 'yellowOrange',
            r: 254,
            g: 160,
            b: 8
          },
        },
        {
          'lowerBound': 3 / 6,
          'upperBound': 4 / 6,
          'lowerColor': {
            name: 'yellowOrange',
            r: 254,
            g: 160,
            b: 8
          },
          'upperColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
        },
        {
          'lowerBound': 4 / 6,
          'upperBound': 5 / 6,
          'lowerColor': {
            name: 'orangeRed',
            r: 240,
            g: 90,
            b: 0
          },
          'upperColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
        },
        {
          'lowerBound': 5 / 6,
          'upperBound': 1.01,
          'lowerColor': {
            name: 'red',
            r: 219,
            g: 21,
            b: 0
          },
          'upperColor': {
            name: 'darkRed',
            r: 174,
            g: 17,
            b: 0
          }
        },
      ],
    }
  },
  methods: {
    val(day, hour) {

      let noPrefixHour = hour

      if (hour[0] == '0') {
        noPrefixHour = hour.split('').splice(1).join('')
      }

      if (!!this.dayHours[day][noPrefixHour]) {
        return this.dayHours[day][noPrefixHour]['occupancyPercent']
      } else {
        return 0
      }
    },
  },
  props: {
    dayHours: Object
  }
}

</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    font-weight: bold;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  .row {
    display: flex;
    flex-direction: column;
  }

  .textarea-label {
    padding-top: 0;
  }

  th, tr {
    font-size: smaller;
  }

  textarea {
    width: 30em;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  .wider-input {
    width: 30em;
  }

  button {
    padding: 1em 3em;
  }

  table {
    text-align: center;
    border-spacing: 0;
  }
</style>
