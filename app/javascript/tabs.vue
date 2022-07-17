<template>
  <div class='wide border-showing'>
    <div class='container centered'>
      <button :class='{ focused: isFocused("Prevalence") }' @click='setFocus("Prevalence")'>Prevalence</button>
      <button :class='{ focused: isFocused("Measures") }' @click='setFocus("Measures")'>Measures</button>
      <button :class='{ focused: isFocused("Google Maps Info") }' @click='setFocus("Google Maps Info")'>Google Maps Info</button>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { mapActions, mapState, mapWritableState } from 'pinia';
import axios from 'axios';

export default {
  name: 'Confirmation',
  components: {
  },
  computed: {
    ...mapState(useMainStore, ['message']),
    ...mapWritableState(useMainStore, ['focusSubTab'])
  },
  created() { },
  data() {
    return {}
  },
  methods: {
    isFocused(string) {
      return this.focusSubTab == string
    },
    setFocus(val) {
      this.focusSubTab = val
    }
  },
}

</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    font-weight: bold;
  }
  .wide {
    flex-direction: column;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    justify-content: center;
  }

  button {
    padding: 1em 3em;
  }

  .focused {
    background-color: #e6e6e6;
  }

</style>
