<template>
  <div class='align-items-center flex-dir-col top-container'>
    <div class='flex align-items-center row phone'>
      <h2 class='tagline'>{{pageTitle}}</h2>
    </div>


    <div class='menu row'>
      <TabSet
        v-if='tabToShow == "QLFT" || tabToShow == "QNFT"'
        :options='secondaryTabToShowOptions'
        @update='setSecondaryTab'
        :tabToShow='secondaryTabToShow'
      />
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
        :comfort="comfort"
        :completedSteps="completedFitTestSteps"
        :currentStep="tabToShow"
        @navigate-to-step="navigateToStep"
      />

      <div v-show='tabToShow == "User"' class='right-pane'>
        <div>
          <h2 class='text-align-center'>User selection</h2>
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
                <td>{{selectedUser.fullName}}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>

      <div v-show='tabToShow == "Mask"' class='main right-pane'>

        <div>
          <h2 class='text-align-center'>Mask Selection</h2>
          <h3 class='text-align-center'>Search for and pick a mask</h3>

          <div class='row justify-content-center'>
            <input type="text" :value='selectedMask && selectedMask.uniqueInternalModelCode' @change='updateSearch($event, "mask")' :disabled='!createOrEdit'>
            <SearchIcon height='2em' width='2em'/>
          </div>

          <h3 v-show="selectMaskDisplayables.length == 0" class='text-align-center'>Not able to find the mask?
            <router-link :to="{name: 'NewMask'}"> Click here to add information about the mask. </router-link>
          </h3>


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
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>

      <div v-show='tabToShow == "Facial Hair"' class='justify-content-center flex-dir-col align-content-center right-pane'>
        <h2 class='text-align-center'>Facial Hair Check</h2>

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
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>

      </div>



      <div v-show='tabToShow == "User Seal Check"' class='justify-content-center flex-dir-col align-content-center right-pane'>
        <h2 class='text-align-center'>User Seal Check</h2>
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
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>
      </div>

      <div v-show='tabToShow == "QLFT"' class='justify-content-center flex-dir-col align-content-center right-pane'>
        <div class='grid qlft'>
          <table v-show='secondaryTabToShow == "Choose Procedure"'>
            <tbody>

              <tr>
                <th>Procedure</th>
                <td>
                  <select v-model='qualitativeProcedure' :disabled='!createOrEdit'>
                    <option>Skipping</option>
                    <option>Full OSHA</option>
                  </select>
                </td>
              </tr>

              <tr v-show='qualitativeProcedure != "Skipping"'>
                <th>Solution</th>
                <td>
                  <select v-model='qualitativeAerosolSolution' :disabled='!createOrEdit'>
                    <option>Saccharin</option>
                    <option>Bitrex</option>
                  </select>
                </td>
              </tr>

              <tr v-show='qualitativeProcedure != "Skipping"'>
                <th>Notes</th>
                <td>
                  <textarea id="" name="" cols="30" rows="10" v-model='qualitativeAerosolNotes' :disabled='!createOrEdit'></textarea>
                </td>
              </tr>
            </tbody>
          </table>

          <div class='instructions' v-show='secondaryTabToShow == "Choose Procedure" && (tabToShow == "QLFT") && qualitativeProcedure == "Full OSHA"'>
            <h3>{{instructionTitle}}</h3>
            <p v-for='text in instructionParagraphs'>
              {{text}}
            </p>
          </div>

          <div class='instructions' v-show='secondaryTabToShow == "Choose Procedure" && tabToShow == "QLFT" && qualitativeProcedure == "Skipping"'>
            <p>
              Qualitative fit testing can be skipped if:
              <ul>
                <li>user seal check failed from the previous step</li>
                <li>user seal check passed and you are going to do quantitative fit testing (QNFT)</li>
              </ul>
            </p>
          </div>


          <table v-show='secondaryTabToShow == "Results"'>
            <tbody >
              <template v-for='(ex, index) in qualitativeExercises' >
                <tr v-if='index < 4'>
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

          <table v-show='secondaryTabToShow == "Results"'>
            <tbody class='qlft'>
              <template v-for='(ex, index) in qualitativeExercises' >
                <tr v-if='index >= 4'>
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

        </div>

        <br>
        <div class='row buttons'>
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
          <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
          <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
        </div>
      </div>

      <div v-show='tabToShow == "QNFT"' class='justify-content-center flex-dir-col align-content-center right-pane'>
        <div class='grid qlft'>
          <table v-show='secondaryTabToShow == "Choose Procedure"'>
            <tbody>

              <tr>
                <th>Procedure</th>
                <td>
                  <select v-model='quantitativeProcedure' :disabled='!createOrEdit'>
                    <option>Skipping</option>
                    <option>OSHA Fast Filtering Face Piece Respirators</option>
                    <option>Full OSHA</option>
                  </select>
                </td>
              </tr>

              <tr>
                <th>Device</th>
                <td>
                  <select v-model='quantitativeFitTestingDeviceId' :disabled='!createOrEdit'>
                    <option v-for='d in measurementDevices' :value='d.id'>
                    {{deviceInfo(d)}}
                    </option>
                  </select>
                </td>
              </tr>

              <tr v-show='quantitativeProcedure != "Skipping"'>
                <th>Testing mode</th>
                <td>
                  <select v-model='quantitativeTestingMode' :disabled='!createOrEdit'>
                    <option>N95</option>
                    <option>N99</option>
                  </select>
                </td>
              </tr>

              <tr v-show='quantitativeProcedure != "Skipping"'>
                <th>Aerosol</th>
                <td>
                  <select v-model='quantitativeAerosolSolution' :disabled='!createOrEdit'>
                    <option>Ambient</option>
                  </select>
                </td>
              </tr>

              <tr v-show='quantitativeProcedure != "Skipping"'>
                <th>Initial count (particles / cm3)</th>
                <td>
                  <input type='number' v-model='initialCountPerCm3' :disabled='!createOrEdit'>
                </td>
              </tr>

              <tr v-show='quantitativeProcedure != "Skipping"'>
                <th>Notes</th>
                <td>
                  <textarea id="" name="" cols="30" rows="10" v-model='quantitativeAerosolNotes' :disabled='!createOrEdit' ></textarea>
                </td>
              </tr>
            </tbody>
          </table>

          <div class='instructions' v-if='secondaryTabToShow == "Choose Procedure" && tabToShow == "QNFT" && quantitativeProcedure == "Skipping"'>
            <p>
              Quantitative fit testing can be skipped if:
              <ul>
                <li>user seal check failed from the previous step</li>
                <li>user seal check passed but you are skipping qualitative fit testing (QLFT)</li>
              </ul>
            </p>
          </div>

          <div class='instructions' v-show='quantitativeProcedure != "Skipping" && secondaryTabToShow != "Results"'>
            <h3>{{instructionTitle}}</h3>
            <p v-for='text in instructionParagraphs'>
              {{text}}
            </p>
          </div>

          <table v-show='secondaryTabToShow == "Results"'>
            <tbody >
              <template v-for='(ex, index) in quantitativeExercises' >
                <tr v-if='index < numExercisesHalf'>
                  <th>{{ex.name}}</th>
                  <td>
                    <CircularButton text="?" @click="showDescription(ex.name)"/>
                  </td>
                  <td>
                    <input type="number" v-model='ex.fit_factor' :disabled='!createOrEdit'>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>

          <table v-show='secondaryTabToShow == "Results"'>
            <tbody >
              <template v-for='(ex, index) in quantitativeExercises' >
                <tr v-if='index >= numExercisesHalf'>
                  <th>{{ex.name}}</th>
                  <td>
                    <CircularButton text="?" @click="showDescription(ex.name)"/>
                  </td>
                  <td>
                    <input type="number" v-model='ex.fit_factor' :disabled='!createOrEdit'>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>

        </div>


      <br>
      <div class='row buttons'>
        <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
        <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
        <Button shadow='true' class='button' text="Save and Continue" @click='validateAndSaveFitTest' v-if='createOrEdit'/>
        <Button shadow='true' class='button' text="Delete" @click='deleteFitTest' v-if='mode == "Edit"'/>
      </div>

    </div>

      <div v-show='tabToShow == "Comfort"' class='justify-content-center flex-dir-col right-pane'>
        <h2 class='text-align-center'>Comfort Assessment</h2>

        <SurveyQuestion
          question="How comfortable is the position of the mask on the nose?"
          :answer_options="['Uncomfortable', 'Unsure', 'Comfortable']"
          @update="selectComfortNose"
          :selected="comfort['How comfortable is the position of the mask on the nose?']"
          :disabled="!createOrEdit"
        />

        <SurveyQuestion
          question="Is there adequate room for eye protection?"
          :answer_options="['Inadequate', 'Adequate', 'Not applicable']"
          @update="selectComfortEyeProtection"
          :selected="comfort['Is there adequate room for eye protection?']"
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
          <Button shadow='true' class='button' text="View Mode" @click='mode = "View"' v-if='mode == "Edit"'/>
          <Button shadow='true' class='button' text="Edit Mode" @click='mode = "Edit"' v-if='!createOrEdit'/>
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

export default {
  name: 'FitTest',
  components: {
    AddingDataToFitTestProgress,
    Button,
    CircularButton,
    ClosableMessage,
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
          text: "QLFT"
        },
        {
          text: "QNFT"
        },
        {
          text: "Comfort",
        },
      ],
      oshaFastFFRExercises: {
        'Bending over': {
          'description': 'The test subject shall bend at the waist, as if going to touch his/her toes for 50 seconds and inhale 2 times at the bottom.',
        },
        'Talking': {
          'description': 'The subject shall talk out loud slowly and loud enough so as to be heard clearly by the test conductor. The subject can read from a prepared text such as the Rainbow Passage, count backward from 100, or recite a memorized poem or song.  Rainbow Passage: When the sunlight strikes raindrops in the air, they act like a prism and form a rainbow. The rainbow is a division of white light into many beautiful colors. These take the shape of a long round arch, with its path high above, and its two ends apparently beyond the horizon. There is, according to legend, a boiling pot of gold at one end. People look, but no one ever finds it. When a man looks for something beyond reach, his friends say he is looking for the pot of gold at the end of the rainbow.'
        },
        'Head side-to-side': {
          'description': "The test subject shall stand in place, slowly turning his/her head from side to side for 30 seconds and inhale 2 times at each extreme."
        },
        'Head up-and-down': {
          'description': "The test subject shall stand in place, slowly moving his/her head up and down for 39 seconds and inhale 2 times at each extreme."
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
        "Is there adequate room for eye protection?": null,
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
      if (this.quantitativeProcedure == 'Full OSHA') {
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

      return this.fitTestingInstructions[this.tabToShow][this.aerosol].title
    },
    instructionParagraphs() {
      if (!this.aerosol) {
        return
      }

      return this.fitTestingInstructions[this.tabToShow][this.aerosol].paragraphs
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
        quantitative_fit_testing_device_id: this.quantitativeFitTestingDeviceId,
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
      if (this.searchMask == "") {
        return this.masks
      } else {
        let lowerSearch = this.searchMask.toLowerCase()
        return this.masks.filter((mask) => mask.uniqueInternalModelCode.toLowerCase().match(lowerSearch))
      }
    },
    selectMaskDisplayables() {
      let lengthToDisplay = 6
      if (this.maskDisplayables.length < 6) {
        lengthToDisplay = this.maskDisplayables.length
      }

      return this.maskDisplayables.slice(0, lengthToDisplay)
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

      // Check QLFT completion (simplified check)
      if (this.qualitativeProcedure && this.qualitativeProcedure !== 'Skipping') {
        completed.push('QLFT')
      }

      // Check QNFT completion (simplified check)
      if (this.quantitativeProcedure && this.quantitativeProcedure !== 'Skipping') {
        completed.push('QNFT')
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

            successCallback = function () {
              this.$router.push({
                name: 'FitTests',
                query: {
                  managedId: managedUser.managedId
                }
              })
            }.bind(this)
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
            this.tabToShow = toQuery['tabToShow']
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

      this.messages.push(
        {
          str: this.oshaExercises[name].description
        }
      )
    },
    updateSearch(event, userOrMask) {
      if (userOrMask == 'mask') {
        this.selectedMask = {
          'uniqueInternalModelCode': null
        }
        this.searchMask = event.target.value
      } else {
        this.selectedUser = new RespiratorUser({
        })
        this.searchUser = event.target.value
      }
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
      this.selectedUser = this.managedUsers.filter((m) => m.managedId == id)[0]
      this.searchUser = this.selectedUser.fullName
    },
    async loadMasks() {
      // TODO: make this more flexible so parents can load data of their children
      await axios.get(
        `/masks.json`,
      )
        .then(response => {
          let data = response.data
          if (response.data.masks) {
            this.masks = deepSnakeToCamel(data.masks)
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

            this.quantitativeFitTestingDeviceId = fitTestData.quantitative_fit_testing_device_id

            this.qualitativeAerosolSolution = results.qualitative.aerosol.solution
            this.qualitativeNotes = results.qualitative.notes
            this.qualitativeProcedure = results.qualitative.procedure
            this.qualitativeExercises = results.qualitative.exercises

            this.quantitativeTestingMode = results.quantitative.testing_mode
            this.quantitativeAerosolSolution = results.quantitative.aerosol.solution
            this.quantitativeNotes = results.quantitative.notes
            this.quantitativeProcedure = results.quantitative.procedure

            this.setQuantitativeExercises(results.quantitative.exercises)
            this.initialCountPerCm3 = results.quantitative.aerosol.initial_count_per_cm3

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
                    tabToShow: 'QNFT',
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
      if (this.quantitativeProcedure != 'Skipping' && !this.quantitativeFitTestingDeviceId) {
        this.messages.push(
          {
            str: `Please choose a quantitative fit testing device. If you'd like to add one not currently listed, see "Measurement Devices" section'`,
            to: {
              name: "MeasurementDevices"
            }
          }
        )
      }
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
        this.validatePresenceOfDevice()
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
        this.validateUserSealCheck()

        if (this.messages.length == 0) {
          await this.saveFitTest({
            tabToShow: 'QLFT',
            secondaryTabToShow: 'Choose Procedure'
          })

          // Save first before potentially displaying this message
          if (!this.userSealCheckPassed) {
            this.messages.push(
              {
                str: "User seal check failed. You may skip adding qualitative or quantitative fit testing data, along with comfort data if you wish, by clicking here.",
                to: {
                  'name': 'FitTests'
                }
              }
            )
          }
        } else {
          return
        }

      }

      else if (this.tabToShow == 'QLFT' && this.secondaryTabToShow == 'Choose Procedure') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()
        this.validateQLFT('Choose Procedure')

        if (this.qualitativeProcedure == 'Skipping') {
          await this.saveFitTest(
            {
              tabToShow: 'QNFT',
              secondaryTabToShow: 'Choose Procedure'
            }
          )
        }
        else if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'QLFT',
              secondaryTabToShow: 'Results'
            }
          )
        } else {
          return
        }
      }

      else if (this.tabToShow == 'QLFT' && this.secondaryTabToShow == 'Results') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()
        this.validateQLFT('Results')

        if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'QNFT',
              secondaryTabToShow: 'Choose Procedure'
            }
          )


          if (this.qualitativeHasAFailure) {
            this.messages.push(
              {
                str: "QLFT has a failure. You may skip adding quantitative fit testing data and comfort data if you wish, by clicking here.",
                to: {
                  'name': 'FitTests'
                }
              }
            )

          }
        } else {
          return
        }
      }
      else if (this.tabToShow == 'QNFT' && this.secondaryTabToShow != 'Results') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()
        this.validateQLFT()
        this.validatePresenceOfDevice()

        this.validatePresenceOfInitialCountPerCM3()
        this.validateValueOfInitialCountPerCM3()
        this.validateQLFTorQNFTExists()


        if (this.messages.length == 0) {
          if (this.quantitativeProcedure == 'Skipping') {
            await this.saveFitTest(
              {
                tabToShow: 'Comfort',
              }
            )
          } else {
            await this.saveFitTest(
              {
                tabToShow: 'QNFT',
                secondaryTabToShow: 'Results'
              }
            )
          }
        } else {
          return
        }
      }

      else if (this.tabToShow == 'QNFT' && this.secondaryTabToShow == 'Results') {
        this.validateUser()
        this.validateMask()
        this.validateUserSealCheck()
        this.validateQLFT()
        this.validateQNFT()
        this.validateQLFTorQNFTExists()

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
        this.validateQLFTorQNFTExists()
        this.validateComfort()

        if (this.messages.length == 0) {
          await this.saveFitTest(
            {
              tabToShow: 'Comfort',
            }
          )

          this.$router.push({
            name: 'FitTests'
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
    selectBeardLength(value) {
      this['facialHair']['beard_length_mm'] = value
    },
    selectBeardCoverTechnique(value) {
      this['facialHair']['beard_cover_technique'] = value
    },
    selectComfortNose(value) {
      this['comfort']['How comfortable is the position of the mask on the nose?'] = value
    },
    selectComfortEyeProtection(value) {
      this['comfort']['Is there adequate room for eye protection?'] = value
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
    setRouteTo(opt) {
      let query = JSON.parse(JSON.stringify(this.$route.query))

      query = Object.assign(query, {
        tabToShow: opt.name
      })

      this.$router.push({
        name: this.$route.name,
        query: query
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
      })
    },
    setSecondaryTab(opt) {
      this.$router.push({
        name: this.$route.name,
        query: {
          tabToShow: this.$route.query.tabToShow,
          secondaryTabToShow: opt.name
        }
      })
    },
  }
}
</script>

<style scoped>
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
    padding: 1em 0;
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
  }

  .right-pane {
    position: relative;
    left: 20%;
    display: flex;
    flex-direction: column;
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

  @media(max-width: 700px) {
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
    }

    .grid.qlft {
      grid-template-columns: 100%;
    }

    .main, .grid.selectedMask, .grid.selectedMask.oneCol {
      display: grid;
      grid-template-columns: 100%;
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

  }
</style>
