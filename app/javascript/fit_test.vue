<template>
  <div class='align-items-center flex-dir-col top-container'>
    <div class='flex align-items-center row phone'>
      <h2 class='tagline'>{{pageTitle}}</h2>
    </div>


    <div class='container chunk'>
      <ClosableMessage @onclose='messages = []' :messages='messages'/>
      <br>
    </div>

    <!-- Progress Component -->
    <div class='columns'>
      <AddingDataToFitTestProgress
        :selectedUser="selectedUser"
        :selectedMask="selectedMask"
        :facialHair="facialHair"
        :userSealCheck="userSealCheck"
        :qualitativeProcedure="qualitativeProcedure"
        :quantitativeProcedure="quantitativeProcedure"
        :fitTestProcedure="fitTestProcedure"
        :comfort="comfort"
        :hasExistingFitTestUser="hasExistingFitTestUser"
        :hasFitTestData="hasFitTestData"
        :completedSteps="completedFitTestSteps"
        :currentStep="tabToShow"
        @navigate-to-step="navigateToStep"
      />

      <div v-show='tabToShow == "User"' class='right-pane narrow-width'>
        <div>
          <div class='title-row'>
            <h2 class='title-row-item text-align-center'>User selection</h2>
            <div class='title-row-item mode-buttons'>
              <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
              <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
            </div>
          </div>
          <h3 class='text-align-center'>Search for user</h3>

          <div class='row justify-content-center'>
            <input type="text" @change='updateSearch($event, "user")' :disabled='!createOrEdit'>
            <SearchIcon height='2em' width='2em'/>
          </div>

          <h3 v-show="userDisplayables.length == 0" class='text-align-center'>Not able to find the user?
            <router-link :to="{name: 'RespiratorUsers'}"> Click here to add user information. </router-link>
          </h3>


          <div :class='{main: true}'>
            <div class='text-row pointable flex flex-dir-col align-items-center justify-content-center' v-for='u in userDisplayables' @click='selectUser(u.managedId)'>
              <div class='description'>
                <span>
                  {{u.firstName + ' ' + u.lastName}}
                </span>
              </div>
            </div>
          </div>

          <table>
            <tbody>
              <tr>
                <th>Selected User</th>
                <td>{{ selectedUser ? selectedUser.fullName : '' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>

      <div v-show='tabToShow == "Mask"' class='main right-pane'>

        <div>
          <div class='title-row'>
            <h2 class='header title-row-item'>Mask Selection</h2>
            <div class='mode-buttons title-row-item'>
              <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
              <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
            </div>
          </div>

          <div class='row justify-content-center'>
            <input type="text" :value='selectedMask && selectedMask.uniqueInternalModelCode' @change='updateSearch($event, "mask")' :disabled='!createOrEdit' placeholder='Search for mask'>
            <SearchIcon height='2em' width='2em'/>
          </div>

          <h3 v-show="selectMaskDisplayables.length == 0" class='text-align-center'>Not able to find the mask?
            <router-link :to="{name: 'NewMask'}"> Click here to add information about the mask. </router-link>
          </h3>

          <Pagination
            :currentPage="maskCurrentPage"
            :perPage="maskPerPage"
            :totalCount="maskTotalCount"
            itemName="masks"
            @page-change="handleMaskPageChange"
          />

          <div :class='{main: true, grid: true, selectedMask: true, oneCol: maskDisplayables.length == 1}'>
            <div class='card pointable flex flex-dir-col align-items-center justify-content-center' v-for='m in selectMaskDisplayables' @click='selectMask(m.id)'>
              <img :src="m.imageUrls[0]" alt="" class='thumbnail'>
              <div class='description'>
                <span>
                  {{m.uniqueInternalModelCode}}
                </span>
              </div>
            </div>
          </div>

          <Pagination
            :currentPage="maskCurrentPage"
            :perPage="maskPerPage"
            :totalCount="maskTotalCount"
            itemName="masks"
            @page-change="handleMaskPageChange"
          />

          <table>
            <tbody>
              <tr>
                <th>Selected Mask</th>
                <td>{{selectedMask && selectedMask.uniqueInternalModelCode}}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>

      <div v-show='tabToShow == "Facial Hair"' class='flex-dir-col align-content-center right-pane'>
        <div class='title-row'>
          <h2 class='text-align-center title-row-item'>Facial Hair Check</h2>
          <div class='mode-buttons title-row-item'>
            <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
            <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          </div>
        </div>

        <p class='narrow-p'>Having a beard can increase seal leakage. If you don't have one, please select "0mm" for the following question. If you do have one, please use a caliper or tape measure to estimate beard length.</p>

        <SurveyQuestion
          question="How long is your beard?"
          :answer_options="beardLengthOptions"
          @update="selectBeardLength"
          :selected="facialHair['beard_length_mm']"
          :disabled="!createOrEdit"
        />

        <p class='narrow-p'>Beard Cover Technique: To improve the seal for those with beards without shaving or trimming the beard itself, one could cover the beard with an elastic band, as shown <a href="https://www.youtube.com/watch?v=pBMSydda5WY">in this video</a>.
        </p>

        <SurveyQuestion
          question="If you do have a beard, are you using the beard cover technique?"
          :answer_options="['Yes', 'No', 'Not applicable']"
          @update="selectBeardCoverTechnique"
          :selected="facialHair['beard_cover_technique']"
          :disabled="!createOrEdit"
        />

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>



      <div v-show='tabToShow == "User Seal Check"' class='flex-dir-col align-content-center right-pane'>
        <div class='title-row'>
          <h2 class='text-align-center title-row-item'>User Seal Check</h2>
          <div class='mode-buttons title-row-item'>
            <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
            <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          </div>
        </div>
        <div>
          <SurveyQuestion
              question="What do you think about the sizing of this mask relative to your face?"
              :answer_options="['Too big', 'Somewhere in-between too small and too big', 'Too small']"
              @update="selectSizingUserSealCheck"
              :selected="userSealCheck['sizing']['What do you think about the sizing of this mask relative to your face?']"
              :disabled="!createOrEdit"
              />
        </div>

        <a class='text-align-center' href="//cdc.gov/niosh/docs/2018-130/pdfs/2018-130.pdf" target='_blank'>What are user seal checks?</a>
        <div v-show="showPositiveUserSealCheck">
          <h4>While performing a *positive-pressure* user seal check, </h4>

          <SurveyQuestion
              question="...how much air movement on your face along the seal of the mask did you feel?"
              :answer_options="['A lot of air movement', 'Some air movement', 'No air movement']"
              @update="selectPositivePressureAirMovement"
              :selected="userSealCheck['positive']['...how much air movement on your face along the seal of the mask did you feel?']"
              :disabled="!createOrEdit"
              />
        </div>

        <div v-show="!showPositiveUserSealCheck">
          <h4>While performing a *negative-pressure* user seal check, </h4>
          <SurveyQuestion
              question="...how much air passed between your face and the mask?"
              :answer_options="['A lot of air', 'Some air', 'Unnoticeable']"
              @update="selectNegativePressureAirMovement"
              :selected="userSealCheck['negative']['...how much air passed between your face and the mask?']"
              :disabled="!createOrEdit"
              />
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>
      </div>

      <div v-show='tabToShow == "Fit Test"' class='flex-dir-col align-content-center right-pane'>
        <div class='title-row'>
          <h2 class='text-align-center title-row-item'>Fit Test</h2>
          <div class='mode-buttons title-row-item'>
            <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
            <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          </div>
        </div>

        <div class='menu row'>
          <TabSet
            v-if='tabToShow == "Fit Test"'
            :options='secondaryTabToShowOptions'
            @update='setSecondaryTab'
            :tabToShow='secondaryTabToShow'
          />
        </div>


        <div v-show='secondaryTabToShow == "Choose Procedure"'>
          <p v-if='!fitTestProcedure' class='text-align-center'>Please select a fit testing procedure</p>

          <table>
            <tbody>
              <tr>
                <th>Procedure</th>
                <td>
                  <select v-model='fitTestProcedure' @change='onFitTestProcedureChange' :disabled='!createOrEdit'>
                    <option :value='null'>-- Select --</option>
                    <option value='qualitative_full_osha'>qualitative: Full OSHA</option>
                    <option value='quantitative_osha_fast'>quantitative: OSHA Fast Face Piece Respirators</option>
                    <option value='quantitative_full_osha'>quantitative: Full OSHA</option>
                  </select>
                </td>
              </tr>

              <!-- Instructions row -->
              <tr v-if='fitTestProcedure && aerosol'>
                <th>Instructions</th>
                <td>
                  <CircularButton text="?" @click="showInstructions" />
                </td>
              </tr>

              <!-- Qualitative fields -->
              <template v-if='fitTestProcedure === "qualitative_full_osha"'>
                <tr>
                  <th>Solution</th>
                  <td>
                    <select v-model='qualitativeAerosolSolution' :disabled='!createOrEdit'>
                      <option>Saccharin</option>
                      <option>Bitrex</option>
                    </select>
                  </td>
                </tr>
              </template>

              <!-- Quantitative fields -->
              <template v-if='fitTestProcedure && fitTestProcedure.startsWith("quantitative")'>
                <tr>
                  <th>Testing mode</th>
                  <td>
                    <select v-model='quantitativeTestingMode' :disabled='!createOrEdit'>
                      <option>N95</option>
                      <option>N99</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <th>Aerosol</th>
                  <td>
                    <select v-model='quantitativeAerosolSolution' :disabled='!createOrEdit'>
                      <option>Ambient</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <th>Initial count (particles / cm3)</th>
                  <td>
                    <input type='number' v-model='initialCountPerCm3' :disabled='!createOrEdit'>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <!-- Results tab -->
        <div v-show='secondaryTabToShow == "Results" && fitTestProcedure'>
          <!-- Qualitative exercises -->
          <template v-if='fitTestProcedure === "qualitative_full_osha"'>
            <table>
              <tbody>
                <template v-for='(ex, index) in qualitativeExercises' :key='index'>
                  <tr>
                    <th>{{ex.name}}</th>
                    <td>
                      <CircularButton text="?" @click="showDescription(ex.name)"/>
                    </td>
                    <td>
                      <select v-model='ex.result' :disabled='!createOrEdit'>
                        <option>Pass</option>
                        <option>Fail</option>
                        <option>Not applicable</option>
                      </select>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </template>

          <!-- Quantitative exercises -->
          <template v-if='fitTestProcedure && fitTestProcedure.startsWith("quantitative")'>
            <table>
              <tbody>
                <template v-for='(ex, index) in quantitativeExercises' :key='index'>
                  <tr>
                    <th>{{ex.name}}</th>
                    <td>
                      <CircularButton text="?" @click="showDescription(ex.name)"/>
                    </td>
                    <td>
                      <input type="number" v-model='ex.fit_factor' :disabled='!createOrEdit' placeholder='Fit factor'>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </template>
        </div>

        <!-- Notes tab -->
        <div v-show='secondaryTabToShow == "Notes" && fitTestProcedure'>
          <table>
            <tbody>
              <tr>
                <th>Notes</th>
                <td>
                  <textarea
                    v-if='fitTestProcedure === "qualitative_full_osha"'
                    v-model='qualitativeAerosolNotes'
                    :disabled='!createOrEdit'
                    cols="30"
                    rows="10">
                  </textarea>
                  <textarea
                    v-else
                    v-model='quantitativeAerosolNotes'
                    :disabled='!createOrEdit'
                    cols="30"
                    rows="10">
                  </textarea>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>
      </div>

      <div v-show='tabToShow == "Comfort"' class='flex-dir-col right-pane'>
        <div class='title-row'>
          <h2 class='text-align-center title-row-item'>Comfort Assessment</h2>
          <div class='mode-buttons title-row-item'>
            <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
            <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          </div>
        </div>

        <SurveyQuestion
          question="How comfortable is the position of the mask on the nose?"
          :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
          @update="selectComfortNose"
          :selected="comfort['How comfortable is the position of the mask on the nose?']"
          :disabled="!createOrEdit"
        />

        <SurveyQuestion
          question="Is there enough room to talk?"
          :answer_options="['Not enough', 'Unsure', 'Enough']"
          @update="selectComfortEnoughRoomToTalk"
          :selected="comfort['Is there enough room to talk?']"
          :disabled="!createOrEdit"
        />

        <SurveyQuestion
          question="How comfortable is the position of the mask on face and cheeks?"
          :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
          @update="selectComfortFaceAndCheeks"
          :selected="comfort['How comfortable is the position of the mask on face and cheeks?']"
          :disabled="!createOrEdit"
        />

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import Button from './button.vue'
import CircularButton from './circular_button.vue'
import ClosableMessage from './closable_message.vue'
import TabSet from './tab_set.vue'
import { deepSnakeToCamel, setupCSRF } from './misc.js'
import SearchIcon from './search_icon.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { RespiratorUser } from './respirator_user.js';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';
import { useManagedUserStore } from './stores/managed_users_store';
import { useMeasurementDeviceStore } from './stores/measurement_devices_store';
import { FitTest } from './fit_testing.js'
import AddingDataToFitTestProgress from './adding_data_to_fit_test_progress.vue'
import Pagination from './pagination.vue'

export default {
  name: 'FitTest',
  components: {
    AddingDataToFitTestProgress,
    Button,
    CircularButton,
    ClosableMessage,
    Pagination,
    SearchIcon,
    SurveyQuestion,
    TabSet
  },
  data() {
    return {
      id: 0,
      mode: 'View',
      initialCountPerCm3: null,
      quantitativeProcedure: null,
      quantitativeFitTestingDeviceId: null,
      quantitativeTestingMode: 'N99',
      facialHair: {
        beard_length_mm: '0mm',
        beard_cover_technique: 'No',
      },
      beardLengthOptions: [
        '0mm', '1.5mm', '3mm', '6mm', '9mm', '>10mm'
      ],
      selectedPressureCheckOption: 'Positive',
      pressureCheckOptions: [
        {
          'text': 'Positive',
        },
        {
          'text': 'Negative',
        }
      ],
      tabToShow: 'User',
      secondaryTabToShow: 'Choose Procedure',
      secondaryTabToShowOptions: [
        {
          text: 'Choose Procedure'
        },
        {
          text: 'Results'
        },
        {
          text: 'Notes'
        },
      ],
      tabToShowOptions: [
        {
          text: "User",
        },
        {
          text: "Mask",
        },
        {
          text: "Facial Hair"
        },
        {
          text: "User Seal Check"
        },
        {
          text: "Fit Test"
        },
        {
          text: "Comfort",
        },
      ],
      fitTestProcedure: null, // 'qualitative_full_osha', 'quantitative_osha_fast', 'quantitative_full_osha'
      oshaFastFFRExercises: {
        'Bending over': {
          'description': 'The test subject shall bend at the waist, as if going to touch his/her toes for 50 seconds and inhale 2 times at the bottom.',
        },
        'Talking': {
          'description': 'The subject shall talk out loud slowly and loud enough so as to be heard clearly by the test conductor. The subject can read from a prepared text such as the Rainbow Passage, count backward from 100, or recite a memorized poem or song.  Rainbow Passage: When the sunlight strikes raindrops in the air, they act like a prism and form a rainbow. The rainbow is a division of white light into many beautiful colors. These take the shape of a long round arch, with its path high above, and its two ends apparently beyond the horizon. There is, according to legend, a boiling pot of gold at one end. People look, but no one ever finds it. When a man looks for something beyond reach, his friends say he is looking for the pot of gold at the end of the rainbow.'
        },
        'Turning head side to side': {
          'description': "The test subject shall stand in place, slowly turning his/her head from side to side for 30 seconds and inhale 2 times at each extreme."
        },
        'Moving head up and down': {
          'description': "The test subject shall stand in place, slowly moving his/her head up and down for 39 seconds and inhale 2 times at each extreme."
        },
        'Normal breathing (SEALED)': {
          'description': 'The purpose of this exercise is to get an estimate of filtration efficiency of the mask material. The test subject shall seal the mask to their face using their hands as best as they can. For each hand, the tester can create a letter C. With the thumb and pointer finger holding the C position, squeeze the edges of the mask to the face. If the test subject feels that all air is going through the filter (i.e. no gaps), then you can enter the associated fit factor here. Otherwise, leave blank'
        }
      },
      oshaExercises: {
        'Normal breathing': {
          'description': 'In a normal standing position, without talking, the subject shall breathe normally.'
        },
        'Deep breathing': {
          'description': 'In a normal standing position, the subject shall breathe slowly and deeply, taking caution so as not to hyperventilate.'
        },
        'Turning head side to side': {
          'description': 'Standing in place, the subject shall slowly turn his/her head from side to side between the extreme positions on each side. The head shall be held at each extreme momentarily so the subject can inhale at each side.'
        },

        'Moving head up and down': {
          'description': 'Standing in place, the subject shall slowly move his/her head up and down. The subject shall be instructed to inhale in the up position (i.e., when looking toward the ceiling).'
        },
        'Talking': {
          'description': 'The subject shall talk out loud slowly and loud enough so as to be heard clearly by the test conductor. The subject can read from a prepared text such as the Rainbow Passage, count backward from 100, or recite a memorized poem or song.  Rainbow Passage: When the sunlight strikes raindrops in the air, they act like a prism and form a rainbow. The rainbow is a division of white light into many beautiful colors. These take the shape of a long round arch, with its path high above, and its two ends apparently beyond the horizon. There is, according to legend, a boiling pot of gold at one end. People look, but no one ever finds it. When a man looks for something beyond reach, his friends say he is looking for the pot of gold at the end of the rainbow.'
        },
        'Grimace': {
          'description': 'The test subject shall grimace by smiling or frowning. (This applies only to QNFT testing; it is not performed for QLFT)',
        },
        'Bending over': {
          'description': 'The test subject shall bend at the waist as if he/she were to touch his/her toes. Jogging in place shall be substituted for this exercise in those test environments such as shroud type QNFT or QLFT units that do not permit bending over at the waist.',
        },
        'Normal breathing (SEALED)': {
          'description': 'The purpose of this exercise is to get an estimate of filtration efficiency of the mask material. The test subject shall seal the mask to their face using their hands as best as they can. For each hand, the tester can create a letter C. With the thumb and pointer finger holding the C position, squeeze the edges of the mask to the face. If the test subject feels that all air is going through the filter (i.e. no gaps), then you can enter the associated fit factor here. Otherwise, leave blank'
        }
      },
      fitTestingInstructions: {
        QNFT: {
          'Ambient': {
            'title': 'AMBIENT AEROSOL CONDENSATION NUCLEI COUNTER (CNC) QUANTITATIVE FIT TESTING PROTOCOL.',
            'paragraphs': [
              "The ambient aerosol condensation nuclei counter (CNC) quantitative fit testing (PortaCount®) protocol quantitatively fit tests respirators with the use of a probe. The probed respirator is only used for quantitative fit tests. A probed respirator has a special sampling device, installed on the respirator, that allows the probe to sample the air from inside the mask. A probed respirator is required for each make, style, model, and size that the employer uses and can be obtained from the respirator manufacturer or distributor. The primary CNC instrument manufacturer, TSI Incorporated, also provides probe attachments (TSI mask sampling adapters) that permit fit testing in an employee's own respirator. A minimum fit factor pass level of at least 100 is necessary for a half-mask respirator (elastomeric or filtering facepiece), and a minimum fit factor pass level of at least 500 is required for a full-facepiece elastomeric respirator. The entire screening and testing procedure shall be explained to the test subject prior to the conduct of the screening test.",

              "(a) PortaCount® Fit Test Requirements. (1) Check the respirator to make sure the sampling probe and line are properly attached to the facepiece and that the respirator is fitted with a particulate filter capable of preventing significant penetration by the ambient particles used for the fit test (e.g., NIOSH 42 CFR 84 series 100, series 99, or series 95 particulate filter) per manufacturer's instruction.",

              "(2) Instruct the person to be tested to don the respirator for five minutes before the fit test starts. This purges the ambient particles trapped inside the respirator and permits the wearer to make certain the respirator is comfortable. This individual shall already have been trained on how to wear the respirator properly.",

              "(3) Check the following conditions for the adequacy of the respirator fit: Chin properly placed; Adequate strap tension, not overly tightened; Fit across nose bridge; Respirator of proper size to span distance from nose to chin; Tendency of the respirator to slip; Self-observation in a mirror to evaluate fit and respirator position.",

              "(4) Have the person wearing the respirator do a user seal check. If leakage is detected, determine the cause. If leakage is from a poorly fitting facepiece, try another size of the same model respirator, or another model of respirator.",

              "(5) Follow the manufacturer's instructions for operating the Portacount® and proceed with the test.",

              "(6) The test subject shall be instructed to perform the exercises in section I. A. 14. of this appendix.",

              "(7) After the test exercises, the test subject shall be questioned by the test conductor regarding the comfort of the respirator upon completion of the protocol. If it has become unacceptable, another model of respirator shall be tried.",

              "(b) PortaCount® Test Instrument.",

              "(1) The PortaCount® will automatically stop and calculate the overall fit factor for the entire set of exercises. The overall fit factor is what counts. The Pass or Fail message will indicate whether or not the test was successful. If the test was a Pass, the fit test is over.",

              "(2) Since the pass or fail criterion of the PortaCount® is user programmable, the test operator shall ensure that the pass or fail criterion meet the requirements for minimum respirator performance in this Appendix.",

              "(3) A record of the test needs to be kept on file, assuming the fit test was successful. The record must contain the test subject's name; overall fit factor; make, model, style, and size of respirator used; and date tested.",
            ]
          }
        },
        QLFT: {
          Saccharin: {
            'title': 'SACCHARIN SOLUTION AEROSOL PROTOCOL',
            paragraphs: [
              'The entire screening and testing procedure shall be explained to the test subject prior to the conduct of the screening test.',

              '(a) Taste threshold screening. The saccharin taste threshold screening, performed without wearing a respirator, is intended to determine whether the individual being tested can detect the taste of saccharin.',

              '(1) During threshold screening as well as during fit testing, subjects shall wear an enclosure about the head and shoulders that is approximately 12 inches in diameter by 14 inches tall with at least the front portion clear and that allows free movements of the head when a respirator is worn. An enclosure substantially similar to the 3M hood assembly, parts # FT 14 and # FT 15 combined, is adequate.',

              "(2) The test enclosure shall have a 3⁄4 -inch (1.9 cm) hole in front of the test subject's nose and mouth area to accommodate the nebulizer nozzle.",

              '(3) The test subject shall don the test enclosure. Throughout the threshold screening test, the test subject shall breathe through his/her slightly open mouth with tongue extended. The subject is instructed to report when he/she detects a sweet taste.',

              '(4) Using a DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent, the test conductor shall spray the threshold check solution into the enclosure. The nozzle is directed away from the nose and mouth of the person. This nebulizer shall be clearly marked to distinguish it from the fit test solution nebulizer.',

              '(5) The threshold check solution is prepared by dissolving 0.83 gram of sodium saccharin USP in 100 ml of warm water. It can be prepared by putting 1 ml of the fit test solution (see (b)(5) below) in 100 ml of distilled water.',

              '(6) To produce the aerosol, the nebulizer bulb is firmly squeezed so that it collapses completely, then released and allowed to fully expand.',

              '(7) Ten squeezes are repeated rapidly and then the test subject is asked whether the saccharin can be tasted. If the test subject reports tasting the sweet taste during the ten squeezes, the screening test is completed. The taste threshold is noted as ten regardless of the number of squeezes actually completed.',

              '(8) If the first response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the saccharin is tasted. If the test subject reports tasting the sweet taste during the second ten squeezes, the screening test is completed. The taste threshold is noted as twenty regardless of the number of squeezes actually completed.',

              '(9) If the second response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the saccharin is tasted. If the test subject reports tasting the sweet taste during the third set of ten squeezes, the screening test is completed. The taste threshold is noted as thirty regardless of the number of squeezes actually completed.',

              '(10) The test conductor will take note of the number of squeezes required to solicit a taste response.',

              '(11) If the saccharin is not tasted after 30 squeezes (step 10), the test subject is unable to taste saccharin and may not perform the saccharin fit test.',

              'Note to paragraph 3(a): If the test subject eats or drinks something sweet before the screening test, he/she may be unable to taste the weak saccharin solution.',

              '(12) If a taste response is elicited, the test subject shall be asked to take note of the taste for reference in the fit test.',

              '(13) Correct use of the nebulizer means that approximately 1 ml of liquid is used at a time in the nebulizer body.',

              '(14) The nebulizer shall be thoroughly rinsed in water, shaken dry, and refilled at least each morning and afternoon or at least every four hours.',

              '(b) Saccharin solution aerosol fit test procedure.',

              '(1) The test subject may not eat, drink (except plain water), smoke, or chew gum for 15 minutes before the test.',

              '(2) The fit test uses the same enclosure described in 3. (a) above.',

              '(3) The test subject shall don the enclosure while wearing the respirator selected in section I. A. of this appendix. The respirator shall be properly adjusted and equipped with a particulate filter(s).',

              '(4) A second DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent is used to spray the fit test solution into the enclosure. This nebulizer shall be clearly marked to distinguish it from the screening test solution nebulizer.',

              '(5) The fit test solution is prepared by adding 83 grams of sodium saccharin to 100 ml of warm water.',

              '(6) As before, the test subject shall breathe through the slightly open mouth with tongue extended, and report if he/she tastes the sweet taste of saccharin.',

              '(7) The nebulizer is inserted into the hole in the front of the enclosure and an initial concentration of saccharin fit test solution is sprayed into the enclosure using the same number of squeezes (either 10, 20 or 30 squeezes) based on the number of squeezes required to elicit a taste response as noted during the screening test. A minimum of 10 squeezes is required.',

              '(8) After generating the aerosol, the test subject shall be instructed to perform the exercises in section I. A. 14. of this appendix.',

              '(9) Every 30 seconds the aerosol concentration shall be replenished using one half the original number of squeezes used initially (e.g., 5, 10 or 15).',

              '(10) The test subject shall indicate to the test conductor if at any time during the fit test the taste of saccharin is detected. If the test subject does not report tasting the saccharin, the test is passed.',

              '(11) If the taste of saccharin is detected, the fit is deemed unsatisfactory and the test is failed. A different respirator shall be tried and the entire test procedure is repeated (taste threshold screening and fit testing).',

              '(12) Since the nebulizer has a tendency to clog during use, the test operator must make periodic checks of the nebulizer to ensure that it is not clogged. If clogging is found at the end of the test session, the test is invalid.',
            ],
          },
            Bitrex: {
              title: ' BITREX™ (DENATONIUM BENZOATE) SOLUTION AEROSOL QUALITATIVE FIT TEST PROTOCOL',
              paragraphs: [
                "The Bitrex™ (Denatonium benzoate) solution aerosol QLFT protocol uses the published saccharin test protocol because that protocol is widely accepted. Bitrex is routinely used as a taste aversion agent in household liquids which children should not be drinking and is endorsed by the American Medical Association, the National Safety Council, and the American Association of Poison Control Centers. The entire screening and testing procedure shall be explained to the test subject prior to the conduct of the screening test.",

                "(a) Taste Threshold Screening.",

                "The Bitrex taste threshold screening, performed without wearing a respirator, is intended to determine whether the individual being tested can detect the taste of Bitrex.",

                "(1) During threshold screening as well as during fit testing, subjects shall wear an enclosure about the head and shoulders that is approximately 12 inches (30.5 cm) in diameter by 14 inches (35.6 cm) tall. The front portion of the enclosure shall be clear from the respirator and allow free movement of the head when a respirator is worn. An enclosure substantially similar to the 3M hood assembly, parts # FT 14 and # FT 15 combined, is adequate.",

                "(2) The test enclosure shall have a 3⁄4 inch (1.9 cm) hole in front of the test subject's nose and mouth area to accommodate the nebulizer nozzle.",

                "(3) The test subject shall don the test enclosure. Throughout the threshold screening test, the test subject shall breathe through his or her slightly open mouth with tongue extended. The subject is instructed to report when he/she detects a bitter taste.",

                "(4) Using a DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent, the test conductor shall spray the Threshold Check Solution into the enclosure. This Nebulizer shall be clearly marked to distinguish it from the fit test solution nebulizer.",

                "(5) The Threshold Check Solution is prepared by adding 13.5 milligrams of Bitrex to 100 ml of 5% salt (NaCl) solution in distilled water.",

                "(6) To produce the aerosol, the nebulizer bulb is firmly squeezed so that the bulb collapses completely, and is then released and allowed to fully expand.",

                "(7) An initial ten squeezes are repeated rapidly and then the test subject is asked whether the Bitrex can be tasted. If the test subject reports tasting the bitter taste during the ten squeezes, the screening test is completed. The taste threshold is noted as ten regardless of the number of squeezes actually completed.",

                "(8) If the first response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the Bitrex is tasted. If the test subject reports tasting the bitter taste during the second ten squeezes, the screening test is completed. The taste threshold is noted as twenty regardless of the number of squeezes actually completed.",

                "(9) If the second response is negative, ten more squeezes are repeated rapidly and the test subject is again asked whether the Bitrex is tasted. If the test subject reports tasting the bitter taste during the third set of ten squeezes, the screening test is completed. The taste threshold is noted as thirty regardless of the number of squeezes actually completed.",

                "(10) The test conductor will take note of the number of squeezes required to solicit a taste response.",

                "(11) If the Bitrex is not tasted after 30 squeezes (step 10), the test subject is unable to taste Bitrex and may not perform the Bitrex fit test.",

                "(12) If a taste response is elicited, the test subject shall be asked to take note of the taste for reference in the fit test.",

                "(13) Correct use of the nebulizer means that approximately 1 ml of liquid is used at a time in the nebulizer body.",

                "(14) The nebulizer shall be thoroughly rinsed in water, shaken to dry, and refilled at least each morning and afternoon or at least every four hours.",

                "(b) Bitrex Solution Aerosol Fit Test Procedure.",

                "(1) The test subject may not eat, drink (except plain water), smoke, or chew gum for 15 minutes before the test.",

                "(2) The fit test uses the same enclosure as that described in 4. (a) above.",

                "(3) The test subject shall don the enclosure while wearing the respirator selected according to section I. A. of this appendix. The respirator shall be properly adjusted and equipped with any type particulate filter(s).",

                "(4) A second DeVilbiss Model 40 Inhalation Medication Nebulizer or equivalent is used to spray the fit test solution into the enclosure. This nebulizer shall be clearly marked to distinguish it from the screening test solution nebulizer.",

                "(5) The fit test solution is prepared by adding 337.5 mg of Bitrex to 200 ml of a 5% salt (NaCl) solution in warm water.",

                "(6) As before, the test subject shall breathe through his or her slightly open mouth with tongue extended, and be instructed to report if he/she tastes the bitter taste of Bitrex.",

                "(7) The nebulizer is inserted into the hole in the front of the enclosure and an initial concentration of the fit test solution is sprayed into the enclosure using the same number of squeezes (either 10, 20 or 30 squeezes) based on the number of squeezes required to elicit a taste response as noted during the screening test.",

                "(8) After generating the aerosol, the test subject shall be instructed to perform the exercises in section I. A. 14. of this appendix.",

                "(9) Every 30 seconds the aerosol concentration shall be replenished using one half the number of squeezes used initially (e.g., 5, 10 or 15).",

                "(10) The test subject shall indicate to the test conductor if at any time during the fit test the taste of Bitrex is detected. If the test subject does not report tasting the Bitrex, the test is passed.",

                "(11) If the taste of Bitrex is detected, the fit is deemed unsatisfactory and the test is failed. A different respirator shall be tried and the entire test procedure is repeated (taste threshold screening and fit testing).",

              ],
            }
        }
      },
      masks: [],
      qualitativeProcedure: null,
      qualitativeAerosolSolution: 'Saccharin',
      qualitativeAerosolNotes: '',
      quantitativeAerosolSolution: 'Ambient',
      quantitativeAerosolProcedure: 'Not applicable',
      quantitativeAerosolInitialCount: 0,
      quantitativeAerosolNotes: '',
      originalQualitativeExercises: [
        {
          name: 'Normal breathing',
          result: null
        },
        {
          name: 'Deep breathing',
          result: null
        },
        {
          name: 'Turning head side to side',
          result: null
        },
        {
          name: 'Moving head up and down',
          result: null
        },
        {
          name: 'Talking',
          result: null
        },
        {
          name: 'Bending over',
          result: null
        },
        {
          name: 'Normal breathing',
          result: null
        }
      ],
      qualitativeExercises: [
        {
          name: 'Normal breathing',
          result: null
        },
        {
          name: 'Deep breathing',
          result: null
        },
        {
          name: 'Turning head side to side',
          result: null
        },
        {
          name: 'Moving head up and down',
          result: null
        },
        {
          name: 'Talking',
          result: null
        },
        {
          name: 'Bending over',
          result: null
        },
        {
          name: 'Normal breathing',
          result: null
        }
      ],
      originalQuantitativeExercises: [
        {
          name: 'Normal breathing',
          fit_factor: null
        },
        {
          name: 'Deep breathing',
          fit_factor: null
        },
        {
          name: 'Turning head side to side',
          fit_factor: null
        },
        {
          name: 'Moving head up and down',
          fit_factor: null
        },
        {
          name: 'Talking',
          fit_factor: null
        },
        {
          name: 'Grimace',
          fit_factor: null
        },
        {
          name: 'Bending over',
          fit_factor: null
        },
        {
          name: 'Normal breathing',
          fit_factor: null
        }
      ],
      quantitativeExercisesFullOsha: [
        {
          name: 'Normal breathing',
          fit_factor: null
        },
        {
          name: 'Deep breathing',
          fit_factor: null
        },
        {
          name: 'Turning head side to side',
          fit_factor: null
        },
        {
          name: 'Moving head up and down',
          fit_factor: null
        },
        {
          name: 'Talking',
          fit_factor: null
        },
        {
          name: 'Grimace',
          fit_factor: null
        },
        {
          name: 'Bending over',
          fit_factor: null
        },
        {
          name: 'Normal breathing',
          fit_factor: null
        },
        {
          name: 'Normal breathing (SEALED)',
          fit_factor: null
        }
      ],
      quantitativeExercisesOSHAFastFFR: [
        {
          name: 'Bending over',
          fit_factor: null
        },
        {
          name: 'Talking',
          fit_factor: null
        },

        {
          name: 'Turning head side to side',
          fit_factor: null
        },

        {
          name: 'Moving head up and down',
          fit_factor: null
        },
        {
          name: 'Normal breathing (SEALED)',
          fit_factor: null
        }
      ],
      selectedMask: {
        id: null,
        uniqueInternalModelCode: '',
        hasExhalationValve: false
      },
      selectedUser: {
        firstName: '',
        lastName: '',
        id: 0,
      },
      comfort: {
        "How comfortable is the position of the mask on the nose?": null,
        "Is there enough room to talk?": null,
        "How comfortable is the position of the mask on face and cheeks?": null
      },
      userSealCheck: {
        'sizing': {
          "What do you think about the sizing of this mask relative to your face?": null
        },
        'positive': {
          "...how much air movement on your face along the seal of the mask did you feel?": null
        },
        'negative': {
          '...how much air passed between your face and the mask?': null
        }
      },
      searchMask: "",
      searchUser: "",
      hasExistingFitTestUser: false,
      maskCurrentPage: 1,
      maskPerPage: 6,
      maskTotalCount: 0,
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
        ]
    ),
    ...mapWritableState(
        useMainStore,
        [
          'messages'
        ]
    ),
    ...mapWritableState(
        useMeasurementDeviceStore,
        [
          'measurementDevices'
        ]
    ),
    ...mapState(
        useManagedUserStore,
        [
          'managedUsers'
        ]
    ),
    numExercisesHalf() {
      return this.quantitativeExercises.length / 2;
    },
    quantitativeExercises() {
      // Has a "name" field
      // Check fitTestProcedure first, then fall back to quantitativeProcedure for backwards compatibility
      if (this.fitTestProcedure === 'quantitative_full_osha' ||
          (this.quantitativeProcedure == 'Full OSHA' && !this.fitTestProcedure)) {
        return this.quantitativeExercisesFullOsha
      }

      return this.quantitativeExercisesOSHAFastFFR
    },
    acceptableRouteName() {
      return ["EditFitTest", "ViewFitTest", "NewFitTest"].includes(this.$route.name)
    },
    managedUsersWhoCanAddFitTestData() {
      return this.managedUsers
    },
    fitTest() {
      return new FitTest({
        user_seal_check: this.userSealCheck,
        results: this.results,
        comfort: this.comfort,
        uniqueInternalModelCode: this.selectedMask && this.selectedMask.uniqueInternalModelCode,
        has_exhalation_valve: this.selectedMask && this.selectedMask['hasExhalationValve']
      })
    },
    hasFitTestData() {
      const r = this.results
      if (!r) return false
      const qual = r.qualitative && Array.isArray(r.qualitative.exercises) ? r.qualitative.exercises : []
      const quant = r.quantitative && Array.isArray(r.quantitative.exercises) ? r.quantitative.exercises : []
      const hasQual = qual.some(ex => ex && ex.result != null && String(ex.result).trim() !== '')
      const hasQuant = quant.some(ex => ex && ex.fit_factor != null && String(ex.fit_factor).trim() !== '')
      return hasQual || hasQuant
    },
    missingDataUserSealCheck() {
      let missingValues = []

      if (this.userSealCheck['sizing']["What do you think about the sizing of this mask relative to your face?"] == undefined) {
        missingValues.push("What do you think about the sizing of this mask relative to your face?")
      }
      let branch = 'positive'

      if (this.showPositiveUserSealCheck) {
        branch = 'positive'
      } else {
        branch = 'negative'
      }

      for (const [key, value] of Object.entries(this.userSealCheck[branch])) {
        if (value == null) {
          missingValues.push(key)
        }
      }

      return missingValues
    },
    qualitativeHasAFailure() {
      for(let q of this.qualitativeExercises) {
        if (q.result == 'Fail') {
          return true
        }
      }

      return false
    },
    userSealCheckPassed() {
      return this.fitTest.userSealCheckPassed
    },
    aerosol() {
      if (this.fitTestProcedure === 'qualitative_full_osha') {
        return this.qualitativeAerosolSolution
      } else if (this.fitTestProcedure && this.fitTestProcedure.startsWith('quantitative')) {
        return this.quantitativeAerosolSolution
      }
      // Fallback to old structure for backwards compatibility
      if (this.tabToShow == "QLFT") {
        return this.qualitativeAerosolSolution
      } else if (this.tabToShow == "QNFT"){
        return this.quantitativeAerosolSolution
      } else {
        return
      }
    },
    instructionTitle() {
      if (!this.aerosol) {
        return
      }

      // Map fitTestProcedure to instruction key
      let instructionKey = this.tabToShow
      if (this.fitTestProcedure === 'qualitative_full_osha') {
        instructionKey = 'QLFT'
      } else if (this.fitTestProcedure && this.fitTestProcedure.startsWith('quantitative')) {
        instructionKey = 'QNFT'
      }

      if (this.fitTestingInstructions[instructionKey] && this.fitTestingInstructions[instructionKey][this.aerosol]) {
        return this.fitTestingInstructions[instructionKey][this.aerosol].title
      }
      return ''
    },
    instructionParagraphs() {
      if (!this.aerosol) {
        return []
      }

      // Map fitTestProcedure to instruction key
      let instructionKey = this.tabToShow
      if (this.fitTestProcedure === 'qualitative_full_osha') {
        instructionKey = 'QLFT'
      } else if (this.fitTestProcedure && this.fitTestProcedure.startsWith('quantitative')) {
        instructionKey = 'QNFT'
      }

      if (this.fitTestingInstructions[instructionKey] && this.fitTestingInstructions[instructionKey][this.aerosol]) {
        return this.fitTestingInstructions[instructionKey][this.aerosol].paragraphs
      }
      return []
    },
    results() {
      // TODO: if this.qualitativeExercises is blank, add null results to it
      // TODO: if this.quantitativeExercises is blank, add null results to it
      let qualExerToSave = this.qualitativeExercises
      if (this.qualitativeExercises == null) {
        qualExerToSave = this.originalQualitativeExercises
      }

      let quantExerToSave = this.quantitativeExercises
      if (this.quantitativeExercises == null) {
        quantExerToSave = this.originalQuantitativeExercises
      }

      let qualAerSolToSave = this.qualitativeAerosolSolution
      if (this.qualitativeAerosolSolution == null) {
        qualAerSolToSave = 'Saccharin'
      }

      let quantAerSolToSave = this.quantitativeAerosolSolution
      if (this.quantitativeAerosolSolution == null) {
        quantAerSolToSave = 'Ambient'
      }

      return {
        'qualitative': {
          'exercises': qualExerToSave,
          'procedure': this.qualitativeProcedure,
          'aerosol': {
            solution: qualAerSolToSave,
          },
          'notes': this.qualitativeNotes,
        },
        'quantitative': {
          'testing_mode': this.quantitativeTestingMode,
          'exercises': quantExerToSave,
          'procedure': this.quantitativeProcedure,
          'aerosol': {
            'initial_count_per_cm3': this.initialCountPerCm3,
            solution: quantAerSolToSave,
          },
          'notes': this.quantitativeNotes,
        }
      }
    },
    toSave() {
      return {
        comfort: this.comfort,
        mask_id: this.selectedMask && this.selectedMask.id,
        user_seal_check: this.userSealCheck,
        results: this.results,
        facial_hair: this.facialHair
      }
    },
    createOrEdit() {
      return (this.mode == 'Create' || this.mode == 'Edit')
    },
    showPositiveUserSealCheck() {
      return this.selectedMask &&
        'hasExhalationValve' in this.selectedMask &&
        this.selectedMask && this.selectedMask['hasExhalationValve'] == false
    },
    maskHasBeenSelected() {
      return !!this.selectedMask && this.selectedMask['id'] != 0
    },
    pageTitle() {
      if (this.$route.name == 'NewFitTest') {
        return "Add Fit Testing Results"
      } else if (this.$route.name == 'EditFitTest') {
        return `${this.mode} Fit Testing Results`
      }
    },
    userDisplayables() {
      if (this.searchUser == "") {
        return this.managedUsersWhoCanAddFitTestData
      } else {
        let lowerSearch = this.searchUser.toLowerCase()
        return this.managedUsersWhoCanAddFitTestData.filter((user) => user.fullName.toLowerCase().match(lowerSearch))
      }
    },
    maskDisplayables() {
      // Backend now handles search and pagination
      return this.masks
    },
    selectMaskDisplayables() {
      // Backend now handles pagination, so return all masks from current page
      return this.maskDisplayables
    },
    completedFitTestSteps() {
      const completed = []

      // Check Facial Hair completion
      if (this.facialHair &&
          this.facialHair.beard_length_mm !== null &&
          this.facialHair.beard_cover_technique !== null) {
        completed.push('Facial Hair')
      }

      // Check User Seal Check completion
      if (this.userSealCheck) {
        const sizingComplete = this.userSealCheck.sizing &&
          Object.values(this.userSealCheck.sizing).every(value => value !== null)

        const positiveComplete = this.userSealCheck.positive &&
          Object.values(this.userSealCheck.positive).every(value => value !== null)

        const negativeComplete = this.userSealCheck.negative &&
          Object.values(this.userSealCheck.negative).every(value => value !== null)

        if (sizingComplete && positiveComplete && negativeComplete) {
          completed.push('User Seal Check')
        }
      }

      // Check Comfort completion
      if (this.comfort && Object.values(this.comfort).every(value => value !== null)) {
        completed.push('Comfort')
      }

      // Check Fit Test completion
      if (this.fitTestProcedure ||
          (this.qualitativeProcedure && this.qualitativeProcedure !== 'Skipping') ||
          (this.quantitativeProcedure && this.quantitativeProcedure !== 'Skipping') ||
          this.hasFitTestData) {
        completed.push('Fit Test')
      }

      return completed
    },
  },
  async created() {
    await this.getCurrentUser()

    let toQuery = this.$route.query
    let toParams = this.$route.params

    await this.loadQuery(toQuery, null)
    await this.loadParams(toParams, null)


    this.$watch(
      () => this.$route.params,
      this.loadParams
    )

    // TODO: add param watchers
    this.$watch(
      () => this.$route.query,
      this.loadQuery
    )
  },
  methods: {
    ...mapActions(useMainStore, ['addMessages', 'getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    ...mapActions(useManagedUserStore, ['loadManagedUsers']),
    ...mapActions(useMeasurementDeviceStore, ['loadMeasurementDevices']),
    async loadParams(toParams, fromParams) {
      if (toParams['id'] && this.acceptableRouteName) {
        this.id = toParams['id']
      }
    },
    async loadQuery(toQuery, fromQuery) {
      if (!this.currentUser) {
        signIn.call(this)
      } else {
        // Initialize mask pagination from URL
        if (toQuery.maskPage) {
          this.maskCurrentPage = parseInt(toQuery.maskPage) || 1
        }

        if (this.$route.name == 'NewFitTest') {
          this.mode = 'Create'
        }

        if (this.$route.name == 'NewFitTest' && toQuery.userId && toQuery.maskId) {
          // handle quick way to add too small / too big
          await this.loadMasks()
          await this.loadManagedUsers()
          let managedUser = this.managedUsers.filter((m) => m.managedId == parseInt(toQuery.userId))[0]

          let successCallback = undefined;
          let tabToShow = 'Facial Hair'

          if (this.$route.query.size) {
            this.userSealCheck["sizing"]["What do you think about the sizing of this mask relative to your face?"] = toQuery.size

            successCallback = () => {
              this.$router.push({
                name: 'FitTests',
                query: {
                  managedId: managedUser.managedId
                }
              }).then(() => {
                this.scrollToTop()
              })
            }
          }

          if (managedUser) {
            this.selectedUser = managedUser

            await this.saveFitTest(
              {
                tabToShow: tabToShow
              },
              successCallback
            )
          }
        } else if (this.$route.name == 'NewFitTest' && toQuery.userId) {
          // Handle case where only userId is provided (e.g., from clicking "+" button)
          await this.loadManagedUsers()
          let managedUser = this.managedUsers.filter((m) => m.managedId == parseInt(toQuery.userId))[0]

          if (managedUser) {
            this.selectedUser = managedUser
            this.searchUser = managedUser.fullName
            // Set tabToShow from query if provided, otherwise default to 'Mask'
            if (toQuery.tabToShow) {
              this.tabToShow = toQuery.tabToShow
            }
          }
        }

        if (this.acceptableRouteName) {
          // pull the data
          if ('tabToShow' in toQuery) {
            // Map old QLFT/QNFT to Fit Test for backwards compatibility
            if (toQuery['tabToShow'] === 'QLFT' || toQuery['tabToShow'] === 'QNFT') {
              this.tabToShow = 'Fit Test'
            } else {
              this.tabToShow = toQuery['tabToShow']
            }
          }

          if (toQuery['mode']) {
            this.mode = toQuery['mode']
          }

          if (toQuery['secondaryTabToShow'] && this.acceptableRouteName) {
            this.secondaryTabToShow = toQuery['secondaryTabToShow']
          }

        }

        await this.loadManagedUsers()
        await this.loadMasks()
        await this.loadMeasurementDevices()
        await this.loadFitTest()

        if (toQuery.maskId) {
          const foundMask = this.masks.filter((m) => m.id == parseInt(toQuery.maskId))[0]
          this.selectedMask = foundMask || {
            id: null,
            uniqueInternalModelCode: '',
            hasExhalationValve: false
          }
          this.searchMask = this.selectedMask && this.selectedMask.uniqueInternalModelCode
        }
      }

    },
    setQuantitativeExercises(exercises) {
      // Has a "name" field
      if (this.quantitativeProcedure == 'Full OSHA') {
        this.quantitativeExercisesFullOsha = exercises
        return
      }

      // If procedure is not set, infer from number of exercises
      // Full OSHA typically has 9 exercises, OSHA Fast has 5
      if (!this.quantitativeProcedure && exercises && exercises.length >= 8) {
        this.quantitativeExercisesFullOsha = exercises
        return
      }

      this.quantitativeExercisesOSHAFastFFR = exercises
    },
    deviceInfo(d) {
      let message = '';
      if (d.remove_from_service) {
        message = "- REMOVED FROM SERVICE"
      }
      return `${d.manufacturer} ${d.model} ${d.serial} ${message}`
    },
    showDescription(name) {
      this.messages = []

      // Check both exercise sets to find the description
      let description = null
      if (this.oshaExercises && this.oshaExercises[name]) {
        description = this.oshaExercises[name].description
      } else if (this.oshaFastFFRExercises && this.oshaFastFFRExercises[name]) {
        description = this.oshaFastFFRExercises[name].description
      }

      if (description) {
        this.messages.push({ str: description })
      } else {
        this.messages.push({ str: 'Description not available' })
      }
    },
    showInstructions() {
      this.messages = []

      if (!this.instructionTitle || !this.instructionParagraphs || this.instructionParagraphs.length === 0) {
        this.messages.push({ str: 'Instructions not available. Please select a procedure and solution/aerosol.' })
        return
      }

      // Add title and paragraphs as separate messages
      this.messages.push({ str: this.instructionTitle })
      this.instructionParagraphs.forEach(paragraph => {
        this.messages.push({ str: paragraph })
      })
    },
    updateSearch(event, userOrMask) {
      if (userOrMask == 'mask') {
        this.selectedMask = {
          'uniqueInternalModelCode': null
        }
        this.searchMask = event.target.value
        // Reset to page 1 when search changes
        this.maskCurrentPage = 1
        this.updateMaskPaginationInUrl()
        this.loadMasks()
      } else {
        this.selectedUser = new RespiratorUser({
        })
        this.searchUser = event.target.value
      }
    },
    handleMaskPageChange(page) {
      this.maskCurrentPage = page
      this.updateMaskPaginationInUrl()
      this.loadMasks()
    },
    updateMaskPaginationInUrl() {
      const query = { ...this.$route.query }
      if (this.maskCurrentPage > 1) {
        query.maskPage = this.maskCurrentPage
      } else {
        delete query.maskPage
      }
      this.$router.replace({ query })
    },
    getAbsoluteHref(href) {
      // TODO: make sure this works for all
      return `${href}`
    },
    newFitTest() {
      this.$router.push(
        {
          name: "AddFitTest"
        }
      )
    },
    selectMask(id) {
      if (!id) {
        this.selectedMask = {
          uniqueInternalModelCode: null
        }
      } else {
        let query = JSON.parse(JSON.stringify(this.$route.query))

        let newQuery = Object.assign(query, { maskId: id })

        this.$router.push(
          {
            name: this.$route.name,
            query: newQuery
          }
        )
      }
    },
    selectUser(id) {
      const found = this.managedUsers.filter((m) => m.managedId == id)[0]
      if (found) {
        this.selectedUser = found
        this.searchUser = this.selectedUser.fullName
      } else {
        // Fallback to an empty RespiratorUser to avoid render errors
        this.selectedUser = new RespiratorUser({
          firstName: '',
          lastName: '',
          managedId: id
        })
        this.searchUser = ''
      }
    },
    async loadMasks() {
      // Build query params for pagination and search
      const params = new URLSearchParams()
      params.append('page', this.maskCurrentPage)
      params.append('per_page', this.maskPerPage)

      if (this.searchMask) {
        params.append('search', this.searchMask)
      }

      await axios.get(`/masks.json?${params.toString()}`)
        .then(response => {
          let data = response.data
          if (response.data.masks) {
            this.masks = deepSnakeToCamel(data.masks)
            this.maskTotalCount = data.total_count || 0
            this.maskCurrentPage = data.page || 1
            this.maskPerPage = data.per_page || 6
          }
        })
        .catch(error => {
          if (error && error.response && error.response.data && error.response.data.messages) {
            this.addMessages(error.response.data.messages)
          } else {
            this.addMessages([error.message])
          }
        })
    },
    async deleteFitTest() {
      setupCSRF();
      let answer = window.confirm("Are you sure you want to delete data?");

      if (answer) {
        await axios.delete(
          `/fit_tests/${this.$route.params.id}`,
        )
          .then(response => {
            let data = response.data
            this.$router.push({
              'name': 'FitTests'
            })

          })
          .catch(error => {
            if (error && error.response && error.response.data && error.response.data.messages) {
              this.addMessages(error.response.data.messages)
            } else {
              this.addMessages([error.message])
            }
          })
      }
    },
    async loadFitTest() {
      // TODO: make this more flexible so parents can load data of their children
      if (['EditFitTest', 'ViewFitTest'].includes(this.$route.name) && this.$route.params.id) {

        await axios.get(
          `/fit_tests/${this.$route.params.id}.json`,
        )
          .then(response => {
            let data = response.data
            let fitTestData = response.data.fit_test

            this.id = fitTestData.id
            this.hasExistingFitTestUser = !!fitTestData.user_id

            const foundMask = this.masks.filter((m) => m.id == fitTestData.mask_id)[0]
            this.selectedMask = foundMask || {
              id: null,
              uniqueInternalModelCode: '',
              hasExhalationValve: false
            }
            this.comfort = fitTestData.comfort
            this.userSealCheck = fitTestData.user_seal_check
            this.facialHair = fitTestData.facial_hair
            if (!this.facialHair) {
              this.facialHair = {
                beard_length_mm: '0mm',
                beard_cover_technique: 'No',
              }
            }

            let results = fitTestData.results

            this.qualitativeAerosolSolution = results.qualitative?.aerosol?.solution
            this.qualitativeNotes = results.qualitative?.notes
            this.qualitativeProcedure = results.qualitative?.procedure
            this.qualitativeExercises = results.qualitative?.exercises || []

            this.quantitativeTestingMode = results.quantitative?.testing_mode
            this.quantitativeAerosolSolution = results.quantitative?.aerosol?.solution
            this.quantitativeNotes = results.quantitative?.notes
            this.quantitativeProcedure = results.quantitative?.procedure

            this.setQuantitativeExercises(results.quantitative?.exercises || [])
            this.initialCountPerCm3 = results.quantitative?.aerosol?.initial_count_per_cm3

            // Sync fitTestProcedure from existing data for backwards compatibility
            // Pass the raw exercises as a fallback in case the arrays aren't set correctly
            // Ensure we have the exercises array before syncing
            const quantExercises = results.quantitative && results.quantitative.exercises ? results.quantitative.exercises : []
            this.syncFitTestProcedureFromExisting(quantExercises)

            this.selectUser(fitTestData.user_id)

            // whatever you want
          })
          .catch(error => {
            this.message = "Failed to load masks."
            // whatever you want
          })
      }
    },

    validateQLFTorQNFTExists() {
      // if user seal check passed, then we should have qualitative procedure be not "Skipping"
      // OR quantitative procedure be not "Skipping"
      if (this.userSealCheckPassed && this.qualitativeProcedure == 'Skipping' && this.quantitativeProcedure == 'Skipping') {
        this.messages.push(
          {
            str: `Since User Seal Check passed, cannot skip QLFT and QNFT. Please do the procedures in one of those sections and fill out the data accordingly.`
          }
        )
      }
    },
    validateComfort() {
      let missingValue = []

      for (const [key, value] of Object.entries(this.comfort)) {
        if (value == null) {
          this.messages.push(
            {
              str: `Please fill out: "${key}"`
            }
          )
        }
      }
    },
    validateUserSealCheck() {
      for (let key of this.missingDataUserSealCheck) {
          this.messages.push(
            {
              str: `Please fill out: "${key}"`
            }
          )
      }
    },

    validatePresenceOfInitialCountPerCM3() {
      if (!this.initialCountPerCm3 && this.quantitativeProcedure != 'Skipping') {
            this.messages.push(
              {
                str: "Please fill out initial count per cm3.",
                to: {
                  'name': 'EditFitTest',
                  params: {
                    id: this.$route.params.id
                  },
                  query: {
                    tabToShow: 'Fit Test',
                    secondaryTabToShow: 'Choose Procedure',
                  }
                }
              }
            )
      }
    },
    validateValueOfInitialCountPerCM3() {
      let n99ModeAmbientCountCriteria = this.initialCountPerCm3 < 1000 && this.quantitativeProcedure != 'Skipping' && this.quantitativeTestingMode == 'N99'
      let n95ModeAmbientCountCriteria = this.initialCountPerCm3 < 30 && this.quantitativeProcedure != 'Skipping' && this.quantitativeTestingMode == 'N95'

      let cutoffs = {
        'N95': {
          'minimumCutoff': 30
        },
        'N99': {
          'minimumCutoff': 1000
        }
      }

      if (n99ModeAmbientCountCriteria || n95ModeAmbientCountCriteria) {
          this.messages.push(
            {
              str: `Initial particle count too low. Please take this test at an environment where the number of particles per cubic centimeter is greater than ${cutoffs[this.quantitativeTestingMode]['minimumCutoff']}. Note: For model 8038, the cutoff is 30 particles per cubic centimeter, while for 8020, the cutoff is actually 70 particles per cubic centimeter.`,
            }
          )

      }
    },
    validateQLFT(part) {
      if (!this.qualitativeProcedure) {
        this.messages.push(
          {
            str: `Please choose a QLFT procedure.`
          }
        )

        return
      }

      if (this.qualitativeProcedure == 'Full OSHA' && part == 'Results') {
        let failCount = 0

        for (const [key, value] of Object.entries(this.qualitativeExercises)) {
          // Quit early if there is a failure
          if (value['result'] == 'Fail') {
            return
          }

          if (value['result'] == null) {
            this.messages.push(
              {
                str: `Please fill out: "${value['name']}"`
              }
            )
          }
        }
      }
    },
    validatePresenceOfTestingMode() {
      if (!this.quantitativeTestingMode) {
        this.messages.push(
          {
            str: `Please choose a QNFT testing mode.`
          }
        )
      }
    },
    validatePresenceOfDevice() {
    },
    validateQNFT(part) {
      if (!this.quantitativeProcedure) {
        this.messages.push(
          {
            str: `Please choose a QNFT procedure.`
          }
        )

        return
      }

      if (this.quantitativeProcedure != 'Skipping') {
        this.validatePresenceOfInitialCountPerCM3()
        this.validateValueOfInitialCountPerCM3()
        this.validatePresenceOfTestingMode()
      }

      if (this.quantitativeProcedure == 'Full OSHA' && this.secondaryTabToShow == 'Results') {
        let failCount = 0

        for (const [key, value] of Object.entries(this.quantitativeExercises)) {
          if (value['fit_factor'] < 0) {
            this.messages.push(
              {
                str: `Cannot have a negative fit factor for "${value['name']}"`
              }
            )
          }
        }
      }
    },
    validateMask() {
      if (this.selectedMask && this.selectedMask.id == 0) {
        this.messages.push(
          {
            str: "Please select a mask."
          }
        )
      }
    },

    async saveFitTest(query, successCallback) {
      if (!this.tabToShow) {
        this.tabToShow = 'Mask'
      }

      // Sync fitTestProcedure to old structure before saving for backwards compatibility
      this.syncProceduresFromFitTestProcedure()

      if (this.id) {
        await axios.put(
          `/fit_tests/${this.id}.json`, {
            fit_test: this.toSave,
            user: {
              id: this.selectedUser.managedId
            }
          }
        )
          .then(response => {
            let data = response.data
            // whatever you want

            // this.mode = 'View'

            this.$router.push({
              path: `/fit_tests/${this.id}`,
              query: query,
              force: true
            }).then(() => {
              this.scrollToTop()
            })
          })
          .catch(error => {
            //  TODO: actually use the error message
            this.messages.push({
              str: "Failed to update fit test."
            })
          })
      } else {
        if (this.messages.length > 0) {
          return
        }

        // create
        await axios.post(
          `/fit_tests.json`, {
            fit_test: this.toSave,
            user: {
              id: this.selectedUser.managedId
            }
          }
        )
          .then(response => {
            let data = response.data

            // TODO: could get the id from data
            // We could save it
            // whatever you want

            this.id = response.data.fit_test.id

            // We assume that the user hits save first at the "Mask" section.
            // It might not be always the case, but good enough

            if (!!successCallback) {
              successCallback()
            } else {
              this.$router.push({
                name: 'EditFitTest',
                params: {
                  id: this.id
                },
                query: query,
                force: true
              }).then(() => {
                this.scrollToTop()
              })
            }
          })
          .catch(error => {
            //  TODO: actually use the error message
            if (error && error.response && error.response.data && error.response.data.messages) {
              this.addMessages(error.response.data.messages)
            } else {
              this.addMessages(
                [error.message]
              )
            }
          })
      }
    },
    validateUser() {
      if (!this.selectedUser.fullName) {

        this.addMessages(["Please select a user."])
      }
    },
    async validateAndSaveFitTest() {
      // this.runValidations()
      this.messages = []

      if (this.tabToShow == 'User') {
        this.validateUser()

        if (this.messages.length == 0) {
          await this.saveFitTest({
            tabToShow: 'Mask'
          })
        } else {
          return
        }
      }
      else if (this.tabToShow == 'Mask') {
        this.validateUser()
        this.validateMask()

        if (this.messages.length == 0) {
          await this.saveFitTest({
            tabToShow: 'Facial Hair'
          })
        } else {
          return
        }

        return
      }

      else if (this.tabToShow == 'Facial Hair') {
        this.validateUser()
        this.validateMask()

        if (this.messages.length == 0) {
          await this.saveFitTest({
            tabToShow: 'User Seal Check'
          })
        } else {
          return
        }
      }

      else if (this.tabToShow == 'User Seal Check') {
        this.validateUser()
        this.validateMask()

        // Check if we should skip validation based on early failure conditions
        const sizingAnswer = this.userSealCheck['sizing']["What do you think about the sizing of this mask relative to your face?"]
        const airMovementAnswer = this.userSealCheck['positive']["...how much air movement on your face along the seal of the mask did you feel?"]

        // If air movement is "A lot of air movement", proceed regardless of other answers
        const hasAirMovementFailure = airMovementAnswer === 'A lot of air movement'

        // If sizing is "Too big" or "Too small", proceed to Fit Test
        const hasSizingFailure = sizingAnswer === 'Too big' || sizingAnswer === 'Too small'

        // Only validate if we're not skipping due to early failure conditions
        if (!hasAirMovementFailure && !hasSizingFailure) {
          this.validateUserSealCheck()
        } else if (hasAirMovementFailure) {
          // If air movement indicates failure, we can proceed regardless of sizing
          // But we should still ensure the air movement question itself is answered
          if (!airMovementAnswer) {
            this.messages.push({
              str: `Please fill out: "...how much air movement on your face along the seal of the mask did you feel?"`
            })
          }
        } else if (hasSizingFailure) {
          // If sizing indicates failure, ensure sizing question is answered
          if (!sizingAnswer) {
            this.messages.push({
              str: `Please fill out: "What do you think about the sizing of this mask relative to your face?"`
            })
          }
        }

        if (this.messages.length == 0) {
          await this.saveFitTest({
            tabToShow: 'Fit Test',
            secondaryTabToShow: 'Choose Procedure'
          })

          // Save first before potentially displaying this message
          if (!this.userSealCheckPassed) {
            this.messages.push(
              {
                str: "User seal check failed. You may skip adding qualitative or quantitative fit testing data, along with comfort data if you wish, by clicking here.",
                to: {
                  'name': 'FitTests',
                  'query': {
                    'managedId': this.selectedUser.managedId
                  }
                }
              }
            )
          }
        } else {
          return
        }

      }

      else if (this.tabToShow == 'Fit Test' && this.secondaryTabToShow == 'Choose Procedure') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()

        // Validate procedure is selected
        if (!this.fitTestProcedure) {
          this.messages.push({ str: 'Please select a fit testing procedure.' })
          return
        }

        // Sync to old structure before validation
        this.syncProceduresFromFitTestProcedure()

        // Validate based on procedure type
        if (this.fitTestProcedure === 'qualitative_full_osha') {
          this.validateQLFT('Choose Procedure')
        } else if (this.fitTestProcedure && this.fitTestProcedure.startsWith('quantitative')) {
          this.validatePresenceOfDevice()
          this.validatePresenceOfInitialCountPerCM3()
          this.validateValueOfInitialCountPerCM3()
        }

        if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'Fit Test',
              secondaryTabToShow: 'Results'
            }
          )
        } else {
          return
        }
      }

      else if (this.tabToShow == 'Fit Test' && this.secondaryTabToShow == 'Results') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()

        // Sync to old structure before validation
        this.syncProceduresFromFitTestProcedure()

        // Validate based on procedure type
        if (this.fitTestProcedure === 'qualitative_full_osha') {
          this.validateQLFT('Results')
        } else if (this.fitTestProcedure && this.fitTestProcedure.startsWith('quantitative')) {
          this.validateQLFT()
          this.validateQNFT()
        }

        if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'Comfort',
            }
          )
        } else {
          return
        }
      }

      else if (this.tabToShow == 'Comfort') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()
        // Sync fitTestProcedure before checking if fit test exists
        this.syncProceduresFromFitTestProcedure()
        this.validateQLFTorQNFTExists()
        this.validateComfort()

        if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'Comfort',
            }
          )

          this.$router.push({
            name: 'FitTests',
            query: {
              managedId: this.selectedUser.managedId
            }
          }).then(() => {
            this.scrollToTop()
          })

          this.messages.push(
            {
              str: 'Successfully edited a fit test'
            }
          )
        } else {
          return
        }
      }

    },

    selectSizingUserSealCheck(value) {
      this['userSealCheck']['sizing']['What do you think about the sizing of this mask relative to your face?'] = value
    },
    selectPositivePressureAirMovement(value) {
      this['userSealCheck']['positive']['...how much air movement on your face along the seal of the mask did you feel?'] = value
    },
    selectNegativePressureAirMovement(value) {
      this['userSealCheck']['negative']['...how much air passed between your face and the mask?'] = value
    },
    selectNegativePressure(value) {
      this['userSealCheck']['While performing a negative user seal check, did you notice any leakage?'] = value
    },
    // Sync fitTestProcedure from existing qualitativeProcedure/quantitativeProcedure for backwards compatibility
    // rawQuantitativeExercises is an optional parameter with the raw exercises from the API (for fallback checking)
    syncFitTestProcedureFromExisting(rawQuantitativeExercises = null) {
      if (this.qualitativeProcedure && this.qualitativeProcedure !== 'Skipping') {
        if (this.qualitativeProcedure === 'Full OSHA') {
          this.fitTestProcedure = 'qualitative_full_osha'
          return
        }
      } else if (this.quantitativeProcedure && this.quantitativeProcedure !== 'Skipping') {
        if (this.quantitativeProcedure === 'OSHA Fast Filtering Face Piece Respirators') {
          this.fitTestProcedure = 'quantitative_osha_fast'
          return
        } else if (this.quantitativeProcedure === 'Full OSHA') {
          this.fitTestProcedure = 'quantitative_full_osha'
          return
        }
      } else {
        // If no explicit procedure, try to infer from exercise data
        // Prioritize checking raw exercises if provided (most reliable)
        if (rawQuantitativeExercises && Array.isArray(rawQuantitativeExercises) && rawQuantitativeExercises.length > 0) {
          const hasQuantData = rawQuantitativeExercises.some(ex => ex && ex.fit_factor != null && String(ex.fit_factor).trim() !== '')
          if (hasQuantData) {
            // Infer procedure type based on number of exercises
            // Full OSHA typically has 9 exercises, OSHA Fast has 5
            const exerciseCount = rawQuantitativeExercises.length
            if (exerciseCount >= 8) {
              this.fitTestProcedure = 'quantitative_full_osha'
              return
            } else if (exerciseCount >= 4) {
              this.fitTestProcedure = 'quantitative_osha_fast'
              return
            }
          }
        }

        // Fallback: check arrays if raw exercises not provided
        const quantExercisesFull = this.quantitativeExercisesFullOsha || []
        const quantExercisesFast = this.quantitativeExercisesOSHAFastFFR || []

        // Check which array has exercises with actual fit_factor data
        const hasQuantDataFull = quantExercisesFull.some(ex => ex && ex.fit_factor != null && String(ex.fit_factor).trim() !== '')
        const hasQuantDataFast = quantExercisesFast.some(ex => ex && ex.fit_factor != null && String(ex.fit_factor).trim() !== '')

        if (hasQuantDataFull || hasQuantDataFast) {
          // Determine which procedure type based on which array has data and exercise count
          if (hasQuantDataFull) {
            // If FullOsha array has data, it's Full OSHA
            this.fitTestProcedure = 'quantitative_full_osha'
          } else if (hasQuantDataFast) {
            // If Fast array has data, check count to be sure
            const exerciseCount = quantExercisesFast.length
            if (exerciseCount >= 8) {
              // If it has 8+ exercises, it's actually Full OSHA (might have been mis-categorized)
              this.fitTestProcedure = 'quantitative_full_osha'
            } else {
              // Otherwise it's OSHA Fast
              this.fitTestProcedure = 'quantitative_osha_fast'
            }
          }
        } else {
          // Check qualitative exercises
          const qualExercises = this.qualitativeExercises || []
          const hasQualData = qualExercises.some(ex => ex && ex.result != null && String(ex.result).trim() !== '')

          if (hasQualData) {
            // Qualitative Full OSHA typically has 7 exercises
            this.fitTestProcedure = 'qualitative_full_osha'
          }
        }
      }
    },
    // Map fitTestProcedure to qualitativeProcedure/quantitativeProcedure when saving
    syncProceduresFromFitTestProcedure() {
      if (!this.fitTestProcedure) {
        return
      }

      if (this.fitTestProcedure === 'qualitative_full_osha') {
        this.qualitativeProcedure = 'Full OSHA'
        this.quantitativeProcedure = 'Skipping'
      } else if (this.fitTestProcedure === 'quantitative_osha_fast') {
        this.qualitativeProcedure = 'Skipping'
        this.quantitativeProcedure = 'OSHA Fast Filtering Face Piece Respirators'
      } else if (this.fitTestProcedure === 'quantitative_full_osha') {
        this.qualitativeProcedure = 'Skipping'
        this.quantitativeProcedure = 'Full OSHA'
      }
    },
    // Get exercises based on fitTestProcedure
    getExercisesForProcedure() {
      if (this.fitTestProcedure === 'qualitative_full_osha') {
        return this.qualitativeExercises || []
      } else if (this.fitTestProcedure === 'quantitative_osha_fast') {
        return this.quantitativeExercises || []
      } else if (this.fitTestProcedure === 'quantitative_full_osha') {
        return this.quantitativeExercises || []
      }
      return []
    },
    // Initialize exercises based on selected procedure
    initializeExercisesForProcedure() {
      if (this.fitTestProcedure === 'qualitative_full_osha') {
        // Only initialize if not already set (to preserve existing data)
        if (!this.qualitativeExercises || this.qualitativeExercises.length === 0) {
          this.qualitativeExercises = [
            { name: 'Normal breathing', result: null },
            { name: 'Deep breathing', result: null },
            { name: 'Turning head side to side', result: null },
            { name: 'Moving head up and down', result: null },
            { name: 'Talking', result: null },
            { name: 'Bending over', result: null },
            { name: 'Normal breathing', result: null }
          ]
        }
      } else if (this.fitTestProcedure === 'quantitative_osha_fast') {
        // Only initialize if not already set
        if (!this.quantitativeExercisesOSHAFastFFR || this.quantitativeExercisesOSHAFastFFR.length === 0) {
          this.setQuantitativeExercises([
            { name: 'Bending over', fit_factor: null },
            { name: 'Talking', fit_factor: null },
            { name: 'Turning head side to side', fit_factor: null },
            { name: 'Moving head up and down', fit_factor: null },
            { name: 'Normal breathing (SEALED)', fit_factor: null }
          ])
        }
      } else if (this.fitTestProcedure === 'quantitative_full_osha') {
        // Only initialize if not already set
        if (!this.quantitativeExercisesFullOsha || this.quantitativeExercisesFullOsha.length === 0) {
          this.setQuantitativeExercises([
            { name: 'Normal breathing', fit_factor: null },
            { name: 'Deep breathing', fit_factor: null },
            { name: 'Turning head side to side', fit_factor: null },
            { name: 'Moving head up and down', fit_factor: null },
            { name: 'Talking', fit_factor: null },
            { name: 'Grimace', fit_factor: null },
            { name: 'Bending over', fit_factor: null },
            { name: 'Normal breathing', fit_factor: null },
            { name: 'Normal breathing (SEALED)', fit_factor: null }
          ])
        }
      }
    },
    onFitTestProcedureChange() {
      // Sync to old structure for backwards compatibility
      this.syncProceduresFromFitTestProcedure()

      // Initialize exercises for the selected procedure
      this.initializeExercisesForProcedure()

      // Set secondary tab to "Choose Procedure" when procedure changes
      this.secondaryTabToShow = 'Choose Procedure'
    },
    selectBeardLength(value) {
      this['facialHair']['beard_length_mm'] = value
    },
    selectBeardCoverTechnique(value) {
      this['facialHair']['beard_cover_technique'] = value
    },
    selectComfortNose(value) {
      this['comfort']['How comfortable is the position of the mask on the nose?'] = value
    },
    selectComfortEnoughRoomToTalk(value) {
      this['comfort']['Is there enough room to talk?'] = value
    },
    selectComfortFaceAndCheeks(value) {
      this['comfort']['How comfortable is the position of the mask on face and cheeks?'] = value
    },
    selectGeneralComfort(value) {
      this['comfort']['How comfortable is this mask/respirator?'] = value
    },
    scrollToTop() {
      // Scroll to top with smooth behavior after a short delay to allow content to render
      this.$nextTick(() => {
        setTimeout(() => {
          window.scrollTo({
            top: 0,
            behavior: 'smooth'
          })
        }, 100)
      })
    },
    setRouteTo(opt) {
      let query = JSON.parse(JSON.stringify(this.$route.query))

      query = Object.assign(query, {
        tabToShow: opt.name
      })

      this.$router.push({
        name: this.$route.name,
        query: query
      }).then(() => {
        this.scrollToTop()
      })
    },
    navigateToStep(stepKey) {
      // Navigate to the specified step
      this.tabToShow = stepKey

      // Update URL query parameter
      let query = JSON.parse(JSON.stringify(this.$route.query))
      query = Object.assign(query, {
        tabToShow: stepKey
      })

      this.$router.push({
        name: this.$route.name,
        query: query
      }).then(() => {
        this.scrollToTop()
      })
    },
    setSecondaryTab(opt) {
      this.$router.push({
        name: this.$route.name,
        query: {
          tabToShow: this.$route.query.tabToShow,
          secondaryTabToShow: opt.name
        }
      }).then(() => {
        this.scrollToTop()
      })
    },
  }
}
</script>

<style scoped>

  .header {
    align-items: left;
  }

  .title-row-item {
    margin-left: 1em;
    margin-right: 1em;
  }
  .title-row {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-bottom: 1em;
  }

  .title-row h2 {
    margin: 0;
  }

  .mode-buttons {
    display: flex;
    gap: 0.5em;
    flex-shrink: 0;
  }

  .flex {
    display: flex;
  }
  .main {
    display: flex;
    flex-direction: column;
  }
  .add-facial-measurements-button {
    margin: 1em auto;
  }

  .card {
    padding: 1em 0;
  }

  table {
    width: 100%;
  }

  .pointable:hover {
    background-color: #eee;
    cursor: pointer;
  }

  .text-row {
    padding: 0.5em;
  }

  .text-row:hover {
    background-color: #eee;
  }

  .card .description {
    padding: 1em;
  }

  input[type='number'] {
    min-width: 2em;
    font-size: 24px;
    padding-left: 0.25em;
    padding-right: 0.25em;
  }
  .thumbnail {
    max-width:10em;
    max-height:10em;
  }

  td,th {
    padding: 0.5em;
  }
  .text-for-other {
    margin: 0 1.25em;
  }

  .justify-items-center {
    justify-items: center;
  }

  .menu {
    justify-content:center;
    min-width: 500px;
    background-color: #eee;
    margin-top: 0;
    margin-bottom: 0;
  }
  .row {
    display: flex;
    flex-direction: row;
  }

  .row.buttons {
    justify-content: center;
  }


  .flex-dir-col {
    display: flex;
    flex-direction: column;
  }
  p {

  }

  select {
    padding: 0.25em;
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

  .align-items-center {
    display: flex;
    align-items: center;
  }

  .left-pane-image {

  }
  p.left-pane {
    max-width: 50%;
  }

  p.narrow-p {
    max-width: 40em;
    padding: 1em;
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
  .label-input {
    align-items:center;
    justify-content:space-between;
  }

  .main, .grid.selectedMask {
    display: grid;
    grid-template-rows: auto;
  }

  .align-content-center {
    display: flex;
    align-content: center;
  }

  .justify-content-center {
    display: flex;
    justify-content: center;
  }

  .adaptive-wide img {
    width: 100%;
  }
  img {
    max-width: 30em;
  }
  .edit-facial-measurements {
    display: flex;
    flex-direction: row;
  }
  tbody tr:hover {
    cursor: pointer;
  }

  .columns {
    display: grid;
    grid-template-columns: 33% 66%;
    grid-template-rows: auto;
    width: 100vw;
  }

  .right-pane.narrow-width {
    display: flex;
    flex-direction: column;
  }

  .right-pane {
    position: relative;
    left: 34vw;
    width: 66vw;
    max-width: 700px;
  }

  .grid {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .grid.qlft {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
  }

  .grid.qlft.one-col {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .text-align-center {
    text-align: center;
  }

  p {
    max-width: 50em;
  }


  .instructions {
    overflow: scroll;
    max-height: 32em;

  }

  h3 {
    padding: 1em;
  }

  input[type='number'] {
    width: 6em;
  }

  .top-container {
    margin-bottom: 5em;
  }
  .top-container > div {
    padding-left: 1em;
    padding-right: 1em;
  }

  .grid.selectedMask.oneCol {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .phone {
    display: none;
  }

  @media(max-width: 1000px) {
    img {
      width: 100vw;
    }

    .instructions p, h4 {
      padding: 1em;
    }

    .call-to-actions {
      height: 14em;
    }

    .edit-facial-measurements {
      flex-direction: column;
    }

    .row.buttons {
      flex-direction: column;
      width: 95vw;
      align-items: center;
    }

    .grid.qlft {
      grid-template-columns: 100%;
    }

    .main, .grid.selectedMask, .grid.selectedMask.oneCol {
      display: grid;
      grid-template-columns: 50% 50%;
      grid-template-rows: auto;
    }

    input[type='text'] {
      width: 82vw;
    }

    .columns {
      grid-template-columns: 100%;
    }

    .phone {
      display: flex;
    }

    .right-pane {
      left: 0;
      display: flex;
      justify-content: center;
      width: auto;
      max-width: none;
    }

  }
</style>
