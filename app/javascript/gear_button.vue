<template>
  <CircularButton @click='$emit("click")' class='gear-button'>
    <svg
      viewBox="0 0 100 100"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Gear icon"
      class='gear'
    >
      <!-- Gear body & teeth use currentColor so you can tint via CSS -->
      <g fill="currentColor">
        <!-- Main gear body -->
        <circle cx="50" cy="50" r="30" />

        <!-- Six teeth -->
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2" />
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
              transform="rotate(60 50 50)" />
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
              transform="rotate(120 50 50)" />
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
              transform="rotate(180 50 50)" />
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
              transform="rotate(240 50 50)" />
        <rect x="45" y="8" width="10" height="12" rx="2" ry="2"
              transform="rotate(300 50 50)" />

        <!-- Inner ring -->
        <circle cx="50" cy="50" r="14" fill="none" stroke="currentColor" stroke-width="6" />
      </g>
    </svg>
  </CircularButton>
</template>

<script>
import CircularButton from './circular_button.vue'

export default {
  name: 'GearButton',
  components: {
    CircularButton
  },
  emits: ['click']
}
</script>

<style scoped>
  .gear-button svg {
    display: block;
    margin: 0 auto;
    color: #80808080;
  }
</style>
