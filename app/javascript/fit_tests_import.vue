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
        :sourceName="sourceName"
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

          <div v-if="importedFile || sourceName" class='file-info'>
            <h3 class='text-align-center'>Selected File</h3>
            <table>
              <tbody>
                <tr>
                  <th>File Name</th>
                  <td>{{ sourceName || importedFile.name }}</td>
                </tr>
                <tr v-if="bulkImportFileSize">
                  <th>File Size</th>
                  <td>{{ formatFileSize(bulkImportFileSize) }}</td>
                </tr>
                <tr v-else-if="importedFile">
                  <th>File Size</th>
                  <td>{{ formatFileSize(importedFile.size) }}</td>
                </tr>
                <tr v-if="bulkImportCreatedAt">
                  <th>Upload Date/Time</th>
                  <td>{{ formatDateTime(bulkImportCreatedAt) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='!importedFile || isSaving'/>
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
                      <option :value="''">-- Select --</option>
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
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='!fileColumns || fileColumns.length === 0 || isSaving'/>
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
import axios from 'axios'
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import FitTestsImportProgressBar from './fit_tests_import_progress_bar.vue'
import { setupCSRF } from './misc.js'
import { mapState, mapActions } from 'pinia'
import { useMainStore } from './stores/main_store.js'

export default {
  name: 'FitTestsImport',
  components: {
    Button,
    ClosableMessage,
    FitTestsImportProgressBar
  },
  computed: {
    ...mapState(useMainStore, ['currentUser'])
  },
  data() {
    return {
      messages: [],
      currentStep: 'Import File',
      sourceName: null,
      importedFile: null,
      fileColumns: [],
      csvLines: [],
      csvFullContent: null,
      headerRowIndex: 0,
      columnMappings: {},
      columnMatching: null,
      userMatching: null,
      maskMatching: null,
      userSealCheckMatching: null,
      fitTestDataMatching: null,
      completedSteps: [],
      bulkFitTestsImportId: null,
      isSaving: false,
      bulkImportCreatedAt: null,
      bulkImportFileSize: null
    }
  },
  async mounted() {
    setupCSRF()

    // Check if we're returning from sign-in (check for attempt-name in query)
    if (this.$route.query['attempt-name'] && this.$route.query['attempt-name'] !== 'SignIn') {
      // User was redirected here after sign-in, reload data
      if (this.$route.params.id) {
        await this.loadBulkImport()
      }
    } else {
      // Normal load
      if (this.$route.params.id) {
        await this.loadBulkImport()
      }
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    buildReturnRouteQuery() {
      // Build query params for returning to this route after sign-in
      const query = {
        'attempt-name': this.$route.name
      }

      // Add route params as params-* query params
      if (this.$route.params && Object.keys(this.$route.params).length > 0) {
        Object.keys(this.$route.params).forEach(key => {
          query[`params-${key}`] = this.$route.params[key]
        })
      }

      // Preserve existing query params (except attempt-name and params-*)
      Object.keys(this.$route.query).forEach(key => {
        if (key !== 'attempt-name' && !key.startsWith('params-')) {
          query[key] = this.$route.query[key]
        }
      })

      return query
    },
    redirectToSignIn() {
      // Redirect to SignIn with return route information
      const query = this.buildReturnRouteQuery()
      this.$router.push({
        name: 'SignIn',
        query: query
      })
    },
    async checkAuthentication() {
      // Check if user is authenticated, refresh if needed
      if (!this.currentUser) {
        await this.getCurrentUser()
      }
      return !!this.currentUser
    },
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
    readFullFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()

        reader.onload = (e) => {
          try {
            this.csvFullContent = e.target.result
            resolve(e.target.result)
          } catch (error) {
            reject(error)
          }
        }

        reader.onerror = () => {
          reject(new Error('File reading error'))
        }

        reader.readAsText(file)
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
      // Update the columnMatching object with current mappings (excluding header_row_index)
      // header_row_index is stored separately and added when saving
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
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return ''
      const date = new Date(dateTimeString)
      return date.toLocaleString()
    },
    navigateToStep(stepKey) {
      this.currentStep = stepKey

      // If navigating back to Column Matching, reload from backend
      if (stepKey === 'Column Matching' && this.bulkFitTestsImportId) {
        this.reloadColumnMatching()
      }
    },
    async reloadColumnMatching() {
      if (!this.bulkFitTestsImportId) {
        return
      }

      // Check authentication before reloading
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      try {
        const response = await axios.get(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`)

        if (response.status === 200 && response.data.bulk_fit_tests_import) {
          const bulkImport = response.data.bulk_fit_tests_import

          // Restore header_row_index FIRST before parsing columns
          if (bulkImport.column_matching_mapping && bulkImport.column_matching_mapping.header_row_index !== undefined) {
            this.headerRowIndex = bulkImport.column_matching_mapping.header_row_index
          }

          // Re-parse columns using the restored header_row_index
          if (bulkImport.import_data) {
            this.csvLines = bulkImport.import_data.split('\n').filter(line => line.trim() !== '')
            this.updateColumnsFromHeaderRow()
          }

          // Restore column mappings
          if (bulkImport.column_matching_mapping) {
            this.columnMatching = bulkImport.column_matching_mapping

            // Initialize columnMappings for all fileColumns first (with empty strings)
            this.fileColumns.forEach(column => {
              this.columnMappings[column] = ''
            })

            // Populate columnMappings from saved data (excluding header_row_index)
            // Use empty string if mapping is null/undefined to show "-- Select --"
            Object.keys(bulkImport.column_matching_mapping).forEach(csvColumn => {
              if (csvColumn !== 'header_row_index') {
                // Only set if the column exists in fileColumns
                if (this.fileColumns.includes(csvColumn)) {
                  this.columnMappings[csvColumn] = bulkImport.column_matching_mapping[csvColumn] || ''
                }
              }
            })
          } else {
            // If no saved mappings, initialize all columns with empty strings
            this.fileColumns.forEach(column => {
              this.columnMappings[column] = ''
            })
          }
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to reload column matching.'
        this.messages = [{ str: errorMsg }]
      }
    },
    async goToNextStep() {
      // Check authentication before proceeding
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      // If we're on the "Import File" step, save to backend first
      if (this.currentStep === 'Import File') {
        await this.saveBulkImport()
        return // Navigation will happen in saveBulkImport
      }

      // If we're on the "Column Matching" step, save column matching data
      if (this.currentStep === 'Column Matching') {
        await this.saveColumnMatching()
        return // Navigation will happen in saveColumnMatching if successful
      }

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
    async saveColumnMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }

      // Check authentication before saving
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        // Update columnMatching with current mappings
        this.updateColumnMatching()

        // Create the column_matching_mapping object with header_row_index included
        // Include all columns from fileColumns, even if they have empty mappings
        const columnMatchingMapping = {
          header_row_index: this.headerRowIndex
        }

        // Add mappings for all file columns (empty string if no mapping selected)
        this.fileColumns.forEach(column => {
          columnMatchingMapping[column] = this.columnMappings[column] || ''
        })

        const payload = {
          bulk_fit_tests_import: {
            column_matching_mapping: columnMatchingMapping
          }
        }

        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, payload)

        if (response.status === 200) {
          // Update local state
          this.columnMatching = columnMatchingMapping

          // Move to User Matching step
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

          // Mark Column Matching as completed
          if (!this.completedSteps.includes('Column Matching')) {
            this.completedSteps.push('Column Matching')
          }
        } else {
          const errorMessages = response.data.messages || ['Failed to save column matching.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to save column matching.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
      }
    },
    async saveBulkImport() {
      if (!this.importedFile || this.isSaving) {
        return
      }

      // Check authentication before saving
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        // Read the full file content if not already read
        if (!this.csvFullContent) {
          await this.readFullFile(this.importedFile.file)
        }

        const payload = {
          bulk_fit_tests_import: {
            source_name: this.importedFile.name,
            source_type: 'CSV',
            import_data: this.csvFullContent,
            status: 'pending',
            column_matching_mapping: this.columnMatching || {},
            mask_matching: this.maskMatching || {},
            user_seal_check_matching: this.userSealCheckMatching || {},
            fit_testing_matching: this.fitTestDataMatching || {}
          }
        }

        const response = await axios.post('/bulk_fit_tests_imports.json', payload)

        if (response.status === 201 && response.data.bulk_fit_tests_import) {
          this.bulkFitTestsImportId = response.data.bulk_fit_tests_import.id

          // Set source_name for progress bar display
          if (response.data.bulk_fit_tests_import.source_name) {
            this.sourceName = response.data.bulk_fit_tests_import.source_name
          }

          // Store created_at for display
          if (response.data.bulk_fit_tests_import.created_at) {
            this.bulkImportCreatedAt = response.data.bulk_fit_tests_import.created_at
          }

          // Calculate file size
          if (this.csvFullContent) {
            this.bulkImportFileSize = new Blob([this.csvFullContent]).size
          }

          // Mark Import File as completed
          if (!this.completedSteps.includes('Import File')) {
            this.completedSteps.push('Import File')
          }

          // Navigate to Column Matching step
          this.currentStep = 'Column Matching'

          // Update URL to reflect the bulk import ID (for refresh/back button support)
          // Only update if we're on the new route, not if we're already on a specific import
          if (!this.$route.params.id) {
            this.$router.replace({
              name: 'BulkFitTestsImport',
              params: { id: this.bulkFitTestsImportId }
            })
          }
        } else {
          const errorMessages = response.data.messages || ['Failed to save import file.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to save import file.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
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
    async loadBulkImport() {
      // Check authentication before loading
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      try {
        const response = await axios.get(`/bulk_fit_tests_imports/${this.$route.params.id}.json`)

        if (response.status === 200 && response.data.bulk_fit_tests_import) {
          const bulkImport = response.data.bulk_fit_tests_import
          this.bulkFitTestsImportId = bulkImport.id

          // Set source_name for progress bar display
          if (bulkImport.source_name) {
            this.sourceName = bulkImport.source_name
          }

          // Store created_at for display
          if (bulkImport.created_at) {
            this.bulkImportCreatedAt = bulkImport.created_at
          }

          // Calculate file size from import_data if available
          if (bulkImport.import_data) {
            this.bulkImportFileSize = new Blob([bulkImport.import_data]).size
            this.csvFullContent = bulkImport.import_data
            this.csvLines = bulkImport.import_data.split('\n').filter(line => line.trim() !== '')
          }

          // Restore header_row_index FIRST before parsing columns
          if (bulkImport.column_matching_mapping && bulkImport.column_matching_mapping.header_row_index !== undefined) {
            this.headerRowIndex = bulkImport.column_matching_mapping.header_row_index
          }

          // Parse columns using the restored header_row_index
          if (bulkImport.import_data) {
            this.updateColumnsFromHeaderRow()
          }

          // Load column mappings if available
          if (bulkImport.column_matching_mapping) {
            this.columnMatching = bulkImport.column_matching_mapping

            // Initialize columnMappings for all fileColumns first (with empty strings)
            this.fileColumns.forEach(column => {
              if (!this.columnMappings.hasOwnProperty(column)) {
                this.columnMappings[column] = ''
              }
            })

            // Populate columnMappings from saved data (excluding header_row_index)
            // Use empty string if mapping is null/undefined to show "-- Select --"
            Object.keys(bulkImport.column_matching_mapping).forEach(csvColumn => {
              if (csvColumn !== 'header_row_index') {
                // Only set if the column exists in fileColumns
                if (this.fileColumns.includes(csvColumn)) {
                  this.columnMappings[csvColumn] = bulkImport.column_matching_mapping[csvColumn] || ''
                }
              }
            })
          } else {
            // If no saved mappings, initialize all columns with empty strings
            this.fileColumns.forEach(column => {
              this.columnMappings[column] = ''
            })
          }

          // Set current step and completed steps
          if (bulkImport.column_matching_mapping && Object.keys(bulkImport.column_matching_mapping).length > 1) {
            // If column matching exists (has more than just header_row_index), we're on Column Matching step
            this.currentStep = 'Column Matching'
            this.completedSteps = ['Import File']
          } else if (bulkImport.import_data) {
            // If import_data exists but no column matching yet, start at Column Matching
            this.currentStep = 'Column Matching'
            this.completedSteps = ['Import File']
          }
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to load bulk import.'
        this.messages = [{ str: errorMsg }]
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
  overflow-y: scroll;
  height: 50vh;
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
