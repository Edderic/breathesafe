import { defineStore } from 'pinia'

export const useMasksStore = defineStore('masks', {
  state: () => ({
    search: "",
    sortByStatus: 'ascending',
    sortByField: undefined,
    filterForColor: 'none',
    filterForStrapType: 'none',
    filterForStyle: 'none',
    filterForMissing: [],
    filterForAvailable: 'true'
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
    setFilterForMissing(missing) {
      this.filterForMissing = missing || []
    },
    setFilterForAvailable(available) {
      this.filterForAvailable = available || 'true'
    },

    setFilterQuery(query, key) {
      if (key == 'search') {
        this[key] = query[key] || ''
      } else if (key == 'filterForMissing') {
        const rawValue = query[key]
        if (!rawValue || rawValue === 'none') {
          this[key] = []
        } else if (Array.isArray(rawValue)) {
          this[key] = rawValue.filter((value) => value && value !== 'none')
        } else {
          this[key] = rawValue.split(',').map((value) => value.trim()).filter((value) => value)
        }
      } else if (key == 'filterForAvailable') {
        this[key] = query[key] || 'true'
      } else if (key == 'filterForColor') {
        this[key] = query[key] || 'none'
      } else if (key == 'filterForStrapType') {
        this[key] = query[key] || 'none'
      } else if (key == 'filterForStyle') {
        this[key] = query[key] || 'none'
      } else if (key == 'sortByStatus') {
        this[key] = query[key] || 'ascending'
      } else if (key == 'sortByField') {
        this[key] = query[key] || undefined
      } else if (query[key]) {
        this[key] = query[key]
      }
    },
    resetFilters() {
      this.filterForColor = 'none'
      this.filterForStrapType = 'none'
      this.filterForStyle = 'none'
      this.filterForMissing = []
      this.filterForAvailable = 'true'
    }
  }
})
