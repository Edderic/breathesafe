<template>
  <div class="initial-cost-bar-graph">
    <div v-if="isMissing" class="stat-bar-wrapper stat-bar-missing">
      <div class="stat-bar-axis"></div>
      <div class="stat-bar stat-bar-missing-fill"></div>
      <div class="stat-bar-label">{{ missingText }}</div>
    </div>
    <div v-else class="stat-bar-wrapper" :style="statBarWrapperStyle">
      <div class="stat-bar-axis"></div>
      <div class="stat-bar" :style="statBarStyle"></div>
      <div class="stat-bar-marker" :style="statMarkerStyle"></div>
      <div class="stat-bar-cover" :style="statCoverStyle"></div>
      <div class="stat-bar-label">{{ valueLabel }}</div>
      <div class="stat-bar-tick stat-bar-tick-left">{{ maxLabel }}</div>
      <div class="stat-bar-tick stat-bar-tick-right">{{ minLabel }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InitialCostBarGraph',
  props: {
    value: {
      type: [Number, String],
      default: null
    },
    maxValue: {
      type: [Number, String],
      default: null
    },
    missingText: {
      type: String,
      default: 'Missing'
    }
  },
  computed: {
    numericValue() {
      return Number(this.value)
    },
    numericMax() {
      return Number(this.maxValue)
    },
    isMissing() {
      return !Number.isFinite(this.numericValue) || this.numericValue <= 0 || !Number.isFinite(this.numericMax) || this.numericMax <= 0
    },
    percent() {
      if (this.isMissing) {
        return null
      }
      const scaled = Math.log1p(Math.max(0, this.numericValue)) / Math.log1p(this.numericMax)
      return Math.max(0, Math.min(1, 1 - scaled))
    },
    statBarWrapperStyle() {
      return { background: this.costGradient() }
    },
    statBarStyle() {
      if (this.percent === null) {
        return {}
      }
      return {
        width: '100%',
        backgroundColor: 'transparent'
      }
    },
    statMarkerStyle() {
      if (this.percent === null) {
        return {}
      }
      const position = Math.round(this.percent * 10000) / 100
      return {
        left: `calc(${position}% - 1px)`
      }
    },
    statCoverStyle() {
      if (this.percent === null) {
        return {}
      }
      const position = Math.round(this.percent * 10000) / 100
      return {
        left: `calc(${position}% + 1px)`,
        backgroundColor: '#f1f1f1'
      }
    },
    valueLabel() {
      return this.formatCurrency(this.numericValue)
    },
    maxLabel() {
      return this.formatCurrency(this.numericMax)
    },
    minLabel() {
      return this.formatCurrency(0)
    }
  },
  methods: {
    costGradient() {
      const red = '#c0392b'
      const yellow = '#f1c40f'
      const green = '#27ae60'
      return `linear-gradient(90deg, ${red} 0%, ${yellow} 33%, ${green} 100%)`
    },
    formatCurrency(value) {
      if (!Number.isFinite(value)) {
        return this.missingText
      }
      return `$${Number(value).toFixed(2)}`
    }
  }
}
</script>

<style scoped>
.initial-cost-bar-graph {
  min-width: 9em;
  max-width: 14em;
}

.stat-bar-wrapper {
  position: relative;
  height: 2.25em;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.4em;
  background-color: #f1f1f1;
  overflow: hidden;
}

.stat-bar-axis {
  position: absolute;
  left: 0.5em;
  right: 0.5em;
  bottom: 0.35em;
  height: 2px;
  background-color: rgba(0, 0, 0, 0.2);
  z-index: 1;
}

.stat-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  border-radius: 0.4em;
  opacity: 0.9;
}

.stat-bar-marker {
  position: absolute;
  width: 2px;
  top: 0;
  bottom: 0;
  background-color: #ffffff;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.6);
  z-index: 2;
}

.stat-bar-cover {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;
  z-index: 1;
}

.stat-bar-label {
  position: relative;
  z-index: 3;
  font-weight: bold;
  color: #111;
  text-shadow: 1px 1px 2px #fff;
}

.stat-bar-tick {
  position: absolute;
  bottom: 0.15em;
  font-size: 0.7em;
  color: #333;
  opacity: 0.75;
  z-index: 1;
}

.stat-bar-tick-left {
  left: 0.4em;
}

.stat-bar-tick-right {
  right: 0.4em;
}

.stat-bar-missing {
  background-color: #e0e0e0;
}

.stat-bar-missing-fill {
  width: 100%;
  background-color: #b5b5b5;
}
</style>
