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
          <span class="step-status">
            {{ getStepStatus(step.key) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddingDataToFitTestProgress',
  props: {
    selectedUser: {
      type: Object,
      default: null
    },
    selectedMask: {
      type: Object,
      default: null
    },
    completedSteps: {
      type: Array,
      default: () => []
    },
    currentStep: {
      type: String,
      default: 'User'
    }
  },
  data() {
    return {
      isMobile: false,
      allSteps: [
        { key: 'User', name: 'User Selection' },
        { key: 'Mask', name: 'Mask Selection' },
        { key: 'Facial Hair', name: 'Facial Hair Check' },
        { key: 'User Seal Check', name: 'User Seal Check' },
        { key: 'Comfort', name: 'Comfort Assessment' },
        { key: 'QLFT', name: 'Qualitative Fit Test' },
        { key: 'QNFT', name: 'Quantitative Fit Test' }
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

      // User step is completed if selectedUser exists
      if (this.selectedUser && this.selectedUser.fullName) {
        completed.push('User')
      }

      // Mask step is completed if selectedMask exists
      if (this.selectedMask && this.selectedMask.uniqueInternalModelCode) {
        completed.push('Mask')
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
      if (this.isStepCompleted(stepKey)) {
        return 'Complete'
      } else if (this.currentStep === stepKey) {
        return 'In Progress'
      } else {
        return 'Not Started'
      }
    },
    getStepValue(stepKey) {
      switch (stepKey) {
        case 'User':
          return this.selectedUser ? this.selectedUser.fullName : 'Not Selected'
        case 'Mask':
          return this.selectedMask ? this.selectedMask.uniqueInternalModelCode : 'Not Selected'
        default:
          return this.getStepStatus(stepKey)
      }
    },
    getStepDisplayValue(stepKey) {
      const value = this.getStepValue(stepKey)

      // For User and Mask, show actual values or "Not Selected"
      if (stepKey === 'User' || stepKey === 'Mask') {
        if (value === 'Not Selected') {
          return value
        }
        // Truncate to 30 characters
        return value.length > 30 ? value.substring(0, 30) + '...' : value
      }

      // For other steps, show status
      return value
    },
    navigateToStep(stepKey) {
      // Emit event to parent component to change the current step
      this.$emit('navigate-to-step', stepKey)
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
  top: 20px;
  right: 20px;
  width: 300px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}

/* Removed table styles since we removed the table */

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

/* Special styling for "Not Selected" values */
.step-value:contains("Not Selected") {
  color: #dc3545;
  font-weight: 500;
}

/* Alternative approach using CSS classes */
.step-item .step-value.not-selected {
  color: #dc3545;
  font-weight: 500;
}

/* Mobile-specific styles */
@media (max-width: 700px) {
  .desktop-sidebar {
    position: static;
    width: 100%;
    max-height: none;
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