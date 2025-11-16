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
    facialHair: {
      type: Object,
      default: null
    },
    userSealCheck: {
      type: Object,
      default: null
    },
    qualitativeProcedure: {
      type: String,
      default: null
    },
    quantitativeProcedure: {
      type: String,
      default: null
    },
    fitTestProcedure: {
      type: String,
      default: null
    },
    comfort: {
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
        { key: 'Fit Test', name: 'Fit Test' },
        { key: 'Comfort', name: 'Comfort Assessment' },
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

      // User Seal Check is completed if all questions are answered
      if (this.isUserSealCheckComplete()) {
        completed.push('User Seal Check')
      }

      // Fit Test is completed if fitTestProcedure is set (or old structure has a procedure)
      if (this.fitTestProcedure ||
          (this.qualitativeProcedure && this.qualitativeProcedure !== 'Skipping') ||
          (this.quantitativeProcedure && this.quantitativeProcedure !== 'Skipping')) {
        completed.push('Fit Test')
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
        case 'User':
          return (this.selectedUser && this.selectedUser.fullName) ? this.selectedUser.fullName : 'Not Selected'
        case 'Mask':
          return (this.selectedMask && this.selectedMask.uniqueInternalModelCode) ? this.selectedMask.uniqueInternalModelCode : 'Not Selected'
        case 'Facial Hair':
          if (this.facialHair && this.facialHair.beard_length_mm && this.facialHair.beard_cover_technique) {
            return `${this.facialHair.beard_length_mm}, ${this.facialHair.beard_cover_technique}`
          }
          return 'Not Selected'
        case 'User Seal Check':
          return this.evaluateUserSealCheck()
        case 'Fit Test':
          if (this.fitTestProcedure) {
            // Map internal values to display names
            const procedureMap = {
              'qualitative_full_osha': 'qualitative: Full OSHA',
              'quantitative_osha_fast': 'quantitative: OSHA Fast Face Piece Respirators',
              'quantitative_full_osha': 'quantitative: Full OSHA'
            }
            return procedureMap[this.fitTestProcedure] || this.fitTestProcedure
          }
          // Fallback to old structure for backwards compatibility
          if (this.qualitativeProcedure && this.qualitativeProcedure !== 'Skipping') {
            return `qualitative: ${this.qualitativeProcedure}`
          }
          if (this.quantitativeProcedure && this.quantitativeProcedure !== 'Skipping') {
            return `quantitative: ${this.quantitativeProcedure}`
          }
          return 'Not Selected'
        case 'Comfort':
          if (this.comfort && this.isComfortComplete()) {
            const comfortCount = Object.values(this.comfort).filter(value => value !== null).length
            return `${comfortCount} questions answered`
          }
          return 'Not Selected'
        default:
          return this.getStepStatus(stepKey)
      }
    },
    getStepDisplayValue(stepKey) {
      const value = this.getStepValue(stepKey)

      // For all steps that show actual values, show actual values or "Not Selected"
      const stepsWithValues = ['User', 'Mask', 'Facial Hair', 'User Seal Check', 'Fit Test', 'Comfort']

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
    // Evaluates user seal check using the same logic as UserSealCheckService
    // Returns 'Passed', 'Failed', or 'Not Selected' (for incomplete)
    evaluateUserSealCheck() {
      if (!this.userSealCheck) return 'Not Selected'

      const sizingQuestion = 'What do you think about the sizing of this mask relative to your face?'
      const airMovementQuestion = '...how much air movement on your face along the seal of the mask did you feel?'

      const sizing = this.userSealCheck.sizing && this.userSealCheck.sizing[sizingQuestion]
      const airMovement = this.userSealCheck.positive && this.userSealCheck.positive[airMovementQuestion]

      // Check if sizing question is missing
      if (!sizing || sizing.toString().trim() === '') {
        return 'Not Selected'
      }

      // Check if air movement question is missing
      if (!airMovement || airMovement.toString().trim() === '') {
        return 'Not Selected'
      }

      // Fail if "Too big" or "Too small" is selected
      if (sizing.toString() === 'Too big' || sizing.toString() === 'Too small') {
        return 'Failed'
      }

      // Fail if "A lot of air movement" is selected
      if (airMovement.toString() === 'A lot of air movement') {
        return 'Failed'
      }

      // Pass if "Somewhere in-between too small and too big" AND ("Some air movement" OR "No air movement")
      if (sizing.toString() === 'Somewhere in-between too small and too big') {
        if (airMovement.toString() === 'Some air movement' || airMovement.toString() === 'No air movement') {
          return 'Passed'
        }
      }

      // If we get here, the combination doesn't match our pass criteria
      return 'Not Selected'
    },
    isUserSealCheckComplete() {
      const result = this.evaluateUserSealCheck()
      return result === 'Passed'
    },
    isComfortComplete() {
      if (!this.comfort) return false
      return Object.values(this.comfort).every(value => value !== null)
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

/* Green styling for selected User and Mask values */
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
