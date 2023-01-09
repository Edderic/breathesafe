<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" :viewBox="viewBox" height='20em' width='30em'>
    <text x="10%" y="45%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em ">Concentration</text>
    <text x="55%" y="95%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em ">Time (min)</text>

    <path :d='yAxis' stroke='black' fill='black' :stroke-width='axisStrokeWidth'/>
    <path :d='xAxis' stroke='black' fill='black' :stroke-width='axisStrokeWidth'/>

    <path :d='xTicks' stroke='black' fill='black' stroke-width='100'/>
    <text v-for='(xTickLabel, index) in xTickLabels' :x='getXTickLabelXPos(index, xTickLabels.length)' :y='getXTickLabelYPos' text-anchor='middle'>{{xTickLabel}}</text>

    <text v-for='(yTickLabel, index) in yTickLabels' :x='getYTickLabelXPos' :y='getYTickLabelYPos(index, yTickLabels.length)' text-anchor='middle' alignment-baseline='middle'>{{yTickLabel}}</text>

    <path :d='path(line)' :stroke='line.color' fill='transparent' stroke-width='50' v-for='line in lines'/>

  </svg>
</template>

<script>
export default {
  name: 'LineGraph',
  components: {
  },
  data() {
    return {
      xTickLabels: [0, 10, 20, 30, 40],
      yTickLabels: [0, 250, 500, 750, 1000]
    }
  },
  props: {
    lines: Array
  },
  computed: {
    axisStrokeWidth() {
      return 100
    },
    xTickLength() {
      return 0.025 * this.viewBoxY
    },
    xTickAndxTickLabelSpacing() {
      return 0.025 * this.viewBoxY
    },
    yTickLength() {
      return 0.025 * this.viewBoxX
    },
    yTickAndyTickLabelSpacing() {
      return 0.025 * this.viewBoxX
    },
    getYTickLabelXPos() {
      return this.yAxisXStart - this.yTickLength - this.yTickAndyTickLabelSpacing
    },
    getXTickLabelYPos() {
      return this.yAxisYEnd + this.xTickLength + this.xTickAndxTickLabelSpacing
    },
    xTicks() {
      let collection = `M ${this.yAxisLineEnd} v ${this.xTickLength}`
      let len = this.xTickLabels.length
      for (let i = 0; i < len; i++) {

        collection += `M ${this.yAxisXStart + this.xAxisNormalizer * i / (len - 1)} ${this.xAxisYEnd} v ${this.xTickLength}`
      }
      return collection
    },
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

    yAxisXEnd() {
      return this.yAxisXStart
    },
    yAxisYStart() {
      return 1000
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
      return this.viewBoxY * 0.8
    },

    xAxisXEnd() {
      return this.viewBoxX * 0.9
    },

    xAxisXStart() {
      return this.viewBoxX * 0.23
    },

    yAxisXStart() {
      return this.viewBoxX * 0.3
    },

    yAxisYEnd() {
      return this.xAxisYEnd
    },



    xAxisNormalizer() {
      return parseFloat(this.xAxisXEnd) - parseFloat(this.yAxisXStart)
    },

    yAxisNormalizer() {
      return parseFloat(this.yAxisYEnd) - parseFloat(this.yAxisYStart)
    },

  },
  methods: {
    getXTickLabelXPos(i, len) {
      // Ideally this would be independent of y-Axis
      // But since we're only plotting in the first quadrant, it works
      return this.yAxisXStart + this.xAxisNormalizer * i / (len - 1)
    },
    getYTickLabelYPos(i, len) {
      return this.yAxisYStart + (1 - i / (len - 1)) * this.yAxisNormalizer
    },

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
  text {
    font-size: 20em;
  }
</style>
