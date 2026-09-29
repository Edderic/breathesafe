<template>
  <main class="container anonymous-admin">
    <h1>Anonymous submissions</h1>
    <p>Review anonymous facial measurements and fit tests submitted through MasqFit.</p>
    <form class="filters" @submit.prevent="load()">
      <label>Receipt ID
        <input v-model.trim="receipt" :disabled="busy || !!preview" placeholder="Complete receipt ID" />
      </label>
      <label>Participant ID
        <input v-model.trim="participant" :disabled="busy || !!preview" inputmode="numeric" placeholder="Any participant" />
      </label>
      <button :disabled="busy || !!preview">Search / refresh</button>
      <button type="button" :disabled="busy || !!preview" @click="resetFilters">Clear filters</button>
    </form>

    <p v-if="message" role="status">{{ message }}</p>
    <div v-if="error" role="alert" class="error">
      <p>{{ error }}</p>
      <template v-if="dependentIds.length">
        <p>These receipts reuse the selected measurements. Find and review them before adding any to your selection.</p>
        <ul><li v-for="id in dependentIds" :key="id"><code>{{ id }}</code></li></ul>
      </template>
    </div>

    <section v-if="preview" class="confirmation" aria-labelledby="deletion-title">
      <h2 id="deletion-title" tabindex="-1" ref="deletionTitle">Review permanent deletion</h2>
      <p>This deletes <strong>{{ countLabel(preview.contributions.length, 'submission') }}</strong>, including
        <strong>{{ countLabel(preview.fit_test_count, 'fit test') }}</strong> and all facial measurements in those submissions.</p>
      <ul>
        <li v-for="row in preview.contributions" :key="row.contribution_id">
          <code>{{ row.contribution_id }}</code> — participant {{ row.anonymous_participant_id }},
          received {{ date(row.created_at) }}, {{ countLabel(row.fit_tests.length, 'fit test') }}
          <details>
            <summary>Review the current data being deleted</summary>
            <dl class="measurements">
              <template v-for="(label, key) in measurementLabels" :key="key">
                <dt>{{ label }} (mm)</dt><dd>{{ row.measurements[key] ?? 'Not recorded' }}</dd>
              </template>
            </dl>
            <ul>
              <li v-for="(test, index) in row.fit_tests" :key="index">
                {{ test.mask || 'Unspecified mask' }} — final {{ test.final ?? 'not recorded' }},
                {{ test.status || 'unknown status' }}, mode {{ test.testing_mode || 'unknown' }}
              </li>
            </ul>
          </details>
        </li>
      </ul>
      <p>This cannot be undone. Participant codes, mask catalog entries, and mask matching decisions remain available.</p>
      <p>Remove any pending copies from the phone’s queue first; retrying a deleted submission could recreate it.</p>
      <label>Type DELETE to confirm
        <input v-model="confirmation" :disabled="busy" autocomplete="off" />
      </label>
      <div class="actions">
        <button class="danger" :disabled="busy || confirmation !== 'DELETE'" @click="deleteSelected">
          {{ busy ? 'Deleting…' : 'Permanently delete submissions' }}
        </button>
        <button :disabled="busy" @click="cancelPreview">Cancel</button>
      </div>
    </section>

    <div v-else class="actions">
      <strong>{{ selectedIds.length }} selected</strong>
      <button :disabled="busy || !selectedIds.length" @click="reviewDeletion">Review deletion</button>
      <button :disabled="busy || !selectedIds.length" @click="clearSelection">Clear selection</button>
      <span>Selections are kept across searches and pages (up to 100).</span>
    </div>
    <p v-if="busy && !preview" role="status">Loading…</p>
    <p v-if="!busy && !rows.length">No anonymous submissions match these filters.</p>

    <article v-for="row in rows" :key="row.contribution_id" class="submission">
      <label class="selection">
        <input v-model="selectedIds" type="checkbox" :value="row.contribution_id"
          :disabled="busy || !!preview || (selectedIds.length >= 100 && !selectedIds.includes(row.contribution_id))" />
        <strong>Receipt <code>{{ row.contribution_id }}</code></strong>
      </label>
      <p>Participant {{ row.anonymous_participant_id }} · Received {{ date(row.created_at) }} ·
        {{ countLabel(row.fit_tests.length, 'fit test') }}</p>
      <p v-if="row.measurement_source_contribution_id">Reuses measurements from receipt
        <code>{{ row.measurement_source_contribution_id }}</code>.</p>
      <details>
        <summary>View measurements and test results</summary>
        <p>Consent recorded {{ date(row.consent_accepted_at) }}. Measurements in millimeters:</p>
        <dl class="measurements">
          <template v-for="(label, key) in measurementLabels" :key="key">
            <dt>{{ label }}</dt><dd>{{ row.measurements[key] ?? 'Not recorded' }}</dd>
          </template>
        </dl>
        <p v-if="!row.fit_tests.length">Measurements only; no fit tests.</p>
        <ol>
          <li v-for="(test, index) in row.fit_tests" :key="index" class="test-result">
            <strong>{{ test.mask || 'Unspecified mask' }}</strong>
            <p>Final: {{ test.final ?? 'Not recorded' }} · {{ test.status || 'Unknown status' }} ·
              Testing mode: {{ test.testing_mode || 'unknown' }}</p>
            <p>Protocol: {{ test.protocol_name || 'Not recorded' }}</p>
            <p>Exercise scores:
              {{ Object.entries(test.exercises || {}).map(([exercise, score]) => `${exercise}: ${score}`).join(', ') || 'None recorded' }}</p>
          </li>
        </ol>
      </details>
    </article>
    <button v-if="hasMore" :disabled="busy || !!preview" @click="load(true)">Load more submissions</button>
  </main>
</template>

<script>
import axios from 'axios'
import { setupCSRF } from './misc.js'

export default {
  data() {
    return {
      rows: [], selectedIds: [], receipt: '', participant: '', hasMore: false, busy: false,
      error: '', message: '', dependentIds: [], preview: null, confirmation: '', activeFilters: {},
      measurementLabels: { nose_mm: 'Nose', strap_mm: 'Strap', top_cheek_mm: 'Top cheek', mid_cheek_mm: 'Mid cheek', chin_mm: 'Chin' }
    }
  },
  mounted() { this.load() },
  methods: {
    date(value) { return value ? new Date(value).toLocaleString() : 'Not recorded' },
    countLabel(count, noun) { return `${count} ${noun}${count === 1 ? '' : 's'}` },
    showError(error, fallback) {
      this.error = error.response?.data?.error || fallback
      this.dependentIds = error.response?.data?.dependent_ids || []
    },
    async load(append = false) {
      if (this.busy || this.preview) return
      this.busy = true; this.error = ''; this.dependentIds = []
      const filters = append ? this.activeFilters : { receipt: this.receipt, participant: this.participant }
      try {
        const { data } = await axios.get('/admin/anonymous_contributions.json', { params: {
          ...filters, before_id: append ? this.rows[this.rows.length - 1]?.id : undefined
        } })
        this.rows = append ? this.rows.concat(data.contributions) : data.contributions
        this.hasMore = data.has_more
        this.activeFilters = { ...filters }
      } catch (e) {
        this.showError(e, 'Unable to load submissions. Sign in as an admin and try again.')
        if (!append) { this.rows = []; this.hasMore = false }
      } finally { this.busy = false }
    },
    resetFilters() { this.receipt = ''; this.participant = ''; this.load() },
    clearSelection() { this.selectedIds = []; this.error = ''; this.dependentIds = [] },
    cancelPreview() { this.preview = null; this.confirmation = '' },
    async reviewDeletion() {
      if (this.busy || this.preview || !this.selectedIds.length) return
      this.busy = true; this.error = ''; this.message = ''; this.dependentIds = []; this.confirmation = ''
      try {
        await setupCSRF()
        const { data } = await axios.post('/admin/anonymous_contributions/deletion_preview.json', {
          contribution_ids: [...this.selectedIds]
        })
        this.preview = data
        this.$nextTick(() => this.$refs.deletionTitle?.focus())
      } catch (e) { this.showError(e, 'Unable to preview deletion. Nothing was deleted.') }
      finally { this.busy = false }
    },
    async deleteSelected() {
      if (this.busy || !this.preview || this.confirmation !== 'DELETE') return
      this.busy = true; this.error = ''; this.dependentIds = []
      try {
        await setupCSRF()
        const { data } = await axios.delete('/admin/anonymous_contributions/destroy_selected.json', {
          data: { token: this.preview.token }
        })
        const deleted = new Set(data.deleted_ids)
        this.rows = this.rows.filter(row => !deleted.has(row.contribution_id))
        this.selectedIds = this.selectedIds.filter(id => !deleted.has(id))
        this.message = `Deleted ${this.countLabel(deleted.size, 'submission')} and the associated facial measurements.`
      } catch (e) {
        this.showError(e, 'Deletion could not be confirmed. Refresh the list before trying again.')
      } finally {
        this.cancelPreview()
        this.busy = false
      }
    }
  }
}
</script>

<style scoped>
.anonymous-admin { max-width: 1000px; padding-bottom: 3rem; }
.filters, .actions { display: flex; flex-wrap: wrap; gap: .75rem; align-items: end; margin: 1rem 0; }
.filters label, .confirmation label { display: flex; flex-direction: column; gap: .3rem; }
input:not([type=checkbox]) { padding: .5rem; max-width: 100%; }
button { padding: .6rem .9rem; cursor: pointer; }
button:disabled { cursor: default; opacity: .55; }
.submission { border-top: 1px solid #ccc; padding: 1rem 0; }
.selection { display: flex; align-items: baseline; gap: .6rem; }
code { overflow-wrap: anywhere; }
.confirmation { border: 2px solid #a32424; padding: 1rem; margin: 1rem 0; }
.danger { background: #a32424; color: white; border: 1px solid #a32424; }
.error { color: #8a1717; }
.measurements { display: grid; grid-template-columns: max-content auto; gap: .4rem 1rem; }
.measurements dd { margin: 0; }
.test-result { margin: 1rem 0; }
summary { cursor: pointer; }
</style>
