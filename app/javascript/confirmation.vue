<template>
  <div class='wide border-showing'>

    <div class='container centered'>
      <h2>Confirmation</h2>
    </div>

    <div class='container centered'>
      <h3>{{ message }}</h3>
    </div>
  </div>
</template>

<script>
// Have a VueX store that maintains state across components
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { mapActions, mapState } from 'pinia';
import axios from 'axios';

export default {
  name: 'Confirmation',
  components: {
  },
  computed: {
    ...mapState(useMainStore, ['message'])
  },
  created() { },
  data() {
    return {}
  },
  methods: {
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
</style>
