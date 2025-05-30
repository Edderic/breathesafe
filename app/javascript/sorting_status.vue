<template>
    <div v-if='status == "ascending"'>
      Ascending
    </div>
    <div v-if='status == "descending"'>
      Descending
    </div>
</template>

<script>
export default {
  name: 'SortingStatus',
  components: {
  },
  data() {
    return {
    }
  },
  props: {
    status: {
      type: String,
      default: '',
    }
  },
  computed: {

  },
  methods: {
  }

}
</script>

<style scoped>
</style>
