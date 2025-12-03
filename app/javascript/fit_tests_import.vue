<template>
  <div class='align-items-center flex-dir-col top-container'>
    <div class='flex align-items-center row phone'>
      <h2 class='tagline'>Import Fit Tests</h2>
    </div>

    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []; showGoToBulkImports = false' :messages='messages'>
        <div v-if="showGoToBulkImports" class="row justify-content-center" style="margin-top: 0.5em;">
          <router-link :to="{ name: 'BulkFitTestsImportsList' }" @click="messages = []; showGoToBulkImports = false">
            <Button shadow='true' class='button' text="Go to Bulk Imports"/>
          </router-link>
        </div>
      </ClosableMessage>
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
        :testingModeMatching="testingModeMatching"
        :qlftValuesMatching="qlftValuesMatching"
        :qlftValuesMatchingNotApplicable="qlftValuesMatchingNotApplicable"
        :comfortMatching="comfortMatching"
        :fitTestDataMatching="fitTestDataMatching"
        :completedSteps="completedSteps"
        :currentStep="currentStep"
        :userSealCheckMatchingSkipped="userSealCheckMatchingSkipped"
        @navigate-to-step="navigateToStep"
      >
        <template #actions>
          <router-link :to="{ name: 'BulkFitTestsImportsList' }">
            <Button shadow='true' class='button' text="Bulk Imports"/>
          </router-link>
        </template>
      </FitTestsImportProgressBar>

      <!-- Import File Step -->
      <div v-show='currentStep == "Import File"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Import File</h2>
          <div class='text-align-center justify-content-center align-items-center'>
            <h3 style='display: inline-block; margin-right: 8px;'>Select a file to import</h3>
            <CircularButton text="?" @click="showImportFileHelp = true"/>
          </div>

          <Popup v-if="showImportFileHelp" @onclose="showImportFileHelp = false">
            <div>
              <h3>What should the file contain?</h3>
              <p>Your CSV should include columns similar to:</p>
              <ul style="text-align: left; margin-left: 1.2em;">
                <li><strong>Manager email</strong></li>
                <li><strong>User name</strong></li>
                <li><strong>At least one fit testing exercise result</strong>, e.g.:
                  <ul>
                    <li>Normal breathing 1</li>
                    <li>Deep breathing</li>
                    <li>Talking</li>
                    <li>Turning head side to side</li>
                    <li>Moving head up and down</li>
                    <li>Grimace</li>
                    <li>Bending over</li>
                    <li>Normal breathing 2</li>
                    <li>Normal breathing (SEALED)</li>
                  </ul>
                </li>
                <li><strong>Testing mode</strong> (e.g., N99, N95, or QLFT)</li>
              </ul>
              <p>Optional columns</p>
              <ul style="text-align: left; margin-left: 1.2em;">
                <li><strong>User seal check questions</strong>, e.g.:
                  <ul>
                    <li>What do you think about the sizing of this mask relative to your face?</li>
                    <li>How much air movement on your face along the seal of the mask did you feel?</li>
                  </ul>
                </li>
                <li><strong>Comfort questions</strong>, e.g.:
                  <ul>
                    <li>How comfortable is the position of the mask on the nose?</li>
                    <li>Is there enough room to talk?</li>
                    <li>How comfortable is the position of the mask on face and cheeks?</li>
                  </ul>
                </li>
              </ul>
              <p>
                <a href="/sample_fit_tests_import.csv" download>Download sample CSV template</a>
              </p>
              <h4>What to expect during import</h4>
              <ul style="text-align: left; margin-left: 1.2em;">
                <li>Columns in your file will be matched to columns Breathesafe understands.</li>
                <li>Values in those columns will be matched to values that Breathesafe understands.</li>
              </ul>
            </div>
          </Popup>

          <div class='row justify-content-center'>
            <input
              type="file"
              @change='handleFileSelect'
              accept=".csv,.xlsx,.xls"
              ref="fileInput"
              :disabled="isCompleted"
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

      <!-- Comfort Matching Step -->
      <div v-show='currentStep == "Comfort Matching"' class='right-pane narrow-width'>
        <div class='display'>
          <h2 class='text-align-center'>Comfort Matching</h2>
          <h3 class='text-align-center'>Match comfort questions</h3>

          <div class='user-seal-check-matching-header justify-content-center'>
            <Button shadow='true' class='button match-button' text="Match" @click='attemptComfortAutoMatch' :disabled='comfortMatchingRows.length === 0'/>
          </div>

          <div v-if="comfortMatchingRows.length > 0" class='user-seal-check-matching-table fit-test-data-table content'>
            <table>
              <thead>
                <tr>
                  <th>Breathesafe comfort question</th>
                  <th>Value found in file</th>
                  <th>Breathesafe matching value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in comfortMatchingRows" :key="`${row.question}-${row.fileValue}-${index}`">
                  <td>{{ row.question }}</td>
                  <td>{{ row.fileValue }}</td>
                  <td>
                    <select
                      v-model="row.selectedBreathesafeValue"
                      @change="updateComfortMatching"
                      class="usc-select"
                      :disabled="isCompleted"
                    >
                      <option :value="''">-- Select --</option>
                      <option v-for="opt in getComfortOptions(row.question)" :key="opt" :value="opt">{{ opt }}</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No comfort values found. You may skip this step.</p>
          </div>
        </div>
        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='isSaving'/>
        </div>
        <br>
        <br>
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
            <Button shadow='true' class='button match-button' text="Match" @click='attemptAutoMatch' :disabled='!fileColumns || fileColumns.length === 0'/>
          </div>

          <ClosableMessage
            v-if="visibleColumnMatchingValidationErrors.length > 0"
            :messages="visibleColumnMatchingValidationErrors.map(error => ({ str: getDuplicateErrorMessage(error).str }))"
            @onclose="dismissAllValidationErrors"
          />
          <ClosableMessage
            v-if="beardLengthWarnings.length > 0"
            :messages="beardLengthWarnings"
            @onclose="dismissBeardWarnings"
          />

          <div v-if="fileColumns && fileColumns.length > 0" class='column-matching-table content'>
            <table>
              <thead>
                <tr>
                  <th>Columns Found in File</th>
                  <th>Breathesafe matching column</th>
                  <th>Similarity score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(column, index) in fileColumns" :key="index" :class="{ 'has-duplicate-error': isColumnInDuplicateError(column) }">
                  <td>{{ column }}</td>
                  <td>
                    <select
                      v-model="columnMappings[column]"
                      @change="updateColumnMatching"
                      class="column-select"
                      :class="{ 'has-error': isColumnInDuplicateError(column) }"
                      :disabled="isCompleted"
                    >
                      <option :value="''">-- Select --</option>
                      <option value="manager email">manager email</option>
                      <option value="first name">first name</option>
                      <option value="last name">last name</option>
                      <option value="user name">user name</option>
                      <option value="Mask.unique_internal_model_code">Mask.unique_internal_model_code</option>
                      <option value="Bending over">Bending over</option>
                      <option value="Talking">Talking</option>
                      <option value="Turning head side to side">Turning head side to side</option>
                      <option value="Moving head up and down">Moving head up and down</option>
                      <option value="Normal breathing 1">Normal breathing 1</option>
                      <option value="Normal breathing 2">Normal breathing 2</option>
                      <option value="Normal breathing (SEALED)">Normal breathing (SEALED)</option>
                      <option value="Grimace">Grimace</option>
                      <option value="Deep breathing">Deep breathing</option>
                      <option value="Testing mode">Testing mode (QLFT / N99 / N95)</option>
                      <option value="QLFT -> solution">QLFT -> solution</option>
                      <option value="facial hair beard length mm">facial hair beard length mm</option>
                      <option value='comfort -> "Is there enough room to talk?"'>comfort -> "Is there enough room to talk?"</option>
                      <option value='comfort -> "How comfortable is the position of the mask on the nose?"'>comfort -> "How comfortable is the position of the mask on the nose?"</option>
                      <option value='comfort -> "How comfortable is the position of the mask on face and cheeks?"'>comfort -> "How comfortable is the position of the mask on face and cheeks?"</option>
                      <option value="USC -> What do you think about the sizing of this mask relative to your face?">USC -> What do you think about the sizing of this mask relative to your face?</option>
                      <option value="USC -> How much air movement on your face along the seal of the mask did you feel?">USC -> How much air movement on your face along the seal of the mask did you feel?</option>
                    </select>
                  </td>
                  <td class="similarity-score-cell">
                    <span v-if="getSimilarityScore(column) !== null" class="similarity-score">
                      {{ formatSimilarityScore(getSimilarityScore(column)) }}
                    </span>
                    <span v-else class="similarity-score-empty">--</span>
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
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='!fileColumns || fileColumns.length === 0 || isSaving || hasColumnMatchingValidationErrors'/>
        </div>
        <br>
        <br>
      </div>

      <!-- User Matching Step -->
      <div v-show='currentStep == "User Matching"' class='right-pane narrow-width'>
        <div class='display'>
          <h2 class='text-align-center'>User Matching</h2>
          <h3 class='text-align-center'>Match imported users to existing users</h3>

          <div class='user-matching-header'>
            <Button shadow='true' class='button match-button' text="Match" @click='attemptUserAutoMatch' :disabled='userMatchingRows.length === 0 || loadingManagedUsers || hasUserMatchingErrors'/>
          </div>

          <!-- Match Confirmation Popup for User Matching -->
          <Popup v-if="showUserMatchConfirmation" @onclose="cancelUserMatchConfirmation">
            <div class='match-confirmation-content'>
              <h3>Confirm User Matching</h3>
              <p>The following mappings will overwrite existing selections:</p>
              <ul class='match-overwrites-list'>
                <li v-for="(breathesafeName, fileUserName) in pendingUserMatchOverwrites" :key="fileUserName">
                  <strong>{{ fileUserName }}</strong> → {{ breathesafeName }}
                </li>
              </ul>
              <p>Do you want to proceed?</p>
              <div class='match-confirmation-buttons'>
                <Button shadow='true' class='button' text="Cancel" @click='cancelUserMatchConfirmation'/>
                <Button shadow='true' class='button' text="Confirm" @click='confirmUserMatchOverwrite'/>
              </div>
            </div>
          </Popup>

          <div v-if="userMatchingRows.length > 0" class='user-matching-table content'>
            <table>
              <thead>
                <tr>
                  <th>File manager email</th>
                  <th>File user name</th>
                  <th>Breathesafe user name</th>
                  <th>Similarity score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in userMatchingRows" :key="index" :class="{ 'has-error': row.hasError }">
                  <td>
                    <span v-if="row.managerEmailError" class="error-text">{{ row.managerEmailError }}</span>
                    <span v-else>{{ row.managerEmail }}</span>
                  </td>
                  <td>
                    <span v-if="row.userNameError" class="error-text">{{ row.userNameError }}</span>
                    <span v-else>{{ row.userName }}</span>
                  </td>
                  <td>
                    <select
                      v-model="row.selectedManagedUserId"
                      @change="updateUserMatching"
                      class="user-select"
                      :class="{ 'has-error': row.hasError }"
                      :disabled="row.hasError || loadingManagedUsers || isCompleted"
                    >
                      <option :value="null">-- Select --</option>
                      <option v-for="managedUser in getManagedUsersForRow(row)" :key="managedUser.managed_id" :value="managedUser.managed_id">
                        {{ getManagedUserName(managedUser) }}
                      </option>
                      <option value="__to_be_created__">To be created</option>
                    </select>
                  </td>
                  <td class="similarity-score-cell">
                    <span v-if="getUserMatchingSimilarityScore(row) !== null" class="similarity-score">
                      {{ formatSimilarityScore(getUserMatchingSimilarityScore(row)) }}
                    </span>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No user data found. Please complete column matching first.</p>
          </div>
          <br>
          <br>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='userMatchingRows.length === 0 || isSaving || hasUserMatchingErrors'/>
        </div>
      </div>

      <!-- Mask Matching Step -->
      <div v-show='currentStep == "Mask Matching"' class='right-pane narrow-width'>
        <div class='display'>
          <h2 class='text-align-center'>Mask Matching</h2>
          <h3 class='text-align-center'>Match imported masks to existing masks</h3>

          <div class='mask-matching-header'>
            <Button shadow='true' class='button match-button' text="Match" @click='attemptMaskAutoMatch' :disabled='maskMatchingRows.length === 0 || loadingMasks'/>
          </div>

          <!-- Match Confirmation Popup for Mask Matching -->
          <Popup v-if="showMaskMatchConfirmation" @onclose="cancelMaskMatchConfirmation">
            <div class='match-confirmation-content'>
              <h3>Confirm Mask Matching</h3>
              <p>The following mappings will overwrite existing selections:</p>
              <ul class='match-overwrites-list'>
                <li v-for="(breathesafeName, fileMaskName) in pendingMaskMatchOverwrites" :key="fileMaskName">
                  <strong>{{ fileMaskName }}</strong> → {{ breathesafeName }}
                </li>
              </ul>
              <p>Do you want to proceed?</p>
              <div class='match-confirmation-buttons'>
                <Button shadow='true' class='button' text="Cancel" @click='cancelMaskMatchConfirmation'/>
                <Button shadow='true' class='button' text="Confirm" @click='confirmMaskMatchOverwrite'/>
              </div>
            </div>
          </Popup>

          <div v-if="maskMatchingRows.length > 0" class='mask-matching-table content'>
            <table>
              <thead>
                <tr>
                  <th>File Mask name</th>
                  <th>Breathesafe Mask name</th>
                  <th>Breathesafe Mask id</th>
                  <th>Similarity Score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in maskMatchingRows" :key="index">
                  <td>{{ row.fileMaskName }}</td>
                  <td>
                    <select
                      v-model="row.selectedMaskId"
                      @change="updateMaskMatching"
                      class="mask-select"
                      :disabled="isCompleted"
                    >
                      <option :value="null">-- Select --</option>
                      <option v-for="mask in deduplicatedMasks" :key="mask.id" :value="mask.id">
                        {{ mask.unique_internal_model_code }}
                      </option>
                      <option value="__to_be_created__">To be created</option>
                    </select>
                  </td>
                  <td>
                    <router-link
                      v-if="row.selectedMaskId && row.selectedMaskId !== '__to_be_created__'"
                      :to="{ name: 'ShowMask', params: { id: row.selectedMaskId }, query: { displayTab: 'Misc. Info' } }"
                      target="_blank"
                      class="mask-id-link"
                    >
                      {{ row.selectedMaskId }}
                    </router-link>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                  <td class="similarity-score-cell">
                    <span v-if="getMaskMatchingSimilarityScore(row) !== null" class="similarity-score">
                      {{ formatSimilarityScore(getMaskMatchingSimilarityScore(row)) }}
                    </span>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No mask data found. Please complete column matching first.</p>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='maskMatchingRows.length === 0 || isSaving'/>
        </div>
        <br>
        <br>
      </div>

      <!-- User Seal Check Matching Step -->
      <div v-show='currentStep == "User Seal Check Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>User Seal Check Matching</h2>
          <h3 class='text-align-center'>Match user seal check data</h3>

          <div v-if="!hasUSCColumnsMatched" class='text-align-center' style='margin-top: 2em; padding: 1em; background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;'>
            <p style='margin: 0; color: #856404;'>
              ⚠️ No columns were matched to Breathesafe user seal check columns. Doing so is optional. If you think this is a mistake, please go to the Column Matching section by
              <a href="#" @click.prevent="navigateToStep('Column Matching')" style='color: #007bff; text-decoration: underline; cursor: pointer;'>clicking here</a>. Otherwise, please hit Next to continue.
            </p>
          </div>

          <div v-else >
            <div class='user-seal-check-matching-header justify-content-center'>
              <Button shadow='true' class='button match-button' text="Match" @click='attemptUSCAutoMatch' :disabled='userSealCheckMatchingRows.length === 0'/>
            </div>
            <div v-if="userSealCheckMatchingRows.length > 0" class='user-seal-check-matching-table fit-test-data-table content'>
              <table>
                <thead>
                  <tr>
                    <th>Breathesafe user seal check question</th>
                    <th>Value found in file</th>
                    <th>Breathesafe matching value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in sortedUserSealCheckMatchingRows" :key="index">
                    <td>{{ row.question }}</td>
                    <td>{{ row.fileValue }}</td>
                    <td>
                      <select
                        v-model="row.selectedBreathesafeValue"
                        @change="updateUserSealCheckMatching"
                        class="usc-select"
                        :disabled="isCompleted"
                      >
                        <option :value="''">-- Select --</option>
                        <option v-for="opt in getUSCOptions(row.question)" :key="opt" :value="opt">{{ opt }}</option>
                      </select>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class='text-align-center'>
              <p>No user seal check values found. Please complete column matching first.</p>
            </div>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep'/>
        </div>
      </div>

      <!-- Testing Mode Values Matching Step -->
      <div v-show='currentStep == "Testing Mode Values Matching"' class='right-pane narrow-width'>
        <div class='display'>
          <h2 class='text-align-center'>Testing Mode Values Matching</h2>
          <h3 class='text-align-center'>Match file testing mode values to Breathesafe testing mode values</h3>

          <div class='testing-mode-matching-header'>
            <Button shadow='true' class='button match-button' text="Match" @click='attemptTestingModeAutoMatch' :disabled='testingModeMatchingRows.length === 0'/>
          </div>

          <!-- Match Confirmation Popup for Testing Mode Matching -->
          <Popup v-if="showTestingModeMatchConfirmation" @onclose="cancelTestingModeMatchConfirmation">
            <div class='match-confirmation-content'>
              <h3>Confirm Testing Mode Matching</h3>
              <p>The following mappings will overwrite existing selections:</p>
              <ul class='match-overwrites-list'>
                <li v-for="(breathesafeValue, fileValue) in pendingTestingModeMatchOverwrites" :key="fileValue">
                  <strong>{{ fileValue }}</strong> → {{ breathesafeValue }}
                </li>
              </ul>
              <p>Do you want to proceed?</p>
              <div class='match-confirmation-buttons'>
                <Button shadow='true' class='button' text="Cancel" @click='cancelTestingModeMatchConfirmation'/>
                <Button shadow='true' class='button' text="Confirm" @click='confirmTestingModeMatchOverwrite'/>
              </div>
            </div>
          </Popup>

          <div v-if="testingModeMatchingRows.length > 0" class='testing-mode-matching-table content'>
            <table>
              <thead>
                <tr>
                  <th>File testing mode values</th>
                  <th>Breathesafe testing mode values</th>
                  <th>Similarity Score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in testingModeMatchingRows" :key="index">
                  <td>{{ row.fileValue }}</td>
                  <td>
                    <select
                      v-model="row.selectedBreathesafeValue"
                      @change="updateTestingModeMatching"
                      class="testing-mode-select"
                      :disabled="isCompleted"
                    >
                      <option :value="null">-- Select --</option>
                      <option value="N99">N99</option>
                      <option value="N95">N95</option>
                      <option value="QLFT">QLFT</option>
                    </select>
                  </td>
                  <td class="similarity-score-cell">
                    <span v-if="getTestingModeSimilarityScore(row) !== null" class="similarity-score">
                      {{ formatSimilarityScore(getTestingModeSimilarityScore(row)) }}
                    </span>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No testing mode data found. Please complete column matching first.</p>
          </div>
        </div>
        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='testingModeMatchingRows.length === 0 || hasUnmappedTestingModes || isSaving'/>
        </div>
        <br>
        <br>
      </div>

      <!-- QLFT Values Matching Step -->
      <div v-show='currentStep == "QLFT Values Matching"' class='right-pane narrow-width'>
        <div class='display'>
          <h2 class='text-align-center'>QLFT Values Matching</h2>
          <h3 class='text-align-center'>Match file QLFT exercise values to Breathesafe QLFT values (Pass/Fail)</h3>

          <div class='qlft-values-matching-header'>
            <Button shadow='true' class='button match-button' text="Match" @click='attemptQlftValuesAutoMatch' :disabled='qlftValuesMatchingRows.length === 0'/>
          </div>

          <!-- Match Confirmation Popup for QLFT Values Matching -->
          <Popup v-if="showQlftValuesMatchConfirmation" @onclose="cancelQlftValuesMatchConfirmation">
            <div class='match-confirmation-content'>
              <h3>Confirm QLFT Values Matching</h3>
              <p>The following mappings will overwrite existing selections:</p>
              <ul class='match-overwrites-list'>
                <li v-for="(breathesafeValue, fileValue) in pendingQlftValuesMatchOverwrites" :key="fileValue">
                  <strong>{{ fileValue }}</strong> → {{ breathesafeValue }}
                </li>
              </ul>
              <p>Do you want to proceed?</p>
              <div class='match-confirmation-buttons'>
                <Button shadow='true' class='button' text="Cancel" @click='cancelQlftValuesMatchConfirmation'/>
                <Button shadow='true' class='button' text="Confirm" @click='confirmQlftValuesMatchOverwrite'/>
              </div>
            </div>
          </Popup>

          <div v-if="qlftValuesMatchingRows.length > 0" class='qlft-values-matching-table content'>
            <table>
              <thead>
                <tr>
                  <th>File QLFT values</th>
                  <th>Breathesafe QLFT values</th>
                  <th>Similarity Score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in qlftValuesMatchingRows" :key="index">
                  <td>{{ row.fileValue }}</td>
                  <td>
                    <select
                      v-model="row.selectedBreathesafeValue"
                      @change="updateQlftValuesMatching"
                      class="qlft-values-select"
                      :disabled="isCompleted"
                    >
                      <option :value="null">-- Select --</option>
                      <option value="Pass">Pass</option>
                      <option value="Fail">Fail</option>
                    </select>
                  </td>
                  <td class="similarity-score-cell">
                    <span v-if="getQlftValuesSimilarityScore(row) !== null" class="similarity-score">
                      {{ formatSimilarityScore(getQlftValuesSimilarityScore(row)) }}
                    </span>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No QLFT values found. This step is not applicable if there are no QLFT rows.</p>
          </div>
        </div>
        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button shadow='true' class='button' text="Next" @click='goToNextStep' :disabled='isSaving'/>
        </div>
        <br>
        <br>
      </div>

      <!-- Match Confirmation Popup -->
      <Popup v-if="showMatchConfirmation" @onclose="cancelMatchConfirmation">
        <div class='match-confirmation-content'>
          <h3>Confirm Column Matching</h3>
          <p>The following mappings will overwrite existing selections:</p>
          <ul class='match-overwrites-list'>
            <li v-for="(breathesafeField, csvColumn) in pendingMatchOverwrites" :key="csvColumn">
              <strong>{{ csvColumn }}</strong> → {{ breathesafeField }}
            </li>
          </ul>
          <p>Do you want to proceed?</p>
          <div class='match-confirmation-buttons'>
            <Button shadow='true' class='button' text="Cancel" @click='cancelMatchConfirmation'/>
            <Button shadow='true' class='button' text="Confirm" @click='confirmMatchOverwrite'/>
          </div>
        </div>
      </Popup>

      <!-- Fit Test Data Matching Step -->
      <div v-show='currentStep == "Fit Test Data Matching"' class='right-pane narrow-width'>
        <div>
          <h2 class='text-align-center'>Review</h2>
          <h3 class='text-align-center'>Review and confirm fit test data</h3>

          <!-- Warning about unmapped QLFT values -->
          <div v-if="unmappedQlftValuesCount > 0" class='qlft-unmapped-warning'>
            <p><strong>Warning:</strong> {{ unmappedQlftValuesCount }} QLFT row(s) contain unmapped QLFT values. These rows will not be imported. Unmapped values are highlighted in red.</p>
          </div>

          <!-- Warning about invalid N95/N99 values -->
          <div v-if="invalidN95N99ValuesCount > 0" class='qlft-unmapped-warning'>
            <p><strong>Warning:</strong> {{ invalidN95N99ValuesCount }} N95/N99 row(s) contain non-alphanumeric characters in exercise columns. These rows will not be imported. Invalid values are highlighted in red.</p>
          </div>

          <div v-if="fitTestDataRows.length > 0" class='fit-test-data-table content'>
            <table>
              <thead>
                <tr>
                  <th>Manager email</th>
                  <th>User name</th>
                  <th>Breathesafe user id</th>
                  <th>Breathesafe mask name</th>
                  <th>Breathesafe mask id</th>
                  <th>Testing mode</th>
                  <th>Beard length (mm)</th>
                  <th>USC sizing</th>
                  <th>USC air movement</th>
                  <th>Comfort - Nose</th>
                  <th>Comfort - Talk</th>
                  <th>Comfort - Face/Cheeks</th>
                  <th>Bending over</th>
                  <th>Talking</th>
                  <th>Turning head side to side</th>
                  <th>Moving head up and down</th>
                  <th>Normal breathing 1</th>
                  <th>Normal breathing 2</th>
                  <th>Grimace</th>
                  <th>Deep breathing</th>
                  <th>Normal breathing (SEALED)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in fitTestDataRows" :key="index">
                  <td>{{ row.managerEmail || '--' }}</td>
                  <td :class="{ 'user-name-error': !row.managedUserId }">{{ row.userName || '--' }}</td>
                  <td>
                    <router-link
                      v-if="row.managedUserId"
                      :to="{ name: 'RespiratorUser', params: { id: row.managedUserId } }"
                      target="_blank"
                      class="user-id-link"
                    >
                      {{ row.managedUserId }}
                    </router-link>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                  <td>{{ row.maskName }}</td>
                  <td>
                    <router-link
                      v-if="row.maskId && row.maskId !== '__to_be_created__'"
                      :to="{ name: 'ShowMask', params: { id: row.maskId }, query: { displayTab: 'Misc. Info' } }"
                      target="_blank"
                      class="mask-id-link"
                    >
                      {{ row.maskId }}
                    </router-link>
                    <span v-else class="similarity-score-empty">--</span>
                  </td>
                  <td>{{ row.testingMode || '--' }}</td>
                  <td>
                    <span :class="{ 'qlft-unmapped-value': row.beardLengthInvalid }">
                      {{ row.beardLengthMm ? row.beardLengthMm : '--' }}
                    </span>
                  </td>
                  <td>
                    {{ row.uscSizing || '--' }}
                  </td>
                  <td>
                    {{ row.uscAirMovement || '--' }}
                  </td>
                  <td>{{ row.comfortNose || '--' }}</td>
                  <td>{{ row.comfortTalk || '--' }}</td>
                  <td>{{ row.comfortFace || '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.bendingOver) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.bendingOver) }">{{ row.exercises.bendingOver !== null && row.exercises.bendingOver !== undefined ? row.exercises.bendingOver : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.talking) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.talking) }">{{ row.exercises.talking !== null && row.exercises.talking !== undefined ? row.exercises.talking : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.turningHeadSideToSide) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.turningHeadSideToSide) }">{{ row.exercises.turningHeadSideToSide !== null && row.exercises.turningHeadSideToSide !== undefined ? row.exercises.turningHeadSideToSide : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.movingHeadUpAndDown) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.movingHeadUpAndDown) }">{{ row.exercises.movingHeadUpAndDown !== null && row.exercises.movingHeadUpAndDown !== undefined ? row.exercises.movingHeadUpAndDown : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.normalBreathing1) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.normalBreathing1) }">{{ row.exercises.normalBreathing1 !== null && row.exercises.normalBreathing1 !== undefined ? row.exercises.normalBreathing1 : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.normalBreathing2) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.normalBreathing2) }">{{ row.exercises.normalBreathing2 !== null && row.exercises.normalBreathing2 !== undefined ? row.exercises.normalBreathing2 : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.grimace) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.grimace) }">{{ row.exercises.grimace !== null && row.exercises.grimace !== undefined ? row.exercises.grimace : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.deepBreathing) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.deepBreathing) }">{{ row.exercises.deepBreathing !== null && row.exercises.deepBreathing !== undefined ? row.exercises.deepBreathing : '--' }}</td>
                  <td :class="{ 'qlft-unmapped-value': (row.exerciseHasUnmappedQlftValue && row.exerciseHasUnmappedQlftValue.normalBreathingSealed) || (row.exerciseHasInvalidN95N99Value && row.exerciseHasInvalidN95N99Value.normalBreathingSealed) }">{{ row.exercises.normalBreathingSealed !== null && row.exercises.normalBreathingSealed !== undefined ? row.exercises.normalBreathingSealed : '--' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class='text-align-center'>
            <p>No fit test data found. Please complete previous steps first.</p>
          </div>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Back" @click='goToPreviousStep'/>
          <Button shadow='true' class='button' text="Cancel" @click='cancelImport'/>
          <Button
            v-if="!isCompleted"
            shadow='true'
            class='button'
            text="Import"
            @click='completeImport'
            :disabled="isSaving || fitTestDataRows.length === 0"
          />
          <div v-if="isCompleted" class='text-align-center' style='margin-top: 1em; padding: 1em; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px;'>
            <p style='margin: 0; color: #155724;'>✓ This import has been completed and cannot be modified.</p>
          </div>
        </div>
        <br>
        <br>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Button from './button.vue'
import ClosableMessage from './closable_message.vue'
import FitTestsImportProgressBar from './fit_tests_import_progress_bar.vue'
import Popup from './pop_up.vue'
import CircularButton from './circular_button.vue'
import { setupCSRF } from './misc.js'
import { mapState, mapActions } from 'pinia'
import { useMainStore } from './stores/main_store.js'

export default {
  name: 'FitTestsImport',
  components: {
    Button,
    ClosableMessage,
    FitTestsImportProgressBar,
    Popup,
    CircularButton
  },
  computed: {
    ...mapState(useMainStore, ['currentUser']),
    sortedUserSealCheckMatchingRows() {
      const rows = this.userSealCheckMatchingRows || []
      return [...rows].sort((a, b) => {
        const aq = (a.question || '').toLowerCase()
        const bq = (b.question || '').toLowerCase()
        if (aq < bq) return -1
        if (aq > bq) return 1
        const av = (a.fileValue || '').toLowerCase()
        const bv = (b.fileValue || '').toLowerCase()
        if (av < bv) return -1
        if (av > bv) return 1
        return 0
      })
    },
    columnMatchingValidationErrors() {
      // Check for duplicate Breathesafe matching values
      const errors = []
      const usedBreathesafeValues = {}

      // Track which CSV columns are using each Breathesafe value
      Object.keys(this.columnMappings).forEach(csvColumn => {
        const breathesafeValue = this.columnMappings[csvColumn]
        if (breathesafeValue && breathesafeValue !== '') {
          if (usedBreathesafeValues[breathesafeValue]) {
            // This Breathesafe value is already used by another column
            usedBreathesafeValues[breathesafeValue].push(csvColumn)
          } else {
            usedBreathesafeValues[breathesafeValue] = [csvColumn]
          }
        }
      })

      // Generate error messages for duplicates
      Object.keys(usedBreathesafeValues).forEach(breathesafeValue => {
        const csvColumns = usedBreathesafeValues[breathesafeValue]
        if (csvColumns.length > 1) {
          errors.push({
            breathesafeValue: breathesafeValue,
            csvColumns: csvColumns,
            errorKey: `${breathesafeValue}:${csvColumns.sort().join(',')}` // Create unique key for this error
          })
        }
      })

      return errors
    },
    visibleColumnMatchingValidationErrors() {
      // Filter out dismissed errors
      return this.columnMatchingValidationErrors.filter(error =>
        !this.dismissedValidationErrors.has(error.errorKey)
      )
    },
    hasColumnMatchingValidationErrors() {
      return this.columnMatchingValidationErrors.length > 0 || this.requiredColumnValidationErrors.length > 0
    },
    requiredColumnValidationErrors() {
      const errors = []
      const mappedValues = Object.values(this.columnMappings).filter(v => v && v !== '')

      // Check for manager email
      if (!mappedValues.includes('manager email')) {
        errors.push({
          category: 'required_fields',
          missingField: 'manager email',
          errorKey: 'required_manager_email'
        })
      }

      // Check for user name
      if (!mappedValues.includes('user name')) {
        errors.push({
          category: 'required_fields',
          missingField: 'user name',
          errorKey: 'required_user_name'
        })
      }

      // Check for testing mode (exact match)
      if (!mappedValues.includes('Testing mode')) {
        errors.push({
          category: 'required_fields',
          missingField: 'Testing mode',
          errorKey: 'required_testing_mode'
        })
      }

      // Check for facial hair beard length mm (exact match)
      if (!mappedValues.includes('facial hair beard length mm')) {
        errors.push({
          category: 'required_fields',
          missingField: 'facial hair beard length mm',
          errorKey: 'required_facial_hair_beard_length_mm'
        })
      }

      // Check for at least one exercise
      const exerciseNames = [
        'Talking',
        'Turning head side to side',
        'Moving head up and down',
        'Normal breathing 1',
        'Normal breathing 2',
        'Grimace',
        'Deep breathing',
        'Normal breathing (SEALED)'
      ]

      // Check if any mapped value contains any exercise name (regardless of prefix)
      const hasExercise = exerciseNames.some(exerciseName => {
        return mappedValues.some(mappedValue => {
          if (typeof mappedValue !== 'string') return false
          // Check for direct match or prefixed match (e.g., "QLFT -> Talking" or "QNFT -> Talking")
          return mappedValue === exerciseName ||
                 mappedValue.includes(`-> ${exerciseName}`) ||
                 mappedValue.includes(`->${exerciseName}`)
        })
      })

      if (!hasExercise) {
        errors.push({
          category: 'required_exercises',
          missingExercises: exerciseNames,
          errorKey: 'required_at_least_one_exercise'
        })
      }

      return errors
    },
    hasUserMatchingErrors() {
      return this.userMatchingRows.some(row => row.hasError)
    },
    hasUnmappedTestingModes() {
      return this.testingModeMatchingRows.some(
        row => !row.selectedBreathesafeValue || row.selectedBreathesafeValue === ''
      )
    },
    unmappedQlftValuesCount() {
      if (!this.fitTestDataRows || this.fitTestDataRows.length === 0) {
        return 0
      }
      return this.fitTestDataRows.filter(row => {
        if (row.testingMode !== 'QLFT') {
          return false
        }
        // Check if any exercise has unmapped QLFT value
        return row.exerciseHasUnmappedQlftValue && Object.values(row.exerciseHasUnmappedQlftValue).some(hasUnmapped => hasUnmapped === true)
      }).length
    },
    invalidN95N99ValuesCount() {
      if (!this.fitTestDataRows || this.fitTestDataRows.length === 0) {
        return 0
      }
      return this.fitTestDataRows.filter(row => {
        if (row.testingMode !== 'N95' && row.testingMode !== 'N99') {
          return false
        }
        // Check if any exercise has invalid (non-alphanumeric) value
        return row.exerciseHasInvalidN95N99Value && Object.values(row.exerciseHasInvalidN95N99Value).some(hasInvalid => hasInvalid === true)
      }).length
    },
    deduplicatedMasks() {
      // Filter masks where duplicate_of is null and sort alphabetically by unique_internal_model_code
      return this.allMasks
        .filter(mask => mask.duplicate_of === null || mask.duplicate_of === undefined)
        .sort((a, b) => {
          const codeA = (a.unique_internal_model_code || '').toLowerCase()
          const codeB = (b.unique_internal_model_code || '').toLowerCase()
          if (codeA < codeB) return -1
          if (codeA > codeB) return 1
          return 0
        })
    },
    hasUSCColumnsMatched() {
      // Check if any column matching values start with "USC ->"
      if (!this.columnMatching || typeof this.columnMatching !== 'object') {
        return false
      }
      const columnMatchingValues = Object.values(this.columnMatching)
      return columnMatchingValues.some(value =>
        typeof value === 'string' && value.startsWith('USC ->')
      )
    },
    isCompleted() {
      return this.bulkImportStatus === 'completed'
    }
  },
  data() {
    return {
      messages: [],
      currentStep: 'Import File',
      showImportFileHelp: false,
      showGoToBulkImports: false,
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
      userSealCheckMatchingRows: [],
      testingModeMatching: null,
      qlftValuesMatching: null,
      qlftValuesMatchingNotApplicable: false,
      comfortMatching: null,
      fitTestDataMatching: null,
      completedSteps: [],
      bulkFitTestsImportId: null,
      isSaving: false,
      bulkImportCreatedAt: null,
      bulkImportFileSize: null,
      showMatchConfirmation: false,
      pendingMatchOverwrites: {},
      pendingMatches: {},
      dismissedValidationErrors: new Set(),
      dismissedBeardWarnings: false,
      userMatchingRows: [],
      managedUsersByManager: {},
      loadingManagedUsers: false,
      showUserMatchConfirmation: false,
      pendingUserMatchOverwrites: {},
      pendingUserMatches: {},
      maskMatchingRows: [],
      allMasks: [],
      loadingMasks: false,
      showMaskMatchConfirmation: false,
      pendingMaskMatchOverwrites: {},
      pendingMaskMatches: {},
      userSealCheckMatchingSkipped: false,
      testingModeMatchingRows: [],
      showTestingModeMatchConfirmation: false,
      pendingTestingModeMatchOverwrites: {},
      pendingTestingModeMatches: {},
      qlftValuesMatchingRows: [],
      showQlftValuesMatchConfirmation: false,
      pendingQlftValuesMatchOverwrites: {},
      pendingQlftValuesMatches: {},
      comfortMatchingRows: [],
      fitTestDataRows: [],
      bulkImportStatus: null
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
    getUSCOptions(question) {
      const sizingQ = 'USC -> What do you think about the sizing of this mask relative to your face?'
      const airQ = 'USC -> How much air movement on your face along the seal of the mask did you feel?'
      if (question === sizingQ) {
        return ['Too big', 'Somewhere in-between too small and too big', 'Too small']
      }
      if (question === airQ) {
        return ['A lot of air movement', 'Some air movement', 'No air movement']
      }
      return []
    },
    async initializeUserSealCheckMatching() {
      if (!this.csvFullContent || !this.columnMatching) {
        this.userSealCheckMatchingRows = []
        return
      }
      const sizingQ = 'USC -> What do you think about the sizing of this mask relative to your face?'
      const airQ = 'USC -> How much air movement on your face along the seal of the mask did you feel?'
      // Determine which CSV columns are mapped to USC questions
      const sizingCsvColumn = Object.keys(this.columnMatching).find(col => this.columnMatching[col] === sizingQ)
      const airCsvColumn = Object.keys(this.columnMatching).find(col => this.columnMatching[col] === airQ)
      if (!sizingCsvColumn && !airCsvColumn) {
        this.userSealCheckMatchingRows = []
        return
      }
      const lines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (lines.length <= this.headerRowIndex) {
        this.userSealCheckMatchingRows = []
        return
      }
      const header = this.parseCSVLine(lines[this.headerRowIndex])
      const findIndexCI = (name) => header.findIndex(h => h && h.trim().toLowerCase() === name.trim().toLowerCase())
      const sizingIdx = sizingCsvColumn ? findIndexCI(sizingCsvColumn) : -1
      const airIdx = airCsvColumn ? findIndexCI(airCsvColumn) : -1
      const uniquePairs = new Map() // key: question||value
      for (let i = this.headerRowIndex + 1; i < lines.length; i++) {
        const row = this.parseCSVLine(lines[i])
        if (sizingIdx >= 0) {
          const v = row[sizingIdx]?.trim()
          if (v && v !== '') {
            uniquePairs.set(`${sizingQ}|||${v}`, { question: sizingQ, fileValue: v })
          }
        }
        if (airIdx >= 0) {
          const v = row[airIdx]?.trim()
          if (v && v !== '') {
            uniquePairs.set(`${airQ}|||${v}`, { question: airQ, fileValue: v })
          }
        }
      }
      // Build rows and set selected values from existing mapping if available
      const rows = Array.from(uniquePairs.values()).map(pair => {
        let selected = ''
        if (this.userSealCheckMatching && this.userSealCheckMatching[pair.question]) {
          selected = this.userSealCheckMatching[pair.question][pair.fileValue] || ''
        }
        return {
          question: pair.question,
          fileValue: pair.fileValue,
          selectedBreathesafeValue: selected
        }
      })
      this.userSealCheckMatchingRows = rows
    },
    updateUserSealCheckMatching() {
      // Build nested mapping: { question: { file_value: breathesafe_value } }
      const mapping = {}
      this.userSealCheckMatchingRows.forEach(row => {
        if (!mapping[row.question]) mapping[row.question] = {}
        if (row.selectedBreathesafeValue && row.selectedBreathesafeValue !== '') {
          mapping[row.question][row.fileValue] = row.selectedBreathesafeValue
        }
      })
      this.userSealCheckMatching = mapping
    },
    attemptUSCAutoMatch() {
      if (!this.userSealCheckMatchingRows || this.userSealCheckMatchingRows.length === 0) return
      const THRESHOLD = 0.1
      this.userSealCheckMatchingRows.forEach(row => {
        const options = this.getUSCOptions(row.question)
        let best = ''
        let bestSim = -1
        options.forEach(opt => {
          const sim = this.calculateSimilarity(row.fileValue, opt)
          if (sim > bestSim) {
            bestSim = sim
            best = opt
          }
        })
        if (best && bestSim >= THRESHOLD) {
          row.selectedBreathesafeValue = best
        }
      })
      this.updateUserSealCheckMatching()
    },
    async saveUserSealCheckMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }
      // Check authentication
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }
      this.isSaving = true
      try {
        // Ensure mapping reflects current selections
        this.updateUserSealCheckMatching()
        const payload = {
          bulk_fit_tests_import: {
            user_seal_check_matching: this.userSealCheckMatching || {}
          }
        }
        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, payload)
        if (response.status === 200) {
          // ok
        } else {
          const errorMessages = response.data.messages || ['Failed to save user seal check matching.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (e) {
        const errorMsg = e.response?.data?.messages?.[0] || e.message || 'Failed to save user seal check matching.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
      }
    },
    getComfortOptions(question) {
      const nose = 'How comfortable is the position of the mask on the nose?'
      const talk = 'Is there enough room to talk?'
      const face = 'How comfortable is the position of the mask on face and cheeks?'
      if (question === nose) return ['Uncomfortable', 'Unsure', 'Comfortable']
      if (question === talk) return ['Not enough', 'Unsure', 'Enough']
      if (question === face) return ['Uncomfortable', 'Unsure', 'Comfortable']
      return []
    },
    async initializeComfortMatching() {
      if (!this.csvFullContent || !this.columnMatching) {
        this.comfortMatchingRows = []
        return
      }
      const lines = this.csvFullContent.split('\n').filter(l => l.trim() !== '')
      if (lines.length <= this.headerRowIndex) {
        this.comfortMatchingRows = []
        return
      }
      const header = this.parseCSVLine(lines[this.headerRowIndex])
      const findIndexCI = (name) => header.findIndex(h => h && h.trim().toLowerCase() === name.trim().toLowerCase())
      const questions = [
        'How comfortable is the position of the mask on the nose?',
        'Is there enough room to talk?',
        'How comfortable is the position of the mask on face and cheeks?'
      ]
      const questionToIndex = {}
      questions.forEach(q => {
        const csvCol = Object.keys(this.columnMatching).find(col => this.columnMatching[col] === `comfort -> "${q}"`)
        if (csvCol) {
          const idx = findIndexCI(csvCol)
          if (idx >= 0) questionToIndex[q] = idx
        }
      })
      const uniquePairs = new Map()
      for (let i = this.headerRowIndex + 1; i < lines.length; i++) {
        const row = this.parseCSVLine(lines[i])
        Object.keys(questionToIndex).forEach(q => {
          const idx = questionToIndex[q]
          const v = row[idx]?.trim()
          if (v && v !== '') {
            uniquePairs.set(`${q}|||${v}`, { question: q, fileValue: v })
          }
        })
      }
      const rows = Array.from(uniquePairs.values()).map(pair => {
        let selected = ''
        if (this.comfortMatching && this.comfortMatching[pair.question]) {
          selected = this.comfortMatching[pair.question][pair.fileValue] || ''
        }
        return {
          question: pair.question,
          fileValue: pair.fileValue,
          selectedBreathesafeValue: selected
        }
      })
      // Sort by Breathesafe matching question, then by value found in file
      rows.sort((a, b) => {
        // First sort by question
        if (a.question !== b.question) {
          return a.question.localeCompare(b.question)
        }
        // Then sort by fileValue
        return a.fileValue.localeCompare(b.fileValue)
      })
      this.comfortMatchingRows = rows
    },
    updateComfortMatching() {
      const mapping = {}
      this.comfortMatchingRows.forEach(row => {
        if (!mapping[row.question]) mapping[row.question] = {}
        if (row.selectedBreathesafeValue && row.selectedBreathesafeValue !== '') {
          mapping[row.question][row.fileValue] = row.selectedBreathesafeValue
        }
      })
      this.comfortMatching = mapping
    },
    attemptComfortAutoMatch() {
      if (!this.comfortMatchingRows || this.comfortMatchingRows.length === 0) return
      const THRESHOLD = 0.4
      this.comfortMatchingRows.forEach(row => {
        const options = this.getComfortOptions(row.question)
        let best = ''
        let bestSim = -1
        options.forEach(opt => {
          const sim = this.calculateSimilarity(row.fileValue, opt)
          if (sim > bestSim) {
            bestSim = sim
            best = opt
          }
        })
        if (best && bestSim >= THRESHOLD) {
          row.selectedBreathesafeValue = best
        }
      })
      this.updateComfortMatching()
    },
    async saveComfortMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }
      this.isSaving = true
      try {
        this.updateComfortMatching()
        const payload = {
          bulk_fit_tests_import: {
            comfort_matching: this.comfortMatching || {}
          }
        }
        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, payload)
        if (response.status !== 200) {
          const errorMessages = response.data.messages || ['Failed to save comfort matching.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (e) {
        const errorMsg = e.response?.data?.messages?.[0] || e.message || 'Failed to save comfort matching.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
      }
    },
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

      // Clear dismissed errors that no longer exist (so they can reappear if the same error happens again)
      const currentErrorKeys = new Set(this.columnMatchingValidationErrors.map(e => e.errorKey))
      const keysToRemove = []
      this.dismissedValidationErrors.forEach(key => {
        if (!currentErrorKeys.has(key)) {
          keysToRemove.push(key)
        }
      })
      keysToRemove.forEach(key => this.dismissedValidationErrors.delete(key))
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
    levenshteinDistance(str1, str2) {
      // Calculate Levenshtein distance between two strings
      const len1 = str1.length
      const len2 = str2.length

      if (len1 === 0) return len2
      if (len2 === 0) return len1

      const matrix = []

      // Initialize matrix
      for (let i = 0; i <= len1; i++) {
        matrix[i] = [i]
      }
      for (let j = 0; j <= len2; j++) {
        matrix[0][j] = j
      }

      // Fill matrix
      for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
          const cost = str1[i - 1] === str2[j - 1] ? 0 : 1
          matrix[i][j] = Math.min(
            matrix[i - 1][j] + 1,      // deletion
            matrix[i][j - 1] + 1,      // insertion
            matrix[i - 1][j - 1] + cost // substitution
          )
        }
      }

      return matrix[len1][len2]
    },
    calculateSimilarity(str1, str2) {
      // Normalize strings: lowercase, remove special characters, normalize spaces
      const normalize = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, ' ').replace(/\s+/g, ' ').trim()
      const norm1 = normalize(str1)
      const norm2 = normalize(str2)

      if (norm1 === norm2) return 1.0

      const maxLen = Math.max(norm1.length, norm2.length)
      if (maxLen === 0) return 0.0

      const distance = this.levenshteinDistance(norm1, norm2)
      return 1 - (distance / maxLen)
    },
    getBreathesafeFieldOptions() {
      // Return all available Breathesafe matching column options (must match the select options)
      return [
        'manager email',
        'first name', // Profile.first_name
        'last name', // Profile.last_name
        'user name', // Profile.first_name + Profile.last_name
        'Mask.unique_internal_model_code',
        'Bending over',
        'Talking',
        'Turning head side to side',
        'Moving head up and down',
        'Normal breathing 1',
        'Normal breathing 2',
        'Normal breathing (SEALED)',
        'Grimace',
        'Deep breathing',
        'Testing mode',
        'QLFT -> solution',
        'facial hair beard length mm',
        'comfort -> "Is there enough room to talk?"',
        'comfort -> "How comfortable is the position of the mask on the nose?"',
        'comfort -> "How comfortable is the position of the mask on face and cheeks?"',
        'USC -> What do you think about the sizing of this mask relative to your face?',
        'USC -> How much air movement on your face along the seal of the mask did you feel?'
      ]
    },
    beardLengthWarnings() {
      // Show warnings in Column Matching when beard length is mapped but values are missing/invalid
      if (this.dismissedBeardWarnings) return []
      const messages = []
      try {
        if (!this.csvFullContent || !this.columnMatching) return messages
        // Find mapped CSV column name for beard length
        const beardCsvColumn = Object.keys(this.columnMatching).find(
          col => this.columnMatching[col] === 'facial hair beard length mm'
        )
        if (!beardCsvColumn) return messages
        // Parse header row
        const lines = this.csvFullContent.split('\n').filter(l => l.trim() !== '')
        if (lines.length <= this.headerRowIndex) return messages
        const header = this.parseCSVLine(lines[this.headerRowIndex])
        const idx = header.findIndex(col => col && col.trim().toLowerCase() === beardCsvColumn.trim().toLowerCase())
        if (idx < 0) return messages
        let missing = 0
        let invalid = 0
        for (let i = this.headerRowIndex + 1; i < lines.length; i++) {
          const row = this.parseCSVLine(lines[i])
          const raw = row[idx]
          if (raw == null || raw.trim() === '') {
            missing++
            continue
          }
          const trimmed = raw.trim()
          const numeric = trimmed.match(/^\d+(\.\d+)?$/)
          if (!numeric) invalid++
        }
        if (missing > 0) messages.push({ str: `${missing} row(s) have missing beard length (mm).` })
        if (invalid > 0) messages.push({ str: `${invalid} row(s) have invalid (non-numeric) beard length values.` })
      } catch (e) {
        // ignore parsing issues for warnings
      }
      return messages
    },
    dismissBeardWarnings() {
      this.dismissedBeardWarnings = true
    },
    getPriorityFields() {
      // Return priority fields in order of matching priority
      return [
        'manager email',
        'user name',
        'Mask.unique_internal_model_code',
        'Testing mode',
        'facial hair beard length',
        'Bending over',
        'Talking',
        'Turning head side to side',
        'Moving head up and down',
        'Normal breathing 1',
        'Normal breathing 2',
        'USC -> how much air movement on your face along the seal of the mask did you feel?',
        'USC -> What do you think about the sizing of this mask relative to your face?'
      ]
    },
    findBreathesafeFieldsForPriority(priorityField, availableBreathesafeFields) {
      // Find Breathesafe fields that match the priority pattern
      // For exact matches: return fields that exactly match
      // For contains matches: return fields that contain the priority text
      const exactMatches = ['manager email', 'user name', 'Mask.unique_internal_model_code', 'Testing mode']

      if (exactMatches.includes(priorityField)) {
        return availableBreathesafeFields.filter(field => field === priorityField)
      } else {
        // Contains match - find fields that contain the priority text
        return availableBreathesafeFields.filter(field =>
          field.toLowerCase().includes(priorityField.toLowerCase())
        )
      }
    },
    attemptAutoMatch() {
      if (!this.fileColumns || this.fileColumns.length === 0) {
        return
      }
      const breathesafeOptions = this.getBreathesafeFieldOptions()
      const matches = {}
      const overwrites = {}
      const THRESHOLD = 0.4
      this.fileColumns.forEach(csvColumn => {
        // Pick best similarity above threshold for each CSV column
        let bestField = null
        let bestSim = -1
        breathesafeOptions.forEach(field => {
          const sim = this.calculateSimilarity(csvColumn, field)
          if (sim > bestSim) {
            bestSim = sim
            bestField = field
          }
        })
        if (bestField && bestSim >= THRESHOLD) {
          if (this.columnMappings[csvColumn] && this.columnMappings[csvColumn] !== '') {
            overwrites[csvColumn] = bestField
          }
          matches[csvColumn] = bestField
        }
      })
      if (Object.keys(overwrites).length > 0) {
        this.pendingMatchOverwrites = overwrites
        this.pendingMatches = matches
        this.showMatchConfirmation = true
      } else {
        this.applyMatches(matches)
      }
    },
    applyMatches(matches) {
      // Apply the matches to columnMappings
      Object.keys(matches).forEach(csvColumn => {
        this.columnMappings[csvColumn] = matches[csvColumn]
      })

      // Update columnMatching object
      this.updateColumnMatching()

      this.messages = [{ str: `Matched ${Object.keys(matches).length} column(s) automatically.` }]
    },
    confirmMatchOverwrite() {
      // Apply all matches including overwrites
      this.applyMatches(this.pendingMatches)
      this.cancelMatchConfirmation()
    },
    cancelMatchConfirmation() {
      this.showMatchConfirmation = false
      this.pendingMatchOverwrites = {}
      this.pendingMatches = {}
    },
    getSimilarityScore(csvColumn) {
      // Get normalized probability between CSV column and selected Breathesafe field
      const selectedBreathesafeField = this.columnMappings[csvColumn]

      if (!selectedBreathesafeField || selectedBreathesafeField === '') {
        return null
      }

      // Calculate similarity scores for this Breathesafe field with all CSV columns
      const similarities = {}
      let sumSimilarities = 0

      this.fileColumns.forEach(col => {
        const similarity = this.calculateSimilarity(col, selectedBreathesafeField)
        similarities[col] = similarity
        sumSimilarities += similarity
      })

      // Normalize to get probability
      if (sumSimilarities > 0) {
        return similarities[csvColumn] / sumSimilarities
      }

      return null
    },
    formatSimilarityScore(score) {
      if (score === null || score === undefined) {
        return '--'
      }
      // Format normalized probability as percentage with 1 decimal place
      return (score * 100).toFixed(1) + '%'
    },
    async navigateToStep(stepKey) {
      this.currentStep = stepKey

      // If navigating back to Column Matching, reload from backend
      if (stepKey === 'Column Matching' && this.bulkFitTestsImportId) {
        this.reloadColumnMatching()
      }

      // If navigating to User Matching, initialize user matching
      if (stepKey === 'User Matching' && this.bulkFitTestsImportId) {
        await this.initializeUserMatching()
      }

      // If navigating to Mask Matching, initialize mask matching
      if (stepKey === 'Mask Matching' && this.bulkFitTestsImportId) {
        await this.initializeMaskMatching()
      }

      // If navigating to User Seal Check Matching, initialize USC matching
      if (stepKey === 'User Seal Check Matching' && this.bulkFitTestsImportId) {
        await this.initializeUserSealCheckMatching()
      }

      // If navigating to Testing Mode Values Matching, initialize testing mode matching
      if (stepKey === 'Testing Mode Values Matching' && this.bulkFitTestsImportId) {
        await this.initializeTestingModeMatching()
      }

      // If navigating to QLFT Values Matching, initialize QLFT values matching
      if (stepKey === 'QLFT Values Matching' && this.bulkFitTestsImportId) {
        await this.initializeQlftValuesMatching()
      }

      // If navigating to Comfort Matching, initialize comfort matching
      if (stepKey === 'Comfort Matching' && this.bulkFitTestsImportId) {
        await this.initializeComfortMatching()
      }

      // If navigating to Fit Test Data Matching, initialize fit test data matching
      if (stepKey === 'Fit Test Data Matching' && this.bulkFitTestsImportId) {
        await this.initializeFitTestDataMatching()
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

      // If we're on the "User Matching" step, save user matching data
      if (this.currentStep === 'User Matching') {
        await this.saveUserMatching()
        return // Navigation will happen in saveUserMatching if successful
      }

      // If we're on the "Mask Matching" step, save mask matching data
      if (this.currentStep === 'Mask Matching') {
        await this.saveMaskMatching()
        return // Navigation will happen in saveMaskMatching if successful
      }

      // If we're on the "User Seal Check Matching" step, check if it should be skipped
      if (this.currentStep === 'User Seal Check Matching') {
        if (this.hasUSCColumnsMatched) {
          await this.saveUserSealCheckMatching()
          // Mark as completed
          if (!this.completedSteps.includes('User Seal Check Matching')) {
            this.completedSteps.push('User Seal Check Matching')
          }
          this.currentStep = 'Testing Mode Values Matching'
          await this.initializeTestingModeMatching()
          return
        } else {
          // If no USC columns are matched, mark as skipped
          this.userSealCheckMatchingSkipped = true
          if (!this.completedSteps.includes('User Seal Check Matching')) {
            this.completedSteps.push('User Seal Check Matching')
          }
          this.currentStep = 'Testing Mode Values Matching'
          await this.initializeTestingModeMatching()
          return
        }
      }

      // If we're on the "Testing Mode Values Matching" step, save testing mode matching data
      if (this.currentStep === 'Testing Mode Values Matching') {
        await this.saveTestingModeMatching()
        return // Navigation will happen in saveTestingModeMatching if successful
      }

      // If we're on the "QLFT Values Matching" step, save QLFT values matching data
      if (this.currentStep === 'QLFT Values Matching') {
        await this.saveQlftValuesMatching()
        return // Navigation will happen in saveQlftValuesMatching if successful
      }
      // If we're on the "Comfort Matching" step, save comfort matching data
      if (this.currentStep === 'Comfort Matching') {
        await this.saveComfortMatching()
        // Move to Review
        this.currentStep = 'Fit Test Data Matching'
        await this.initializeFitTestDataMatching()
        return
      }

      const steps = [
        'Import File',
        'Column Matching',
        'User Matching',
        'Mask Matching',
        'User Seal Check Matching',
        'Testing Mode Values Matching',
        'QLFT Values Matching',
        'Comfort Matching',
        'Fit Test Data Matching'
      ]
      const currentIndex = steps.indexOf(this.currentStep)
      if (currentIndex < steps.length - 1) {
        const nextStep = steps[currentIndex + 1]
        this.currentStep = nextStep

        // Initialize user matching when navigating to User Matching step
        if (nextStep === 'User Matching') {
          await this.initializeUserMatching()
        }

        // Initialize mask matching when navigating to Mask Matching step
        if (nextStep === 'Mask Matching') {
          await this.initializeMaskMatching()
        }

        // Initialize testing mode matching when navigating to Testing Mode Values Matching step
        if (nextStep === 'Testing Mode Values Matching') {
          await this.initializeTestingModeMatching()
        }

        // Initialize QLFT values matching when navigating to QLFT Values Matching step
        if (nextStep === 'QLFT Values Matching') {
          await this.initializeQlftValuesMatching()
        }

        // Initialize fit test data matching when navigating to Fit Test Data Matching step
        if (nextStep === 'Fit Test Data Matching') {
          await this.initializeFitTestDataMatching()
        }
      }
    },
    isColumnInDuplicateError(csvColumn) {
      // Check if this CSV column is part of a duplicate error
      return this.columnMatchingValidationErrors.some(error =>
        error.csvColumns.includes(csvColumn)
      )
    },
    getDuplicateErrorMessage(error) {
      // Generate error message for duplicate Breathesafe matching value
      return {
        str: `The Breathesafe matching value "${error.breathesafeValue}" is used by multiple columns: ${error.csvColumns.join(', ')}. Each Breathesafe matching value can only be used once.`
      }
    },
    dismissValidationError(error) {
      // Add error to dismissed set
      this.dismissedValidationErrors.add(error.errorKey)
    },
    dismissAllValidationErrors() {
      // Dismiss all visible validation errors
      this.visibleColumnMatchingValidationErrors.forEach(error => {
        this.dismissedValidationErrors.add(error.errorKey)
      })
    },
    async saveColumnMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }

      // Check for duplicate validation errors
      if (this.columnMatchingValidationErrors.length > 0) {
        this.messages = this.columnMatchingValidationErrors.map(error =>
          this.getDuplicateErrorMessage(error)
        )
        return
      }

      // Check for required column validation errors
      if (this.requiredColumnValidationErrors.length > 0) {
        this.messages = this.requiredColumnValidationErrors.map(error => {
          if (error.category === 'required_fields') {
            return { str: `Required column "${error.missingField}" is not matched. Please select a CSV column for "${error.missingField}".` }
          } else if (error.category === 'required_exercises') {
            return { str: `At least one fit testing exercise must be matched. Please match at least one of the following exercises: ${error.missingExercises.join(', ')}.` }
          }
          return { str: 'Please complete all required column mappings.' }
        })
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
            const nextStep = steps[currentIndex + 1]
            this.currentStep = nextStep
            // Initialize next step immediately to avoid empty view until refresh
            if (nextStep === 'User Matching') {
              await this.initializeUserMatching()
            } else if (nextStep === 'Mask Matching') {
              await this.initializeMaskMatching()
            } else if (nextStep === 'User Seal Check Matching') {
              // nothing to initialize here
            } else if (nextStep === 'Testing Mode Values Matching') {
              await this.initializeTestingModeMatching()
            } else if (nextStep === 'QLFT Values Matching') {
              await this.initializeQlftValuesMatching()
            } else if (nextStep === 'Fit Test Data Matching') {
              await this.initializeFitTestDataMatching()
            }
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
    async initializeUserMatching() {
      // Parse CSV data and extract manager email and user name columns
      if (!this.csvFullContent || !this.columnMatching) {
        this.userMatchingRows = []
        return
      }

      // Find columns mapped to "manager email" and "user name"
      const managerEmailColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'manager email'
      )
      const userNameColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'user name'
      )

      if (!managerEmailColumn || !userNameColumn) {
        this.userMatchingRows = []
        this.messages = [{ str: 'Manager email and user name columns must be mapped in Column Matching.' }]
        return
      }

      // Parse CSV lines
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        this.userMatchingRows = []
        return
      }

      // Get header row
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])
      const managerEmailIndex = headerRow.indexOf(managerEmailColumn)
      const userNameIndex = headerRow.indexOf(userNameColumn)

      if (managerEmailIndex === -1 || userNameIndex === -1) {
        this.userMatchingRows = []
        this.messages = [{ str: 'Could not find manager email or user name columns in CSV.' }]
        return
      }

      // Parse data rows and group by unique (manager email, user name) combinations
      const uniqueCombinations = new Map()

      for (let i = this.headerRowIndex + 1; i < csvLines.length; i++) {
        const row = this.parseCSVLine(csvLines[i])
        const managerEmail = row[managerEmailIndex] ? row[managerEmailIndex].trim() : ''
        const userName = row[userNameIndex] ? row[userNameIndex].trim() : ''

        const key = `${managerEmail}|||${userName}`
        if (!uniqueCombinations.has(key)) {
          uniqueCombinations.set(key, {
            managerEmail: managerEmail,
            userName: userName,
            managerEmailError: null,
            userNameError: null,
            hasError: false,
            selectedManagedUserId: null,
            managerUserId: null
          })
        }
      }

      // Convert to array and validate
      this.userMatchingRows = Array.from(uniqueCombinations.values()).map(row => {
        // Validate manager email
        if (!row.managerEmail || row.managerEmail === '') {
          row.managerEmailError = 'Manager email is required'
          row.hasError = true
        }

        // Validate user name
        if (!row.userName || row.userName === '') {
          row.userNameError = 'User name is required'
          row.hasError = true
        }

        return row
      })

      // Load saved user matching if it exists
      if (this.userMatching && typeof this.userMatching === 'object' && Object.keys(this.userMatching).length > 0) {
        this.userMatchingRows.forEach(row => {
          const key = `${row.managerEmail}|||${row.userName}`
          if (this.userMatching[key]) {
            row.selectedManagedUserId = this.userMatching[key] === '__to_be_created__' ? '__to_be_created__' : this.userMatching[key]
          }
        })
      }

      // Fetch managed users for each unique manager email
      await this.fetchManagedUsersForAllManagers()
    },
    async fetchManagedUsersForAllManagers() {
      // Get unique manager emails (only from rows without errors)
      const uniqueManagerEmails = [...new Set(
        this.userMatchingRows
          .filter(row => !row.hasError && row.managerEmail)
          .map(row => row.managerEmail)
      )]

      this.loadingManagedUsers = true
      this.managedUsersByManager = {}

      for (const managerEmail of uniqueManagerEmails) {
        await this.fetchManagedUsersForManager(managerEmail)
      }

      this.loadingManagedUsers = false
    },
    async fetchManagedUsersForManager(managerEmail) {
      if (!managerEmail || managerEmail === '') {
        return
      }

      try {
        // Check authentication
        const isAuthenticated = await this.checkAuthentication()
        if (!isAuthenticated) {
          return
        }

        // Find manager user by email
        const response = await axios.get(`/users.json`, {
          params: { email: managerEmail }
        })

        if (response.status === 200 && response.data.users && response.data.users.length > 0) {
          const managerUser = response.data.users[0]
          const managerId = managerUser.id

          // Check if current user can manage this manager
          // If current user is admin, they can manage anyone
          // Otherwise, they can only manage themselves
          const currentUserIsAdmin = this.currentUser && this.currentUser.admin
          const canManage = currentUserIsAdmin || (this.currentUser && this.currentUser.id === managerId)

          if (!canManage) {
            // Set error for rows with this manager email
            this.userMatchingRows.forEach(row => {
              if (row.managerEmail === managerEmail) {
                row.managerEmailError = 'You do not have permission to manage users for this manager'
                row.hasError = true
              }
            })
            return
          }

          // Fetch managed users for this manager
          const managedUsersResponse = await axios.get(`/managed_users.json`, {
            params: { manager_id: managerId }
          })

          if (managedUsersResponse.status === 200 && managedUsersResponse.data.managed_users) {
            this.managedUsersByManager[managerEmail] = managedUsersResponse.data.managed_users

            // Store manager user ID for each row
            this.userMatchingRows.forEach(row => {
              if (row.managerEmail === managerEmail) {
                row.managerUserId = managerId
              }
            })
          }
        } else {
          // Manager not found
          this.userMatchingRows.forEach(row => {
            if (row.managerEmail === managerEmail) {
              row.managerEmailError = 'Manager not found with this email'
              row.hasError = true
            }
          })
        }
      } catch (error) {
        // Handle errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        this.userMatchingRows.forEach(row => {
          if (row.managerEmail === managerEmail) {
            row.managerEmailError = 'Error loading managed users'
            row.hasError = true
          }
        })
      }
    },
    getManagedUsersForRow(row) {
      if (!row.managerEmail || row.hasError) {
        return []
      }

      const managedUsers = this.managedUsersByManager[row.managerEmail] || []
      return managedUsers
    },
    getManagedUserName(managedUser) {
      if (!managedUser) {
        return ''
      }

      const firstName = managedUser.first_name || ''
      const lastName = managedUser.last_name || ''
      return `${firstName} ${lastName}`.trim() || `User ${managedUser.managed_id}`
    },
    updateUserMatching() {
      // Update userMatching object when selections change
      // This will be saved when user clicks Next
    },
    attemptUserAutoMatch() {
      if (!this.userMatchingRows || this.userMatchingRows.length === 0) {
        return
      }

      const matches = {}
      const overwrites = {}

      // Group rows by manager email
      const rowsByManager = {}
      this.userMatchingRows.forEach(row => {
        if (row.hasError || !row.managerEmail || !row.userName) {
          return // Skip rows with errors or missing data
        }

        if (!rowsByManager[row.managerEmail]) {
          rowsByManager[row.managerEmail] = []
        }
        rowsByManager[row.managerEmail].push(row)
      })

      // Process each manager group separately
      Object.keys(rowsByManager).forEach(managerEmail => {
        const rows = rowsByManager[managerEmail]
        const managedUsers = this.managedUsersByManager[managerEmail] || []

        if (managedUsers.length === 0) {
          // No managed users available, assign "To be created" to all rows
          rows.forEach(row => {
            if (!row.selectedManagedUserId || row.selectedManagedUserId === '') {
              matches[`${row.managerEmail}|||${row.userName}`] = '__to_be_created__'
            }
          })
          return
        }

        // Sort rows by user name for consistent processing
        const sortedRows = [...rows].sort((a, b) => {
          if (a.userName < b.userName) return -1
          if (a.userName > b.userName) return 1
          return 0
        })

        // Track which managed users have been matched
        const usedManagedUserIds = new Set()

        // For each row, find the best match from available managed users
        sortedRows.forEach(row => {
          let bestManagedUser = null
          let bestSimilarity = 0

          // Find best match from available managed users
          managedUsers.forEach(managedUser => {
            if (usedManagedUserIds.has(managedUser.managed_id)) {
              return // Skip already matched managed users
            }

            const fullName = this.getManagedUserName(managedUser)
            const similarity = this.calculateSimilarity(row.userName, fullName)

            if (similarity > bestSimilarity) {
              bestSimilarity = similarity
              bestManagedUser = managedUser
            }
          })

          // If best similarity is >= 0.4, assign the match
          const key = `${row.managerEmail}|||${row.userName}`
          if (bestSimilarity >= 0.4 && bestManagedUser) {
            // Check if row already has this managed user selected
            const alreadyHasBestMatch = row.selectedManagedUserId &&
              row.selectedManagedUserId.toString() === bestManagedUser.managed_id.toString()

            if (alreadyHasBestMatch) {
              // Already has the best match, mark it as used and skip
              usedManagedUserIds.add(bestManagedUser.managed_id)
            } else {
              // Check if this would overwrite an existing selection
              if (row.selectedManagedUserId && row.selectedManagedUserId !== '' && row.selectedManagedUserId !== '__to_be_created__') {
                // Would overwrite existing selection
                const existingName = this.getManagedUserNameById(row.selectedManagedUserId, managerEmail)
                overwrites[row.userName] = this.getManagedUserName(bestManagedUser)
              }

              matches[key] = bestManagedUser.managed_id.toString()
              usedManagedUserIds.add(bestManagedUser.managed_id)
            }
          } else {
            // Similarity too low, assign "To be created"
            if (!row.selectedManagedUserId || row.selectedManagedUserId === '') {
              matches[key] = '__to_be_created__'
            } else if (row.selectedManagedUserId && row.selectedManagedUserId !== '' && row.selectedManagedUserId !== '__to_be_created__') {
              // Would overwrite existing selection with "To be created"
              const existingName = this.getManagedUserNameById(row.selectedManagedUserId, managerEmail)
              overwrites[row.userName] = 'To be created'
              matches[key] = '__to_be_created__'
            }
          }
        })
      })

      // If there are overwrites, show confirmation popup
      if (Object.keys(overwrites).length > 0) {
        this.pendingUserMatchOverwrites = overwrites
        this.pendingUserMatches = matches
        this.showUserMatchConfirmation = true
      } else {
        // No overwrites, apply matches directly
        this.applyUserMatches(matches)
      }
    },
    applyUserMatches(matches) {
      // Apply the matches to userMatchingRows
      Object.keys(matches).forEach(key => {
        const parts = key.split('|||')
        if (parts.length === 2) {
          const managerEmail = parts[0]
          const userName = parts[1]

          const row = this.userMatchingRows.find(r =>
            r.managerEmail === managerEmail && r.userName === userName
          )

          if (row) {
            row.selectedManagedUserId = matches[key]
          }
        }
      })

      this.messages = [{ str: `Matched ${Object.keys(matches).length} user(s) automatically.` }]
    },
    confirmUserMatchOverwrite() {
      // Apply all matches including overwrites
      this.applyUserMatches(this.pendingUserMatches)
      this.cancelUserMatchConfirmation()
    },
    cancelUserMatchConfirmation() {
      this.showUserMatchConfirmation = false
      this.pendingUserMatchOverwrites = {}
      this.pendingUserMatches = {}
    },
    getManagedUserNameById(managedUserId, managerEmail) {
      const managedUsers = this.managedUsersByManager[managerEmail] || []
      const managedUser = managedUsers.find(mu => mu.managed_id.toString() === managedUserId.toString())
      return managedUser ? this.getManagedUserName(managedUser) : `User ${managedUserId}`
    },
    getUserMatchingSimilarityScore(row) {
      // Get similarity score between File user name and selected Breathesafe user name
      if (!row.selectedManagedUserId || row.selectedManagedUserId === '' || row.selectedManagedUserId === '__to_be_created__') {
        return null
      }

      if (!row.managerEmail || row.hasError) {
        return null
      }

      const managedUsers = this.managedUsersByManager[row.managerEmail] || []
      const selectedManagedUser = managedUsers.find(mu => mu.managed_id.toString() === row.selectedManagedUserId.toString())

      if (!selectedManagedUser) {
        return null
      }

      const fullName = this.getManagedUserName(selectedManagedUser)
      return this.calculateSimilarity(row.userName, fullName)
    },
    async initializeMaskMatching() {
      // Parse CSV data and extract mask names from column mapped to Mask.unique_internal_model_code
      if (!this.csvFullContent || !this.columnMatching) {
        this.maskMatchingRows = []
        return
      }

      // Find column mapped to "Mask.unique_internal_model_code"
      const maskColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'Mask.unique_internal_model_code'
      )

      if (!maskColumn) {
        this.maskMatchingRows = []
        this.messages = [{ str: 'Mask column must be mapped in Column Matching.' }]
        return
      }

      // Parse CSV lines
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        this.maskMatchingRows = []
        return
      }

      // Get header row
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])
      const maskColumnIndex = headerRow.indexOf(maskColumn)

      if (maskColumnIndex === -1) {
        this.maskMatchingRows = []
        this.messages = [{ str: 'Could not find mask column in CSV.' }]
        return
      }

      // Parse data rows and get unique mask names
      const uniqueMaskNames = new Set()

      for (let i = this.headerRowIndex + 1; i < csvLines.length; i++) {
        const row = this.parseCSVLine(csvLines[i])
        const maskName = row[maskColumnIndex] ? row[maskColumnIndex].trim() : ''
        if (maskName && maskName !== '') {
          uniqueMaskNames.add(maskName)
        }
      }

      // Convert to array and create rows
      this.maskMatchingRows = Array.from(uniqueMaskNames).map(maskName => ({
        fileMaskName: maskName,
        selectedMaskId: null
      }))

      // Load saved mask matching if it exists
      if (this.maskMatching && typeof this.maskMatching === 'object' && Object.keys(this.maskMatching).length > 0) {
        this.maskMatchingRows.forEach(row => {
          if (this.maskMatching[row.fileMaskName]) {
            row.selectedMaskId = this.maskMatching[row.fileMaskName] === '__to_be_created__'
              ? '__to_be_created__'
              : this.maskMatching[row.fileMaskName]
          }
        })
      }

      // Fetch deduplicated masks
      await this.fetchDeduplicatedMasks()
    },
    async fetchDeduplicatedMasks() {
      this.loadingMasks = true

      try {
        // Check authentication
        const isAuthenticated = await this.checkAuthentication()
        if (!isAuthenticated) {
          return
        }

        const response = await axios.get('/masks.json')

        if (response.status === 200 && response.data.masks) {
          // Filter masks where duplicate_of is null
          this.allMasks = response.data.masks.filter(mask =>
            mask.duplicate_of === null || mask.duplicate_of === undefined
          )
        }
      } catch (error) {
        // Handle errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        this.messages = [{ str: 'Error loading masks.' }]
      } finally {
        this.loadingMasks = false
      }
    },
    attemptMaskAutoMatch() {
      if (!this.maskMatchingRows || this.maskMatchingRows.length === 0) {
        return
      }

      if (this.deduplicatedMasks.length === 0) {
        // No masks available, assign "To be created" to all rows without selections
        const matches = {}
        this.maskMatchingRows.forEach(row => {
          if (!row.selectedMaskId || row.selectedMaskId === '') {
            matches[row.fileMaskName] = '__to_be_created__'
          }
        })
        this.applyMaskMatches(matches)
        return
      }

      const matches = {}
      const overwrites = {}

      // Sort rows by file mask name for consistent processing
      const sortedRows = [...this.maskMatchingRows].sort((a, b) => {
        if (a.fileMaskName < b.fileMaskName) return -1
        if (a.fileMaskName > b.fileMaskName) return 1
        return 0
      })

      // Track which masks have been matched
      const usedMaskIds = new Set()

      // For each row, find the best match from available masks
      sortedRows.forEach(row => {
        let bestMask = null
        let bestSimilarity = 0

        // Find best match from available masks
        this.deduplicatedMasks.forEach(mask => {
          if (usedMaskIds.has(mask.id)) {
            return // Skip already matched masks
          }

          const similarity = this.calculateSimilarity(row.fileMaskName, mask.unique_internal_model_code)

          if (similarity > bestSimilarity) {
            bestSimilarity = similarity
            bestMask = mask
          }
        })

        // If best similarity is >= 0.4, assign the match
        if (bestSimilarity >= 0.4 && bestMask) {
          // Check if row already has this mask selected
          const alreadyHasBestMatch = row.selectedMaskId &&
            row.selectedMaskId.toString() === bestMask.id.toString()

          if (alreadyHasBestMatch) {
            // Already has the best match, mark it as used and skip
            usedMaskIds.add(bestMask.id)
          } else {
            // Check if this would overwrite an existing selection
            if (row.selectedMaskId && row.selectedMaskId !== '' && row.selectedMaskId !== '__to_be_created__') {
              // Would overwrite existing selection
              const existingMask = this.deduplicatedMasks.find(m => m.id.toString() === row.selectedMaskId.toString())
              const existingName = existingMask ? existingMask.unique_internal_model_code : `Mask ${row.selectedMaskId}`
              overwrites[row.fileMaskName] = bestMask.unique_internal_model_code
            }

            matches[row.fileMaskName] = bestMask.id.toString()
            usedMaskIds.add(bestMask.id)
          }
        } else {
          // Similarity too low, assign "To be created"
          if (!row.selectedMaskId || row.selectedMaskId === '') {
            matches[row.fileMaskName] = '__to_be_created__'
          } else if (row.selectedMaskId && row.selectedMaskId !== '' && row.selectedMaskId !== '__to_be_created__') {
            // Would overwrite existing selection with "To be created"
            const existingMask = this.deduplicatedMasks.find(m => m.id.toString() === row.selectedMaskId.toString())
            const existingName = existingMask ? existingMask.unique_internal_model_code : `Mask ${row.selectedMaskId}`
            overwrites[row.fileMaskName] = 'To be created'
            matches[row.fileMaskName] = '__to_be_created__'
          }
        }
      })

      // If there are overwrites, show confirmation popup
      if (Object.keys(overwrites).length > 0) {
        this.pendingMaskMatchOverwrites = overwrites
        this.pendingMaskMatches = matches
        this.showMaskMatchConfirmation = true
      } else {
        // No overwrites, apply matches directly
        this.applyMaskMatches(matches)
      }
    },
    applyMaskMatches(matches) {
      // Apply the matches to maskMatchingRows
      Object.keys(matches).forEach(fileMaskName => {
        const row = this.maskMatchingRows.find(r => r.fileMaskName === fileMaskName)
        if (row) {
          row.selectedMaskId = matches[fileMaskName]
        }
      })

      this.messages = [{ str: `Matched ${Object.keys(matches).length} mask(s) automatically.` }]
    },
    confirmMaskMatchOverwrite() {
      // Apply all matches including overwrites
      this.applyMaskMatches(this.pendingMaskMatches)
      this.cancelMaskMatchConfirmation()
    },
    cancelMaskMatchConfirmation() {
      this.showMaskMatchConfirmation = false
      this.pendingMaskMatchOverwrites = {}
      this.pendingMaskMatches = {}
    },
    getMaskMatchingSimilarityScore(row) {
      // Get similarity score between File mask name and selected Breathesafe mask
      if (!row.selectedMaskId || row.selectedMaskId === '' || row.selectedMaskId === '__to_be_created__') {
        return null
      }

      const selectedMask = this.deduplicatedMasks.find(m => m.id.toString() === row.selectedMaskId.toString())

      if (!selectedMask) {
        return null
      }

      return this.calculateSimilarity(row.fileMaskName, selectedMask.unique_internal_model_code)
    },
    updateMaskMatching() {
      // Update maskMatching object when selections change
      // This will be saved when user clicks Next
    },
    async initializeTestingModeMatching() {
      // Parse CSV data and extract unique testing mode values from column mapped to "Testing mode"
      if (!this.csvFullContent || !this.columnMatching) {
        this.testingModeMatchingRows = []
        if (!this.csvFullContent) {
          this.messages = [{ str: 'CSV file content not loaded. Please complete Import File step first.' }]
        } else if (!this.columnMatching) {
          this.messages = [{ str: 'Column matching not completed. Please complete Column Matching step first.' }]
        }
        return
      }

      // Find column mapped to "Testing mode"
      const testingModeColumn = Object.keys(this.columnMatching).find(
        col => {
          const mappedValue = this.columnMatching[col]
          return mappedValue === 'Testing mode' || mappedValue === 'Testing mode (QLFT / N99 / N95)'
        }
      )

      if (!testingModeColumn) {
        this.testingModeMatchingRows = []
        // Debug: show what columns are mapped
        const mappedColumns = Object.keys(this.columnMatching).map(col => `${col} => ${this.columnMatching[col]}`).join(', ')
        this.messages = [{ str: `Testing mode column must be mapped in Column Matching. Currently mapped columns: ${mappedColumns}` }]
        return
      }

      // Parse CSV lines
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        this.testingModeMatchingRows = []
        return
      }

      // Get header row
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])
      // Find column index case-insensitively
      const testingModeColumnIndex = headerRow.findIndex(col =>
        col && col.trim().toLowerCase() === testingModeColumn.trim().toLowerCase()
      )

      if (testingModeColumnIndex === -1) {
        this.testingModeMatchingRows = []
        // Debug: show available header columns
        const availableColumns = headerRow.map((col, idx) => `"${col}"`).join(', ')
        this.messages = [{ str: `Could not find testing mode column "${testingModeColumn}" in CSV header. Available columns: ${availableColumns}` }]
        return
      }

      // Extract unique testing mode values from data rows (skip header row)
      const uniqueTestingModes = new Set()
      for (let i = this.headerRowIndex + 1; i < csvLines.length; i++) {
        const row = this.parseCSVLine(csvLines[i])
        if (row[testingModeColumnIndex]) {
          const value = row[testingModeColumnIndex].trim()
          if (value) {
            uniqueTestingModes.add(value)
          }
        }
      }

      // Create rows for each unique testing mode value
      const rows = Array.from(uniqueTestingModes).map(fileValue => ({
        fileValue: fileValue,
        selectedBreathesafeValue: null
      }))

      // Load saved matching if available
      if (this.testingModeMatching && Object.keys(this.testingModeMatching).length > 0) {
        rows.forEach(row => {
          if (this.testingModeMatching[row.fileValue]) {
            row.selectedBreathesafeValue = this.testingModeMatching[row.fileValue]
          }
        })
      }

      this.testingModeMatchingRows = rows
    },
    updateTestingModeMatching() {
      // Update testingModeMatching object when selections change
      // This will be saved when user clicks Next
    },
    getTestingModeSimilarityScore(row) {
      // Get similarity score between File testing mode value and selected Breathesafe testing mode value
      if (!row.selectedBreathesafeValue || row.selectedBreathesafeValue === '') {
        return null
      }

      return this.calculateSimilarity(row.fileValue, row.selectedBreathesafeValue)
    },
    attemptTestingModeAutoMatch() {
      if (!this.testingModeMatchingRows || this.testingModeMatchingRows.length === 0) {
        return
      }

      const matches = {}
      const overwrites = {}

      // Breathesafe testing mode options
      const breathesafeOptions = ['N99', 'N95', 'QLFT']

      // Track which breathesafe options have been matched
      const usedBreathesafeOptions = new Set()

      // Sort rows by file value for consistent processing
      const sortedRows = [...this.testingModeMatchingRows].sort((a, b) => {
        if (a.fileValue < b.fileValue) return -1
        if (a.fileValue > b.fileValue) return 1
        return 0
      })

      // For each row, find the best match from available breathesafe options
      sortedRows.forEach(row => {
        let bestBreathesafeValue = null
        let bestSimilarity = 0

        // Find best match from available breathesafe options
        breathesafeOptions.forEach(breathesafeValue => {
          if (usedBreathesafeOptions.has(breathesafeValue)) {
            return // Skip already matched breathesafe options
          }

          const similarity = this.calculateSimilarity(row.fileValue, breathesafeValue)

          if (similarity > bestSimilarity) {
            bestSimilarity = similarity
            bestBreathesafeValue = breathesafeValue
          }
        })

        // If best similarity is >= 0.4, assign the match
        if (bestSimilarity >= 0.4 && bestBreathesafeValue) {
          // Check if row already has this breathesafe value selected
          const alreadyHasBestMatch = row.selectedBreathesafeValue &&
            row.selectedBreathesafeValue === bestBreathesafeValue

          if (alreadyHasBestMatch) {
            // Already has the best match, mark it as used and skip
            usedBreathesafeOptions.add(bestBreathesafeValue)
            return
          }

          // Check if row has a different selection that would be overwritten
          if (row.selectedBreathesafeValue && row.selectedBreathesafeValue !== bestBreathesafeValue) {
            overwrites[row.fileValue] = bestBreathesafeValue
          }

          matches[row.fileValue] = bestBreathesafeValue
          usedBreathesafeOptions.add(bestBreathesafeValue)
        }
      })

      // If there are overwrites, ask for confirmation
      if (Object.keys(overwrites).length > 0) {
        this.pendingTestingModeMatchOverwrites = overwrites
        this.pendingTestingModeMatches = matches
        this.showTestingModeMatchConfirmation = true
      } else {
        // No overwrites, apply matches directly
        this.applyTestingModeMatches(matches)
      }
    },
    applyTestingModeMatches(matches) {
      // Apply matches to rows
      this.testingModeMatchingRows.forEach(row => {
        if (matches[row.fileValue]) {
          row.selectedBreathesafeValue = matches[row.fileValue]
        }
      })
      this.updateTestingModeMatching()
    },
    confirmTestingModeMatchOverwrite() {
      // Merge pending matches with overwrites
      const allMatches = { ...this.pendingTestingModeMatches, ...this.pendingTestingModeMatchOverwrites }
      this.applyTestingModeMatches(allMatches)
      this.cancelTestingModeMatchConfirmation()
    },
    cancelTestingModeMatchConfirmation() {
      this.showTestingModeMatchConfirmation = false
      this.pendingTestingModeMatchOverwrites = {}
      this.pendingTestingModeMatches = {}
    },
    async saveTestingModeMatching() {
      // Validate that all file testing mode values have a mapping
      const unmappedRows = this.testingModeMatchingRows.filter(
        row => !row.selectedBreathesafeValue || row.selectedBreathesafeValue === ''
      )

      if (unmappedRows.length > 0) {
        this.messages = [{
          str: `Please map all testing mode values. ${unmappedRows.length} value(s) are unmapped: ${unmappedRows.map(r => r.fileValue).join(', ')}`
        }]
        return
      }

      // Build testing mode matching object: { "file_value": "breathesafe_value" }
      const matching = {}
      this.testingModeMatchingRows.forEach(row => {
        if (row.selectedBreathesafeValue) {
          matching[row.fileValue] = row.selectedBreathesafeValue
        }
      })

      // Check authentication before saving
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, {
          bulk_fit_tests_import: {
            testing_mode_matching: matching
          }
        })

        if (response.status === 200) {
          this.testingModeMatching = matching
          // Mark step as completed
          if (!this.completedSteps.includes('Testing Mode Values Matching')) {
            this.completedSteps.push('Testing Mode Values Matching')
          }
          // Move to next step - check if QLFT Values Matching is needed
          if (this.qlftValuesMatchingNotApplicable) {
            // Skip QLFT Values Matching, go to Comfort Matching
            this.currentStep = 'Comfort Matching'
            await this.initializeComfortMatching()
          } else {
            // Go to QLFT Values Matching
            this.currentStep = 'QLFT Values Matching'
            await this.initializeQlftValuesMatching()
          }
        }
      } catch (error) {
        console.error('Error saving testing mode matching:', error)
        if (error.response && error.response.status === 401) {
          // User is not authenticated, redirect to sign in
          await this.handleUnauthorized()
        } else {
          this.messages = [{ str: 'Error saving testing mode matching. Please try again.' }]
        }
      } finally {
        this.isSaving = false
      }
    },
    async initializeQlftValuesMatching() {
      // Check if there are any QLFT rows based on testing_mode_matching
      if (!this.csvFullContent || !this.columnMatching || !this.testingModeMatching) {
        this.qlftValuesMatchingRows = []
        this.qlftValuesMatchingNotApplicable = true
        return
      }

      // Check if any testing mode maps to "QLFT"
      const hasQlftRows = Object.values(this.testingModeMatching).some(value => value === 'QLFT')

      if (!hasQlftRows) {
        this.qlftValuesMatchingRows = []
        this.qlftValuesMatchingNotApplicable = true
        // Mark as completed (not applicable)
        if (!this.completedSteps.includes('QLFT Values Matching')) {
          this.completedSteps.push('QLFT Values Matching')
        }
        return
      }

      // Find all QLFT exercise columns
      const qlftExerciseNames = [
        'Bending over',
        'Talking',
        'Turning head side to side',
        'Moving head up and down',
        'Normal breathing 1',
        'Normal breathing 2',
        'Grimace',
        'Deep breathing',
        'Normal breathing (SEALED)'
      ]

      // Find columns mapped to QLFT exercises
      const qlftExerciseColumns = []
      qlftExerciseNames.forEach(exerciseName => {
        const column = Object.keys(this.columnMatching).find(
          col => {
            const mappedValue = this.columnMatching[col]
            // Check for QLFT -> prefix or direct match
            return mappedValue === `QLFT -> ${exerciseName}` || mappedValue === exerciseName
          }
        )
        if (column) {
          qlftExerciseColumns.push({ column, exerciseName })
        }
      })

      if (qlftExerciseColumns.length === 0) {
        this.qlftValuesMatchingRows = []
        this.qlftValuesMatchingNotApplicable = true
        return
      }

      // Parse CSV lines
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        this.qlftValuesMatchingRows = []
        this.qlftValuesMatchingNotApplicable = true
        return
      }

      // Get header row
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])

      // Find column indices for QLFT exercises
      const qlftExerciseColumnIndices = qlftExerciseColumns.map(({ column }) => {
        const index = headerRow.findIndex(col =>
          col && col.trim().toLowerCase() === column.trim().toLowerCase()
        )
        return { column, index }
      }).filter(({ index }) => index >= 0)

      if (qlftExerciseColumnIndices.length === 0) {
        this.qlftValuesMatchingRows = []
        this.qlftValuesMatchingNotApplicable = true
        return
      }

      // Extract unique QLFT values from all QLFT exercise columns
      const uniqueQlftValues = new Set()

      // Only process rows where testing mode is QLFT
      for (let i = this.headerRowIndex + 1; i < csvLines.length; i++) {
        const csvRow = this.parseCSVLine(csvLines[i])

        // Check if this row has QLFT testing mode
        const testingModeColumn = Object.keys(this.columnMatching).find(
          col => {
            const mappedValue = this.columnMatching[col]
            return mappedValue === 'Testing mode' || mappedValue === 'Testing mode (QLFT / N99 / N95)'
          }
        )

        if (testingModeColumn) {
          const testingModeColumnIndex = headerRow.findIndex(col =>
            col && col.trim().toLowerCase() === testingModeColumn.trim().toLowerCase()
          )

          if (testingModeColumnIndex >= 0) {
            const fileTestingMode = csvRow[testingModeColumnIndex] ? csvRow[testingModeColumnIndex].trim() : null
            const mappedTestingMode = fileTestingMode && this.testingModeMatching[fileTestingMode]

            // Only process if this row maps to QLFT
            if (mappedTestingMode !== 'QLFT') {
              continue
            }
          }
        }

        // Extract values from all QLFT exercise columns
        qlftExerciseColumnIndices.forEach(({ index }) => {
          if (csvRow[index]) {
            const value = csvRow[index].trim()
            if (value) {
              uniqueQlftValues.add(value)
            }
          }
        })
      }

      // Create rows for each unique QLFT value
      const rows = Array.from(uniqueQlftValues).map(fileValue => ({
        fileValue: fileValue,
        selectedBreathesafeValue: null
      }))

      // Load saved matching if available
      if (this.qlftValuesMatching && Object.keys(this.qlftValuesMatching).length > 0) {
        rows.forEach(row => {
          if (this.qlftValuesMatching[row.fileValue]) {
            row.selectedBreathesafeValue = this.qlftValuesMatching[row.fileValue]
          }
        })
      }

      this.qlftValuesMatchingRows = rows
      this.qlftValuesMatchingNotApplicable = false
    },
    updateQlftValuesMatching() {
      // Update qlftValuesMatching object when selections change
      // This will be saved when user clicks Next
    },
    getQlftValuesSimilarityScore(row) {
      // Get similarity score between File QLFT value and selected Breathesafe QLFT value
      if (!row.selectedBreathesafeValue || row.selectedBreathesafeValue === '') {
        return null
      }

      return this.calculateSimilarity(row.fileValue, row.selectedBreathesafeValue)
    },
    attemptQlftValuesAutoMatch() {
      if (!this.qlftValuesMatchingRows || this.qlftValuesMatchingRows.length === 0) {
        return
      }

      const matches = {}
      const overwrites = {}

      // Breathesafe QLFT value options
      const breathesafeOptions = ['Pass', 'Fail']

      // Sort rows by file value for consistent processing
      const sortedRows = [...this.qlftValuesMatchingRows].sort((a, b) => {
        if (a.fileValue < b.fileValue) return -1
        if (a.fileValue > b.fileValue) return 1
        return 0
      })

      // For each row, find the best match from available breathesafe options
      sortedRows.forEach(row => {
        let bestBreathesafeValue = null
        let bestSimilarity = 0

        // Find best match from breathesafe options
        breathesafeOptions.forEach(breathesafeValue => {
          const similarity = this.calculateSimilarity(row.fileValue, breathesafeValue)

          if (similarity > bestSimilarity) {
            bestSimilarity = similarity
            bestBreathesafeValue = breathesafeValue
          }
        })

        // If best similarity is >= 0.4, assign the match
        if (bestSimilarity >= 0.4 && bestBreathesafeValue) {
          // Check if row already has this breathesafe value selected
          const alreadyHasBestMatch = row.selectedBreathesafeValue &&
            row.selectedBreathesafeValue === bestBreathesafeValue

          if (alreadyHasBestMatch) {
            return
          }

          // Check if row has a different selection that would be overwritten
          if (row.selectedBreathesafeValue && row.selectedBreathesafeValue !== bestBreathesafeValue) {
            overwrites[row.fileValue] = bestBreathesafeValue
          }

          matches[row.fileValue] = bestBreathesafeValue
        }
      })

      // If there are overwrites, ask for confirmation
      if (Object.keys(overwrites).length > 0) {
        this.pendingQlftValuesMatchOverwrites = overwrites
        this.pendingQlftValuesMatches = matches
        this.showQlftValuesMatchConfirmation = true
      } else {
        // No overwrites, apply matches directly
        this.applyQlftValuesMatches(matches)
      }
    },
    applyQlftValuesMatches(matches) {
      // Apply matches to rows
      this.qlftValuesMatchingRows.forEach(row => {
        if (matches[row.fileValue]) {
          row.selectedBreathesafeValue = matches[row.fileValue]
        }
      })
      this.updateQlftValuesMatching()
    },
    confirmQlftValuesMatchOverwrite() {
      // Merge pending matches with overwrites
      const allMatches = { ...this.pendingQlftValuesMatches, ...this.pendingQlftValuesMatchOverwrites }
      this.applyQlftValuesMatches(allMatches)
      this.cancelQlftValuesMatchConfirmation()
    },
    cancelQlftValuesMatchConfirmation() {
      this.showQlftValuesMatchConfirmation = false
      this.pendingQlftValuesMatchOverwrites = {}
      this.pendingQlftValuesMatches = {}
    },
    async saveQlftValuesMatching() {
      // Build QLFT values matching object: { "file_value": "breathesafe_value" }
      const matching = {}
      this.qlftValuesMatchingRows.forEach(row => {
        if (row.selectedBreathesafeValue) {
          matching[row.fileValue] = row.selectedBreathesafeValue
        }
      })

      // Check for unmapped values and show warning
      const unmappedRows = this.qlftValuesMatchingRows.filter(
        row => !row.selectedBreathesafeValue || row.selectedBreathesafeValue === ''
      )

      if (unmappedRows.length > 0) {
        // Show warning but allow proceeding
        this.messages = [{
          str: `Warning: ${unmappedRows.length} QLFT value(s) are unmapped. Importing will not include rows with unmapped QLFT values: ${unmappedRows.map(r => r.fileValue).join(', ')}`
        }]
      }

      // Check authentication before saving
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        return
      }

      this.isSaving = true

      try {
        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, {
          bulk_fit_tests_import: {
            qlft_values_matching: matching
          }
        })

        if (response.status === 200) {
          this.qlftValuesMatching = matching
          // Mark step as completed
          if (!this.completedSteps.includes('QLFT Values Matching')) {
            this.completedSteps.push('QLFT Values Matching')
          }
          // Move to next step: Comfort Matching before Review
          this.currentStep = 'Comfort Matching'
          await this.initializeComfortMatching()
        }
      } catch (error) {
        console.error('Error saving QLFT values matching:', error)
        if (error.response && error.response.status === 401) {
          // User is not authenticated, redirect to sign in
          await this.handleUnauthorized()
        } else {
          this.messages = [{ str: 'Error saving QLFT values matching. Please try again.' }]
        }
      } finally {
        this.isSaving = false
      }
    },
    async initializeFitTestDataMatching() {
      // Parse CSV data and create rows for fit test data
      if (!this.csvFullContent || !this.columnMatching || !this.maskMatching) {
        this.fitTestDataRows = []
        return
      }

      // Ensure qlftValuesMatching is loaded if available
      if (!this.qlftValuesMatching) {
        this.qlftValuesMatching = {}
      }

      // Ensure masks are loaded first
      if (this.allMasks.length === 0) {
        await this.fetchDeduplicatedMasks()
      }

      // Find columns mapped to mask, testing mode, manager email, and user name
      // columnMatching structure: { "CSV Column Name": "Breathesafe Column Name" }
      const maskColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'Mask.unique_internal_model_code'
      )

      const testingModeColumn = Object.keys(this.columnMatching).find(
        col => {
          const mappedValue = this.columnMatching[col]
          return mappedValue === 'Testing mode' || mappedValue === 'Testing mode (QLFT / N99 / N95)'
        }
      )

      const managerEmailColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'manager email'
      )

      const userNameColumn = Object.keys(this.columnMatching).find(
        col => this.columnMatching[col] === 'user name'
      )

      if (!maskColumn) {
        this.fitTestDataRows = []
        this.messages = [{ str: 'Mask column must be mapped in Column Matching.' }]
        return
      }

      // Parse CSV lines
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        this.fitTestDataRows = []
        return
      }

      // Get header row
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])
      const maskColumnIndex = headerRow.indexOf(maskColumn)
      // testingModeColumn is the CSV column name (key), use it to find index (case-insensitive)
      let testingModeColumnIndex = -1
      if (testingModeColumn) {
        testingModeColumnIndex = headerRow.findIndex(col =>
          col && col.trim().toLowerCase() === testingModeColumn.trim().toLowerCase()
        )
      }

      // Find manager email and user name column indices (case-insensitive)
      let managerEmailColumnIndex = -1
      if (managerEmailColumn) {
        managerEmailColumnIndex = headerRow.findIndex(col =>
          col && col.trim().toLowerCase() === managerEmailColumn.trim().toLowerCase()
        )
      }

      let userNameColumnIndex = -1
      if (userNameColumn) {
        userNameColumnIndex = headerRow.findIndex(col =>
          col && col.trim().toLowerCase() === userNameColumn.trim().toLowerCase()
        )
      }

      if (maskColumnIndex === -1) {
        this.fitTestDataRows = []
        this.messages = [{ str: 'Could not find mask column in CSV.' }]
        return
      }

      // Find exercise columns
      const exerciseColumns = {
        bendingOver: this.findExerciseColumn('Bending over'),
        talking: this.findExerciseColumn('Talking'),
        turningHeadSideToSide: this.findExerciseColumn('Turning head side to side'),
        movingHeadUpAndDown: this.findExerciseColumn('Moving head up and down'),
        normalBreathing1: this.findExerciseColumn('Normal breathing 1'),
        normalBreathing2: this.findExerciseColumn('Normal breathing 2'),
        grimace: this.findExerciseColumn('Grimace'),
        deepBreathing: this.findExerciseColumn('Deep breathing'),
        normalBreathingSealed: this.findExerciseColumn('Normal breathing (SEALED)')
      }

      // Parse data rows
      const rows = []
      for (let i = this.headerRowIndex + 1; i < csvLines.length; i++) {
        const csvRow = this.parseCSVLine(csvLines[i])
        const fileMaskName = csvRow[maskColumnIndex] ? csvRow[maskColumnIndex].trim() : ''
        const fileTestingMode = testingModeColumnIndex >= 0 && csvRow[testingModeColumnIndex]
          ? csvRow[testingModeColumnIndex].trim()
          : null
        // Beard length column (if mapped)
        const beardCsvColumn = Object.keys(this.columnMatching).find(
          col => this.columnMatching[col] === 'facial hair beard length mm'
        )
        let beardLengthMm = null
        let beardLengthInvalid = false
        if (beardCsvColumn) {
          const beardIdx = headerRow.findIndex(col => col && col.trim().toLowerCase() === beardCsvColumn.trim().toLowerCase())
          if (beardIdx >= 0) {
            const raw = csvRow[beardIdx]
            if (raw != null && raw.trim() !== '') {
              const trimmed = raw.trim()
              const numericMatch = trimmed.match(/^\d+(\.\d+)?$/)
              if (numericMatch) {
                beardLengthMm = trimmed
              } else {
                beardLengthInvalid = true
              }
            }
          }
        }
        // USC columns (if mapped)
        const sizingQ = 'USC -> What do you think about the sizing of this mask relative to your face?'
        const airQ = 'USC -> How much air movement on your face along the seal of the mask did you feel?'
        const sizingCsvColumn = Object.keys(this.columnMatching).find(col => this.columnMatching[col] === sizingQ)
        const airCsvColumn = Object.keys(this.columnMatching).find(col => this.columnMatching[col] === airQ)
        let uscSizing = null
        let uscAirMovement = null
        let uscSizingFile = null
        let uscAirMovementFile = null
        if (sizingCsvColumn) {
          const sizingIdx = headerRow.findIndex(col => col && col.trim().toLowerCase() === sizingCsvColumn.trim().toLowerCase())
          if (sizingIdx >= 0) {
            const raw = csvRow[sizingIdx]
            const fileVal = raw && raw.trim() !== '' ? raw.trim() : null
            if (fileVal) {
              uscSizingFile = fileVal
              const mapped = this.userSealCheckMatching && this.userSealCheckMatching[sizingQ] ? this.userSealCheckMatching[sizingQ][fileVal] : null
              uscSizing = mapped || fileVal
            }
          }
        }
        if (airCsvColumn) {
          const airIdx = headerRow.findIndex(col => col && col.trim().toLowerCase() === airCsvColumn.trim().toLowerCase())
          if (airIdx >= 0) {
            const raw = csvRow[airIdx]
            const fileVal = raw && raw.trim() !== '' ? raw.trim() : null
            if (fileVal) {
              uscAirMovementFile = fileVal
              const mapped = this.userSealCheckMatching && this.userSealCheckMatching[airQ] ? this.userSealCheckMatching[airQ][fileVal] : null
              uscAirMovement = mapped || fileVal
            }
          }
        }

        // Map file testing mode value to Breathesafe testing mode value using testing_mode_matching
        let testingMode = null
        if (fileTestingMode && this.testingModeMatching && this.testingModeMatching[fileTestingMode]) {
          testingMode = this.testingModeMatching[fileTestingMode]
        } else if (fileTestingMode) {
          // If no mapping found, use the file value as-is (for display purposes)
          testingMode = fileTestingMode
        }

        // Extract manager email and user name
        const managerEmail = managerEmailColumnIndex >= 0 && csvRow[managerEmailColumnIndex]
          ? csvRow[managerEmailColumnIndex].trim()
          : null
        const userName = userNameColumnIndex >= 0 && csvRow[userNameColumnIndex]
          ? csvRow[userNameColumnIndex].trim()
          : null

        if (!fileMaskName) {
          continue // Skip rows without mask name
        }

        // Find mask ID from mask_matching
        const maskId = this.maskMatching[fileMaskName]
        if (!maskId || maskId === '__to_be_created__') {
          continue // Skip rows with unmapped or to-be-created masks
        }

        // Find mask name from all masks (not just deduplicated)
        const mask = this.allMasks.find(m => m.id.toString() === maskId.toString())
        const maskName = mask ? mask.unique_internal_model_code : `Mask ${maskId}`

        // Look up managed_user_id from user_matching
        // Format: key is "manager_email|||user_name", value is managed_user_id
        let managedUserId = null
        if (managerEmail && userName && this.userMatching) {
          const userMatchingKey = `${managerEmail}|||${userName}`
          managedUserId = this.userMatching[userMatchingKey] || null
        }

        // Extract exercise values
        const exercises = {}
        const exerciseHasUnmappedQlftValue = {}
        const exerciseHasInvalidN95N99Value = {}
        Object.keys(exerciseColumns).forEach(exerciseKey => {
          const columnInfo = exerciseColumns[exerciseKey]
          if (columnInfo && columnInfo.columnIndex >= 0) {
            const value = csvRow[columnInfo.columnIndex]
            const trimmedValue = value ? value.trim() : null

            // If this is a QLFT row, check if the value is mapped
            if (testingMode === 'QLFT' && trimmedValue && this.qlftValuesMatching) {
              const mappedValue = this.qlftValuesMatching[trimmedValue]
              if (mappedValue) {
                exercises[exerciseKey] = mappedValue
                exerciseHasUnmappedQlftValue[exerciseKey] = false
              } else {
                exercises[exerciseKey] = trimmedValue // Keep original value for display
                exerciseHasUnmappedQlftValue[exerciseKey] = true
              }
              exerciseHasInvalidN95N99Value[exerciseKey] = false
            } else if ((testingMode === 'N95' || testingMode === 'N99') && trimmedValue) {
              // For N95/N99 rows, check if value contains only alphanumeric characters
              // Allow numbers, letters, and common numeric characters like decimal points, minus signs
              // But flag if there are other non-alphanumeric characters
              const alphanumericRegex = /^[a-zA-Z0-9.\-+\s]*$/
              if (alphanumericRegex.test(trimmedValue)) {
                exercises[exerciseKey] = trimmedValue
                exerciseHasInvalidN95N99Value[exerciseKey] = false
              } else {
                exercises[exerciseKey] = trimmedValue // Keep original value for display
                exerciseHasInvalidN95N99Value[exerciseKey] = true
              }
              exerciseHasUnmappedQlftValue[exerciseKey] = false
            } else {
              exercises[exerciseKey] = trimmedValue
              exerciseHasUnmappedQlftValue[exerciseKey] = false
              exerciseHasInvalidN95N99Value[exerciseKey] = false
            }
          } else {
            exercises[exerciseKey] = null
            exerciseHasUnmappedQlftValue[exerciseKey] = false
            exerciseHasInvalidN95N99Value[exerciseKey] = false
          }
        })

        rows.push({
          managerEmail,
          userName,
          managedUserId,
          maskName,
          maskId,
          testingMode,
          exercises,
          exerciseHasUnmappedQlftValue,
          exerciseHasInvalidN95N99Value,
          beardLengthMm,
          beardLengthInvalid,
          uscSizing,
          uscAirMovement,
          uscSizingFile,
          uscAirMovementFile,
          // Comfort display and file values (mapped for display, file for payload)
          comfortNose: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "How comfortable is the position of the mask on the nose?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            if (!val) return null
            const mapped = (this.comfortMatching && this.comfortMatching['How comfortable is the position of the mask on the nose?'])
              ? this.comfortMatching['How comfortable is the position of the mask on the nose?'][val]
              : null
            return mapped || val
          })(),
          comfortTalk: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "Is there enough room to talk?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            if (!val) return null
            const mapped = (this.comfortMatching && this.comfortMatching['Is there enough room to talk?'])
              ? this.comfortMatching['Is there enough room to talk?'][val]
              : null
            return mapped || val
          })(),
          comfortFace: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "How comfortable is the position of the mask on face and cheeks?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            if (!val) return null
            const mapped = (this.comfortMatching && this.comfortMatching['How comfortable is the position of the mask on face and cheeks?'])
              ? this.comfortMatching['How comfortable is the position of the mask on face and cheeks?'][val]
              : null
            return mapped || val
          })(),
          comfortNoseFile: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "How comfortable is the position of the mask on the nose?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            return val || null
          })(),
          comfortTalkFile: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "Is there enough room to talk?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            return val || null
          })(),
          comfortFaceFile: (() => {
            const col = Object.keys(this.columnMatching).find(c => this.columnMatching[c] === 'comfort -> "How comfortable is the position of the mask on face and cheeks?"')
            if (!col) return null
            const idx = headerRow.findIndex(h => h && h.trim().toLowerCase() === col.trim().toLowerCase())
            if (idx < 0) return null
            const val = csvRow[idx] ? csvRow[idx].trim() : null
            return val || null
          })()
        })
      }

      this.fitTestDataRows = rows
    },
    findExerciseColumn(exerciseName) {
      // Find column mapped to this exercise (could be QLFT ->, QNFT ->, or direct match)
      if (!this.columnMatching || !this.fileColumns) {
        return null
      }

      // Parse CSV to get header row
      const csvLines = this.csvFullContent.split('\n').filter(line => line.trim() !== '')
      if (csvLines.length <= this.headerRowIndex) {
        return null
      }
      const headerRow = this.parseCSVLine(csvLines[this.headerRowIndex])

      const normalizedExercise = exerciseName.toLowerCase()

      // Look for columns mapped to exercises containing this name
      // Check both QLFT -> and QNFT -> patterns, as well as direct matches
      for (const csvColumn of this.fileColumns) {
        const mappedValue = this.columnMatching[csvColumn]
        if (typeof mappedValue === 'string') {
          const normalizedMapped = mappedValue.toLowerCase()

          // Check for direct match (e.g., "Talking" matches "Talking")
          if (normalizedMapped === normalizedExercise) {
            const columnIndex = headerRow.indexOf(csvColumn)
            if (columnIndex >= 0) {
              return {
                csvColumn,
                columnIndex
              }
            }
          }

          // Check if it matches QLFT -> Exercise or QNFT -> Exercise
          // e.g., "QLFT -> Talking" or "QNFT -> Talking"
          if (normalizedMapped.includes('->') && normalizedMapped.includes(normalizedExercise)) {
            const columnIndex = headerRow.indexOf(csvColumn)
            if (columnIndex >= 0) {
              return {
                csvColumn,
                columnIndex
              }
            }
          }
        }
      }

      return null
    },
    async saveUserMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }

      // Check for validation errors
      if (this.hasUserMatchingErrors) {
        this.messages = [{ str: 'Please fix all errors before proceeding.' }]
        return
      }

      // Check authentication
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        // Build user_matching object
        const userMatching = {}
        this.userMatchingRows.forEach(row => {
          if (!row.hasError && row.selectedManagedUserId) {
            const key = `${row.managerEmail}|||${row.userName}`
            userMatching[key] = row.selectedManagedUserId
          }
        })

        const payload = {
          bulk_fit_tests_import: {
            user_matching: JSON.stringify(userMatching)
          }
        }

        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, payload)

        if (response.status === 200) {
          // Update local state
          this.userMatching = userMatching

          // Move to Mask Matching step
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
            const nextStep = steps[currentIndex + 1]
            this.currentStep = nextStep
            // Initialize Mask Matching immediately to avoid empty view until refresh
            if (nextStep === 'Mask Matching') {
              await this.initializeMaskMatching()
            }
          }

          // Mark User Matching as completed
          if (!this.completedSteps.includes('User Matching')) {
            this.completedSteps.push('User Matching')
          }
        } else {
          const errorMessages = response.data.messages || ['Failed to save user matching.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to save user matching.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
      }
    },
    async saveMaskMatching() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }

      // Check authentication
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        // Build mask_matching object
        const maskMatching = {}
        this.maskMatchingRows.forEach(row => {
          if (row.selectedMaskId) {
            maskMatching[row.fileMaskName] = row.selectedMaskId
          }
        })

        const payload = {
          bulk_fit_tests_import: {
            mask_matching: maskMatching
          }
        }

        const response = await axios.put(`/bulk_fit_tests_imports/${this.bulkFitTestsImportId}.json`, payload)

        if (response.status === 200) {
          // Update local state
          this.maskMatching = maskMatching

          // Move to User Seal Check Matching step
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
            const nextStep = steps[currentIndex + 1]
            this.currentStep = nextStep
            // Initialize User Seal Check Matching immediately to avoid empty view until refresh
            if (nextStep === 'User Seal Check Matching') {
              await this.initializeUserSealCheckMatching()
            }
          }

          // Mark Mask Matching as completed
          if (!this.completedSteps.includes('Mask Matching')) {
            this.completedSteps.push('Mask Matching')
          }
        } else {
          const errorMessages = response.data.messages || ['Failed to save mask matching.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to save mask matching.'
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
        'Testing Mode Values Matching',
        'QLFT Values Matching',
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
          this.bulkImportStatus = bulkImport.status

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

          // Load user_matching if available
          if (bulkImport.user_matching) {
            try {
              // user_matching is encrypted text, parse it as JSON
              this.userMatching = typeof bulkImport.user_matching === 'string'
                ? JSON.parse(bulkImport.user_matching)
                : bulkImport.user_matching
            } catch (e) {
              // If parsing fails, try to use it as-is or default to empty object
              this.userMatching = bulkImport.user_matching || {}
            }
          } else {
            this.userMatching = {}
          }

          // Load mask_matching if available
          if (bulkImport.mask_matching) {
            this.maskMatching = bulkImport.mask_matching
          } else {
            this.maskMatching = {}
          }

          // Load user_seal_check_matching if available
          if (bulkImport.user_seal_check_matching) {
            this.userSealCheckMatching = bulkImport.user_seal_check_matching
          } else {
            this.userSealCheckMatching = {}
          }

          // Load testing_mode_matching if available
          if (bulkImport.testing_mode_matching) {
            this.testingModeMatching = bulkImport.testing_mode_matching
          } else {
            this.testingModeMatching = {}
          }

          // Load qlft_values_matching if available
          if (bulkImport.qlft_values_matching) {
            this.qlftValuesMatching = bulkImport.qlft_values_matching
          } else {
            this.qlftValuesMatching = {}
          }
          // Load comfort_matching if available
          if (bulkImport.comfort_matching) {
            this.comfortMatching = bulkImport.comfort_matching
          } else {
            this.comfortMatching = {}
          }

          // Check if QLFT Values Matching is applicable
          const hasQlftRows = Object.values(this.testingModeMatching).some(value => value === 'QLFT')
          this.qlftValuesMatchingNotApplicable = !hasQlftRows

          // Set current step and completed steps
          if (bulkImport.qlft_values_matching && Object.keys(this.qlftValuesMatching).length > 0) {
            // If QLFT values matching exists, we're past QLFT Values Matching step
            this.currentStep = 'Fit Test Data Matching'
            this.completedSteps = ['Import File', 'Column Matching', 'User Matching', 'Mask Matching', 'User Seal Check Matching', 'Testing Mode Values Matching', 'QLFT Values Matching']
            // Initialize fit test data matching after a short delay to ensure data is loaded
            this.$nextTick(() => {
              this.initializeFitTestDataMatching()
            })
          } else if (bulkImport.testing_mode_matching && Object.keys(this.testingModeMatching).length > 0) {
            // If testing mode matching exists, check if QLFT Values Matching is needed
            if (this.qlftValuesMatchingNotApplicable) {
          // Skip QLFT Values Matching, go to Comfort Matching
          this.currentStep = 'Comfort Matching'
          this.completedSteps = ['Import File', 'Column Matching', 'User Matching', 'Mask Matching', 'User Seal Check Matching', 'Testing Mode Values Matching', 'QLFT Values Matching']
              // Initialize fit test data matching after a short delay to ensure data is loaded
              this.$nextTick(() => {
            this.initializeComfortMatching()
              })
            } else {
              // Go to QLFT Values Matching
              this.currentStep = 'QLFT Values Matching'
              this.completedSteps = ['Import File', 'Column Matching', 'User Matching', 'Mask Matching', 'User Seal Check Matching', 'Testing Mode Values Matching']
            }
      } else if (bulkImport.mask_matching && Object.keys(this.maskMatching).length > 0) {
            // If mask matching exists, we're past Mask Matching step
            this.currentStep = 'User Seal Check Matching'
            this.completedSteps = ['Import File', 'Column Matching', 'User Matching', 'Mask Matching']
            // Initialize USC matching after a short delay to ensure data is loaded
            this.$nextTick(() => {
              this.initializeUserSealCheckMatching()
            })
      } else if (bulkImport.user_matching && Object.keys(this.userMatching).length > 0) {
            // If user matching exists, we're past User Matching step
            this.currentStep = 'Mask Matching'
            this.completedSteps = ['Import File', 'Column Matching', 'User Matching']
            // Initialize mask matching after a short delay to ensure data is loaded
            this.$nextTick(() => {
              this.initializeMaskMatching()
            })
          } else if (bulkImport.column_matching_mapping && Object.keys(bulkImport.column_matching_mapping).length > 1) {
            // If column matching exists (has more than just header_row_index), check if we should be on User Matching
            // Check if manager email and user name columns are mapped
            const columnMatchingValues = Object.values(bulkImport.column_matching_mapping)
            const hasManagerEmail = columnMatchingValues.includes('manager email')
            const hasUserName = columnMatchingValues.includes('user name')

            if (hasManagerEmail && hasUserName) {
              // Column matching is complete, allow User Matching step
              this.currentStep = 'User Matching'
              this.completedSteps = ['Import File', 'Column Matching']
              // Initialize user matching after a short delay to ensure data is loaded
              this.$nextTick(() => {
                this.initializeUserMatching()
              })
            } else {
              // Still on Column Matching step
              this.currentStep = 'Column Matching'
              this.completedSteps = ['Import File']
            }
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
    async completeImport() {
      if (!this.bulkFitTestsImportId || this.isSaving) {
        return
      }

      // Check authentication
      const isAuthenticated = await this.checkAuthentication()
      if (!isAuthenticated) {
        this.redirectToSignIn()
        return
      }

      if (this.fitTestDataRows.length === 0) {
        this.messages = [{ str: 'No fit test data to import.' }]
        return
      }

      this.isSaving = true
      this.messages = []

      try {
        // Filter out rows with unmapped QLFT values or invalid N95/N99 values
        const validFitTestRows = this.fitTestDataRows.filter(row => {
          // If this is a QLFT row, check if any exercise has unmapped QLFT value
          if (row.testingMode === 'QLFT' && row.exerciseHasUnmappedQlftValue) {
            const hasUnmapped = Object.values(row.exerciseHasUnmappedQlftValue).some(hasUnmapped => hasUnmapped === true)
            return !hasUnmapped // Exclude rows with unmapped values
          }
          // If this is an N95/N99 row, check if any exercise has invalid (non-alphanumeric) value
          if ((row.testingMode === 'N95' || row.testingMode === 'N99') && row.exerciseHasInvalidN95N99Value) {
            const hasInvalid = Object.values(row.exerciseHasInvalidN95N99Value).some(hasInvalid => hasInvalid === true)
            return !hasInvalid // Exclude rows with invalid values
          }
          return true // Include all other rows
        })

        if (validFitTestRows.length === 0) {
          this.messages = [{ str: 'No valid fit test data to import. All rows have unmapped QLFT values or other issues.' }]
          this.isSaving = false
          return
        }

        // Prepare fit tests data for backend
        const fitTestsData = validFitTestRows.map(row => {
          // Map exercise keys to proper exercise names
          const exercises = {}
          if (row.exercises.bendingOver) exercises['Bending over'] = row.exercises.bendingOver
          if (row.exercises.talking) exercises['Talking'] = row.exercises.talking
          if (row.exercises.turningHeadSideToSide) exercises['Turning head side to side'] = row.exercises.turningHeadSideToSide
          if (row.exercises.movingHeadUpAndDown) exercises['Moving head up and down'] = row.exercises.movingHeadUpAndDown
          if (row.exercises.normalBreathing1) exercises['Normal breathing 1'] = row.exercises.normalBreathing1
          if (row.exercises.normalBreathing2) exercises['Normal breathing 2'] = row.exercises.normalBreathing2
          if (row.exercises.grimace) exercises['Grimace'] = row.exercises.grimace
          if (row.exercises.deepBreathing) exercises['Deep breathing'] = row.exercises.deepBreathing
          if (row.exercises.normalBreathingSealed) exercises['Normal breathing (SEALED)'] = row.exercises.normalBreathingSealed

          const payload = {
            user_id: row.managedUserId, // This is the managed_user_id, which is the user_id
            mask_id: row.maskId,
            testing_mode: row.testingMode,
            exercises: exercises
          }
          if (row.beardLengthMm && !row.beardLengthInvalid) {
            payload.facial_hair = { beard_length_mm: `${row.beardLengthMm}mm` }
          }
          // Build user_seal_check payload from row USC mapping
          const sizingQ = 'USC -> What do you think about the sizing of this mask relative to your face?'
          const sizingKey = 'What do you think about the sizing of this mask relative to your face?'
          const airQ = 'USC -> How much air movement on your face along the seal of the mask did you feel?'
          const airKey = '...how much air movement on your face along the seal of the mask did you feel?'
          const fogKey = '...how much did your glasses fog up?'
          const pressureKey = '...how much pressure build up was there?'
          const passedAirKey = '...how much air passed between your face and the mask?'
          const mappedSizing = row.uscSizingFile && this.userSealCheckMatching && this.userSealCheckMatching[sizingQ]
            ? this.userSealCheckMatching[sizingQ][row.uscSizingFile] || null
            : null
          const mappedAir = row.uscAirMovementFile && this.userSealCheckMatching && this.userSealCheckMatching[airQ]
            ? this.userSealCheckMatching[airQ][row.uscAirMovementFile] || null
            : null
          payload.user_seal_check = {
            sizing: { [sizingKey]: mappedSizing },
            negative: { [passedAirKey]: null },
            positive: {
              [fogKey]: null,
              [pressureKey]: null,
              [airKey]: mappedAir
            }
          }
          // Build comfort payload (null-object pattern)
          const comfortObj = {}
          const comfortQuestions = [
            'How comfortable is the position of the mask on the nose?',
            'Is there enough room to talk?',
            'How comfortable is the position of the mask on face and cheeks?'
          ]
          comfortQuestions.forEach(q => {
            const csvVal = (q === comfortQuestions[0]) ? row.comfortNoseFile
              : (q === comfortQuestions[1]) ? row.comfortTalkFile
              : row.comfortFaceFile
            let mapped = null
            if (csvVal && this.comfortMatching && this.comfortMatching[q]) {
              mapped = this.comfortMatching[q][csvVal] || null
            }
            comfortObj[q] = mapped
          })
          payload.comfort = comfortObj
          return payload
        })

        const response = await axios.post(
          `/bulk_fit_tests_imports/${this.bulkFitTestsImportId}/complete_import.json`,
          {
            fit_tests_data: fitTestsData,
            fit_tests_to_add: this.fitTestDataRows.length // Count before filtering
          }
        )

        if (response.status === 200) {
          // Update local state
          this.bulkImportStatus = 'completed'

          // Reload bulk import to get updated status
          await this.loadBulkImport()

          this.messages = [
            { str: `Successfully imported ${fitTestsData.length} fit test(s).` },
          ]
          this.showGoToBulkImports = true

          // Optionally redirect to list view or show success message
        } else {
          const errorMessages = response.data.messages || ['Failed to import fit tests.']
          this.messages = errorMessages.map(msg => ({ str: msg }))
        }
      } catch (error) {
        // Handle authentication errors
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          this.redirectToSignIn()
          return
        }

        const errorMsg = error.response?.data?.messages?.[0] || error.message || 'Failed to import fit tests.'
        this.messages = [{ str: errorMsg }]
      } finally {
        this.isSaving = false
      }
    },
    completeImportOld() {
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
  max-width: 70vw;
}

.text-align-center {
  text-align: center;
}

.tagline {
  text-align: center;
  font-weight: bold;
  margin-left: 300px;
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

.match-button {
  max-width: 1em;
}
.display {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.match-confirmation-content {
  padding: 1em;
}

.match-confirmation-content h3 {
  margin-top: 0;
}

.match-overwrites-list {
  list-style-type: none;
  padding-left: 0;
  margin: 1em 0;
}

.match-overwrites-list li {
  padding: 0.5em;
  margin: 0.5em 0;
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
}

.match-confirmation-buttons {
  display: flex;
  gap: 1em;
  justify-content: center;
  margin-top: 1.5em;
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
  position: sticky;
  top: 0;
  z-index: 10;
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

.similarity-score-cell {
  text-align: center;
  vertical-align: middle;
  min-width: 120px;
}

.validation-errors {
  margin-top: 1em;
  margin-bottom: 1em;
}

.column-matching-table tr.has-duplicate-error {
  background-color: #fff5f5;
}

.column-matching-table tr.has-duplicate-error td {
  border-color: #fc8181;
}

.column-select.has-error {
  border-color: #e53e3e;
  background-color: #fff5f5;
}

.column-select.has-error:focus {
  outline-color: #e53e3e;
  border-color: #e53e3e;
}

.similarity-score {
  font-weight: 500;
  color: #28a745;
}

.similarity-score-empty {
  color: #6c757d;
  font-style: italic;
}

.column-matching-table tbody tr:hover {
  background-color: #f8f9fa;
}

.user-matching-header {
  margin-top: 1em;
  margin-bottom: 1em;
}

.user-matching-table {
  margin-top: 2em;
  overflow-y: scroll;
}

.user-matching-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

.user-matching-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.user-matching-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.user-select {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.user-matching-table tr.has-error {
  background-color: #fff5f5;
}

.user-matching-table tr.has-error td {
  border-color: #fc8181;
}

.error-text {
  color: #e53e3e;
  font-weight: bold;
}

.mask-matching-header {
  margin-top: 1em;
  margin-bottom: 1em;
}

.content {
  max-height: 40vh;
  overflow-y: auto;
  overflow-x: auto;
}

.mask-matching-table {
  margin-top: 2em;
}

.mask-matching-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

.mask-matching-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.mask-matching-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.mask-select {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.mask-matching-table tbody tr:hover {
  background-color: #f8f9fa;
}

.testing-mode-matching-header {
  margin-bottom: 1em;
  display: flex;
  justify-content: flex-start;
}

.testing-mode-matching-table {
  margin-top: 2em;
}

.testing-mode-matching-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

.testing-mode-matching-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.testing-mode-matching-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.testing-mode-select {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.testing-mode-matching-table tbody tr:hover {
  background-color: #f8f9fa;
}

.qlft-values-matching-header {
  margin-bottom: 1em;
  display: flex;
  justify-content: flex-start;
}

.qlft-values-matching-table {
  margin-top: 2em;
}

.qlft-values-matching-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
}

.qlft-values-matching-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.qlft-values-matching-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.qlft-values-select {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.9em;
}

.qlft-values-matching-table tbody tr:hover {
  background-color: #f8f9fa;
}

.qlft-unmapped-warning {
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  padding: 1em;
  margin: 1em 0;
  color: #856404;
}

.qlft-unmapped-value {
  background-color: #f8d7da;
  color: #721c24;
  font-weight: bold;
}

.fit-test-data-table {
  margin-top: 2em;
}

.fit-test-data-table table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1em;
  min-width: 1000px;
}

.fit-test-data-table th {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 0.75em;
  text-align: left;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.fit-test-data-table td {
  border: 1px solid #dee2e6;
  padding: 0.75em;
}

.fit-test-data-table tbody tr:hover {
  background-color: #f8f9fa;
}

.mask-id-link {
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
}

.mask-id-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.user-id-link {
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
}

.user-id-link:hover {
  color: #0056b3;
  text-decoration: underline;
}

.user-name-error {
  color: #dc3545;
  font-weight: bold;
}

@media (max-width: 1000px) {
  .columns {
    flex-direction: column;
  }

  .right-pane {
    margin-left: 0;
  }

  .tagline {
    margin-left: 0;
  }
}
</style>
