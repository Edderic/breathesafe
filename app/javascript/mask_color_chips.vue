<template>
  <div class="mask-color-chips">
    <button
      v-for="color in normalizedColors"
      :key="`mask-color-chip-${color}`"
      type="button"
      :class="chipClasses(color)"
      :title="color"
            @click="onChipClick(color)"
    >
      <span class="mask-color-chip-swatch" :style="swatchStyle(color)"></span>
      <span v-if="showLabels" class="mask-color-chip-label">{{ color }}</span>
    </button>
    <span v-if="normalizedColors.length === 0 && showMissingText">{{ missingText }}</span>
  </div>
</template>

<script>
export default {
  name: 'MaskColorChips',
  props: {
    colors: {
      type: Array,
      default: () => []
    },
    selectedColors: {
      type: Array,
      default: () => []
    },
    selectable: {
      type: Boolean,
      default: false
    },
    interactive: {
      type: Boolean,
      default: true
    },
    showLabels: {
      type: Boolean,
      default: false
    },
    showMissingText: {
      type: Boolean,
      default: true
    },
    missingText: {
      type: String,
      default: 'Missing'
    }
  },
  computed: {
    normalizedColors() {
      return (this.colors || [])
        .map((value) => String(value || '').trim())
        .filter((value, index, arr) => value && arr.indexOf(value) === index)
    }
  },
  methods: {
    swatchStyle(color) {
      const value = this.swatchColor(color)
      if (value.includes('gradient')) {
        return { background: value }
      }
      return { backgroundColor: value }
    },
    swatchColor(color) {
      const palette = {
        White: '#ffffff',
        Black: '#000000',
        Blue: '#2563eb',
        Grey: '#9ca3af',
        Graphics: 'repeating-linear-gradient(135deg, #0f172a 0 4px, #ffffff 4px 8px)',
        Orange: '#f97316',
        Green: '#22c55e',
        Purple: '#a855f7',
        Pink: '#ec4899',
        Multicolored: 'linear-gradient(135deg, #ef4444 0%, #f59e0b 33%, #22c55e 66%, #3b82f6 100%)'
      }
      return palette[color] || color
    },
    chipClasses(color) {
      return {
        'mask-color-chip': true,
        selectable: this.selectable && this.interactive,
        selected: this.selectedColors.includes(color)
      }
    },
    onChipClick(color) {
      if (!this.selectable || !this.interactive) {
        return
      }
      this.$emit('toggle', color)
    }
  }
}
</script>

<style scoped>
.mask-color-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3em;
  align-items: center;
  justify-content: center;
}

.mask-color-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: default;
}

.mask-color-chip.selectable {
  cursor: pointer;
}

.mask-color-chip-swatch {
  width: 0.95em;
  height: 0.95em;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 1);
  display: inline-block;
}

.mask-color-chip.selected .mask-color-chip-swatch {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.95), 0 0 0 4px rgba(0, 0, 0, 1);
}

.mask-color-chip-label {
  color: #444;
  font-size: 0.9em;
}
</style>
