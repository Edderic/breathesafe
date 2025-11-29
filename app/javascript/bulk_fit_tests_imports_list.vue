<template>
  <div class="bulk-imports-list">
    <div class="header-section">
      <h1>Bulk Fit Tests Imports</h1>
      <router-link :to="{ name: 'NewBulkFitTestsImport' }">
        <Button shadow="true" class="button" text="New import" />
      </router-link>
    </div>

    <div v-if="messages.length > 0" class="messages-section">
      <ClosableMessage
        v-for="(message, index) in messages"
        :key="index"
        :messages="[message]"
      />
    </div>

    <div class="filters-section">
      <div class="filter-group">
        <label for="status-filter">Filter by Status:</label>
        <select
          id="status-filter"
          v-model="statusFilter"
          @change="applyFilters"
          class="filter-select"
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="sort-by">Sort by:</label>
        <select
          id="sort-by"
          v-model="sortBy"
          @change="applyFilters"
          class="filter-select"
        >
          <option value="created_at_desc">Newest First</option>
          <option value="created_at_asc">Oldest First</option>
          <option value="source_name_asc">Source Name (A-Z)</option>
          <option value="source_name_desc">Source Name (Z-A)</option>
          <option value="status_asc">Status (A-Z)</option>
          <option value="status_desc">Status (Z-A)</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-section">
      <p>Loading imports...</p>
    </div>

    <div v-else-if="filteredImports.length > 0" class="imports-table-section">
      <table class="imports-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Source Name</th>
            <th>Status</th>
            <th>Number of Fit Tests</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="importItem in filteredImports"
            :key="importItem.id"
            class="import-row"
            @click="navigateToImport(importItem.id)"
          >
            <td>{{ importItem.id }}</td>
            <td>{{ importItem.source_name }}</td>
            <td>
              <span :class="`status-badge status-${importItem.status}`">
                {{ importItem.status }}
              </span>
            </td>
            <td>{{ importItem.fit_tests_to_add }} ({{ importItem.fit_tests_added }})</td>
            <td @click.stop>
              <Button
                shadow="true"
                class="button delete-button"
                text="Delete"
                @click="confirmDelete(importItem)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-section">
      <p>No bulk imports found.</p>
    </div>

    <!-- Delete Confirmation Popup -->
    <Popup v-if="showDeleteConfirmation" @onclose="cancelDelete">
      <div class="delete-confirmation-content">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete this bulk import?</p>
        <p><strong>{{ deleteTarget?.source_name }}</strong></p>
        <div class="delete-confirmation-buttons">
          <Button shadow="true" class="button" text="Cancel" @click="cancelDelete" />
          <Button shadow="true" class="button delete-button" text="Delete" @click="performDelete" />
        </div>
      </div>
    </Popup>
  </div>
</template>

<script>
import axios from 'axios'
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import Popup from './pop_up.vue'
import { setupCSRF } from './misc.js'

export default {
  name: 'BulkFitTestsImportsList',
  components: {
    Button,
    ClosableMessage,
    Popup
  },
  data() {
    return {
      imports: [],
      loading: false,
      messages: [],
      statusFilter: '',
      sortBy: 'created_at_desc',
      showDeleteConfirmation: false,
      deleteTarget: null
    }
  },
  computed: {
    filteredImports() {
      let filtered = [...this.imports]

      // Apply status filter
      if (this.statusFilter) {
        filtered = filtered.filter(importItem => importItem.status === this.statusFilter)
      }

      // Apply sorting
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'created_at_desc':
            return new Date(b.created_at) - new Date(a.created_at)
          case 'created_at_asc':
            return new Date(a.created_at) - new Date(b.created_at)
          case 'source_name_asc':
            return (a.source_name || '').localeCompare(b.source_name || '')
          case 'source_name_desc':
            return (b.source_name || '').localeCompare(a.source_name || '')
          case 'status_asc':
            return (a.status || '').localeCompare(b.status || '')
          case 'status_desc':
            return (b.status || '').localeCompare(a.status || '')
          default:
            return 0
        }
      })

      return filtered
    }
  },
  async mounted() {
    setupCSRF()
    await this.loadImports()
  },
  methods: {
    async loadImports() {
      this.loading = true
      this.messages = []

      try {
        const response = await axios.get('/bulk_fit_tests_imports.json')

        if (response.status === 200 && response.data.bulk_fit_tests_imports) {
          this.imports = response.data.bulk_fit_tests_imports
        } else {
          this.messages = [{ str: 'Failed to load imports.' }]
        }
      } catch (error) {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.$router.push({ name: 'SignIn' })
          return
        }

        this.messages = [{ str: 'Error loading imports.' }]
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      // Filters are applied via computed property
    },
    navigateToImport(id) {
      this.$router.push({ name: 'BulkFitTestsImport', params: { id } })
    },
    confirmDelete(importItem) {
      this.deleteTarget = importItem
      this.showDeleteConfirmation = true
    },
    cancelDelete() {
      this.showDeleteConfirmation = false
      this.deleteTarget = null
    },
    async performDelete() {
      if (!this.deleteTarget) {
        return
      }

      try {
        const response = await axios.delete(`/bulk_fit_tests_imports/${this.deleteTarget.id}.json`)

        if (response.status === 200) {
          // Remove from list
          this.imports = this.imports.filter(importItem => importItem.id !== this.deleteTarget.id)
          this.messages = [{ str: 'Import deleted successfully.' }]
        } else {
          const errorMessages = response.data.messages || ['Failed to delete import.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.$router.push({ name: 'SignIn' })
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to delete import.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.cancelDelete()
      }
    }
  }
}
</script>

<style scoped>
.bulk-imports-list {
  padding: 2em;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2em;
}

.header-section h1 {
  margin: 0;
}

.filters-section {
  display: flex;
  gap: 2em;
  margin-bottom: 2em;
  padding: 1em;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5em;
}

.filter-group label {
  font-weight: 500;
}

.filter-select {
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.imports-table-section {
  margin-top: 2em;
}

.imports-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.imports-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
}

.imports-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.import-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.import-row:hover {
  background-color: #f8f9fa;
}

.status-badge {
  padding: 0.25em 0.75em;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
  text-transform: capitalize;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-processing {
  background-color: #cce7ff;
  color: #004085;
}

.status-completed {
  background-color: #d4edda;
  color: #155724;
}

.status-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.delete-button {
  background-color: #dc3545;
  color: white;
}

.delete-button:hover {
  background-color: #c82333;
}

.delete-confirmation-content {
  padding: 1em;
}

.delete-confirmation-content h3 {
  margin-top: 0;
}

.delete-confirmation-buttons {
  display: flex;
  gap: 1em;
  margin-top: 1em;
  justify-content: flex-end;
}

.loading-section,
.empty-section {
  text-align: center;
  padding: 2em;
  color: #6c757d;
}

.messages-section {
  margin-bottom: 1em;
}
</style>
