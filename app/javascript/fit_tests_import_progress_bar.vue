<template>
  <div class="fit-test-progress-container" :class="{ 'mobile-sticky': isMobile, 'desktop-sidebar': !isMobile }">
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
            'not-started': !isStepCompleted(step.key) && currentStep !== step.key
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
          <span
            class="step-status"
            v-if="getStepStatus(step.key) !== ''"
          >
            {{ getStepStatus(step.key) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FitTestsImportProgressBar',
  props: {
    sourceName: {
      type: String,
      default: null
    },
    importedFile: {
      type: Object,
      default: null
    },
    columnMatching: {
      type: Object,
      default: null
    },
    userMatching: {
      type: Object,
      default: null
    },
    maskMatching: {
      type: Object,
      default: null
    },
    userSealCheckMatching: {
      type: Object,
      default: null
    },
    fitTestDataMatching: {
      type: Object,
      default: null
    },
    completedSteps: {
      type: Array,
      default: () => []
    },
    currentStep: {
      type: String,
      default: 'Import File'
    }
  },
  data() {
    return {
      isMobile: false,
      allSteps: [
        { key: 'Import File', name: 'Import File' },
        { key: 'Column Matching', name: 'Column Matching' },
        { key: 'User Matching', name: 'User Matching' },
        { key: 'Mask Matching', name: 'Mask Matching' },
        { key: 'User Seal Check Matching', name: 'User Seal Check Matching' },
        { key: 'Fit Test Data Matching', name: 'Fit Test Data Matching' },
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

      // Import File step is completed if sourceName exists (from saved import) or importedFile exists (new import)
      if (this.sourceName || (this.importedFile && this.importedFile.name)) {
        completed.push('Import File')
      }

      // Column Matching step is completed if columnMatching exists and is complete
      if (this.columnMatching && this.isColumnMatchingComplete()) {
        completed.push('Column Matching')
      }

      // User Matching step is completed if userMatching exists and is complete
      if (this.userMatching && this.isUserMatchingComplete()) {
        completed.push('User Matching')
      }

      // Mask Matching step is completed if maskMatching exists and is complete
      if (this.maskMatching && this.isMaskMatchingComplete()) {
        completed.push('Mask Matching')
      }

      // User Seal Check Matching step is completed if userSealCheckMatching exists and is complete
      if (this.userSealCheckMatching && this.isUserSealCheckMatchingComplete()) {
        completed.push('User Seal Check Matching')
      }

      // Fit Test Data Matching step is completed if fitTestDataMatching exists and is complete
      if (this.fitTestDataMatching && this.isFitTestDataMatchingComplete()) {
        completed.push('Fit Test Data Matching')
      }

      // Add other steps from props if provided
      this.completedSteps.forEach(step => {
        if (!completed.includes(step)) {
          completed.push(step)
        }
      })

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
    getStepStatus(stepKey) {
      // Remove status text - visual indicators (checkmarks, circles) are sufficient
      return ''
    },
    getStepValue(stepKey) {
      switch (stepKey) {
        case 'Import File':
          // Prefer sourceName (from saved import), fallback to importedFile.name (new import)
          if (this.sourceName) {
            return this.sourceName
          }
          return (this.importedFile && this.importedFile.name) ? this.importedFile.name : 'Not Selected'
        case 'Column Matching':
          if (this.columnMatching && this.isColumnMatchingComplete()) {
            return 'Columns Matched'
          }
          return 'Not Selected'
        case 'User Matching':
          if (this.userMatching && this.isUserMatchingComplete()) {
            return 'Users Matched'
          }
          return 'Not Selected'
        case 'Mask Matching':
          if (this.maskMatching && this.isMaskMatchingComplete()) {
            return 'Masks Matched'
          }
          return 'Not Selected'
        case 'User Seal Check Matching':
          if (this.userSealCheckMatching && this.isUserSealCheckMatchingComplete()) {
            return 'User Seal Checks Matched'
          }
          return 'Not Selected'
        case 'Fit Test Data Matching':
          if (this.fitTestDataMatching && this.isFitTestDataMatchingComplete()) {
            return 'Fit Test Data Matched'
          }
          return 'Not Selected'
        default:
          return this.getStepStatus(stepKey)
      }
    },
    getStepDisplayValue(stepKey) {
      const value = this.getStepValue(stepKey)

      // For all steps that show actual values, show actual values or "Not Selected"
      const stepsWithValues = ['Import File', 'Column Matching', 'User Matching', 'Mask Matching', 'User Seal Check Matching', 'Fit Test Data Matching']

      if (stepsWithValues.includes(stepKey)) {
        if (value === 'Not Selected' || !value) {
          return 'Not Selected'
        }
        // Ensure value is a string before calling .length
        const stringValue = String(value)
        // Truncate to 30 characters
        return stringValue.length > 30 ? stringValue.substring(0, 30) + '...' : stringValue
      }

      // For other steps, show status
      return value || 'Not Started'
    },
    navigateToStep(stepKey) {
      // Emit event to parent component to change the current step
      this.$emit('navigate-to-step', stepKey)
    },
    isColumnMatchingComplete() {
      // Placeholder: return true if column matching is complete
      return this.columnMatching && Object.keys(this.columnMatching).length > 0
    },
    isUserMatchingComplete() {
      // Placeholder: return true if user matching is complete
      return this.userMatching && Object.keys(this.userMatching).length > 0
    },
    isMaskMatchingComplete() {
      // Placeholder: return true if mask matching is complete
      return this.maskMatching && Object.keys(this.maskMatching).length > 0
    },
    isUserSealCheckMatchingComplete() {
      // Placeholder: return true if user seal check matching is complete
      return this.userSealCheckMatching && Object.keys(this.userSealCheckMatching).length > 0
    },
    isFitTestDataMatchingComplete() {
      // Placeholder: return true if fit test data matching is complete
      return this.fitTestDataMatching && Object.keys(this.fitTestDataMatching).length > 0
    }
  }
}
</script>

<style scoped>
.fit-test-progress-container {
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

.step-status {
  font-size: 0.8rem;
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
}

.step-item.completed .step-status {
  background-color: #d4edda;
  color: #155724;
}

.step-item.current .step-status {
  background-color: #cce7ff;
  color: #004085;
}

.step-item.not-started .step-status {
  background-color: #f8f9fa;
  color: #6c757d;
}

.step-item .step-value.not-selected {
  color: #dc3545;
  font-weight: 500;
}

.step-item.completed .step-value:not(.not-selected) {
  color: #28a745;
  font-weight: 500;
}

/* Mobile-specific styles */
@media (max-width: 1000px) {
  .desktop-sidebar {
    position: static;
    width: 97vw;
    max-height: 15em;
    margin-bottom: 1rem;
  }

  .fit-test-progress-container {
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

  .step-status {
    font-size: 0.75rem;
  }
}
</style>
