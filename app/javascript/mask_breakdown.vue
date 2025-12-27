<template>
  <div class="mask-breakdown-container">
    <div class="header">
      <h1>Mask Breakdown Classification</h1>
      <p class="subtitle">Classify tokens in mask names to improve matching accuracy</p>
    </div>

    <!-- Progress Bar -->
    <div class="progress-section" v-if="masks.length > 0">
      <div class="progress-stats">
        <span class="stat">
          <strong>{{ completedCount }}</strong> / {{ totalCount }} masks completed
        </span>
        <span class="stat">
          <strong>{{ remainingCount }}</strong> remaining
        </span>
        <span class="stat">
          Progress: <strong>{{ progressPercentage }}%</strong>
        </span>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progressPercentage + '%' }"></div>
      </div>
    </div>

    <!-- Filter Controls -->
    <div class="filter-controls" v-if="masks.length > 0">
      <label>
        <input type="radio" value="all" v-model="filterMode" />
        Show All ({{ totalCount }})
      </label>
      <label>
        <input type="radio" value="incomplete" v-model="filterMode" />
        Show Incomplete Only ({{ remainingCount }})
      </label>
      <label>
        <input type="radio" value="complete" v-model="filterMode" />
        Show Complete Only ({{ completedCount }})
      </label>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <p>Loading masks...</p>
    </div>

    <!-- No Masks -->
    <div v-else-if="filteredMasks.length === 0" class="no-masks">
      <p v-if="filterMode === 'incomplete'">🎉 All masks have been classified!</p>
      <p v-else>No masks found.</p>
    </div>

    <!-- Current Mask Classification -->
    <div v-else-if="currentMask" class="classification-section">
      <div class="mask-header">
        <h2>{{ currentMask.unique_internal_model_code }}</h2>
        <div class="mask-meta">
          <span>Mask {{ currentMaskIndex + 1 }} of {{ filteredMasks.length }}</span>
          <span v-if="currentMask.breakdown_user">
            Last edited by: {{ currentMask.breakdown_user.email }}
          </span>
          <span v-if="currentMask.breakdown_updated_at">
            {{ formatDate(currentMask.breakdown_updated_at) }}
          </span>
        </div>
      </div>

      <!-- Token Classification -->
      <div class="tokens-section">
        <h3>Classify each token:</h3>
        <div class="tokens-grid">
          <div
            v-for="(token, index) in currentMask.tokens"
            :key="index"
            class="token-row"
          >
            <div class="token-label">
              <span class="token-text">{{ token }}</span>
            </div>
            <div class="token-category">
              <select
                v-model="tokenCategories[index]"
                @change="onCategoryChange"
                class="category-select"
              >
                <option value="">-- Select Category --</option>
                <option
                  v-for="category in categories"
                  :key="category"
                  :value="category"
                >
                  {{ formatCategory(category) }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Category Legend -->
      <div class="legend">
        <h4>Category Definitions:</h4>
        <ul>
          <li><strong>brand:</strong> Manufacturer name (e.g., "3M", "Zimi")</li>
          <li><strong>model:</strong> Model number/name (e.g., "9205+", "7711")</li>
          <li><strong>color:</strong> Color description (e.g., "Black", "White")</li>
          <li><strong>style:</strong> Style type (e.g., "Surgical", "Tri-fold")</li>
          <li><strong>strap:</strong> Strap type (e.g., "Headstraps", "Earloops")</li>
          <li><strong>filter_type:</strong> Filter rating (e.g., "N95", "KN95", "P100")</li>
          <li><strong>size:</strong> Size designation (e.g., "Small", "Large", "Regular")</li>
          <li><strong>valved:</strong> Indicates valve presence (e.g., "Valved")</li>
          <li><strong>misc:</strong> Other tokens (e.g., "w/", "for", "with")</li>
        </ul>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button
          @click="previousMask"
          :disabled="currentMaskIndex === 0"
          class="btn btn-secondary"
        >
          ← Previous
        </button>

        <button
          @click="skipMask"
          class="btn btn-secondary"
        >
          Skip
        </button>

        <button
          @click="saveBreakdown"
          :disabled="saving || !hasAnyLabels"
          class="btn btn-primary"
        >
          {{ saving ? 'Saving...' : 'Save & Next →' }}
        </button>
      </div>

      <!-- Messages -->
      <div v-if="messages.length > 0" class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          {{ message.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { setupCSRF } from './misc.js'

export default {
  name: 'MaskBreakdown',
  data() {
    return {
      masks: [],
      categories: [],
      currentMaskIndex: 0,
      tokenCategories: [],
      loading: true,
      saving: false,
      messages: [],
      filterMode: 'incomplete', // 'all', 'incomplete', 'complete'
    }
  },
  computed: {
    filteredMasks() {
      if (this.filterMode === 'incomplete') {
        return this.masks.filter(m => !m.breakdown_complete)
      } else if (this.filterMode === 'complete') {
        return this.masks.filter(m => m.breakdown_complete)
      }
      return this.masks
    },
    currentMask() {
      return this.filteredMasks[this.currentMaskIndex] || null
    },
    totalCount() {
      return this.masks.length
    },
    completedCount() {
      return this.masks.filter(m => m.breakdown_complete).length
    },
    remainingCount() {
      return this.totalCount - this.completedCount
    },
    progressPercentage() {
      if (this.totalCount === 0) return 0
      return Math.round((this.completedCount / this.totalCount) * 100)
    },
    hasAnyLabels() {
      return this.tokenCategories.some(cat => cat && cat !== '')
    }
  },
  async mounted() {
    await this.loadMasks()
  },
  methods: {
    async loadMasks() {
      this.loading = true
      this.messages = []

      try {
        const response = await axios.get('/mask_breakdowns.json')
        this.masks = response.data.masks
        this.categories = response.data.categories

        // Initialize with first mask
        if (this.currentMask) {
          this.initializeTokenCategories()
        }
      } catch (error) {
        this.messages.push({
          type: 'error',
          text: `Error loading masks: ${error.response?.data?.error || error.message}`
        })
      } finally {
        this.loading = false
      }
    },
    initializeTokenCategories() {
      if (!this.currentMask) return

      // Initialize array with empty strings or existing breakdown
      this.tokenCategories = this.currentMask.tokens.map((token, index) => {
        const existingBreakdown = this.currentMask.breakdown.find(
          b => Object.keys(b)[0] === token
        )
        return existingBreakdown ? Object.values(existingBreakdown)[0] : ''
      })
    },
    onCategoryChange() {
      // Clear messages when user makes changes
      this.messages = []
    },
    async saveBreakdown() {
      if (!this.currentMask || this.saving) return

      setupCSRF()
      this.saving = true
      this.messages = []

      try {
        // Build breakdown array (only include labeled tokens)
        const breakdown = []
        this.currentMask.tokens.forEach((token, index) => {
          const category = this.tokenCategories[index]
          if (category && category !== '') {
            breakdown.push({ [token]: category })
          }
        })

        // Determine if creating or updating
        const url = this.currentMask.breakdown_id
          ? `/mask_breakdowns/${this.currentMask.breakdown_id}.json`
          : '/mask_breakdowns.json'

        const method = this.currentMask.breakdown_id ? 'put' : 'post'

        const payload = {
          mask_id: this.currentMask.id,
          breakdown: breakdown
        }

        const response = await axios[method](url, payload)

        if (response.data.success) {
          // Update local mask data
          const maskIndex = this.masks.findIndex(m => m.id === this.currentMask.id)
          if (maskIndex >= 0) {
            this.masks[maskIndex].breakdown = breakdown
            this.masks[maskIndex].breakdown_id = response.data.breakdown.id
            this.masks[maskIndex].breakdown_complete = response.data.breakdown.complete
            this.masks[maskIndex].breakdown_updated_at = response.data.breakdown.updated_at
            this.masks[maskIndex].breakdown_user = response.data.breakdown.user
          }

          this.messages.push({
            type: 'success',
            text: '✓ Breakdown saved successfully!'
          })

          // Auto-advance to next mask after short delay
          setTimeout(() => {
            this.nextMask()
          }, 500)
        }
      } catch (error) {
        this.messages.push({
          type: 'error',
          text: `Error saving breakdown: ${error.response?.data?.errors?.join(', ') || error.message}`
        })
      } finally {
        this.saving = false
      }
    },
    nextMask() {
      if (this.currentMaskIndex < this.filteredMasks.length - 1) {
        this.currentMaskIndex++
        this.initializeTokenCategories()
        this.messages = []
      } else {
        this.messages.push({
          type: 'info',
          text: 'You have reached the end of the list!'
        })
      }
    },
    previousMask() {
      if (this.currentMaskIndex > 0) {
        this.currentMaskIndex--
        this.initializeTokenCategories()
        this.messages = []
      }
    },
    skipMask() {
      this.nextMask()
    },
    formatCategory(category) {
      return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    }
  },
  watch: {
    filterMode() {
      // Reset to first mask when filter changes
      this.currentMaskIndex = 0
      this.initializeTokenCategories()
      this.messages = []
    }
  }
}
</script>

<style scoped>
.mask-breakdown-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
}

.progress-section {
  background: #f5f5f5;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.stat {
  font-size: 1rem;
}

.progress-bar-container {
  width: 100%;
  height: 30px;
  background: #e0e0e0;
  border-radius: 15px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  transition: width 0.3s ease;
}

.filter-controls {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-controls label {
  cursor: pointer;
  font-size: 1rem;
}

.filter-controls input[type="radio"] {
  margin-right: 0.5rem;
}

.loading, .no-masks {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #666;
}

.classification-section {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 2rem;
}

.mask-header {
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.mask-header h2 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.mask-meta {
  display: flex;
  gap: 2rem;
  color: #666;
  font-size: 0.9rem;
  flex-wrap: wrap;
}

.tokens-section {
  margin-bottom: 2rem;
}

.tokens-section h3 {
  margin-bottom: 1rem;
}

.tokens-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.token-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.token-label {
  font-weight: 500;
}

.token-text {
  font-family: 'Courier New', monospace;
  font-size: 1.1rem;
  color: #333;
}

.category-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.category-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.legend {
  background: #f0f8ff;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border-left: 4px solid #2196F3;
}

.legend h4 {
  margin-top: 0;
  color: #2196F3;
}

.legend ul {
  margin: 0;
  padding-left: 1.5rem;
}

.legend li {
  margin-bottom: 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #616161;
}

.messages {
  margin-top: 1rem;
}

.message {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

@media (max-width: 768px) {
  .token-row {
    grid-template-columns: 1fr;
  }

  .progress-stats {
    flex-direction: column;
    align-items: center;
  }

  .filter-controls {
    flex-direction: column;
    align-items: center;
  }
}
</style>
