<template>
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

  <router-link to="/consent_form#toc-mobile">
    <CircularButton text="TOC" class='toc-button'/>
  </router-link>

<div class="container">
  <!-- Mobile TOC - shown at top on mobile -->
  <div class='toc toc-mobile margined' id='toc-mobile'>
    <h2><strong>TABLE OF CONTENTS</strong></h2>

    <router-link to="/consent_form#top">
      CONSENT FORM: MASK RECOMMENDER BASED ON FACIAL MEASUREMENTS
    </router-link>

    <router-link to="/consent_form#invitation-to-participate">
      INVITATION TO PARTICIPATE
    </router-link>

    <router-link to="/consent_form#why-is-this-project-being-done">
      WHY IS THIS PROJECT BEING DONE?
    </router-link>

    <router-link to="/consent_form#who-can-participate">
      WHO CAN PARTICIPATE?
    </router-link>

    <router-link to="/consent_form#study-procedures">
      WHAT ARE THE STUDY / PROJECT PROCEDURES?
    </router-link>

    <router-link to="/consent_form#baseline-app-use">
      BASELINE APP USE (NOT RESEARCH)
    </router-link>

    <router-link to="/consent_form#optional-research-participation">
      OPTIONAL RESEARCH PARTICIPATION (OPT-IN)
    </router-link>

    <router-link to="/consent_form#information-collected">
      WHAT INFORMATION MAY BE COLLECTED?
    </router-link>

    <router-link to="/consent_form#data-retention">
      HOW LONG WILL THE DATA BE USED?
    </router-link>

    <router-link to="/consent_form#can-participants-leave">
      CAN PARTICIPANTS CHOOSE TO LEAVE?
    </router-link>

    <router-link to="/consent_form#risks-of-participation">
      WHAT ARE THE RISKS OF PARTICIPATION?
    </router-link>

    <router-link to="/consent_form#benefits-of-participation">
      WHAT ARE THE BENEFITS OF PARTICIPATION?
    </router-link>

    <router-link to="/consent_form#privacy-protection">
      HOW IS PRIVACY PROTECTED?
    </router-link>

    <router-link to="/consent_form#compensation">
      ARE PARTICIPANTS COMPENSATED?
    </router-link>

    <router-link to="/consent_form#participant-rights">
      WHAT ARE THE RIGHTS OF PARTICIPANTS?
    </router-link>

    <router-link to="/consent_form#contact">
      WHO CAN I CONTACT WITH QUESTIONS?
    </router-link>
  </div>

<div class="grid">

  <div class='toc toc-desktop margined overflow' id='toc'>
    <br>
    <br>
    <br>
      <div><br></div><h2><strong>TABLE OF CONTENTS</strong></h2><div><br></div>

      <router-link to="/consent_form#top">
        CONSENT FORM: MASK RECOMMENDER BASED ON FACIAL MEASUREMENTS
      </router-link>

      <router-link to="/consent_form#invitation-to-participate">
        INVITATION TO PARTICIPATE
      </router-link>

      <router-link to="/consent_form#why-is-this-project-being-done">
        WHY IS THIS PROJECT BEING DONE?
      </router-link>

      <router-link to="/consent_form#who-can-participate">
        WHO CAN PARTICIPATE?
      </router-link>

      <router-link to="/consent_form#study-procedures">
        WHAT ARE THE STUDY / PROJECT PROCEDURES?
      </router-link>

      <router-link to="/consent_form#baseline-app-use">
        BASELINE APP USE (NOT RESEARCH)
      </router-link>

      <router-link to="/consent_form#optional-research-participation">
        OPTIONAL RESEARCH PARTICIPATION (OPT-IN)
      </router-link>

      <router-link to="/consent_form#information-collected">
        WHAT INFORMATION MAY BE COLLECTED?
      </router-link>

      <router-link to="/consent_form#data-retention">
        HOW LONG WILL THE DATA BE USED?
      </router-link>

      <router-link to="/consent_form#can-participants-leave">
        CAN PARTICIPANTS CHOOSE TO LEAVE?
      </router-link>

      <router-link to="/consent_form#risks-of-participation">
        WHAT ARE THE RISKS OF PARTICIPATION?
      </router-link>

      <router-link to="/consent_form#benefits-of-participation">
        WHAT ARE THE BENEFITS OF PARTICIPATION?
      </router-link>

      <router-link to="/consent_form#privacy-protection">
        HOW IS PRIVACY PROTECTED?
      </router-link>

      <router-link to="/consent_form#compensation">
        ARE PARTICIPANTS COMPENSATED?
      </router-link>

      <router-link to="/consent_form#participant-rights">
        WHAT ARE THE RIGHTS OF PARTICIPANTS?
      </router-link>

      <router-link to="/consent_form#contact">
        WHO CAN I CONTACT WITH QUESTIONS?
      </router-link>

      <br>
      <br>
      <br>

    </div>
    <div class="margined main">
      <br>
      <br>
      <br>
      <div id="top">
      <br>
      <br>
      <br>
      <div class="styles-documentPreviewer-881656"><div><span class="document-previewer-logo-d16635"></span><div class="document-previewer-wrapper-a717db">      <div data-custom-class="body">
      <div><strong><span style="font-size: 26px;"><span data-custom-class="title">CONSENT FORM: MASK RECOMMENDER BASED ON FACIAL MEASUREMENTS (SNAPFIT / BREATHESAFE)</span></span></strong></div>
      <div><br></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text"><strong>Principal Investigator:</strong> Edderic Ugaddan</span></span></span></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Owner, Breathesafe LLC</span></span></span></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Email: info@breathesafe.xyz</span></span></span></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Registered in Nevada, United States</span></span></span></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Principal place of business / mailing address:</span></span></span></div>
      <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">138 Miller Ave., Rumford, RI 02916, United States</span></span></span></div>
      <div><br></div>
      <div><span style="color: rgb(127, 127, 127);"><strong><span style="font-size: 15px;"><span data-custom-class="subtitle">Last updated December 13, 2025</span></span></strong></span></div>
      <div><br></div>

      <!-- Section: Invitation to Participate -->
      <div id="invitation-to-participate">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">INVITATION TO PARTICIPATE</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You are being invited to participate in a project to improve a <strong>mask recommender based on facial features</strong>. Participation is voluntary.</span></span></span></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may use the SnapFit application <strong>without participating in research</strong>. Research participation is optional and requires explicit opt-in.</span></span></span></div>
      </div>

      <!-- Section: Why is this project being done? -->
      <div id="why-is-this-project-being-done">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHY IS THIS PROJECT BEING DONE?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">High-protection respirators work best when both filtration efficiency and <strong>fit</strong> are high. While filtration efficiency is well studied, identifying which masks fit a given face often requires trial and error. The goal of this project is to make it easier for people to find masks that are more likely to fit their face.</span></span></span></div>
      </div>

      <!-- Section: Who can participate? -->
      <div id="who-can-participate">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHO CAN PARTICIPATE?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">SnapFit can be used by:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Adults (18+)</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Minors <strong>with parent or guardian consent and supervision</strong></span></span></span></li>
        </ul>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">To participate in optional research contributions, you must:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Have access to an iOS device with a TrueDepth camera (Face ID–capable), and</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Provide informed consent (or parent/guardian consent, where applicable).</span></span></span></li>
        </ul>
      </div>

      <!-- Section: Study procedures -->
      <div id="study-procedures">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHAT ARE THE STUDY / PROJECT PROCEDURES?</span></span></strong></div>
        <div><br></div>

        <!-- Subsection: Baseline app use -->
        <div id="baseline-app-use">
          <div><strong><span style="font-size: 16px;"><span data-custom-class="heading_2">Baseline app use (not research)</span></span></strong></div>
          <div><br></div>
          <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">If you use SnapFit only for recommendations:</span></span></span></div>
          <ul>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">The app may request access to the iOS TrueDepth camera.</span></span></span></li>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Facial characteristics relevant to respirator fit are converted into <strong>derived numeric measurements</strong>.</span></span></span></li>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">These derived measurements are sent securely to Breathesafe servers to generate mask-fit recommendations.</span></span></span></li>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Raw facial images or full face scans are <strong>not required to be stored</strong> for baseline functionality.</span></span></span></li>
          </ul>
        </div>

        <!-- Subsection: Optional research participation -->
        <div id="optional-research-participation">
          <br>
          <div><strong><span style="font-size: 16px;"><span data-custom-class="heading_2">Optional research participation (opt-in)</span></span></strong></div>
          <div><br></div>
          <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">If you explicitly opt in to research participation:</span></span></span></div>
          <ul>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">A <strong>mask-specific subset of raw facial measurement points</strong> relevant to respirator fit may be stored.</span></span></span></li>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">These data are used to improve and evaluate fit-prediction models and to understand how different masks interact with facial geometry.</span></span></span></li>
            <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Participation in research is <strong>not required</strong> to use SnapFit.</span></span></span></li>
          </ul>
          <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may opt out of research participation at any time in the app.</span></span></span></div>
        </div>
      </div>

      <!-- Section: Information collected -->
      <div id="information-collected">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHAT INFORMATION MAY BE COLLECTED?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Depending on your choices, we may collect:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Email address and account credentials</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Optional profile name (you may use a pseudonym)</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Optional demographic information (e.g., gender/sex, year of birth)</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Derived facial measurements relevant to respirator fit</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text"><strong>If you opt in to research:</strong> a mask-specific subset of raw facial measurement points</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Mask model information and fit-related feedback (e.g., user seal check, qualitative or quantitative fit test results, comfort)</span></span></span></li>
        </ul>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may use aliases or pseudonyms for your profile name. You must not impersonate others and must provide a valid email address for account communications.</span></span></span></div>
      </div>

      <!-- Section: Data retention -->
      <div id="data-retention">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">HOW LONG WILL THE DATA BE USED?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Your data will be retained <strong>until you decide to delete your data</strong>.</span></span></span></div>
        <div><br></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">If you opt in to research participation, your data may be used for research and model improvement <strong>until you delete it</strong>.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">If you use SnapFit only for baseline functionality, your data will be retained <strong>until you delete it</strong>.</span></span></span></li>
        </ul>

        <div><strong><span style="font-size: 14px;"><span data-custom-class="body_text">After account deletion</span></span></strong></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">When you delete your account or use the "delete all my data" option:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Your email address will be deleted.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Your demographic information will be deleted.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Your derived facial measurements will be deleted.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Any stored mask-specific raw facial measurement points (if applicable) will be deleted.</span></span></span></li>
        </ul>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Aggregated, de-identified statistics that do not identify you may be retained.</span></span></span></div>
      </div>

      <!-- Section: Can participants leave? -->
      <div id="can-participants-leave">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">CAN PARTICIPANTS CHOOSE TO LEAVE?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Yes. Participation is voluntary.</span></span></span></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Stop using SnapFit at any time.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Opt out of research participation at any time.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Delete your account and associated data using in-app controls or by contacting info@breathesafe.xyz.</span></span></span></li>
        </ul>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Deleting your data will stop future use of your data for research and model training.</span></span></span></div>
      </div>

      <!-- Section: Risks of participation -->
      <div id="risks-of-participation">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHAT ARE THE RISKS OF PARTICIPATION?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Some data collected (such as facial measurements) are sensitive. Risks include the unlikely possibility of unauthorized access in the event of a data breach.</span></span></span></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">To reduce risk:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Only the minimum facial data needed for fit assessment is collected.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Data are transmitted using encrypted connections.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Data such as raw facial measurement points, names, and demographic information are stored encrypted.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may use a pseudonym to further reduce identifiability.</span></span></span></li>
        </ul>
      </div>

      <!-- Section: Benefits of participation -->
      <div id="benefits-of-participation">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHAT ARE THE BENEFITS OF PARTICIPATION?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Potential benefits include:</span></span></span></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Improved ability to find respirators that fit your face.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Contributing to tools that may help others find better-fitting masks.</span></span></span></li>
        </ul>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">There may be no direct benefit to you.</span></span></span></div>
      </div>

      <!-- Section: Privacy protection -->
      <div id="privacy-protection">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">HOW IS PRIVACY PROTECTED?</span></span></strong></div>
        <div><br></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Personal identifiers (name, email) are not publicly displayed.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Publicly displayed information, if any, is aggregated and de-identified.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Small groups are suppressed or grouped to reduce re-identification risk.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Breathesafe follows reasonable security practices to protect stored data.</span></span></span></li>
        </ul>
      </div>

      <!-- Section: Compensation -->
      <div id="compensation">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">ARE PARTICIPANTS COMPENSATED?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Participation is voluntary. In some cases, Breathesafe may assist with equipment or costs related to data contribution, depending on availability and location. Please contact info@breathesafe.xyz for details.</span></span></span></div>
      </div>

      <!-- Section: Participant rights -->
      <div id="participant-rights">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHAT ARE THE RIGHTS OF PARTICIPANTS?</span></span></strong></div>
        <div><br></div>
        <ul>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Participation is voluntary.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may withdraw at any time.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">You may request access to or deletion of your data.</span></span></span></li>
          <li style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Parents/guardians may exercise these rights on behalf of minors.</span></span></span></li>
        </ul>
      </div>

      <!-- Section: Contact -->
      <div id="contact">
        <br>
        <br>
        <div><strong><span style="font-size: 19px;"><span data-custom-class="heading_1">WHO CAN I CONTACT WITH QUESTIONS?</span></span></strong></div>
        <div><br></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Email: <strong>info@breathesafe.xyz</strong></span></span></span></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Mail:</span></span></span></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Breathesafe LLC</span></span></span></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">138 Miller Ave.</span></span></span></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">Rumford, RI 02916</span></span></span></div>
        <div style="line-height: 1.5;"><span style="color: rgb(127, 127, 127);"><span style="color: rgb(89, 89, 89); font-size: 15px;"><span data-custom-class="body_text">United States</span></span></span></div>
      </div>

      <br>
      <br>
      <br>
      </div>
      </div></div></div>
      </div>
    </div>
  </div>

  <div v-if='showConsentActions' class='consent-bottom-actions'>
    <Button class='accept' @click='onAccept'>Accept</Button>
    <Button class='reject' @click='onReject'>Reject</Button>
  </div>
</div>
</template>

<script>
import CircularButton from './circular_button.vue'
import Button from './button.vue'
import Popup from './pop_up.vue'
import axios from 'axios'
import { mapActions, mapState } from 'pinia'
import { useMainStore } from './stores/main_store'

export default {
  name: 'ConsentForm',
  components: {
    CircularButton,
    Button,
    Popup
  },
  data() {
    return {
      showInfoPopup: false,
      showThanksPopup: false,
      showRejectConfirm: false,
      showRejectInfo: false,
      infoVersion: ''
    }
  },
  computed: {
    ...mapState(useMainStore, ['currentUser', 'consentFormVersion']),
    showConsentActions() {
      return !!this.currentUser && !!this.consentFormVersion && this.currentUser.consent_form_version_accepted !== this.consentFormVersion
    }
  },
  async mounted() {
    await this.getCurrentUser()
    // Only show the "We updated our Consent Form" popup if:
    // 1. User exists and consent form version exists
    // 2. User has previously accepted a consent form (consent_form_version_accepted is not null/undefined)
    // 3. The accepted version is different from the current version (meaning the form was updated)
    // This prevents showing the popup to users who just accepted the current version during registration
    const hasAcceptedBefore = !!this.currentUser?.consent_form_version_accepted
    const versionChanged = hasAcceptedBefore &&
                          this.currentUser.consent_form_version_accepted !== this.consentFormVersion
    const needsInfo = !!this.currentUser &&
                     !!this.consentFormVersion &&
                     versionChanged
    if (needsInfo) {
      this.showInfoPopup = true
      this.infoVersion = this.$route.query.latest_version || this.consentFormVersion || ''
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser', 'setConsentDismissedForSession']),
    async onAccept() {
      await this.getCurrentUser()
      if (!this.currentUser) { return }
      try {
        const response = await axios.post('/users/consent', { decision: 'accept' })
        if (response.status >= 200 && response.status < 300) {
          this.showThanksPopup = true
        }
      } catch (e) {
        console.error(e)
      }
    },
    async onReject() {
      this.showRejectConfirm = true
    },
    async confirmReject() {
      try {
        await axios.post('/users/consent', { decision: 'reject' })
      } catch (e) {
        console.error(e)
      }
      this.showRejectConfirm = false
      this.showRejectInfo = true
    },
    closeThanks() {
      this.showThanksPopup = false
      // Mark consent screen dismissed for this session and return to target
      this.setConsentDismissedForSession(true)
      const name = this.$route.query.return_to_name || 'Landing'
      let params = {}
      let query = {}
      try { params = JSON.parse(this.$route.query.return_to_params || '{}') } catch {}
      try { query = JSON.parse(this.$route.query.return_to_query || '{}') } catch {}
      this.$router.replace({ name, params, query })
    },
    dismissRejectInfo() {
      this.showRejectInfo = false
      // Allow the user to continue using the app; mark dismissed for session
      this.setConsentDismissedForSession(true)
      const name = this.$route.query.return_to_name || 'Landing'
      let params = {}
      let query = {}
      try { params = JSON.parse(this.$route.query.return_to_params || '{}') } catch {}
      try { query = JSON.parse(this.$route.query.return_to_query || '{}') } catch {}
      this.$router.replace({ name, params, query })
    }
  }
}
</script>

<style scoped>
  .container {
    display: flex;
    flex-direction: column;
  }

  .grid {
    display: grid;
    grid-template-columns: 20% 80%;
    grid-template-rows: auto;
  }

  .margined {
    margin: 1em;
  }

  .main {
    max-width: 50em;
  }

  .overflow {
    overflow-y: auto;
    height: 100vh;
    position: sticky;
    top: 0;
  }

  .toc {
    display: flex;
    flex-direction: column;
  }

  .toc a {
    padding: 0.5em;
    text-decoration: none;
    color: #333;
  }

  .toc a:hover {
    background-color: #f0f0f0;
  }

  .toc-button {
    position: fixed;
    top: 4em;
    right: 1em;
    z-index: 1000;
    display: none;
  }

  /* Mobile TOC - hidden on desktop */
  .toc-mobile {
    display: none;
  }

  /* Add scroll margin to all anchor sections to account for fixed nav bar */
  #top,
  #invitation-to-participate,
  #why-is-this-project-being-done,
  #who-can-participate,
  #study-procedures,
  #baseline-app-use,
  #optional-research-participation,
  #information-collected,
  #data-retention,
  #can-participants-leave,
  #risks-of-participation,
  #benefits-of-participation,
  #privacy-protection,
  #compensation,
  #participant-rights,
  #contact,
  #toc-mobile {
    scroll-margin-top: 3.25em;
  }

  .consent-bottom-actions {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: white;
    border-top: 2px solid #ddd;
    padding: 1em;
    display: flex;
    justify-content: center;
    gap: 1em;
    z-index: 1000;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  }

  .consent-bottom-actions .accept {
    background-color: #4CAF50;
    color: white;
    padding: 0.75em 2em;
    font-size: 1.1em;
    font-weight: bold;
  }

  .consent-bottom-actions .accept:hover {
    background-color: #45a049;
  }

  .consent-bottom-actions .reject {
    background-color: #f44336;
    color: white;
    padding: 0.75em 2em;
    font-size: 1.1em;
    font-weight: bold;
  }

  .consent-bottom-actions .reject:hover {
    background-color: #da190b;
  }

  .row {
    display: flex;
    gap: 1em;
    justify-content: center;
    margin-top: 1em;
  }

  .cancel {
    background-color: #999;
    color: white;
  }

  .cancel:hover {
    background-color: #777;
  }

  .confirm {
    background-color: #f44336;
    color: white;
  }

  .confirm:hover {
    background-color: #da190b;
  }

  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 100%;
    }

    /* Hide desktop TOC on mobile */
    .toc-desktop {
      display: none;
    }

    /* Show mobile TOC at top */
    .toc-mobile {
      display: flex;
      background-color: #f8f8f8;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 1em;
      margin-bottom: 1em;
    }

    .toc-mobile h2 {
      font-size: 1.2em;
      margin: 0 0 0.5em 0;
    }

    .toc-mobile a {
      padding: 0.3em 0.5em;
      font-size: 0.9em;
    }

    /* Show TOC button on mobile */
    .toc-button {
      display: block;
    }
  }
</style>
