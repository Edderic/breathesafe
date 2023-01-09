<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" :viewBox="viewBox" height='20em' width='30em'>
    <text x="10%" y="45%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em ">Concentration</text>
    <text x="55%" y="95%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em ">Time (min)</text>

    <path :d='yAxis' stroke='black' fill='black' stroke-width='100'/>
    <path :d='xAxis' stroke='black' fill='black' stroke-width='100'/>

    <path :d='path(line)' :stroke='line.color' fill='transparent' stroke-width='50' v-for='line in lines'/>

  </svg>
</template>

<script>
export default {
  name: 'LineGraph',
  components: {
  },
  data() {
    return {}
  },
  props: {
    lines: Array
  },
  computed: {
    viewBoxX() {
      return 15000
    },
    viewBoxY() {
      return 10000
    },

    viewBox() {
      return `0 0 ${this.viewBoxX} ${this.viewBoxY}`
    },

    yAxis() {
      return `m ${this.yAxisLineStart} L ${this.yAxisLineEnd}`
    },

    yAxisXStart() {
      return 0.23 * this.viewBoxX
    },

    yAxisYStart() {
      return 20
    },
    yAxisLineStart() {
      return `${this.yAxisXStart} ${this.yAxisYStart}`
    },

    yAxisLineEnd() {
      return `${this.yAxisXStart} ${this.yAxisYEnd}`
    },

    xAxis() {
      return `M ${this.yAxisLineEnd} ${this.xAxisLineEnd}`
    },

    xAxisLineEnd() {
      return `L ${this.xAxisXEnd} ${this.xAxisYEnd}`
    },

    xAxisYEnd() {
      return this.viewBoxY * 0.9
    },

    xAxisXEnd() {
      return this.viewBoxX * 0.9
    },

    xAxisXStart() {
      return this.viewBoxX * 0.23
    },

    yAxisXStart() {
      return this.viewBoxX * 0.23
    },

    yAxisYEnd() {
      return this.xAxisYEnd
    },



    xAxisNormalizer() {
      return parseFloat(this.xAxisXEnd) - parseFloat(this.xAxisXStart)
    },

    yAxisNormalizer() {
      return parseFloat(this.yAxisYEnd) - parseFloat(this.yAxisYStart)
    },

  },
  methods: {
    path(line) {
      let collection = ""
      let topX = this.maxX(line)
      let topY = this.maxY(line)

      let proportionX = 0;

      let c = 0

      let letter = ''

      for (let point of line.points) {
        if (c == 0) {
          letter = 'M'
        }
        else {
          letter = 'L'
        }

        collection += `${letter} ${point[0] / (line.points.length - 1) * this.xAxisNormalizer + this.xAxisXStart} ${this.yAxisYStart + (1- (point[1] / topY)) * this.yAxisNormalizer } `
        c += 1

      }

      return collection
    },

    maxX(line) {
      let tmpMax = -1000000

      for (let point of line.points) {
        if (point[0] > tmpMax)
          tmpMax = point[0]
      }

      return tmpMax
    },
    maxY(line) {
      let tmpMax = -1000000

      for (let point of line.points) {
        if (point[1] > tmpMax)
          tmpMax = point[1]
      }

      return tmpMax
    }



  }

}
</script>

<style scoped>
</style>
