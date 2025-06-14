<template>
  <div class="scatter-plot">
    <h3 class="title">{{ title }}</h3>
    <svg :width="width" :height="height" class="plot">
      <!-- X-axis -->
      <line
        :x1="margin"
        :y1="height - margin"
        :x2="width - margin"
        :y2="height - margin"
        stroke="black"
      />
      <text
        :x="width/2"
        :y="height - margin/2"
        text-anchor="middle"
      >
        {{ xLabel }}
      </text>
      <!-- X-axis limits -->
      <text
        :x="margin"
        :y="height - margin/2"
        text-anchor="start"
        class="axis-limit"
      >
        {{ x_lim[0] }}
      </text>
      <text
        :x="width - margin"
        :y="height - margin/2"
        text-anchor="end"
        class="axis-limit"
      >
        {{ x_lim[1] }}
      </text>

      <!-- Y-axis -->
      <line
        :x1="margin"
        :y1="margin"
        :x2="margin"
        :y2="height - margin"
        stroke="black"
      />
      <text
        :x="margin/2"
        :y="height/2"
        text-anchor="middle"
        :transform="`rotate(-90, ${margin/2}, ${height/2})`"
      >
        {{ yLabel }}
      </text>
      <!-- Y-axis limits -->
      <text
        :x="margin/1.25"
        :y="height - margin"
        text-anchor="end"
        class="axis-limit"
      >
        {{ y_lim[0] }}
      </text>
      <text
        :x="margin/1.25"
        :y="margin"
        text-anchor="end"
        class="axis-limit"
      >
        {{ y_lim[1] }}
      </text>

      <!-- Data points -->
      <g v-for="(point, index) in normalizedPoints" :key="index">
        <circle
          :cx="getX(point.x)"
          :cy="getY(point.y)"
          :r="pointRadius"
          :fill="point.color || defaultColor"
          :stroke="point.borderColor || 'black'"
          :stroke-width="point.borderWidth || 1"
          :stroke-dasharray="point.borderStyle || 'none'"
        />
      </g>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'ScatterPlot',
  props: {
    title: {
      type: String,
      required: true
    },
    xLabel: {
      type: String,
      required: true
    },
    yLabel: {
      type: String,
      required: true
    },
    xAxisName: {
      type: String,
      required: true
    },
    yAxisName: {
      type: String,
      required: true
    },
    points: {
      type: Array,
      required: true,
      validator: (points) => {
        return points.every(point =>
          typeof point.x === 'number' &&
          typeof point.y === 'number'
        )
      }
    },
    x_lim: {
      type: Array,
      default: () => [null, null],
      validator: (arr) => {
        return arr.length === 2 &&
          (arr[0] === null || typeof arr[0] === 'number') &&
          (arr[1] === null || typeof arr[1] === 'number')
      }
    },
    y_lim: {
      type: Array,
      default: () => [null, null],
      validator: (arr) => {
        return arr.length === 2 &&
          (arr[0] === null || typeof arr[0] === 'number') &&
          (arr[1] === null || typeof arr[1] === 'number')
      }
    },
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 300
    },
    margin: {
      type: Number,
      default: 30
    },
    pointRadius: {
      type: Number,
      default: 4
    },
    defaultColor: {
      type: String,
      default: '#4CAF50'
    }
  },
  computed: {
    normalizedPoints() {
      if (this.points.length === 0) return []

      // Find min and max values for both axes
      const xValues = this.points.map(p => p.x)
      const yValues = this.points.map(p => p.y)

      // Use provided limits if available, otherwise use data min/max
      const xMin = this.x_lim[0] !== null ? this.x_lim[0] : Math.min(...xValues)
      const xMax = this.x_lim[1] !== null ? this.x_lim[1] : Math.max(...xValues)
      const yMin = this.y_lim[0] !== null ? this.y_lim[0] : Math.min(...yValues)
      const yMax = this.y_lim[1] !== null ? this.y_lim[1] : Math.max(...yValues)

      // Add some padding to the ranges if using data min/max
      const xRange = xMax - xMin
      const yRange = yMax - yMin
      const xPadding = this.x_lim[0] === null ? xRange * 0.1 : 0
      const yPadding = this.y_lim[0] === null ? yRange * 0.1 : 0

      return this.points.map(point => ({
        ...point,
        x: (point.x - (xMin - xPadding)) / (xRange + 2 * xPadding),
        y: (point.y - (yMin - yPadding)) / (yRange + 2 * yPadding)
      }))
    }
  },
  methods: {
    getX(x) {
      return this.margin + (this.width - 2 * this.margin) * x
    },
    getY(y) {
      return this.height - this.margin - (this.height - 2 * this.margin) * y
    }
  }
}
</script>

<style scoped>
.scatter-plot {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1em;
}

.plot {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.title {
  text-align: center;
  margin-bottom: 1em;
}

text {
  font-size: 12px;
  font-family: Arial, sans-serif;
}

.axis-limit {
  font-size: 10px;
  fill: #666;
}
</style>
