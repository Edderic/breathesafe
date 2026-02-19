<template>
  <div class="admin-mask-duplicates container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h1 class="h3 mb-0">Mask Duplicates</h1>
      <button class="btn btn-outline-primary" :disabled="loading" @click="loadMasks(currentPage)">
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
              placeholder="e.g. 3M Aura"
              @keyup.enter="applyFilters"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">Status</label>
            <select v-model="statusFilter" class="form-select">
              <option value="all">All</option>
              <option value="roots">Roots only</option>
              <option value="duplicates">Duplicates only</option>
            </select>
          </div>
          <div class="col-md-4 d-flex gap-2">
            <button class="btn btn-primary" @click="applyFilters">Apply</button>
            <button class="btn btn-outline-secondary" @click="clearFilters">Clear</button>
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
                <th>Status</th>
                <th>Canonical</th>
                <th style="min-width: 220px;">Set Duplicate Of</th>
                <th style="min-width: 220px;">Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mask in filteredMasks" :key="mask.id">
                <td>{{ mask.id }}</td>
                <td class="code-col">{{ mask.unique_internal_model_code }}</td>
                <td>
                  <span v-if="mask.duplicate_of" class="badge bg-warning text-dark">Duplicate</span>
                  <span v-else class="badge bg-success">Root</span>
                </td>
                <td>
                  <span v-if="mask.duplicate_of">
                    #{{ mask.duplicate_of }}
                    <span v-if="maskLookup[mask.duplicate_of]" class="text-muted canonical-name">
                      {{ maskLookup[mask.duplicate_of].unique_internal_model_code }}
                    </span>
                  </span>
                  <span v-else class="text-muted">Self</span>
                </td>
                <td>
                  <input
                    :value="targetMaskIds[mask.id] || ''"
                    class="form-control form-control-sm"
                    type="number"
                    min="1"
                    placeholder="Target mask id"
                    @input="targetMaskIds[mask.id] = $event.target.value"
                  >
                </td>
                <td>
                  <input
                    :value="notesByMaskId[mask.id] || ''"
                    class="form-control form-control-sm"
                    type="text"
                    placeholder="Optional note"
                    @input="notesByMaskId[mask.id] = $event.target.value"
                  >
                </td>
                <td>
                  <div class="d-flex gap-2">
                    <button
                      class="btn btn-sm btn-primary"
                      :disabled="isBusy(mask.id)"
                      @click="linkDuplicate(mask)"
                    >
                      Link
                    </button>
                    <button
                      class="btn btn-sm btn-outline-danger"
                      :disabled="isBusy(mask.id) || !mask.duplicate_of"
                      @click="unlinkDuplicate(mask)"
                    >
                      Unlink
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
                <td colspan="7" class="text-center py-4 text-muted">No masks found for current filters.</td>
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
  name: 'AdminMaskDuplicates',
  data() {
    return {
      loading: false,
      error: '',
      message: '',
      masks: [],
      search: '',
      statusFilter: 'all',
      currentPage: 1,
      perPage: 50,
      totalPages: 1,
      totalCount: 0,
      targetMaskIds: {},
      notesByMaskId: {},
      busyMaskIds: {}
    }
  },
  computed: {
    filteredMasks() {
      if (this.statusFilter === 'roots') {
        return this.masks.filter(mask => !mask.duplicate_of)
      }
      if (this.statusFilter === 'duplicates') {
        return this.masks.filter(mask => !!mask.duplicate_of)
      }
      return this.masks
    },
    maskLookup() {
      const lookup = {}
      this.masks.forEach(mask => {
        lookup[mask.id] = mask
      })
      return lookup
    }
  },
  async mounted() {
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
    async applyFilters() {
      await this.loadMasks(1)
    },
    async clearFilters() {
      this.search = ''
      this.statusFilter = 'all'
      await this.loadMasks(1)
    },
    async changePage(page) {
      if (page < 1 || page > this.totalPages) return
      await this.loadMasks(page)
    },
    async linkDuplicate(mask) {
      this.clearMessages()
      const targetMaskId = this.targetMaskIds[mask.id]
      if (!targetMaskId) {
        this.error = `Mask #${mask.id}: target mask id is required`
        return
      }
      this.setBusy(mask.id, true)
      try {
        setupCSRF()
        await axios.post(`/admin/masks/${mask.id}/duplicate_link`, {
          target_mask_id: Number(targetMaskId),
          notes: this.notesByMaskId[mask.id]
        })
        this.message = `Mask #${mask.id} is now linked to #${targetMaskId}`
        await this.loadMasks(this.currentPage)
      } catch (error) {
        this.error = error.response?.data?.error || error.message
      } finally {
        this.setBusy(mask.id, false)
      }
    },
    async unlinkDuplicate(mask) {
      this.clearMessages()
      this.setBusy(mask.id, true)
      try {
        setupCSRF()
        await axios.delete(`/admin/masks/${mask.id}/duplicate_link`, {
          data: {
            notes: this.notesByMaskId[mask.id]
          }
        })
        this.message = `Mask #${mask.id} duplicate link removed`
        await this.loadMasks(this.currentPage)
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
.admin-mask-duplicates {
  max-width: 1500px;
  margin: 0 auto;
  padding: 2rem 1rem calc(5.5rem + env(safe-area-inset-bottom));
}

.code-col {
  max-width: 520px;
  white-space: normal;
  word-break: break-word;
}

.canonical-name {
  display: block;
  max-width: 320px;
  white-space: normal;
  word-break: break-word;
}
</style>
