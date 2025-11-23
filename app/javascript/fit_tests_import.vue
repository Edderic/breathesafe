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

          <div class='header-row-selector'>
            <label for="header-row-index">Header row index:</label>
            <select id="header-row-index" v-model="headerRowIndex" @change="updateColumnsFromHeaderRow">
              <option :value="0">0</option>
              <option :value="1">1</option>
              <option :value="2">2</option>
              <option :value="3">3</option>
            </select>
          </div>

          <div v-if="fileColumns && fileColumns.length > 0" class='column-matching-table'>
            <table>
              <thead>
                <tr>
                  <th>Columns Found in File</th>
                  <th>Breathesafe matching column</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(column, index) in fileColumns" :key="index">
                  <td>{{ column }}</td>
                  <td>
                    <select
                      v-model="columnMappings[column]"
                      @change="updateColumnMatching"
                      class="column-select"
                    >
                      <option value="">-- Select --</option>
                      <option value="User.email">User.email</option>
                      <option value="Profile.first_name">Profile.first_name</option>
                      <option value="Profile.last_name">Profile.last_name</option>
                      <option value="Mask.unique_internal_model_code">Mask.unique_internal_model_code</option>
                      <option value="QNFT -> Bending over">QNFT -> Bending over</option>
                      <option value="QNFT -> Talking">QNFT -> Talking</option>
                      <option value="QNFT -> Turning head side to side">QNFT -> Turning head side to side</option>
                      <option value="QNFT -> Moving head up and down">QNFT -> Moving head up and down</option>
                      <option value="QNFT -> Normal breathing 1">QNFT -> Normal breathing 1</option>
                      <option value="QNFT -> Normal breathing 2">QNFT -> Normal breathing 2</option>
                      <option value="QNFT -> Normal breathing (SEALED)">QNFT -> Normal breathing (SEALED)</option>
                      <option value="QNFT -> Grimace">QNFT -> Grimace</option>
                      <option value="QNFT -> Deep breathing">QNFT -> Deep breathing</option>
                      <option value="QLFT -> Bending over">QLFT -> Bending over</option>
                      <option value="QLFT -> Talking">QLFT -> Talking</option>
                      <option value="QLFT -> Turning head side to side">QLFT -> Turning head side to side</option>
                      <option value="QLFT -> Moving head up and down">QLFT -> Moving head up and down</option>
                      <option value="QLFT -> Normal breathing 1">QLFT -> Normal breathing 1</option>
                      <option value="QLFT -> Normal breathing 2">QLFT -> Normal breathing 2</option>
                      <option value="QLFT -> Normal breathing (SEALED)">QLFT -> Normal breathing (SEALED)</option>
                      <option value="QLFT -> Grimace">QLFT -> Grimace</option>
                      <option value="QLFT -> Deep breathing">QLFT -> Deep breathing</option>
                      <option value="QNFT mode (N99 / N95)">QNFT mode (N99 / N95)</option>
                      <option value="QLFT -> solution">QLFT -> solution</option>
                      <option value='comfort -> "Is there enough room to talk?"'>comfort -> "Is there enough room to talk?"</option>
                      <option value='comfort -> "Is there adequate room for eye protection?"'>comfort -> "Is there adequate room for eye protection?"</option>
                      <option value='comfort -> "How comfortable is the position of the mask on the nose?"'>comfort -> "How comfortable is the position of the mask on the nose?"</option>
                      <option value='comfort -> "How comfortable is the position of the mask on face and cheeks?"'>comfort -> "How comfortable is the position of the mask on face and cheeks?"</option>
                      <option value="USC -> What do you think about the sizing of this mask relative to your face?">USC -> What do you think about the sizing of this mask relative to your face?</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No columns found. Please import a file first.</p>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='!fileColumns || fileColumns.length === 0'/>
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
      fileColumns: [],
      csvLines: [],
      headerRowIndex: 0,
      columnMappings: {},
      columnMatching: null,
      userMatching: null,
      maskMatching: null,
      userSealCheckMatching: null,
      fitTestDataMatching: null,
      completedSteps: []
    }
  },
  methods: {
    async handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.importedFile = {
          name: file.name,
          size: file.size,
          file: file
        }

        // Parse CSV file to extract column names
        await this.parseCSVFile(file)
      }
    },
    parseCSVFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()

        reader.onload = (e) => {
          try {
            const text = e.target.result
            // Store all lines for later re-parsing
            this.csvLines = text.split('\n').filter(line => line.trim() !== '')

            // Parse columns using the current header row index
            this.updateColumnsFromHeaderRow()

            resolve()
          } catch (error) {
            this.messages = [{ str: `Error parsing file: ${error.message}` }]
            this.fileColumns = []
            reject(error)
          }
        }

        reader.onerror = () => {
          this.messages = [{ str: 'Error reading file.' }]
          this.fileColumns = []
          reject(new Error('File reading error'))
        }

        // Read only the first few KB to get the header rows
        const blob = file.slice(0, 10240) // Read first 10KB
        reader.readAsText(blob)
      })
    },
    updateColumnsFromHeaderRow() {
      if (!this.csvLines || this.csvLines.length === 0) {
        this.fileColumns = []
        return
      }

      // Check if the selected header row index is valid
      if (this.headerRowIndex >= this.csvLines.length) {
        this.fileColumns = []
        this.messages = [{ str: `Header row index ${this.headerRowIndex} is beyond the file length.` }]
        return
      }

      try {
        // Parse the header row at the selected index
        const headerLine = this.csvLines[this.headerRowIndex]
        // Handle CSV parsing - split by comma, but respect quoted fields
        const columns = this.parseCSVLine(headerLine)
        const newColumns = columns.map(col => col.trim()).filter(col => col !== '')

        // Preserve existing mappings for columns that still exist
        const preservedMappings = {}
        newColumns.forEach(column => {
          if (this.columnMappings.hasOwnProperty(column)) {
            preservedMappings[column] = this.columnMappings[column]
          } else {
            preservedMappings[column] = ''
          }
        })

        this.fileColumns = newColumns
        this.columnMappings = preservedMappings

        // Update columnMatching object
        this.updateColumnMatching()

        // Clear any previous error messages if parsing succeeded
        if (this.fileColumns.length > 0) {
          this.messages = []
        }
      } catch (error) {
        this.messages = [{ str: `Error parsing header row: ${error.message}` }]
        this.fileColumns = []
      }
    },
    updateColumnMatching() {
      // Update the columnMatching object with current mappings
      this.columnMatching = { ...this.columnMappings }
    },
    parseCSVLine(line) {
      // Simple CSV parser that handles quoted fields
      const result = []
      let current = ''
      let inQuotes = false

      for (let i = 0; i < line.length; i++) {
        const char = line[i]

        if (char === '"') {
          if (inQuotes && line[i + 1] === '"') {
            // Escaped quote
            current += '"'
            i++ // Skip next quote
          } else {
            // Toggle quote state
            inQuotes = !inQuotes
          }
        } else if (char === ',' && !inQuotes) {
          // End of field
          result.push(current)
          current = ''
        } else {
          current += char
        }
      }

      // Add the last field
      result.push(current)

      return result
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

.header-row-selector {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin: 1em 0;
  justify-content: center;
}

.header-row-selector label {
  font-weight: 500;
}

.header-row-selector select {
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 1em;
}

.column-matching-table {
  margin-top: 2em;
}

.column-matching-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

.column-matching-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
}

.column-matching-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.column-select {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.column-matching-table tbody tr:hover {
  background-color: #f8f9fa;
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
