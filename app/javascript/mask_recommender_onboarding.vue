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
      <router-link :to="tocPath('timeline')">
        Timeline
      </router-link>

      <router-link :to="tocPath('expected-time-commitment')">
        Time Commitment
      </router-link>

      <router-link :to="tocPath('expected-equipment')">
        Expected Equipment
      </router-link>

      <router-link :to="tocPath('account-creation')">
        Account Creation
      </router-link>

      <router-link :to="tocPath('adding-measurement-devices')">
        Adding Measurement Devices
      </router-link>

      <router-link :to="tocPath('adding-respirator-users-name')">
        Adding Respirator Users: Name Tab
      </router-link>

      <router-link :to="tocPath('adding-respirator-users-demographics')">
        Adding Respirator Users: Demographics Tab
      </router-link>

      <router-link :to="tocPath('adding-respirator-users-facial-measurements')">
        Adding Respirator Users: Facial Measurements Tab
      </router-link>

      <router-link :to="tocPath('adding-fit-tests')">
        Adding Fit Tests for a Respirator User
      </router-link>

      <router-link :to="tocPath('adding-fit-tests-selecting-a-user')">
        Adding Fit Tests: Selecting a User
      </router-link>

      <router-link :to="tocPath('adding-fit-tests-searching-for-a-mask')">
        Adding Fit Tests: Searching for a mask
      </router-link>

      <router-link :to="tocPath('adding-fit-tests-facial-hair')">
        Adding Fit Tests: Facial Hair Information
      </router-link>

      <router-link :to="tocPath('adding-fit-tests-user-seal-check')">
        Adding Fit Tests: User Seal Check
      </router-link>

      <router-link :to="tocPath('adding-fit-tests-qlft')">
        Adding Fit Tests: Qualitative Fit Testing (QLFT)
      </router-link>

      <router-link :to="tocPath('running-fit-tests-qlft-setup-equipment')">
        Running a Qualitative Fit Test: Equipment Setup
      </router-link>

      <router-link :to="tocPath('running-fit-tests-qlft-sensitivity-check')">
        Running a Qualitative Fit Test: Sensitivity Check
      </router-link>

      <router-link :to="tocPath('running-fit-tests-qlft-fit-tests')">
        Running a Qualitative Fit Test: Fit Tests
      </router-link>


      <router-link :to="tocPath('adding-fit-tests-comfort')">
        Adding Fit Tests: Comfort Questions
      </router-link>

      <router-link :to="tocPath('fit-testing-results')">
        Fit Testing Results
      </router-link>

      <br>
      <br>
      <br>

    </div>

    <div class='margined main' id='onboarding'>
      <br>
      <br>

      <h2>Onboarding for Mask Recommender Based on Facial Features</h2>

      <div>
        <p>Last updated: Nov. 21, 2024</p>
      </div>

      <div class='row'>
        <p>Welcome! This page is intended for people who have volunteered to become fit testing participants to assist in creating a mask recommender based on facial features.</p>
      </div>

        <div id='timeline'>
          <br>
          <br>
          <h4>Timeline</h4>
        </div>

        <p>There are two phases for this project:</p>
        <ul>
          <li>collect fit testing data and facial measurement data with caliper and tape (to then create a model that predicts fit)</li>
          <li>collect selfies (to predict facial measurement data accurately and seamlessly)</li>
        </ul>

        <p>For collecting fit testing and facial measurement data, Breathesafe LLC hopes to have fit testers be done in 4 months after they get the fit testing equipment and masks from us. Collecting selfies will be done at a later time. You can opt in to this later on, which is voluntary and not required for participation in the former.</p>

        <p>As mentioned in the <router-link :to='tocPath("expected-equipment")'>Expected equipment</router-link> section below, there are 44 masks. I am hoping that for most testers, they will be done in about 4 months after receiving the equipment. Some of these masks are going to be too small or too big. For those, you will be able to quickly mark masks as way too small or way too big and would not have to go through the full qualitative or quantitative fit testing procedure. It will take about 30 seconds or less to mark a mask as such in the
        <router-link :to="{name: 'NewFitTest'}">Adding a Fit Test page</router-link>.
        </p>

        <div id='expected-time-commitment'>
          <br>
          <br>
          <h4>Time Commitment</h4>
        </div>

        <p>
        For qualitative fit testers, you will go through the OSHA set of exercises:

        </p>

        <ul>
          <li>Normal breathing #1</li>
          <li>Deep breathing</li>
          <li>Turning head side-to-side</li>
          <li>Moving head up-and-down</li>
          <li>Talking</li>
          <li>Bending over</li>
          <li>Normal breathing #2</li>
        </ul>

        <p>Each exercise takes a minute to do. Filling out the fit testing data in <router-link :to="{name: 'NewFitTest'}">Adding a Fit Test page</router-link> takes about a couple of minutes max. So in total that's about 9 minutes per mask. Let's say that about 1/3 of the masks are obviously too small / too big for you. That translates to 46 masks / 3  =~ 15 masks. For those masks, let's say you took a minute to fill out the <router-link :to="{name: 'NewFitTest'}">Adding a Fit Test page</router-link>. So that's 15 minutes of your time. And then for those masks you do decide to qualitatively test, that translates to (46 - 15) masks = 31 masks. 31 masks x 10 minutes / mask = 310 minutes. So for the data collection for Phase I, that translates to about 310 minutes + 15 minutes = 325 minutes of your time. To get all the testing done in 4 months, that averages to 325 minutes / 4 months = 81.25 minutes / month, or 1.35 hours per month.


        </p>

        <div id='expected-equipment'>
          <br>
          <br>
          <h4>Expected equipment</h4>
        </div>

        <p>For volunteers who want to  receive a set of masks from Breathesafe LLC, I can also provide the following equipment if you don’t have it:</p>

        <ul>
          <li>Qualitative Fit Testing Kit OR Quantitative Fit Testing Device</li>
          <li>Masks to test</li>
          <li>Digital Caliper &amp; Tape</li>
        </ul>

        <p>
        Masks to test are listed <router-link :to='{query: { sortByField:"uniqueFitTestersCount", "sortByStatus":"descending", "filterForTargeted": "true", "filterForNotTargeted": "false" }}'>here</router-link>. There are about 46 masks.
        </p>


        <div class='grid-images'>
          <figure>
            <a href="https://www.amazon.com/gp/product/B00JALAIIE/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1" target='_blank'>
              <img class='left-pane-image' src="https://c.media-amazon.com/images/I/6194IWMjJEL._SX522_.jpg" alt='iGaging 6" Digital External Outside Caliper OD for Woodworking'>
            </a>
            <figcaption>Digital Caliper</figcaption>
          </figure>

          <figure>
            <a href="https://www.amazon.com/dp/B0BGHCTL45?ref=ppx_yo2ov_dt_b_fed_asin_title" target='_blank'>
              <img class='left-pane-image' src="https://c.media-amazon.com/images/I/71Cwjwnqc6L._SL1500_.jpg" alt='Tape Measure, iBayam Soft Ruler Measuring Tape for Body Weight Loss Fabric Sewing Tailor Cloth Vinyl Measurement Craft Supplies, 60-Inch Double Scale Ruler, 2-Pack White, Blue'>
            </a>
            <figcaption>Tape Measure</figcaption>
          </figure>

          <figure>
            <a href="https://www.youtube.com/watch?v=Syj_zeNtLGI" target='_blank'>
              <img class='left-pane-image' src="https://profittesting.com/cdn/shop/articles/MelFitTest4blog2.jpg?v=1634512473" alt='Tape Measure, iBayam Soft Ruler Measuring Tape for Body Weight Loss Fabric Sewing Tailor Cloth Vinyl Measurement Craft Supplies, 60-Inch Double Scale Ruler, 2-Pack White, Blue'>
            </a>
            <figcaption>Qualitative Fit Testing equipment</figcaption>
          </figure>

          <figure>
            <a href="https://tsi.com/discontinued-products/portacount%C2%AE-respirator-fit-tester-8038/" target='_blank'>
              <img class='left-pane-image' src="https://tsi.com/getmetafile/a296129e-5e8d-48d6-a3a7-05a2d5195987/8038_01" alt='PortaCount'>
            </a>
            <figcaption>A Quantitative Fit Testing device such as a PortaCount</figcaption>
          </figure>

        </div>

        <p>For the <strong>qualitative</strong> fit testing kit, you should have:</p>
        <ul>
          <li>hood</li>
          <li>sensitivity solution</li>
          <li>fit testing solution</li>
          <li>nebulizer for sensitivity solution</li>
          <li>nebulizer for fit testing solution</li>
        </ul>

        <p>Breathesafe LLC may have provided you qualitative fit testing equipment.</p>

        <figure>
          <img  class='single-image' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/breathesafe-facial-measurements-examples/diy_qualitative_fit_testing_kit_2.jpeg" alt='qualitative fit testing equipment with ziploc bag as hood, two bottles of saccharin -- one for sensitivity and another for fit testing, and a battery-powered mesh nebulizer to aerosolize the solutions'>
          <figcaption>DIY Qualitative Fit Testing equipment</figcaption>
        </figure>

        <p>For instructions on how to use the qualitative fit testing kit provided to you by Breathesafe LLC, please take a look at the <router-link :to="tocPath('running-fit-tests-qlft-setup-equipment')"> Running a Qualitative Fit Test </router-link> section.
        </p>


        <p>If you don't have qualitative fit testing equipment, but have access to <strong>quantitative</strong> fit testing equipment, you should have:</p>
        <ul>
          <li>a quantitative fit testing machine (e.g. TSI 8020A)</li>
          <li>probes</li>
        </ul>

        <div id='account-creation'>
          <br>
          <br>
          <h4>Account Creation</h4>
        </div>

        <p>
        Please create an account by going to the <router-link :to="{name: 'SignIn'}">sign-up/sign-in page</router-link>.
        You will be asked for an email and password. You'll be asked to agree to some forms such as the Consent Form specific to this project, Terms of Service, and Privacy Policy. Once you hit "Sign Up", you'll get a confirmation email. Please click on the link provided in the confirmation email.
        </p>

        <div class='center'>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/registration-page.png" alt="Registration page" width="100%">
        </div>

        <div id='adding-measurement-devices'>
          <br>
          <br>
          <h4>Adding Measurement Devices</h4>
        </div>

        <p>
        <strong>If you are planning to use a qualitative fit testing (QLFT) equipment, please skip this section. This is only applicable for quantitative fit testing (QNFT).</strong>
        </p>

        <div class='center'>
          <figure>
            <a href="https://www.amazon.com/gp/product/B00JALAIIE/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1" target='_blank'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/measurement-devices.png" alt='Measurement Devices page'>
            </a>
            <figcaption>Measurement Devices page.</figcaption>
          </figure>
        </div>

        <p>The
        <router-link :to="{'name': 'MeasurementDevices'}">Measurement Devices</router-link>
        Data is meant for diagnosing potential calibration issues.</p>

        <div id='adding-respirator-users-name'>
          <br>
          <br>
          <h4>Adding Respirator Users: Name Tab</h4>
        </div>


        <p>The <router-link :to='{name: "RespiratorUsers"}'>Respirator Users</router-link> page displays the users you will be able to add facial measurements and fit testing data to.
</p>
        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-users-empty.png" alt='Respirator users'>
            </router-link>
            <figcaption>Respirator Users</figcaption>
          </figure>
        </div>

        <p>Clicking on the plus button will let you create a Respirator User, which will take you the Name tab:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-name.png" alt='Adding a new Respirator User. Page is asking about the name of the user'>
            </router-link>
            <figcaption>Adding a new Respirator User: Name tab</figcaption>
          </figure>
        </div>

        <p>You can fill out the name of the user you'll be adding info for (e.g. yourself, members in your household, etc.)</p>


        <p>Clicking on the plus button will allow you to add data about people of interest (e.g. yourself, your kids, your partner).</p>

        <div id='adding-respirator-users-demographics'>
          <br>
          <br>
          <h4>Adding Respirator Users: Demographics Tab</h4>
        </div>

        <p>After filling out a name, demographic questions will be asked next:</p>


        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-demog.png" alt='Adding a new Respirator User. Page is asking about demographics'>
            </router-link>
            <figcaption>Adding a new Respirator User: Demographics Questions Tab</figcaption>
          </figure>
        </div>

        <div id='adding-respirator-users-facial-measurements'>
          <br>
          <br>
          <h4>Adding Respirator Users: Facial Measurements Tab</h4>
        </div>

        <p>After anwering demographics questions, you will then be asked for facial measurement information:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-facial-measurements-1.png" alt='Adding a new Respirator User. Facial Measurements Part I'>
            </router-link>
            <figcaption>Adding a new Respirator User: Facial Measurements Tab</figcaption>
          </figure>
        </div>

        <p>Clicking on the question mark buttons will show you what a particular measurement means:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-facial-measurements-2.png" alt='Adding a new Respirator User. Facial Measurements Part I'>
            </router-link>
            <figcaption>Adding a new Respirator User: User clicked on "Face width" question mark button</figcaption>
          </figure>
        </div>

        <p>There are three sections. Please fill them out to the best of your ability. In <strong>Edit Mode</strong>, you will have a <strong>Save and continue</strong> button. Make sure to click on that to save the data. It will save your progress. Once you are done adding data for a Respirator User, you should see a notice that says the last step was successfully saved:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-done.png" alt='Adding a new Respirator User. Last step successfully saved'>
            </router-link>
            <figcaption>Adding a new Respirator User: Last step successfully saved</figcaption>
          </figure>
        </div>

        <p>Going to the
            <router-link :to='{name: "RespiratorUsers"}'>
              Respirator Users
            </router-link> page shows that information for the user has been completed (for Phase I):
        </p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-complete.png" alt='Added a new Respirator User. User is ready for fit testing'>
            </router-link>
            <figcaption>Added a new Respirator User. User is ready for fit testing</figcaption>
          </figure>
        </div>

        <div id='adding-fit-tests'>
          <br>
          <br>
          <h4>Adding Fit Tests</h4>
        </div>

        <p>You can visit the Fit Tests section by clicking on this
        <router-link :to='{name: FitTests}'>
        link
        </router-link>. You'll see something like this:
        </p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-tests-empty.png" alt='Fit Tests Page. Initially Empty'>
            </router-link>
            <figcaption>Fit Tests page. Initially empty.</figcaption>
          </figure>
        </div>

        <p>You will be able to add qualitative fit testing (QLFT) and quantitative fit testing (QNFT) data for the
        <router-link :to='{name: "RespiratorUsers"}'>
              Respirator Users
            </router-link>
        you created in the earlier step. Clicking on the plus button will let you add a fit test. The first thing that will be asked is for the testing administrator to select a user that was created in the


        <router-link :to='{name: "RespiratorUsers"}'>
              Respirator Users
            </router-link>
        section</p>
        <div id='adding-fit-tests-selecting-a-user'>
          <br>
          <br>
          <h4>Adding Respirator Users: Selecting a user</h4>
        </div>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-select-a-user.png" alt='Selecting a user'>
            </router-link>
            <figcaption>Adding a Fit Test: Selecting a user</figcaption>
          </figure>
        </div>

        <p>Clicking on the user of interest will list the user as a <strong>Selected user</strong>.  </p>

        <div id='adding-fit-tests-searching-for-a-mask'>
          <br>
          <br>
          <h4>Adding Respirator Users: Searching for a mask</h4>
        </div>
        <p>
        Hitting <strong>Save &amp; Continue</strong>, the testing administrator will be able to search for a mask to be tested: </p>


        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-search-for-mask.png" alt='Searching for a mask'>
            </router-link>
            <figcaption>Adding a Fit Test: Searching for a mask</figcaption>
          </figure>
        </div>

        <p>Testing administrator can then select a mask for testing:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-select-a-mask.png" alt='Selecting a mask'>
            </router-link>
            <figcaption>Adding a Fit Test: Selecting a mask</figcaption>
          </figure>
        </div>

        <p>After that, a user will be asked questions about facial hair:</p>

        <div id='adding-fit-tests-facial-hair'>
          <br>
          <br>
          <h4>Adding Respirator Users: Facial Hair Information</h4>
        </div>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-facial-hair-questions.png" alt='Facial Hair questions'>
            </router-link>
            <figcaption>Adding a Fit Test: Facial Hair Questions</figcaption>
          </figure>
        </div>

        <div id='adding-fit-tests-user-seal-check'>
          <br>
          <br>
          <h4>Adding Respirator Users: User Seal Check</h4>
        </div>
        <p>After that, user seal check questions will be asked:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-user-seal-check.png" alt='User seal check questions'>
            </router-link>
            <figcaption>Adding a Fit Test: User Seal Check Questions</figcaption>
          </figure>
        </div>

        <p>If the mask is obviously too big or too small, or if the tester detects leaks, the testing administrator will be notified that the tester doesn't have to proceed with adding more data. i.e. The qualitative/quantitative fit testing and comfort questions in the sections following this won't need to be answered:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-user-seal-check-failed.png" alt='User seal check failed'>
            </router-link>
            <figcaption>Adding a Fit Test: User Seal Check Failed</figcaption>
          </figure>
        </div>

        <div id='adding-fit-tests-qlft'>
          <br>
          <br>
          <h4> Adding Fit Tests: Qualitative Fit Testing (QLFT) </h4>
        </div>

        <p>If the User Seal Check does pass, the user can then add QLFT and/or QNFT data. First, the user will be asked about if they wanna add QLFT testing results:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-qlft-choose-procedure.png" alt='QLFT: Choose Procedure'>
            </router-link>
            <figcaption>Adding a Fit Test: QLFT: Choose Procedure</figcaption>
          </figure>
        </div>

        <p>Currently, only Full OSHA protocol is supported:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-choose-full-osha.png" alt='QLFT: Choose Full OSHA'>
            </router-link>
            <figcaption>Adding a Fit Test: QLFT: Choose Full OSHA</figcaption>
          </figure>
        </div>

        <p>User can select saccharin or bitrex for the solution, and the instructions about the procedure updates accordingly.</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-qlft-osha-procedures.png" alt='QLFT: OSHA exercises list'>
            </router-link>
            <figcaption>Adding a Fit Test: QLFT: OSHA Exercises list</figcaption>
          </figure>
        </div>

        <p>Testing administrator proceed to run the qualitative testing procedure and add the data there. If there are questions about what the exercise entails, the testing administrator can click on the question mark buttons to get an explanation:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-explainer-button.png" alt='QLFT: Explainer button'>
            </router-link>
            <figcaption>Adding a Fit Test: QLFT: OSHA Exercises list: Explainer for Normal Breathing Exercise</figcaption>
          </figure>
        </div>

        <p>After filling those out, the user can add quantitative fit testing data if they choose. But most likely, if the user did a qualitative fit test, they probably won't add quantitative fit testing data at the same session, so the testing administrator can choose "Skipping" for the QNFT procedure:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-qnft-choose-procedure.png" alt='QNFT: Choose Procedure: Skipping'>
            </router-link>
            <figcaption>Adding a Fit Test: QNFT: Choose Procedure: Skipping</figcaption>
          </figure>
        </div>


        <div id='running-fit-tests-qlft-setup-equipment'>
          <br>
          <br>
          <h4> Running Qualitative Fit Tests (QLFT): Equipment Setup</h4>
        </div>

        <p>You may have been provided a Mayluck Mesh Nebulizer. Open the battery compartment underneath to check that 2 AA batteries are in place.</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-mayluck-neb-1.jpeg" alt='Mayluck Mesh Nebulizer'>
            <figcaption>Mayluck Nebulizer</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-mayluck-neb-2.jpeg" alt='Mayluck Mesh Nebulizer - Bottom'>
            <figcaption>Mayluck Nebulizer - Bottom</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-mayluck-neb-3.jpeg" alt='Prying open the battery compartment of the Mayluck Mesh Nebulizer'>
            <figcaption>Prying open the battery compartment of the Mayluck Mesh Nebulizer</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-mayluck-neb-4.jpeg" alt='2AA Batteries in the battery compartment'>
            <figcaption>2AA Batteries in the battery compartment</figcaption>
          </figure>
        </div>

        <p>Notice the negative and positive signs on the metal. The negative side should have the side with the thicker ring-end, while the positive side should have the thinner ring-end. </p>

        <p>Next, remove the nozzle cap from the nebulizer:</p>
        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-1-removed-nozzle-cap.jpeg" alt='Removing the nozzle cap'>
            <figcaption>Remove nozzle cap</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-2-remove-nozzle-cap.jpeg" alt='Removed the nozzle cap'>
            <figcaption>Removed nozzle cap</figcaption>
          </figure>
        </div>

        <p>If there is some solution buildup in the middle, please remove said buildup by running the nozzle through running water.</p>
        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-3-observe-nozzle-buildup.jpeg" alt='Some buildup'>
            <figcaption>Some builup</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-4-removed-buildup.jpeg" alt='Some buildup'>
            <figcaption>Removed builup</figcaption>
          </figure>
        </div>

        <p>Next, unlock the solution latch </p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-5-unlock-solution-container.jpeg" alt='Unlock solution latch'>
            <figcaption>Unlock solution latch Part I</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-6-unlock-solution-container-2.jpeg" alt='Unlock solution latch'>
            <figcaption>Unlock solution latch Part II</figcaption>
          </figure>
        </div>

        <p>Add the sensitivity solution:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-7-unlock-solution-container-3.jpeg" alt='Ready to add solution'>
            <figcaption>Ready to add solution</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-8-add-sensitivity-solution.jpeg" alt='Adding sensitivity solution'>
            <figcaption>Adding sensitivity solution</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-9-6ml.jpeg" alt='Add 6mL of solution'>
            <figcaption>Add 6mL of solution</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-10-close-and-lock-solution-container.jpeg" alt='Close and lock solution container'>
            <figcaption>Close and lock solution container</figcaption>
          </figure>
        </div>

        <p>Please add in 6 mL of the sensitivity solution.</p>

        <div id='running-fit-tests-qlft-sensitivity-check'>
          <br>
          <br>
          <h4> Running Qualitative Fit Tests (QLFT): Sensitivity Check</h4>
        </div>

        <p>Qualitative fit testing involves using your sense of taste to detect whether or not a mask meets a particular threshold of protection for your particular face. Since it depends on taste, you should</p>
        <ul>
          <li>not consume food or beverages besides water 30 minutes before testing, </li>
          <li>gargle with water to wash out your tongue and lips prior to performing sensitivity step and after it,</li>
          <li>gargle with water to wash out your tongue and lips after failing a fit test.</li>
        </ul>


        <div class='center'>
          <figure>
            <img class='left-pane-image' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-mouth-lips-rinse.png" alt='Mouth and Lips Rinse'>
            <figcaption>Mouth and Lips Rinse using Water</figcaption>
          </figure>
        </div>

        <p>Don the ziploc bag (hood). Have the nebulizer hole be in front of the face.</p>

        <div class='center'>
          <figure>
            <img class='left-pane-image' src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-11-don-hood-with-hole-side-in-front.jpeg" alt='Don hood with hole in front'>
            <figcaption>Don hood with hole in front</figcaption>
          </figure>
        </div>

        <p>Zip the ziploc bag to decrease air movement between inside of the bag and outside:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-12-pre-zip-hood.jpeg" alt='Don hood with hole in front'>
            <figcaption>Don hood with hole in front</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-13-zip-hood.jpeg" alt='Hood zipped'>
            <figcaption>Hood zipped</figcaption>
          </figure>
        </div>

        <p>Insert the nebulizer outlet into the hole in the hood:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-14-insert-nebulizer-nozzle-through-hole.jpeg" alt='Insert nebulizer nozzle through hole'>
            <figcaption>Insert nebulizer nozzle through hole</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-stick-tongue-out.jpg" alt='Stick tongue out while breathing in'>
            <figcaption>Stick tongue out while breathing in.</figcaption>
          </figure>
        </div>

        <p>While in the hood, have your tongue be slightly out, and breathe in using the mouth. Sticking your tongue out a little bit maximizes the contact of air with the tongue (and should increase sensitivity).</p>
        <p>Insert the nebulizer nozzle into the hole on the hood. Press the button in the middle of the nebulizer to aerosolize the sensitivity solution. You should be able to see fine mist coming out of the nebulizer and into the hood. You should see a blue light coming out of the nebulizer.  </p>
        <p>Once you are able to taste the solution, immediately turn off the nebulizer by pressing the button twice. The first button press will make the color green. The second button press will turn off the device. <strong>IMPORTANT: Please make note of how many seconds it took you to know that you are tasting the saccharin sensitivity solution. This information will be used at the next step.</strong></p>

        <p>However, if you cannot taste the solution even after 10 seconds of having the sensitivity solution aerosolized in the bag, <strong> please reach out to <a href="mailto:info@breathesafe.xyz?subject=Cannot Taste Sensitivity Solution">info@breathesafe.xyz</a>. Edderic could send you a bitrex solution instead of the saccharin.</strong></p>

        Assuming you have passed the sensitivity threshold check, you can proceed to doing the fit testing exercises.


        <div id='running-fit-tests-qlft-fit-tests'>
          <br>
          <br>
          <h4> Running Qualitative Fit Tests (QLFT): Fit Testing using the Fit Test solution</h4>
        </div>

        <p>This section assumes that you succeeded in tasting the aerosolized sensitivity solution.</p>

        <p>Unlock the solution latch:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-5-unlock-solution-container.jpeg" alt='Unlock solution latch'>
            <figcaption>Unlock solution latch Part I</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-neb-setup-6-unlock-solution-container-2.jpeg" alt='Unlock solution latch'>
            <figcaption>Unlock solution latch Part II</figcaption>
          </figure>
        </div>

        <p>Dump the sensitivity solution back into the sensitivity solution container. Please add 6mL of the fit test solution into the nebulizer.</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-dump-sensitivity-solution-back.jpeg" alt='Dump sensitivity solution back into sensitivity solution container'>
            <figcaption>Dump sensitivity solution back into sensitivity solution container</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-add-fit-test-solution.jpeg" alt='Unlock solution latch'>
            <figcaption>Add fit test solution</figcaption>
          </figure>
        </div>


        <p>
        Now you may don a mask, don the hood, and insert the nebulizer:
        </p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-fit-test-don-mask.jpeg" alt='Wear a mask'>
            <figcaption>Wear a mask of interest</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-fit-test-don-hood.jpeg" alt='Wear the hood'>
            <figcaption>Wear the hood</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-fit-test-zip-hood.jpeg" alt='Zip the hood'>
            <figcaption>Zip the hood</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/qlft-fit-test-insert-nebulizer-outlet.jpeg" alt='Insert the nebulizer outlet'>
            <figcaption>Insert the nebulizer outlet into the hole.</figcaption>
          </figure>
        </div>

        <p>There are seven exercises:</p>
        <ul>
          <li>
          Normal breathing 1
          </li>
          <li>
          Deep Breathing,
          </li>
          <li>
          Moving head side to side
          </li>

          <li>
          Moving head up and down
          </li>

          <li>
          Talking
          </li>

          <li>
          Bending over
          </li>

          <li>
          Normal breathing 2
          </li>
        </ul>

        <p>Please see the section on <router-link :to="tocPath('adding-fit-tests-qlft')">
          OSHA Qualitative Fit Testing exercises here
          </router-link> to learn how to add data for these exercises.
        </p>

      <p>Each exercise takes a minute. <strong>At the beginning of each exercise, use the same amount of time running the nebulizer as you did as in the sensitivity step. On the other hand, at the 30-second mark, you should use half the amount of time of nebulization as in the sensitivity step.</strong>  For example, if it only took you 2 seconds of running the nebulizer to detect the sensitivity solution in the earlier step, you should run the nebulizer for 2 seconds with the fit test solution in the beginning of each exercise, and run the nebulizer for 1 second at the 30-second mark for each exercise. </p>

        <p>
        The fit test solution is 100x more concentrated than the sensitivity solution. Succeeding in tasting the sensitivity solution, while wearing a mask and not detecting the 100x stronger (fit test) solution for a particular exercise implies that the mask has a fit factor of at least 100 for that particular instance of an exercise.  However, there are several exercises. To pass the qualitative fit test, the tester should not be able to taste the fit test solution through <em>all</em> the exercises. If the tester tastes the fit test solution midway, that is considered a failure (i.e. the overall fit factor is less than 100.)
        </p>



        <div id='adding-fit-tests-comfort'>
          <br>
          <br>
          <h4>Adding Respirator Users: Comfort Questions</h4>
        </div>
        <p>The user will then be asked questions about comfort:</p>
        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/add-fit-test-comfort.png" alt='Comfort questions'>
            </router-link>
            <figcaption>Adding a Fit Test: Comfort Questions</figcaption>
          </figure>
        </div>


        <div id='fit-testing-results'>
          <br>
          <br>
          <h4>Fit Testing Results</h4>
        </div>
        <p>After that, you'll be taken to the Fit Tests page. After doing this for many masks, you'll see your results displayed like so:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "NewFitTest"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-test-results.png" alt='Fit Test Results'>
            </router-link>
            <figcaption>Fit Test Results</figcaption>
          </figure>
        </div>
        <br>
        <br>
        <br>
        <br>
        <br>
        <br>

    </div>
  </div>

</template>
<script>

import CircularButton from './circular_button.vue';

export default {
  name: 'ConsentForm',
  components: {
    CircularButton,
  },
  data() { return {} },
  props: { },
  computed: {
  },
  methods: {
    tocPath(suffix) {
      return `/onboarding#${suffix}`
    }
  }
}
</script>
<style scoped>
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

  .grid.even {
    display: grid;
    grid-template-columns: 50% 50%;
    grid-template-rows: auto;
  }

  .center {
    display: flex;
    justify-content: center;
  }

  .grid-images {
    display: grid;
    grid-template-columns: 50% 50%;
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

  figure {
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
  }

  img {
    max-width: 700px;
  }

  .tos-header {
    display: flex;
    flex-direction: row;
    width: 100%;
  }

  th, td {
    padding: 0.5em;
  }
  .single-image {
    max-width: 40em;
  }

  @media(min-width: 1200px) {
    .toc-button {
      display: none;
    }
  }


  @media(min-width: 1201px) {
    .grid.even {
      display: grid;
      grid-template-columns: 50% 50%;
      grid-template-rows: auto;
    }

    .grid.even img {
      width: 100%;
    }

  }
  @media(max-width: 1200px) {
    .grid {
      display: flex;
      flex-direction: column;
    }

    .grid.even {
      display: grid;
      grid-template-columns: 50vw 50vw;
      grid-template-rows: auto;
    }

    .grid.even img {
      width: 100%
    }


    .toc {
      position: relative;
      width: 75vw;
    }

    .main {
      width: 75vw;
      margin-left: 0;
    }

    img {
      max-width: 90vw;
    }

  }

  @media (max-width: 900px) {
    .grid.even {
      display: grid;
      grid-template-columns: 100vw;
    }
    .single-image {
      max-width: 20em;
    }
  }

</style>
