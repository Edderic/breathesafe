<template>
  <div class="fit-test-progress-container" :class="{ 'mobile-sticky': isMobile, 'desktop-sidebar': !isMobile }">
    <table class="fit-test-progress-table">
      <tbody>
        <tr>
          <th>Selected User</th>
          <td>{{ selectedUser ? selectedUser.fullName : 'Not Selected' }}</td>
        </tr>
        <tr>
          <th>Selected Mask</th>
          <td>{{ selectedMask ? selectedMask.uniqueInternalModelCode : 'Not Selected' }}</td>
        </tr>
      </tbody>
    </table>

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
        >
          <span class="step-indicator">
            <span v-if="isStepCompleted(step.key)" class="checkmark">✓</span>
            <span v-else-if="currentStep === step.key" class="current-indicator">●</span>
            <span v-else class="not-started-indicator">○</span>
          </span>
          <span class="step-name">{{ step.name }}</span>
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

.fit-test-progress-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.fit-test-progress-table th,
.fit-test-progress-table td {
  padding: 0.5rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.fit-test-progress-table th {
  background-color: #e9ecef;
  font-weight: bold;
  width: 40%;
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
  }

  .step-list {
    gap: 0.125rem;
  }
}
</style>