<template>
  <Popup
    v-if="showPopup"
    @onclose="$emit('hidePopUp')"
  >
    <h2>Help Guide</h2>
    <p v-if="recommenderModelTimestamp" class="model-version-line">
      Recommender model version: {{ recommenderModelTimestamp }}
    </p>

    <div class="section">
      <h4>Searching Masks</h4>
      <p>Use the search bar to find masks by name, brand, or other keywords.</p>
    </div>

    <div class="section">
      <h4>Recommendations</h4>
      <p>Use the MasqFit app once it is available in the iOS App Store. After a face scan, it will lead you to the mask page here, with added information about which masks are most likely to fit your face.</p>
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
          <td>A number between 1 and infinity, describing how much cleaner the air is in the range of 0.02 - 1 microns when wearing a mask, relative to the surroundings, assuming that one has a good seal. E.g. A filtration factor of 100 means that if the mask is fully sealed to the face, that the air being breathed in is 100 times cleaner, in the 0.02 - 1 microns range.</td>
        </tr>
        <tr>
          <th>Breathability</th>
          <td>Measured in Pascals. Lower is better. This describes the vacuum pressure when you're breathing in air through a well-fitting mask. The lower the pascals, the easier it is to pull / push air through the filter media.</td>
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
    },
    recommenderModelTimestamp: {
      type: String,
      default: null
    }
  }
}
</script>

<style scoped>
.section {
  margin-bottom: 1.5em;
}

.model-version-line {
  margin: 0.25em 0 1em 0;
  color: #444;
  font-size: 0.95em;
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
