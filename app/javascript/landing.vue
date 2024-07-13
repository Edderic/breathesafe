<template>
  <div>
    <h2 class='tagline'>Find Clean Air Indoors</h2>
    <div class='main'>
      <div class='centered'>
        <router-link :to='{ name: "Venues" }'>
        <img src="https://breathesafe-development.s3.us-east-2.amazonaws.com/images/map-screenshot.png" alt="Map with locations marked with circles with different colors, indicating indoor air quality">
        </router-link>
      </div>

      <div class='call-to-actions centered'>
        <router-link :to='{ name: "Venues" }'>
          <Button text='Find Safer Venues' major='true'/>
        </router-link>
        <router-link :to='{ name: "RespiratorUsers"}'>
          <Button text='Find Respirators' major='true'/>
        </router-link>
      </div>

    </div>

    <div>
      <div class='quote'>
        <a href="https://twitter.com/CorsIAQ/status/1424274541426008069">Our lifetime exposure to and uptake of air pollutants is largely DOMINATED by the air we breathe indoors - from our homes, workplaces, and schools.</a>
      </div>

      <a class='author' href="https://leadership.ucdavis.edu/people/richard-corsi">- Richard Corsi, Ph.D</a>
    </div>

  </div>
</template>

<script>
import Button from './button.vue'
export default {
  name: 'Landing',
  components: {
    Button
  },
  data() {
    return {}
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
