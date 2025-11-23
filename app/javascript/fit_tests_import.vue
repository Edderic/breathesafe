<template>
  <div class='align-items-center flex-dir-col top-container'>
    <div class='flex align-items-center row phone'>
      <h2 class='tagline'>Import Fit Tests</h2>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <!-- Progress Component -->
    <div class='columns'>
      <FitTestsImportProgressBar
        :importedFile="importedFile"
        :columnMatching="columnMatching"
        :userMatching="userMatching"
        :maskMatching="maskMatching"
        :userSealCheckMatching="userSealCheckMatching"
        :fitTestDataMatching="fitTestDataMatching"
        :completedSteps="completedSteps"
        :currentStep="currentStep"
        @navigate-to-step="navigateToStep"
      />

      <!-- Import File Step -->
      <div v-show='currentStep == "Import File"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Import File</h2>
          <h3 class='text-align-center'>Select a file to import</h3>

          <div class='row justify-content-center'>
            <input
              type="file"
              @change='handleFileSelect'
              accept=".csv,.xlsx,.xls"
              ref="fileInput"
            />
          </div>

          <div v-if="importedFile" class='file-info'>
            <h3 class='text-align-center'>Selected File</h3>
            <table>
              <tbody>
                <tr>
                  <th>File Name</th>
                  <td>{{ importedFile.name }}</td>
                </tr>
                <tr>
                  <th>File Size</th>
                  <td>{{ formatFileSize(importedFile.size) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='!importedFile'/>
        </div>
      </div>

      <!-- Column Matching Step -->
      <div v-show='currentStep == "Column Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Column Matching</h2>
          <h3 class='text-align-center'>Match CSV columns to fit test fields</h3>

          <p class='text-align-center'>Placeholder: Column matching interface will go here</p>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep'/>
        </div>
      </div>

      <!-- User Matching Step -->
      <div v-show='currentStep == "User Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>User Matching</h2>
          <h3 class='text-align-center'>Match imported users to existing users</h3>

          <p class='text-align-center'>Placeholder: User matching interface will go here</p>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep'/>
        </div>
      </div>

      <!-- Mask Matching Step -->
      <div v-show='currentStep == "Mask Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Mask Matching</h2>
          <h3 class='text-align-center'>Match imported masks to existing masks</h3>

          <p class='text-align-center'>Placeholder: Mask matching interface will go here</p>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep'/>
        </div>
      </div>

      <!-- User Seal Check Matching Step -->
      <div v-show='currentStep == "User Seal Check Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>User Seal Check Matching</h2>
          <h3 class='text-align-center'>Match user seal check data</h3>

          <p class='text-align-center'>Placeholder: User seal check matching interface will go here</p>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep'/>
        </div>
      </div>

      <!-- Fit Test Data Matching Step -->
      <div v-show='currentStep == "Fit Test Data Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Fit Test Data Matching</h2>
          <h3 class='text-align-center'>Review and confirm fit test data</h3>

          <p class='text-align-center'>Placeholder: Fit test data matching interface will go here</p>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Import" @click='completeImport'/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import FitTestsImportProgressBar from './fit_tests_import_progress_bar.vue'

export default {
  name: 'FitTestsImport',
  components: {
    Button,
    ClosableMessage,
    FitTestsImportProgressBar
  },
  data() {
    return {
      messages: [],
      currentStep: 'Import File',
      importedFile: null,
      columnMatching: null,
      userMatching: null,
      maskMatching: null,
      userSealCheckMatching: null,
      fitTestDataMatching: null,
      completedSteps: []
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.importedFile = {
          name: file.name,
          size: file.size,
          file: file
        }
      }
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    navigateToStep(stepKey) {
      this.currentStep = stepKey
    },
    goToNextStep() {
      const steps = [
        'Import File',
        'Column Matching',
        'User Matching',
        'Mask Matching',
        'User Seal Check Matching',
        'Fit Test Data Matching'
      ]
      const currentIndex = steps.indexOf(this.currentStep)
      if (currentIndex < steps.length - 1) {
        this.currentStep = steps[currentIndex + 1]
      }
    },
    goToPreviousStep() {
      const steps = [
        'Import File',
        'Column Matching',
        'User Matching',
        'Mask Matching',
        'User Seal Check Matching',
        'Fit Test Data Matching'
      ]
      const currentIndex = steps.indexOf(this.currentStep)
      if (currentIndex > 0) {
        this.currentStep = steps[currentIndex - 1]
      }
    },
    cancelImport() {
      // Navigate back to fit tests list
      this.$router.push({ name: 'FitTests' })
    },
    completeImport() {
      // Placeholder: Complete the import process
      this.messages = [{ str: 'Import completed successfully!' }]
      // Navigate back to fit tests list after a delay
      setTimeout(() => {
        this.$router.push({ name: 'FitTests' })
      }, 2000)
    }
  }
}
</script>

<style scoped>
.flex {
  display: flex;
}

.flex-dir-row {
  display: flex;
  flex-direction: row;
}

.flex-dir-col {
  display: flex;
  flex-direction: column;
}

.align-items-center {
  display: flex;
  align-items: center;
}

.justify-content-center {
  display: flex;
  justify-content: center;
}

.top-container {
  padding: 1em;
}

.row {
  display: flex;
  flex-direction: row;
}

.columns {
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.right-pane {
  flex: 1;
  margin-left: 320px;
}

.narrow-width {
  max-width: 600px;
  margin: 0 auto;
}

.text-align-center {
  text-align: center;
}

.tagline {
  text-align: center;
  font-weight: bold;
}

.container {
  margin: 1em;
}

.chunk {
  margin-bottom: 1em;
}

.buttons {
  display: flex;
  gap: 1em;
  justify-content: center;
  margin-top: 1em;
}

.button {
  min-width: 100px;
}

.file-info {
  margin-top: 2em;
}

.file-info table {
  width: 100%;
  margin-top: 1em;
}

.file-info th {
  text-align: left;
  padding-right: 1em;
  font-weight: bold;
}

.file-info td {
  padding: 0.5em;
}

input[type="file"] {
  padding: 0.5em;
  margin: 1em;
}

@media (max-width: 1000px) {
  .columns {
    flex-direction: column;
  }

  .right-pane {
    margin-left: 0;
  }
}
</style>
