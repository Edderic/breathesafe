<template>
  <div class="mask-progress-container" :class="{ 'mobile-sticky': isMobile, 'desktop-sidebar': !isMobile }">
    <div class="progress-steps">
      <h4>Progress</h4>
      <div class="step-list">
        <div
          v-for="step in allSteps"
          :key="step.key"
          class="step-item"
          :class="{
            'completed': isStepCompleted(step.key),
            'current': currentStep === step.key,
            'not-started': !isStepCompleted(step.key) && currentStep !== step.key,
          }"
          @click="navigateToStep(step.key)"
        >
          <span class="step-indicator">
            <span v-if="isStepCompleted(step.key)" class="checkmark">✓</span>
            <span v-else-if="currentStep === step.key" class="current-indicator">●</span>
            <span v-else class="not-started-indicator">○</span>
          </span>
          <span class="step-name">{{ step.name }}</span>
          <span
            class="step-value"
            :class="{ 'not-selected': getStepValue(step.key) === 'Not Selected' }"
            :title="getStepValue(step.key)"
          >
            {{ getStepDisplayValue(step.key) }}
          </span>
        </div>
      </div>
      <div class="progress-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaskProgressBar',
  props: {
    uniqueInternalModelCode: {
      type: String,
      default: ''
    },
    initialCostUsDollars: {
      type: Number,
      default: 0
    },
    colors: {
      type: Array,
      default: () => []
    },
    filterType: {
      type: String,
      default: ''
    },
    style: {
      type: String,
      default: ''
    },
    strapType: {
      type: String,
      default: ''
    },
    hasExhalationValve: {
      type: [Boolean, String],
      default: false
    },
    imageUrls: {
      type: Array,
      default: () => []
    },
    whereToBuyUrls: {
      type: Array,
      default: () => []
    },
    perimeterMm: {
      type: [Number, String],
      default: null
    },
    massGrams: {
      type: [Number, String],
      default: null
    },
    filtrationEfficiencies: {
      type: Array,
      default: () => []
    },
    breathability: {
      type: Array,
      default: () => []
    },
    currentStep: {
      type: String,
      default: 'Basic Info'
    }
  },
  data() {
    return {
      isMobile: false,
      allSteps: [
        { key: 'Basic Info', name: 'Basic Info' },
        { key: 'Image & Purchasing', name: 'Image & Purchasing' },
        { key: 'Dimensions', name: 'Dimensions' },
        { key: 'Filtration & Breathability', name: 'Filtration & Breathability' },
      ]
    }
  },
  mounted() {
    this.checkScreenSize()
    window.addEventListener('resize', this.checkScreenSize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize)
  },
  computed: {
    computedCompletedSteps() {
      const completed = []

      // Basic Info step is completed if all required fields are filled
      if (this.isBasicInfoComplete()) {
        completed.push('Basic Info')
      }

      // Image & Purchasing step is completed if at least one image URL exists
      if (this.isImagePurchasingComplete()) {
        completed.push('Image & Purchasing')
      }

      // Dimensions step is completed if perimeter is present
      if (this.isDimensionsComplete()) {
        completed.push('Dimensions')
      }

      // Filtration & Breathability step is completed if at least one entry exists
      if (this.isFiltrationBreathabilityComplete()) {
        completed.push('Filtration & Breathability')
      }

      return completed
    }
  },
  methods: {
    checkScreenSize() {
      this.isMobile = window.innerWidth < 700
    },
    isStepCompleted(stepKey) {
      return this.computedCompletedSteps.includes(stepKey)
    },
    isBasicInfoComplete() {
      return !!(
        this.uniqueInternalModelCode &&
        this.filterType &&
        this.style &&
        this.strapType &&
        (this.hasExhalationValve !== null && this.hasExhalationValve !== '')
      )
    },
    isImagePurchasingComplete() {
      return this.imageUrls && this.imageUrls.length > 0 && this.imageUrls[0] !== ''
    },
    isDimensionsComplete() {
      return !!(this.perimeterMm !== null && this.perimeterMm !== '')
    },
    isFiltrationBreathabilityComplete() {
      return this.filtrationEfficiencies && this.filtrationEfficiencies.length > 0
    },
    getStepValue(stepKey) {
      switch (stepKey) {
        case 'Basic Info':
          if (this.uniqueInternalModelCode) {
            return this.uniqueInternalModelCode
          }
          return 'Not Selected'
        case 'Image & Purchasing':
          if (this.isImagePurchasingComplete()) {
            const imageCount = this.imageUrls.filter(url => url !== '').length
            const purchaseCount = this.whereToBuyUrls.filter(url => url !== '').length
            return `${imageCount} image${imageCount !== 1 ? 's' : ''}, ${purchaseCount} link${purchaseCount !== 1 ? 's' : ''}`
          }
          return 'Not Selected'
        case 'Dimensions':
          if (this.isDimensionsComplete()) {
            let parts = []
            if (this.perimeterMm) parts.push(`${this.perimeterMm}mm perimeter`)
            if (this.massGrams) parts.push(`${this.massGrams}g`)
            return parts.join(', ')
          }
          return 'Not Selected'
        case 'Filtration & Breathability':
          if (this.isFiltrationBreathabilityComplete()) {
            return `${this.filtrationEfficiencies.length} entr${this.filtrationEfficiencies.length !== 1 ? 'ies' : 'y'}`
          }
          return 'Not Selected'
        default:
          return ''
      }
    },
    getStepDisplayValue(stepKey) {
      const value = this.getStepValue(stepKey)

      if (value === 'Not Selected' || !value) {
        return 'Not Selected'
      }

      // Ensure value is a string before calling .length
      const stringValue = String(value)
      // Truncate to 30 characters
      return stringValue.length > 30 ? stringValue.substring(0, 30) + '...' : stringValue
    },
    navigateToStep(stepKey) {
      // Emit event to parent component to change the current step
      this.$emit('navigate-to-step', stepKey)
    }
  }
}
</script>

<style scoped>
.mask-progress-container {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.mobile-sticky {
  position: sticky;
  top: 0;
  z-index: 100;
  margin-bottom: 1rem;
}

.desktop-sidebar {
  position: fixed;
  top: 3em;
  left: 0;
  height: 85vh;
  width: 300px;
  overflow-y: auto;
}

.progress-steps h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #495057;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.step-item {
  display: flex;
  align-items: center;
  padding: 0.25rem 0;
  font-size: 0.9rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.step-item:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.step-indicator {
  margin-right: 0.5rem;
  width: 1rem;
  text-align: center;
}

.checkmark {
  color: #28a745;
  font-weight: bold;
}

.current-indicator {
  color: #007bff;
  font-weight: bold;
}

.not-started-indicator {
  color: #6c757d;
}

.step-name {
  margin-left: 0.5em;
  margin-right: 0.5em;
  flex: 1;
  font-weight: 500;
  min-width: 120px;
}

.step-value {
  flex: 1;
  font-size: 0.85rem;
  margin-right: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

.step-item .step-value.not-selected {
  color: #dc3545;
  font-weight: 500;
}

.step-item.completed .step-value:not(.not-selected) {
  color: #28a745;
  font-weight: 500;
}

.progress-actions {
  margin-top: 0.5rem;
}

/* Mobile-specific styles */
@media (max-width: 1000px) {
  .desktop-sidebar {
    position: static;
    width: 97vw;
    max-height: 15em;
    margin-bottom: 1rem;
  }

  .mask-progress-container {
    margin-bottom: 0.5rem;
  }

  .step-item {
    font-size: 0.85rem;
    flex-wrap: wrap;
  }

  .step-list {
    gap: 0.125rem;
  }

  .step-name {
    min-width: 100px;
  }

  .step-value {
    max-width: 120px;
    font-size: 0.8rem;
  }
}
</style>
