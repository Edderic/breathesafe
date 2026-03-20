<template>
  <div class="admin-mask-fit-families container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h3 mb-0">Mask Fit Families</h1>
      <button class="btn btn-outline-primary" :disabled="loading" @click="refreshCurrentPage">
        Refresh
      </button>
    </div>

    <div class="card mb-3">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col-md-5">
            <label class="form-label">Search model code</label>
            <input
              v-model.trim="search"
              class="form-control"
              type="text"
              placeholder="e.g. Trident"
              @keyup.enter="applyFilters"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">Current Fit Family</label>
            <select v-model="familyFilter" class="form-select">
              <option value="">All</option>
              <option v-for="family in fitFamilies" :key="family.id" :value="String(family.id)">
                {{ family.name }} (#{{ family.id }})
              </option>
            </select>
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-primary" @click="applyFilters">Apply</button>
            <button class="btn btn-outline-secondary" @click="clearFilters">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-3">
      <div class="card-body">
        <div class="row g-2 align-items-end">
          <div class="col-md-8">
            <label class="form-label">New Fit Family Name</label>
            <input
              v-model.trim="newFamilyName"
              class="form-control"
              type="text"
              placeholder="e.g. Trident Regular family"
              @keyup.enter="createFitFamily"
            >
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-success" :disabled="creatingFamily" @click="createFitFamily">
              Create Fit Family
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger mb-3">
      {{ error }}
    </div>
    <div v-if="message" class="alert alert-success mb-3">
      {{ message }}
    </div>

    <div
      v-if="selectedFamilySummary && selectedFamilyMismatchBadges.length"
      class="alert alert-warning d-flex flex-wrap gap-2 align-items-center"
    >
      <strong class="me-2">
        {{ selectedFamilySummary.name }} (#{{ selectedFamilySummary.id }}) has custom_lr-relevant mismatches:
      </strong>
      <span
        v-for="badge in selectedFamilyMismatchBadges"
        :key="badge.field"
        class="badge text-bg-warning"
        :title="badge.title"
      >
        {{ badge.label }}
      </span>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2 mb-0">Loading masks...</p>
    </div>

    <div v-else class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Model Code</th>
                <th>Current Fit Family</th>
                <th>Perimeter</th>
                <th>Style</th>
                <th>Strap</th>
                <th>Family Warnings</th>
                <th style="min-width: 240px;">Assign To Fit Family</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mask in filteredMasks" :key="mask.id">
                <td>{{ mask.id }}</td>
                <td class="code-col">{{ mask.unique_internal_model_code }}</td>
                <td>
                  <span v-if="fitFamilyLookup[mask.fit_family_id]">
                    {{ fitFamilyLookup[mask.fit_family_id].name }}
                    <span class="text-muted">#{{ mask.fit_family_id }}</span>
                  </span>
                  <span v-else class="text-muted">Unknown</span>
                </td>
                <td>{{ displayValue(mask.perimeter_mm) }}</td>
                <td>{{ displayValue(mask.style) }}</td>
                <td>{{ displayValue(mask.strap_type) }}</td>
                <td>
                  <div v-if="familyMismatchBadges(mask).length" class="d-flex flex-wrap gap-1">
                    <span
                      v-for="badge in familyMismatchBadges(mask)"
                      :key="`${mask.id}-${badge.field}`"
                      class="badge text-bg-warning"
                      :title="badge.title"
                    >
                      {{ badge.label }}
                    </span>
                  </div>
                  <span v-else class="text-muted">None</span>
                </td>
                <td>
                  <select
                    class="form-select form-select-sm"
                    :value="targetFitFamilyIds[mask.id] || String(mask.fit_family_id)"
                    @change="targetFitFamilyIds[mask.id] = $event.target.value"
                  >
                    <option v-for="family in fitFamilies" :key="family.id" :value="String(family.id)">
                      {{ family.name }} (#{{ family.id }})
                    </option>
                  </select>
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button
                      class="btn btn-sm btn-primary"
                      :disabled="isBusy(mask.id)"
                      @click="assignFitFamily(mask)"
                    >
                      Assign
                    </button>
                    <router-link
                      class="btn btn-sm btn-outline-secondary"
                      :to="{ name: 'ShowMask', params: { id: mask.id } }"
                    >
                      Open
                    </router-link>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredMasks.length === 0">
                <td colspan="9" class="text-center py-4 text-muted">No masks found for current filters.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card-footer d-flex justify-content-between align-items-center">
        <span class="text-muted">
          Showing {{ filteredMasks.length }} on page {{ currentPage }} ({{ totalCount }} total)
        </span>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-secondary" :disabled="currentPage <= 1" @click="changePage(currentPage - 1)">
            Previous
          </button>
          <button class="btn btn-sm btn-outline-secondary" :disabled="currentPage >= totalPages" @click="changePage(currentPage + 1)">
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { setupCSRF } from './misc.js'

export default {
  name: 'AdminMaskFitFamilies',
  data() {
    return {
      loading: false,
      creatingFamily: false,
      error: '',
      message: '',
      masks: [],
      fitFamilies: [],
      search: '',
      familyFilter: '',
      currentPage: 1,
      perPage: 50,
      totalPages: 1,
      totalCount: 0,
      targetFitFamilyIds: {},
      busyMaskIds: {},
      newFamilyName: ''
    }
  },
  computed: {
    filteredMasks() {
      if (!this.familyFilter) return this.masks
      return this.masks.filter(mask => String(mask.fit_family_id) === String(this.familyFilter))
    },
    fitFamilyLookup() {
      return this.fitFamilies.reduce((lookup, family) => {
        lookup[family.id] = family
        return lookup
      }, {})
    },
    selectedFamilySummary() {
      if (!this.familyFilter) return null
      return this.fitFamilyLookup[this.familyFilter] || null
    },
    selectedFamilyMismatchBadges() {
      const family = this.selectedFamilySummary
      if (!family || !family.mismatch_summary) return []
      return this.mismatchBadgesForFamily(family)
    }
  },
  async mounted() {
    await this.loadFitFamilies()
    await this.loadMasks(1)
  },
  methods: {
    isBusy(maskId) {
      return !!this.busyMaskIds[maskId]
    },
    setBusy(maskId, value) {
      this.busyMaskIds = {
        ...this.busyMaskIds,
        [maskId]: value
      }
    },
    clearMessages() {
      this.error = ''
      this.message = ''
    },
    displayValue(value) {
      if (value === null || value === undefined || value === '') return 'Missing'
      return value
    },
    familyMismatchBadges(mask) {
      const family = this.fitFamilyLookup[mask.fit_family_id]
      return this.mismatchBadgesForFamily(family)
    },
    mismatchBadgesForFamily(family) {
      if (!family || !family.mismatch_summary) return []

      const fields = [
        { field: 'perimeter_mm', label: 'Perimeter mismatch' },
        { field: 'style', label: 'Style mismatch' },
        { field: 'strap_type', label: 'Strap mismatch' }
      ]
      return fields
        .filter(({ field }) => family.mismatch_summary[field]?.mismatch)
        .map(({ field, label }) => ({
          field,
          label,
          title: `${label}: ${family.mismatch_summary[field].values.join(', ')}`
        }))
    },
    async loadFitFamilies() {
      const response = await axios.get('/admin/fit_families.json')
      this.fitFamilies = response.data.fit_families || []
    },
    async loadMasks(page = 1) {
      this.loading = true
      this.clearMessages()
      try {
        const response = await axios.get('/masks.json', {
          params: {
            page: page,
            per_page: this.perPage,
            search: this.search || undefined,
            filter_available: false
          }
        })
        this.masks = response.data.masks || []
        this.currentPage = response.data.page || page
        this.perPage = response.data.per_page || this.perPage
        this.totalCount = response.data.total_count || 0
        this.totalPages = Math.max(1, Math.ceil(this.totalCount / this.perPage))
      } catch (error) {
        this.error = error.response?.data?.error || error.message
      } finally {
        this.loading = false
      }
    },
    async refreshCurrentPage() {
      await this.loadFitFamilies()
      await this.loadMasks(this.currentPage)
    },
    async applyFilters() {
      await this.loadMasks(1)
    },
    async clearFilters() {
      this.search = ''
      this.familyFilter = ''
      await this.loadMasks(1)
    },
    async changePage(page) {
      if (page < 1 || page > this.totalPages) return
      await this.loadMasks(page)
    },
    async createFitFamily() {
      this.clearMessages()
      if (!this.newFamilyName) {
        this.error = 'Fit family name is required.'
        return
      }

      this.creatingFamily = true
      try {
        setupCSRF()
        const response = await axios.post('/admin/fit_families.json', {
          fit_family: {
            name: this.newFamilyName
          }
        })
        const fitFamily = response.data.fit_family
        this.fitFamilies = [...this.fitFamilies, fitFamily].sort((a, b) => a.name.localeCompare(b.name))
        this.message = `Created fit family "${fitFamily.name}".`
        this.newFamilyName = ''
      } catch (error) {
        this.error = error.response?.data?.error || error.message
      } finally {
        this.creatingFamily = false
      }
    },
    async assignFitFamily(mask) {
      this.clearMessages()
      const fitFamilyId = this.targetFitFamilyIds[mask.id] || String(mask.fit_family_id)
      if (!fitFamilyId) {
        this.error = `Mask #${mask.id}: fit family is required.`
        return
      }

      this.setBusy(mask.id, true)
      try {
        setupCSRF()
        await axios.put(`/admin/masks/${mask.id}/fit_family.json`, {
          mask_fit_family: {
            fit_family_id: Number(fitFamilyId)
          }
        })
        this.message = `Assigned mask #${mask.id} to fit family #${fitFamilyId}.`
        await this.refreshCurrentPage()
      } catch (error) {
        this.error = error.response?.data?.error || error.message
      } finally {
        this.setBusy(mask.id, false)
      }
    }
  }
}
</script>

<style scoped>
.code-col {
  word-break: break-word;
}
</style>
