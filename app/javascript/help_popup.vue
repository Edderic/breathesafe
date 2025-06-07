<template>
  <div v-if="showPopup" class="help-popup">
    <div class="help-content">
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

      <button class="close-button" @click="$emit('hidePopUp')">Close</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpPopup',
  props: {
    showPopup: {
      type: Boolean,
      required: true
    }
  }
}
</script>

<style scoped>
.help-popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.help-content {
  background-color: white;
  padding: 2em;
  border-radius: 8px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  margin: 2em;
}

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
</style> 