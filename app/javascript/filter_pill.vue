<template>
  <button class="filter-pill" @click="$emit('remove')" type="button">
    <span class="filter-pill-label">{{ label }}</span>
    <span class="filter-pill-close">x</span>
  </button>
</template>

<script>
export default {
  name: 'FilterPill',
  props: {
    label: {
      type: String,
      required: true,
    },
  },
}
</script>

<style scoped>
.filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45em;
  border: 1px solid #c6c6c6;
  background: #f3f3f3;
  color: #222;
  border-radius: 999px;
  padding: 0.25em 0.65em;
  font-size: 0.85em;
  cursor: pointer;
}

.filter-pill:hover {
  background: #e9e9e9;
}

.filter-pill-label {
  line-height: 1.1;
}

.filter-pill-close {
  font-weight: 700;
  line-height: 1;
}
</style>
