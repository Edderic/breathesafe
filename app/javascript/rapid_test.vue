<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" :width="width" :height="height">
    <path d='m 30 10 h 20 v 60 h -20 z m 7 10 h 5 v 25 h -5 z m 0 35 h 5 v 5 h -5 z' stroke='black' fill='transparent'/>
    <text x="57%" y="30%" text-anchor="middle" fill="black" dy=".4em" style='font-size: 0.4em;'>
      C
    </text>
    <text x="57%" y="50%" text-anchor="middle" fill="black" dy=".4em" style='font-size: 0.4em;'>
      T
    </text>

    <path d='m 38 24.5 h 3' fill='gray' stroke='gray'/>
    <path d='m 38 40 h 3' fill='gray' stroke='red'/>
  </svg>
</template>

<script>
export default {
  name: 'RapidTest',
  components: {
  },
  data() {
    return {}
  },
  props: {
    width: {
      type: String,
      default: '30px',
    },
    height: {
      type: String,
      default: '30px',
    }
  },
  computed: {

  }, methods: {
  }

}
</script>

<style scoped>
</style>
