<template>
  <div>
    <h2 class='tagline'>Respirator Users</h2>
    <div class='main'>
      <div class='centered'>
        <table>
          <thead>
            <tr>
              <th>Name</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

  </div>
</template>

<script>
import Button from './button.vue'
export default {
  name: 'RespiratorUsers',
  components: {
    Button
  },
  data() {
    return {
    }
  },
  props: {
  },
  computed: {

  },
  methods: {

  }

}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  p {
    margin: 1em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  img {
    width: 30em;
  }
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
  }
</style>
