<template>
  <div class='main'>
    <p class='tagline'>Breathesafe: The <span class='italic'>Yelp</span> of Indoor Air Quality</p>
    <router-link :to='{ name: "Venues" }'>
    <img src="https://breathesafe-development.s3.us-east-2.amazonaws.com/images/map-screenshot.png" alt="Map with locations marked with circles with different colors, indicating indoor air quality">
    </router-link>

    <div style='display: none;'>
      <div class='quote'>
        <a href="https://twitter.com/kprather88/status/1551262466813726720?ref_src=twsrc%5Etfw">Humans take 22,000 breaths per day. Air is the #1 exposure route to all pollution and pathogens.</a>
      </div>

      <a class='author' href="https://kprather.scrippsprofiles.ucsd.edu/">- Kimberly Prather, Ph.D</a>
    </div>

    <div>
      <div class='quote'>
        <a href="https://twitter.com/CorsIAQ/status/1424274541426008069">Our lifetime exposure to and uptake of air pollutants is largely DOMINATED by the air we breathe indoors - from our homes, workplaces, and schools.</a>
      </div>

      <a class='author' href="https://leadership.ucdavis.edu/people/richard-corsi">- Richard Corsi, Ph.D</a>
    </div>

    <div class='call-to-actions'>
      <router-link :to='{ name: "Venues" }'>
        <Button text='Find Safer Venues'/>
      </router-link>
      <Button text='Add Indoor Air Quality Measurements'/>
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
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  img {
    width: 100vw;
  }
  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions a {
    text-decoration: none;
  }
</style>
