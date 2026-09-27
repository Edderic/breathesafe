<template>
  <div class="container">
    <h1>Mask proposals</h1>
    <p>Review masks proposed with anonymous contributions. Matching updates all linked fit tests.</p>
    <label><input v-model="includeResolved" type="checkbox" @change="load()"> Include reviewed proposals</label>
    <button :disabled="busy" @click="load()">Refresh</button>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="!busy && !proposals.length">No proposals to review.</p>
    <section v-for="proposal in proposals" :key="proposal.id" class="proposal">
      <h2>{{ proposal.name }}</h2>
      <p v-if="proposal.resolved_at">Matched to catalog: {{ proposal.mask_name }}</p>
      <template v-else>
        <label>Search catalog <input v-model="queries[proposal.id]" @keyup.enter="search(proposal)"></label>
        <button :disabled="busy" @click="search(proposal)">Search</button>
        <button :disabled="busy" @click="suggest(proposal)">Suggest matches</button>
        <p v-if="results[proposal.id] && !results[proposal.id].length">No matches. Try another search or create a mask.</p>
        <ul>
          <li v-for="mask in results[proposal.id] || []" :key="mask.id">
            {{ mask.name }} <button :disabled="busy" @click="resolve(proposal, mask)">Match to this mask</button>
          </li>
        </ul>
        <p v-if="moreResults[proposal.id]">Showing the first 50 matches. Narrow the search to find the correct model.</p>
        <label>New catalog name <input v-model="names[proposal.id]" maxlength="200"></label>
        <button :disabled="busy || !names[proposal.id]?.trim()" @click="resolve(proposal)">Create mask and match</button>
      </template>
    </section>
    <button v-if="hasMore" :disabled="busy" @click="load(true)">Load more proposals</button>
  </div>
</template>
<script>
import axios from 'axios'
import { setupCSRF } from './misc.js'

export default {
  data() {
    return { proposals: [], queries: {}, names: {}, results: {}, moreResults: {}, busy: false, error: '', includeResolved: false, hasMore: false }
  },
  mounted() { this.includeResolved = !!this.$route.query.proposal; this.load() },
  methods: {
    async load(append = false) {
      this.busy = true; this.error = ''
      try {
        const { data } = await axios.get('/admin/mask_proposals.json', { params: {
          include_resolved: this.includeResolved, id: this.$route.query.proposal,
          after_id: append ? this.proposals[this.proposals.length - 1]?.id : 0
        } })
        this.proposals = append ? this.proposals.concat(data.proposals) : data.proposals
        this.hasMore = data.has_more
        data.proposals.forEach(p => { this.names[p.id] = p.name; this.queries[p.id] = p.name })
      } catch (e) { this.error = e.response?.data?.error || 'Unable to load proposals. Sign in as an admin.' }
      finally { this.busy = false }
    },
    async search(proposal) { await this.matches(proposal, false) },
    async suggest(proposal) { await this.matches(proposal, true) },
    async matches(proposal, suggested) {
      this.busy = true; this.error = ''
      try {
        const route = suggested ? 'mask_suggestions' : 'masks'
        const params = suggested ? { name: proposal.name } : { search: this.queries[proposal.id] }
        const { data } = await axios.get(`/anonymous_contributions/${route}`, { params })
        this.results[proposal.id] = data.masks; this.moreResults[proposal.id] = data.has_more || false
      } catch (e) { this.error = 'Unable to load masks. Please retry.' }
      finally { this.busy = false }
    },
    async resolve(proposal, mask = null) {
      const name = mask ? mask.name : this.names[proposal.id]?.trim()
      if (!window.confirm(`${mask ? 'Match to' : 'Create'} “${name}” and update all linked fit tests?`)) return
      this.busy = true; this.error = ''
      try {
        await setupCSRF()
        const { data } = await axios.patch(`/admin/mask_proposals/${proposal.id}.json`, mask ? { mask_id: mask.id } : { name })
        Object.assign(proposal, data)
      } catch (e) { this.error = e.response?.data?.error || 'Unable to save. Please retry.' }
      finally { this.busy = false }
    }
  }
}
</script>
<style scoped>
.proposal { border-top: 1px solid #ccc; padding: 1rem 0; }
button, input { margin: .3rem; }
</style>
