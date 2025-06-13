import { defineStore } from 'pinia'

export const useMasksStore = defineStore('masks', {
  state: () => ({
    search: "",
    sortByStatus: 'ascending',
    sortByField: undefined,
    filterForColor: 'none',
    filterForStrapType: 'none',
    filterForStyle: 'none'
  }),
  actions: {
    setSortByStatus(status) {
      this.sortByStatus = status || 'ascending'
    },
    setSortByField(field) {
      this.sortByField = field
    },
    setFilterForColor(color) {
      this.filterForColor = color || 'none'
    },
    setFilterForStrapType(strapType) {
      this.filterForStrapType = strapType || 'none'
    },
    setFilterForStyle(style) {
      this.filterForStyle = style || 'none'
    },

    setFilterQuery(query, key) {
      if (key == 'search') {
        this[key] = query[key] || ''
      } else if (query[key]) {
        this[key] = query[key]
      }
    },
    resetFilters() {
      this.filterForColor = 'none'
      this.filterForStrapType = 'none'
      this.filterForStyle = 'none'
    }
  }
})
