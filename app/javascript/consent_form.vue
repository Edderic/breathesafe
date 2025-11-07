<template>

  <router-link :to="tocPath('toc')">
    <CircularButton text="TOC" class='toc-button'/>
  </router-link>

  <div class='grid'>
    <div class='toc margined overflow' id='toc'>
      <br>
      <br>
      <br>
      <div  ><br></div><h2 ><strong>TABLE OF CONTENTS</strong></h2><div  ><br></div>


      <router-link :to="tocPath('invitation-to-participate')">
        Invitation to participate
      </router-link>

      <router-link :to="tocPath('why-study')">
        Why is this study being done?
      </router-link>

      <router-link :to="tocPath('who-can-participate')">
        Who can participate?
      </router-link>

      <router-link :to="tocPath('study-procedures')">
        What are the study procedures?
      </router-link>

      <router-link :to="tocPath('how-long-study')">
        How long will you be in this study?
      </router-link>

      <router-link :to="tocPath('leave-study')">
        Can participants choose to leave the study?
      </router-link>

      <router-link :to="tocPath('risks-harms')">
        What are the risks and harms of participating in the study?
      </router-link>

      <router-link :to="tocPath('benefits')">
        What are the benefits of participating in this study?
      </router-link>

      <router-link :to="tocPath('privacy')">
        How will participants' privacy be protected?
      </router-link>

      <router-link :to="tocPath('data-use-over-time')">
        How long will the data be used?
      </router-link>

      <router-link :to="tocPath('compensation')">
        Are participants compensated in this study?
      </router-link>

      <router-link :to="tocPath('participant-rights')">
        What are the rights of the participants?
      </router-link>

      <router-link :to="tocPath('reach-out')">
        Whom do participants contact for questions?
      </router-link>

      <router-link :to="tocPath('onboarding')">
        Do you have more details about the data collection process?
      </router-link>
      <br>
      <br>
      <br>

    </div>

    <div class='margined main'>
      <h2>Mask recommender based on facial measurements</h2>

      <div class='row'>
        <h4 for="">Principal Investigator</h4>

        <div>
          Edderic Ugaddan
        </div>
        <div>
          Owner, Breathesafe LLC
        </div>
        <div>
          info@breathesafe.xyz
        </div>
        <div>
          138 Miller Ave.
        </div>
        <div>
          Rumford, RI 02916
        </div>
      </div>

      <div>
        <p>Last updated: Oct. 10, 2025</p>
      </div>
        <div id='invitation-to-participate'>
          <br>
          <br>
          <h4>Invitation to Participate</h4>
        </div>

        <p>You are being invited to participate in this research study to create a mask recommender based on facial features.</p>

        <div id='why-study'>
          <br>
          <br>
          <h4>Why is this study being done?</h4>
        </div>

        <p>
        As of this time, it is not that easy to find high protection masks for
        some people.

        Protection is a combination of high filtration efficiency and fit.
        Lots of work has been done on vetting the filtration efficiency side. However,
        without a good fitting mask, the efficacy of high filtration masks can
        be severely diminished.

        To find masks that fit well, there is still a bunch of trial and error
        involved. We want to make the search for masks that do both (high
        filtration efficiency and good fit) simpler and easier. For more
        details, please see the <a
        href="https://docs.google.com/document/d/1XZ2foY_cpDYImOBE5P048byj1jqLZ5JHdif6rfx3HAU/edit#heading=h.akrinhrxttzu">Respirator
        Recommender proposal</a>.

        </p>

        <div id='who-can-participate'>
          <br>
          <br>
          <h4>Who can participate?</h4>
        </div>

        <p>
        As a participant, you will need access to the following:
        </p>

        <div class='grid-images'>
          <figure>
            <a href="https://aiden.health/products/makrite-801" target='_blank'>
              <img class='left-pane-image' src="https://aiden.health/cdn/shop/files/766B9B3B-9325-407B-B94E-E4C41C6207BB_710x589@2x.png?v=1718600885" alt='Makrite 801-N95 (adj. head straps), NIOSH 84A-9223, 160mmHg fluid resistance'>
            </a>
            <figcaption>A Mask</figcaption>
          </figure>

          <figure>
            <a href="https://www.verizon.com/smartphones/apple-iphone-14/" target='_blank'>
              <img class='left-pane-image' src="https://ss7.vzw.com/is/image/VerizonWireless/iphone-14-midnight-fall22-a?wid=930&hei=930&fmt=webp" alt='An iPhone'>
            </a>
            <figcaption>A device equipped with a camera</figcaption>
          </figure>
        </div>

        <p>
        ...and either quantitative or qualitative fit testing equipment:
        </p>

        <div class='grid-images'>
          <figure>
            <a href="https://tsi.com/discontinued-products/portacount%C2%AE-respirator-fit-tester-8038/" target='_blank'>
              <img class='left-pane-image' src="https://tsi.com/getmetafile/a296129e-5e8d-48d6-a3a7-05a2d5195987/8038_01" alt='PortaCount'>
            </a>
            <figcaption>A Quantitative Fit Testing device such as a PortaCount</figcaption>
          </figure>

          <figure>
            <a href="https://www.youtube.com/watch?v=Syj_zeNtLGI" target='_blank'>
              <img class='left-pane-image' src="https://profittesting.com/cdn/shop/articles/MelFitTest4blog2.jpg?v=1634512473" alt='Tape Measure, iBayam Soft Ruler Measuring Tape for Body Weight Loss Fabric Sewing Tailor Cloth Vinyl Measurement Craft Supplies, 60-Inch Double Scale Ruler, 2-Pack White, Blue'>
            </a>
            <figcaption>Qualitative Fit Testing equipment</figcaption>
          </figure>

        </div>

        <p>
        If you are interested in becoming a participant, missing at least one of the required equipment, and live close to Breathesafe LLC's address, you may be able to borrow equipment to do the study. Please email <a href="mailto:info@breathesafe.xyz?subject=Mask Recommender Question">info@breathesafe.xyz</a> to inquire about the possibility.
        </p>

        <p>
        You can contribute valuable data by submitting <a
          href="https://www.cdc.gov/niosh/docs/2018-130/pdfs/2018-130.pdf"
          target='_blank'>user seal check</a> information. If you know that a
        mask does not fit your face and has obvious leaks, you could contribute
        this data in the User Seal Check section of "Adding a Fit Test".
        </p>

        <div id='study-procedures'>
          <br>
          <br>
          <h4>What are the study procedures?</h4>
        </div>


        <h5>Acquiring facial measurements</h5>

        <p>To get facial measurements quickly and seamlessly, the study requires access to an iPhone True Depth camera (i.e. has FaceID feature -- standard in the recent base models, iPhone X model onward). You will be able to install an application made by Breathesafe LLC (currently being developed), or if you live close enough to the address of Breathesafe LLC, you may be able to borrow an iPhone for the purposes of obtaining facial measurements. The app will store facial measurements relevant to mask fitting, and will be sent to Breathesafe's secure server for storage for creation and improvement of statistical model to predict fit based on facial measurements.
        </p>

        <h5>Demographics</h5>

        <p>
        You will be asked to give information about demographics. See the <router-link :to="tocPath('privacy')">data privacy section</router-link> to learn more.
        Once that is filled out, you can add the following fit testing data:
        </p>

        <h5>Fit Testing</h5>
        <ul>
          <li>user seal check</li>
          <li>qualitative fit testing (if applicable)</li>
          <li>quantitative fit testing (if applicable)</li>
          <li>comfort</li>
        </ul>

        <p>
        You will be guided by the UI. Clicking on the "Save and Continue" button will validate the information being saved and will show helpful error messages and general messages. For example, if a user fails the user seal check section, they don't need to add qualitative or quantitative fit testing data (as it is assumed that they will most likely fail either of those more stringent tests).
        </p>


        <div id='how-long-study'>
          <br>
          <br>
          <h4>How long will you be in this study?</h4>
        </div>

        In terms of adding data to the system, it can vary, depending on
        whether or not you have access to qualitative fit testing (QLFT) or
        quantitative fit testing (QNFT) devices.
        <table>
          <thead>
            <tr>
              <th>Steps</th>
              <th>Time commitment</th>
              <th>Frequency</th>
              <th>Necessity</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Answering demographics questions</td>
              <td>1 minute</td>
              <td>once</td>
              <td>Necessary</td>
            </tr>
            <tr>
              <td>Adding facial measurements manually</td>
              <td>3 minutes</td>
              <td>once, or over the years</td>
              <td>Necessary</td>
            </tr>
            <tr>
              <td>Adding user seal check data</td>
              <td>1 minute</td>
              <td>per mask</td>
              <td>Necessary</td>
            </tr>
            <tr>
              <td>Adding qualitative fit testing data</td>
              <td>10 minutes</td>
              <td>per mask</td>
              <td>Depends on you having access to QLFT tools</td>
            </tr>
            <tr>
              <td>Adding quantitative fit testing data</td>
              <td>5 minutes</td>
              <td>per mask</td>
              <td>Depends on you having access to a QNFT device</td>
            </tr>
            <tr>
              <td>Adding comfort data</td>
              <td>1 minute</td>
              <td>per mask</td>
              <td>Can be skipped if user seal check fails.</td>
            </tr>
          </tbody>
        </table>

        <div id='leave-study'>
          <br>
          <br>
          <h4>Can participants choose to leave the study?</h4>
        </div>
        <p>Participants may be able to delete their data by visiting the
        <router-link :to='{name: "RespiratorUsers"}'>
          Respirator Users
        </router-link> section, and clicking on an individual they have access
        to, click "Edit" and then click "Delete." This functionality is
        available for people who have gone through the registration process.
        That will delete user information such as email, password,
        demographics, and fit testing data. Users will have the ability to
        delete their data and have their data not contribute to research until
        publication (which is TBD). Deletion of data in the future will have no
        effect to the state of previously published research, but may alter
        existing statistical machine learning models that are being used at the
        time on the web application.

        </p>

        <div id='risks-harms'>
          <br>
          <br>
          <h4>What are the risks and harms of participating in the study?</h4>
        </div>
        <p>Sensitive data like facial measurements will be stored in a database.
        Data such as the following will be collected:
        <ul>
          <li>first name</li>
          <li>last name</li>
          <li>email</li>
          <li>home address (optional) - If you need financial assistance with buying equipment for testing purposes. Breathesafe LLC can order equipment on your behalf and send them your way. See the <a href="#compensation">compensation</a> section for details.</li>
          <li>facial measurement data - to create a recommendation system tailored to the individual.</li>
          <li>fit testing measurement tools used (e.g. PortaCount)</li>
          <li>fit testing results (e.g. pass/fail for Qualitative Fit Testing, fit factors for Quantitative Fit Testing)</li>
        </ul>
        </p>

        <p>
          To protect your sensitive data, Breathesafe uses <a href='https://guides.rubyonrails.org/active_record_encryption.html'>application-level encryption</a>
          to minimize risk in the unlikely event of a data breach. Further, you can make use of an alias (i.e. first name, last name, email that does not reference your real names) to mitigate risk even further.
        </p>

        <p>With respect to facial measurements, only the minimal amount related to mask fitting will be recorded (e.g. nose, cheek, chin measurements).</p>

        <div id='benefits'>
          <br>
          <br>
          <h4>What are the benefits of participating in this study?</h4>
        </div>

        <p>One direct benefit is one might be able to find a mask that has overall high protection (combination of fit and high filtration efficiency), if they haven't aready. Another benefit is gaining a sense of accomplishment in helping others find masks that offer high protection for their faces by providing data that will be used to improve performance of a personalized recommender system.</p>

        <div id='privacy'>
          <br>
          <br>
          <h4>How will participants' privacy be protected?</h4>
        </div>

        <h4>First name, Last name, Email</h4>
        <p>Strictly confidential and will not be displayed on the app. However, study participants can are encouraged to make use of aliases for enhanced protection in the very unlikely, but non-zero probability, event of a data breach.</p>

        <h4>Data aggregation</h4>
        <p> In terms
        of data publicly displayed on this web app, demographic information will
        only be shown in aggregate. We will preserve privacy
        of individuals in the aggregation of the data: if a demographic has
        less than 5 people in it, they will be automatically grouped in the "Prefer not to
        disclose / too small sample size" group.
        </p>

        <h4>Facial measurements and Fit Testing Data</h4>
        <p>

        Facial measurements and fit testing data could be displayed in scatter plots to help future users understand the weaknesses of the model in predicting fit. For example, let's say an individual is looking to find a mask that fits their face. Let's say the model says 70% probability of fit for a particular mask, and the user is interested in getting more context about this prediction. The user could take a look at scatter plots to have a better understanding of this number (i.e. are there a bunch of data points that are similar to user's that have passed with this mask?)

        </p>

        <p>This study may go on indefinitely. If for any reason you want your data deleted, you may do so. See
<router-link :to="tocPath('leave-study')"> Can participants choose to leave the study?</router-link>
        section above for details.</p>

        <p>
        Breathesafe LLC will follow best security practices to prevent malicious actors from accessing said database. Example of such actions are:
        <ul>
          <li>using application-level encryption.</li>
          <li>using https to prevent man-in-the-middle attacks.</li>
          <li>admins will be using password managers and two factor authentication.</li>
          <li>number of admins will be as small as possible to limit risk.</li>
        </ul>
        </p>

        <p>Users could also choose to be anonymous when signing up. They are
        free to use fake names to decrease the risk of their biometric data
        identifying them in the small but non-zero chance that a hacker gets a
        hold of the database.</p>

        <div id='data-use-over-time'>
          <br>
          <br>
          <h4>How long will the data be used?</h4>
        </div>

        <p>Data could be stored indefinitely. Models might get refined over time, which uses the data.</p>

        <div id='compensation'>
          <br>
          <br>
          <h4>Are participants compensated in this study?</h4>
        </div>

        <p>Participation in this study is on a voluntary basis. However, if you need financial assistance with getting the equipment or labor, please let us know by emailing <a href='subject=Mask Recommender Financial Assistance Question'>info@breathesafe.xyz</a>.
        </p>

        <p>Here are things we can help with, provided you live close by to the Breathesafe LLC address:</p>

        <ul>
          <li>buying masks</li>
          <li>buying probes</li>
          <li>buying qualitative fit testing equipment</li>
          <li>access to an iPhone with True Depth camera</li>
          <li>paying for your time to do the testing</li>
        </ul>

        <div id='participant-rights'>
          <br>
          <br>
          <h4> What are the rights of the participants? </h4>
        </div>

        <p>Your participation in this study is voluntary. You may decide not to
        be in this study. Even if you consent to participate, you have the
        right to withdraw and delete your data later on. See the

        <router-link :to="tocPath('leave-study')">Can participants choose to leave the study?</router-link> section for details.
</p>

        <div id='reach-out'>
          <br>
          <br>
          <h4>Whom do participants contact for questions?</h4>
        </div>

        <p>You may reach out to <a href="mailto:info@breathesafe.xyz?subject=Mask Recommender Question">info@breathesafe.xyz</a>. For general questions and discussion, you could also join this <a href="https://discord.com/channels/1220937763751465001/1249885817724473485">Discord group</a>.</p>
      <br>
      <br>
      <br>
      <br>
      <br>

      <div id='onboarding'>
        <br>
        <br>
        <h4>Do you have more details about the data collection process?</h4>
      </div>

      <p>
      Please visit the <router-link to="/onboarding#onboarding">onboarding page</router-link> to learn more about details.
      </p>
      <br>
      <br>
      <br>
      <br>
      <br>

      <div></div>
      <br>
      <br>
      <br>
      <br>

    </div>
  </div>

  <Popup v-if='showInfoPopup' @onclose='showInfoPopup = false'>
    <div>
      <h3>We updated our Consent Form</h3>
      <p>
        You are seeing this because your accepted version does not match the
        latest version ({{ infoVersion }}). Please review the consent
        form below. You can accept to continue sharing your data for research
        purposes, or reject and continue using the app.
      </p>
    </div>
  </Popup>

  <Popup v-if='showThanksPopup' @onclose='closeThanks'>
    <p>Thank you for giving consent. Have a great day!</p>
  </Popup>

  <Popup v-if='showRejectConfirm' @onclose='showRejectConfirm = false'>
    <div>
      <h3>Are you sure?</h3>
      <div class='row'>
        <Button class='cancel' @click='showRejectConfirm = false'>Cancel</Button>
        <Button class='confirm' @click='confirmReject'>Yes</Button>
      </div>
    </div>
  </Popup>

  <Popup v-if='showRejectInfo' @onclose='dismissRejectInfo'>
    <p>
      You could go to the Respirator Users page
      <router-link :to="{ name: 'RespiratorUsers' }">(link)</router-link>, click on each of the users you manage, hit edit, and delete their data. That will delete facial measurements, demographics, fit tests, etc.
    </p>
  </Popup>

  <div v-if='showConsentActions' class='consent-bottom-actions'>
    <Button class='accept' @click='onAccept'>Accept</Button>
    <Button class='reject' @click='onReject'>Reject</Button>
  </div>

</template>
<script>

import CircularButton from './circular_button.vue';
import Button from './button.vue';
import Popup from './pop_up.vue';
import axios from 'axios';
import { mapActions, mapState } from 'pinia';
import { useMainStore } from './stores/main_store';

export default {
  name: 'ConsentForm',
  components: {
    CircularButton,
    Button,
    Popup,
  },
  data() {
    return {
      showInfoPopup: false,
      showThanksPopup: false,
      showRejectConfirm: false,
      showRejectInfo: false,
      infoVersion: '',
    }
  },
  props: { },
  computed: {
    ...mapState(useMainStore, ['currentUser', 'consentFormVersion']),
    showConsentActions() {
      return !!this.currentUser && !!this.consentFormVersion && this.currentUser.consent_form_version_accepted !== this.consentFormVersion;
    }
  },
  async mounted() {
    await this.getCurrentUser();
    const needsInfo = !!this.currentUser && !!this.consentFormVersion && this.currentUser.consent_form_version_accepted !== this.consentFormVersion;
    if (needsInfo) {
      this.showInfoPopup = true;
      this.infoVersion = this.$route.query.latest_version || this.consentFormVersion || '';
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'setConsentDismissedForSession']),
    tocPath(suffix) {
      return `/consent_form#${suffix}`
    },
    async onAccept() {
      await this.getCurrentUser();
      if (!this.currentUser) { return }
      try {
        const response = await axios.post('/users/consent', { decision: 'accept' });
        if (response.status >= 200 && response.status < 300) {
          this.showThanksPopup = true;
        }
      } catch (e) {
        console.error(e);
      }
    },
    async onReject() {
      this.showRejectConfirm = true;
    },
    async confirmReject() {
      try {
        await axios.post('/users/consent', { decision: 'reject' });
      } catch (e) {
        console.error(e);
      }
      this.showRejectConfirm = false;
      this.showRejectInfo = true;
    },
    closeThanks() {
      this.showThanksPopup = false;
      // Mark consent screen dismissed for this session and return to target
      this.setConsentDismissedForSession(true);
      const name = this.$route.query.return_to_name || 'Landing';
      let params = {};
      let query = {};
      try { params = JSON.parse(this.$route.query.return_to_params || '{}') } catch {}
      try { query = JSON.parse(this.$route.query.return_to_query || '{}') } catch {}
      this.$router.replace({ name, params, query });
    },
    dismissRejectInfo() {
      this.showRejectInfo = false;
      // Allow the user to continue using the app; mark dismissed for session
      this.setConsentDismissedForSession(true);
      const name = this.$route.query.return_to_name || 'Landing';
      let params = {};
      let query = {};
      try { params = JSON.parse(this.$route.query.return_to_params || '{}') } catch {}
      try { query = JSON.parse(this.$route.query.return_to_query || '{}') } catch {}
      this.$router.replace({ name, params, query });
    }
  }
}
</script>
<style scoped>
  .consent-bottom-actions {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
    z-index: 1002;
  }

  .consent-bottom-actions .accept {
    background: #2e7d32;
    color: white;
  }

  .consent-bottom-actions .reject {
    background: #c62828;
    color: white;
  }
  .margined {
    margin: 1em;
  }

  .toc {
    width: 35vw;
    position: fixed;
    top: 0;
    display: flex;
    flex-direction: column;
    height: 90vh;
  }

  .grid {
    display: grid;
    grid-template-columns: 35vw 65vw;
    justify-content: center;
  }

  .grid-images {
    display: grid;
    grid-template-columns: 33% 33% 33%;
    grid-template-rows: auto;
  }

  .main {
    margin-left: 35vw;
    width: 60vw;
  }

  .overflow {

    overflow: auto;
  }

  .toc-button {
    position: fixed;
    right: 1em;
    top: 4em;
  }

  .left-pane-image {
    max-width: 15em;
  }

  @media(min-width: 1200px) {
    .toc-button {
      display: none;
    }

  }
  @media(max-width: 1200px) {
    .left-pane-image {
      max-width: 8em;
    }
    .grid {
      display: flex;
      flex-direction: column;
    }

    .toc {
      position: relative;
      width: 75vw;
    }

    .main {
      width: 75vw;
      margin-left: 0;
    }

  }

  .tos-header {
    display: flex;
    flex-direction: row;
    width: 100%;
  }

  th, td {
    padding: 0.5em;
  }

</style>
