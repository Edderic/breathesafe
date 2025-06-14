<template>
  <Popup
    v-if="showPopup"
    @onclose="$emit('hidePopUp')"
  >
    <h2>Help Guide</h2>

    <div class="section">
      <h4>Searching Masks</h4>
      <p>Use the search bar to find masks by name, brand, or other keywords.</p>
    </div>

    <div class="section">
      <h4>Recommendations</h4>
      <p>Click the "R" button to get personalized mask recommendations based on your facial measurements.</p>
    </div>

    <div class="section">
      <h4>Sorting</h4>
      <p>Use the "⇵" button to sort masks by different criteria like fit probability, brand, or style.</p>
    </div>

    <div class="section">
      <h4>Filtering</h4>
      <p>Click the filter icon to filter masks by color, style type, or strap type.</p>
    </div>

    <div class="section">
      <h4>Adding New Masks</h4>
      <p>Click the "+" button to add a new mask to the database.</p>
    </div>

    <div class="section">
      <h4>Terminology</h4>
      <table>
        <tr>
          <th></th><th>Explanation</th>
        </tr>
        <tr>
          <th>Proba fit</th>
          <td>The probability that a mask will fit for your face, where fit is defined as passing a qualitative fit test. Fit directly affects how much unfiltered air you're breathing in.</td>
        </tr>

        <tr>
          <th>Filtration factor</th>
          <td>An estimate of filtration efficiency. <strong>If you have your mask sealed to your face (i.e. great fit)</strong>, this metric captures how many times cleaner the air is that you're breathing in with the mask, compared to not wearing one. <strong>If you don't have a good seal, then you are getting lower than this protection factor.</strong> For example, assuming you have a great fit, and this is 100, then the air you're breathing in should be close to 100 times cleaner of particulates, in the 0.02 - 1 micron range. This is measured by a PortaCount with normal breathing rates. Multiple results from the same mask are averaged.</td>
        </tr>
      </table>
    </div>


      <button class="close-button" @click="$emit('hidePopUp')">Close</button>
  </Popup>
</template>

<script>
import Popup from './pop_up.vue'

export default {
  name: 'HelpPopup',
  components: {
    Popup
  },
  props: {
    showPopup: {
      type: Boolean,
      required: true
    }
  }
}
</script>

<style scoped>
.section {
  margin-bottom: 1.5em;
}

.section h4 {
  margin-bottom: 0.5em;
  color: #333;
}

.close-button {
  margin-top: 1em;
  padding: 0.5em 1em;
  background-color: #eee;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-button:hover {
  background-color: #ddd;
}

td, th {
  padding: 0.5em;
}
</style>
