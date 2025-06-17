<template>
  <div class='spinner-background'>
    <span class='loader'></span>
  </div>
</template>

<script>
  export default {
    name: 'Spinner',
    components: {
    },
    data() {
      return {}
    },
    props: {
    },
    computed: {

    }, methods: {
    }

  }
</script>

<style scoped>
  .spinner-background {
    background-color: rgba(128,128,128,0.5);
    position: absolute;
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100vw;
  }
   .loader {
    width: 48px;
    height: 48px;
    border: 5px solid #FFF;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
    }

    @keyframes rotation {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
  }
</style>
