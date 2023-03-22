<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" :viewBox="viewBox" height='20em' width='30em'>
    <text class='label' x="10%" y="45%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em" transform='translate(-3000, 6000) rotate(-90)'>{{ylabel}}</text>

    <text class='label' :x="xLabelX" y="95%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 20em ">{{xlabel}}</text>

    <text :x="xLabelX" y="2%" text-anchor="middle" fill="black" dy=".4em" style="font-size: 40em ">{{title}}</text>

    <path :d='yAxis' stroke='black' fill='black' :stroke-width='axisStrokeWidth'/>
    <path :d='xAxis' stroke='black' fill='black' :stroke-width='axisStrokeWidth'/>

    <path :d='xTicks' stroke='black' fill='black' stroke-width='100'/>
    <text v-for='(xTickLabel, index) in getXTickLabels' :x='getXTickLabelXPos(index, getXTickLabels.length)' :y='getXTickLabelYPos' text-anchor='middle'>{{xTickProcessed(xTickLabel)}}</text>

    <text v-for='(yTickLabel, index) in getYTickLabels' :x='getYTickLabelXPos' :y='getYTickLabelYPos(index, getYTickLabels.length)' text-anchor='middle' alignment-baseline='middle'>{{yTickProcessed(yTickLabel)}}</text>

    <path :d='path(line)' :stroke='line.color' fill='transparent' stroke-width='50' v-for='line in lines' />


    <path :d='legendBox' :stroke='legend.color' :fill='legend.color' stroke-width='10'/>

    <g v-for='(line, index) in lines'>
      <circle v-if='showHighlighter' :cx='highlighterX(line)' :cy='highlighterY(line)' r='100' :fill='line.color'/>
      <path :d='plotLegend(line, index)' :stroke='line.color' :fill='transparent' stroke-width='20' />
      <text :x='getXLegend(index)' :y='getYLegend(index)' anchor='middle' alignment-baseline='middle'>{{line.legend}}</text>
    </g>

  </svg>
</template>

<script>
import { round } from './misc.js'
export default {
  name: 'LineGraph',
  components: {
  },
  data() {
    return {
      showHighlighter: true
    }
  },
  props: {
    legend: {
      type: Object,
      default: {
        color: '#fcefd4'
      }
    },
    lines: Array,
    title: String,
    xlabel: String,
    ylabel: String,
    xHighlighter: Number,
    xTickLabels: Array,
    yTickLabels: Array,
    ylim: Array,
    setYTicksToPercentages: Boolean,
    roundYTicksTo: {
      type: Number,
      default: 2
    },
    roundXTicksTo: {
      type: Number,
      default: 2
    },
    legendStartOffset: {
      type: Array,
      default: [0.6, 0.4]
    }
  },
  computed: {
    legendStartX() {
      return this.legendStartOffset[0] * this.viewBoxX
    },
    legendStartY() {
      return this.legendStartOffset[1] * this.viewBoxY
    },
    legendBox() {
      return `M ${this.legendStartX} ${this.legendStartY} h ${this.legendWidth} v ${this.legendHeight} h -${this.legendWidth} z`
    },

    maxCharLengthLegend() {
      let maxLength = 0
      for (let line of this.lines) {
        if (line.legend.length > maxLength) {
          maxLength = line.legend.length
        }
      }

      return maxLength
    },

    legendWidth() {
      return 0.2 * this.viewBoxX + (this.maxCharLengthLegend - 7) * 0.01 * this.viewBoxX
    },
    legendHeight() {
      return this.legendOffsetY * (this.lines.length + 1)
    },
    globalMinX() {
      let gMinX = 1000000

      for (let line of this.lines) {
        for (let point of line.points) {
          if (point[0] < gMinX)
            gMinX = point[0]
        }
      }

      return gMinX
    },
    globalMinY() {
      if (this.ylim) {
        return this.ylim[0]
      }
      let gMinY = 1000000

      for (let line of this.lines) {
        for (let point of line.points) {
          if (point[1] < gMinY)
            gMinY = point[1]
        }
      }

      return gMinY
    },
    globalMaxX() {

      let gMaxX = -1000000

      for (let line of this.lines) {
        for (let point of line.points) {
          if (point[0] > gMaxX)
            gMaxX = point[0]
        }
      }

      return gMaxX
    },
    globalMaxY() {
      if (this.ylim) {
        return this.ylim[1]
      }
      let gMaxY = -1000000

      for (let line of this.lines) {
        for (let point of line.points) {
          if (point[1] > gMaxY)
            gMaxY = point[1]
        }
      }

      return gMaxY
    },
    getXTickLabels() {
      if (this.xTickLabels) {
        return this.xTickLabels
      }

      let xDiff = this.globalMaxX - this.globalMinX

      let collection = []
      let length = 5
      for (let i = 0; i < length; i++) {
        collection.push(this.globalMinX + xDiff * i / (length - 1))
      }

      return collection
    },
    getYTickLabels() {
      if (this.yTickLabels) {
        return this.yTickLabels
      }

      let xDiff = this.globalMaxY - this.globalMinY

      let collection = []
      let length = 5
      for (let i = 0; i < length; i++) {
        collection.push(this.globalMinY + xDiff * i / (length - 1))
      }

      return collection
    },

    xLabelX() {
      return this.yAxisXStart + this.xAxisNormalizer / 2
    },
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
      let len = this.getXTickLabels.length
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
    xAxisYStart() {
      return this.xAxisYEnd
    },

    yAxisXStart() {
      return this.xAxisXStart
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

    legendOffsetX() {
      return this.viewBoxX * 0.025
    },

    legendOffsetY() {
      return this.viewBoxY * 0.05
    },

    legendLineLength () {
      return this.viewBoxX * 0.05
    },

    legendXTextOffset() {
      return this.viewBoxX * 0.07
    }
  },
  methods: {
    highlighterX(line) {
      return this.convertXToPlottable(this.nearestPoint(line)[0])
    },
    highlighterY(line) {
      return this.convertYToPlottable(this.nearestPoint(line)[1])
    },
    nearestPoint(line) {
      if (line.points.length == 0 || !this.xHighlighter) {
        this.showHighlighter = false
        return [0, 0]
      }

      this.showHighlighter = true
      return line.points[parseInt(this.xHighlighter)]
    },
    getXLegend(index) {
      return `${this.legendStartX + this.legendOffsetX + this.legendXTextOffset}`
    },
    getYLegend(index) {
      return `${this.legendStartY + this.legendOffsetY * (index + 1)}`
    },
    plotLegend(line, index) {
      return `M ${this.legendStartX + this.legendOffsetX} ${this.getYLegend(index)} h ${this.legendLineLength}`
    },
    mouseover(event) {
      let offsetX = event.offsetX
      let offsetY = event.offsetY

      let element = event.srcElement
      let xNormalized = offsetX / element.clientWidth * this.viewBoxX
      let yNormalized = offsetY / element.clientHeight * this.viewBoxY

      if (this.pointWithinData(xNormalized, yNormalized)) {
        let nearestPoint = this.findNearestPoint(xNormalized, yNormalized)
        this.highlighterX = this.convertXToPlottable(nearestPoint[0])
        this.highlighterY = this.convertYToPlottable(nearestPoint[1])

        this.$emit('point', nearestPoint)
      }
    },

    findNearestPoint(x, y) {
      let line = this.lines[0]
      let xProportion = (x - this.xAxisXStart) / this.xAxisNormalizer
      let xIndex = parseInt(xProportion * line.points.length)

      return line.points[xIndex]
    },
    pointWithinData(xNormalized, yNormalized) {
      return this.xAxisXStart <= xNormalized && xNormalized <= this.xAxisXEnd
        && this.yAxisYStart <= yNormalized && yNormalized <= this.yAxisYEnd
    },
    yTickProcessed(yTick) {
      if (this.setYTicksToPercentages) {
        return `${round(yTick * 100, this.roundYTicksTo)}%`
      }

      return round(yTick, this.roundYTicksTo)
    },
    xTickProcessed(xTick) {
      return round(xTick, this.roundXTicksTo)
    },
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

        collection += `${letter} ${this.convertXToPlottable(point[0])} ${this.convertYToPlottable(point[1])} `
        c += 1

      }

      return collection
    },

    convertXToPlottable(x) {
      return x / (this.globalMaxX) * this.xAxisNormalizer + this.yAxisXStart
    },

    convertYToPlottable(y) {
      return this.yAxisYStart + (1- ((y - this.globalMinY)/ (this.globalMaxY - this.globalMinY))) * this.yAxisNormalizer
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

  .label {
    font-weight: bold;
  }

  svg {
    margin: 0 auto;
  }

  @media (max-width: 750px) {
    svg {
      width: 25em;
    }
  }
</style>
