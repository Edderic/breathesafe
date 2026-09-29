const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')
const path = require('node:path')

function page(axios) {
  const source = fs.readFileSync(path.join(__dirname, '../../app/javascript/admin_anonymous_contributions.vue'), 'utf8')
  const script = source.match(/<script>([\s\S]*?)<\/script>/)[1]
    .replace(/^import .*$/gm, '').replace('export default', 'module.exports =')
  const context = { module: { exports: {} }, axios, setupCSRF: async () => {} }
  vm.runInNewContext(script, context)
  const component = context.module.exports
  const instance = { ...component.data(), $nextTick: fn => fn(), $refs: {} }
  for (const [key, method] of Object.entries(component.methods)) instance[key] = method.bind(instance)
  return instance
}

test('pagination uses the last successful filters, not unsubmitted edits', async () => {
  const calls = []
  const view = page({ get: async (url, config) => {
    calls.push(config.params)
    return { data: { contributions: [{ id: 10, contribution_id: 'receipt' }], has_more: true } }
  } })
  view.participant = '12'
  await view.load()
  view.participant = '99'
  await view.load(true)
  assert.equal(calls[1].participant, '12')
  assert.equal(calls[1].before_id, 10)
})

test('failed preview never enables deletion and surfaces dependencies', async () => {
  let deletes = 0
  const view = page({
    post: async () => { throw { response: { data: { error: 'Dependent measurements', dependent_ids: ['child'] } } } },
    delete: async () => { deletes++ }
  })
  view.selectedIds = ['parent']
  await view.reviewDeletion()
  view.confirmation = 'DELETE'
  await view.deleteSelected()
  assert.equal(deletes, 0)
  assert.equal(view.preview, null)
  assert.equal(view.dependentIds[0], 'child')
})

test('delete requires exact confirmation and sends only the preview token', async () => {
  const calls = []
  const view = page({ delete: async (url, config) => {
    calls.push(config.data)
    return { data: { deleted_ids: ['one'] } }
  } })
  view.preview = { token: 'signed-preview' }
  view.rows = [{ contribution_id: 'one' }, { contribution_id: 'two' }]
  view.selectedIds = ['one', 'two']
  view.confirmation = 'delete'
  await view.deleteSelected()
  assert.equal(calls.length, 0)
  view.confirmation = 'DELETE'
  await view.deleteSelected()
  assert.equal(calls.length, 1)
  assert.equal(calls[0].token, 'signed-preview')
  assert.deepEqual(Object.keys(calls[0]), ['token'])
  assert.equal(view.rows.length, 1)
  assert.equal(view.rows[0].contribution_id, 'two')
  assert.equal(view.selectedIds[0], 'two')
  assert.equal(view.preview, null)
})

test('duplicate clicks do not duplicate a delete request', async () => {
  let complete
  let calls = 0
  const view = page({ delete: () => {
    calls++
    return new Promise(resolve => { complete = resolve })
  } })
  view.preview = { token: 'signed-preview' }
  view.confirmation = 'DELETE'
  const first = view.deleteSelected()
  await view.deleteSelected()
  assert.equal(calls, 1)
  complete({ data: { deleted_ids: [] } })
  await first
})

test('a rejected or uncertain deletion requires a new preview', async () => {
  const view = page({ delete: async () => { throw new Error('Lost response') } })
  view.preview = { token: 'old' }
  view.confirmation = 'DELETE'
  view.selectedIds = ['one']
  await view.deleteSelected()
  assert.equal(view.preview, null)
  assert.equal(view.confirmation, '')
  assert.equal(view.busy, false)
  assert.equal(view.selectedIds[0], 'one')
  assert.match(view.error, /Refresh/)
})
