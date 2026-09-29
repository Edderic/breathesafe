const { test } = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')
const path = require('node:path')

// Exercise the component's request coordination without a browser or real network.
function component(axios) {
  const vue = fs.readFileSync(path.join(__dirname, '../../app/javascript/admin_mask_proposals.vue'), 'utf8')
  const script = vue.match(/<script>([\s\S]*?)<\/script>/)[1]
    .replace(/^import .*$/gm, '').replace('export default', 'module.exports =')
  const context = { module: { exports: {} }, axios, setupCSRF: async () => {}, window: { confirm: () => true } }
  vm.runInNewContext(script, context)
  const options = context.module.exports
  const state = { ...options.data(), $route: { query: {} } }
  for (const [name, method] of Object.entries(options.methods)) state[name] = method.bind(state)
  return { state, options }
}
function deferred() { let resolve; const promise = new Promise(r => { resolve = r }); return { promise, resolve } }

test('queue load automatically suggests unresolved names with at most two requests and no decisions', async () => {
  let active = 0; let peak = 0; let suggestions = 0; let writes = 0
  const proposals = Array.from({ length: 5 }, (_, i) => ({ id: i + 1, name: `Model ${i}`, resolved_at: i === 4 ? 'yesterday' : null }))
  const { state } = component({
    get: async url => {
      if (url === '/admin/mask_proposals.json') return { data: { proposals, has_more: false } }
      suggestions++; active++; peak = Math.max(active, peak)
      await new Promise(r => setImmediate(r)); active--
      return { data: { masks: [{ id: 727, name: 'Suggested model' }] } }
    },
    patch: async () => { writes++ }
  })
  let automatic
  const original = state.autoSuggest
  state.autoSuggest = (...args) => (automatic = original(...args))
  await state.load(); await automatic
  assert.equal(suggestions, 4); assert.equal(peak, 2); assert.equal(writes, 0)
  assert.equal(state.results[1][0].id, 727); assert.equal(state.results[5], undefined)
  assert.equal(proposals[0].resolved_at, null)
})

test('a delayed suggestion cannot overwrite a newer manual search', async () => {
  const old = deferred()
  const { state } = component({ get: url => url.endsWith('mask_suggestions') ? old.promise : Promise.resolve({ data: { masks: [{ id: 42 }] } }) })
  const proposal = { id: 1, name: 'Model' }; state.queries[1] = 'edited'
  const pending = state.suggest(proposal)
  await state.search(proposal)
  old.resolve({ data: { masks: [{ id: 99 }] } }); await pending
  assert.equal(state.results[1][0].id, 42); assert.equal(state.matching[1], false)
})

test('leaving the screen stops queued work and ignores late responses', async () => {
  const pending = deferred(); let calls = 0
  const { state, options } = component({ get: () => { calls++; return pending.promise } })
  const work = state.autoSuggest([{ id: 1 }, { id: 2 }, { id: 3 }], state.generation)
  options.beforeUnmount.call(state)
  pending.resolve({ data: { masks: [{ id: 99 }] } }); await work
  assert.equal(calls, 2); assert.equal(Object.keys(state.results).length, 0)
})

test('one failed suggestion leaves other proposals reviewable and supports retry', async () => {
  let fail = true
  const { state } = component({ get: async (_, config) => {
    if (config.params.name === 'Bad' && fail) throw new Error('offline')
    return { data: { masks: [] } }
  } })
  const proposals = [{ id: 1, name: 'Bad' }, { id: 2, name: 'Good' }]
  await state.autoSuggest(proposals, state.generation)
  assert.match(state.matchErrors[1], /Retry/); assert.equal(state.results[2].length, 0)
  fail = false; await state.suggest(proposals[0])
  assert.equal(state.matchErrors[1], ''); assert.equal(state.results[1].length, 0)
})
