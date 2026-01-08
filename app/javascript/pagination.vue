<template>
  <div v-if="totalCount > 0" class="pagination-container">
    <nav aria-label="Pagination">
      <ul v-if="totalPages > 1" class="pagination">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button @click="goToPage(1)" class="page-link" :disabled="currentPage === 1">First</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button @click="goToPage(currentPage - 1)" class="page-link" :disabled="currentPage === 1">Previous</button>
        </li>

        <li
          v-for="page in visiblePages"
          :key="page"
          class="page-item"
          :class="{ active: page === currentPage }"
        >
          <button @click="goToPage(page)" class="page-link">{{ page }}</button>
        </li>

        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button @click="goToPage(currentPage + 1)" class="page-link" :disabled="currentPage === totalPages">Next</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button @click="goToPage(totalPages)" class="page-link" :disabled="currentPage === totalPages">Last</button>
        </li>
      </ul>
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * perPage + 1 }}-{{ Math.min(currentPage * perPage, totalCount) }} of {{ totalCount }} {{ itemName }}
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    perPage: {
      type: Number,
      required: true
    },
    totalCount: {
      type: Number,
      required: true
    },
    itemName: {
      type: String,
      default: 'items'
    }
  },
  emits: ['page-change'],
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.perPage)
    },
    visiblePages() {
      const pages = [];
      const start = Math.max(1, this.currentPage - 2);
      const end = Math.min(this.totalPages, this.currentPage + 2);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.$emit('page-change', page)
      }
    }
  }
}
</script>

<style scoped>
  .pagination-container {
    margin: 0 1em;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .pagination {
    display: flex;
    list-style: none;
    padding: 0;
    gap: 0.5em;
    margin: 0.5em;
    flex-wrap: wrap;
    justify-content: center;
  }

  .page-item {
    display: inline-block;
  }

  .page-link {
    padding: 0.5em 1em;
    border: 1px solid #ddd;
    background-color: white;
    color: #007bff;
    cursor: pointer;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.2s;
  }

  .page-link:hover:not(:disabled) {
    background-color: #e9ecef;
  }

  .page-item.active .page-link {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
  }

  .page-item.disabled .page-link {
    color: #6c757d;
    cursor: not-allowed;
    opacity: 0.5;
  }

  .pagination-info {
    text-align: center;
    margin: 0.5em;
    color: #666;
    font-size: 0.9em;
  }

  @media(max-width: 700px) {
    .pagination {
      font-size: 0.85em;
    }

    .page-link {
      padding: 0.4em 0.7em;
    }
  }
</style>
