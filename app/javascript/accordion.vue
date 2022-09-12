<template>
  <svg xmlns="http://www.w3.org/2000/svg" fill="#000000" viewBox="0 0 80 80" height='2em' width='3em'>
    <path d="m 0 0 v 80 h 80 v -80 z" fill='#333' stroke='#111' stroke-linecap='round'/>
    <path d="m 20 20 h 40" stroke='#fff' stroke-width='5'/>
    <path d="m 20 40 h 40" stroke='#fff' stroke-width='5'/>
    <path d="m 20 60 h 40" stroke='#fff' stroke-width='5'/>

  </svg>
</template>

<script>
export default {
  name: 'Accordion',
  data() {
    return {
      activated: false
    }
  }
}
</script>
