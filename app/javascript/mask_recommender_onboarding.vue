<template>

  <router-link :to="tocPath('toc')">
    <CircularButton text="TOC" class='toc-button'/>
  </router-link>

  <div class='grid'>
    <div class='toc margined overflow' id='toc'>
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

      <br>

      <router-link :to="tocPath('adding-a-respirator-user')">
        Adding a Respirator User
      </router-link>

      <div style="margin-left: 2em;">
        <router-link :to="tocPath('adding-respirator-users-name')">
          Name
        </router-link>
        <br>
        <router-link :to="tocPath('adding-respirator-users-demographics')">
          Demographics
        </router-link>
        <br>
        <router-link :to="tocPath('adding-respirator-users-facial-measurements')">
          Facial Measurements
        </router-link>
      </div>

      <br>

      <router-link :to="tocPath('adding-a-fit-test')">
        Adding a Fit Test
      </router-link>

      <div style="margin-left: 2em;">
        <router-link :to="tocPath('adding-fit-tests-selecting-a-user')">
          Selecting a User
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-searching-for-a-mask')">
          Searching for a Mask
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-facial-hair')">
          Facial Hair Information
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-user-seal-check')">
          User Seal Check
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-qnft')">
          Quantitative Fit Testing (QNFT)
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-qlft')">
          Qualitative Fit Testing (QLFT)
        </router-link>
        <br>
        <router-link :to="tocPath('adding-fit-tests-comfort')">
          Comfort
        </router-link>
      </div>
      <br>

      <router-link :to="tocPath('fit-testing-results')">
        Fit Testing Results
      </router-link>


      <br>
      <router-link :to="tocPath('running-a-quantitative-fit-test')">
        Running a Quantitative Fit Test
      </router-link>

      <div style="margin-left: 2em;">
        <router-link :to="tocPath('tsi-8020a-with-n95-companion')">
          TSI 8020A w/ N95 Companion Training Video
        </router-link>
        <br>
        <router-link :to="tocPath('tsi-8020-manual')">
          TSI 8020 Manual
        </router-link>
        <br>
        <router-link :to="tocPath('tsi-8095-n95-companion-manual')">
          TSI 8095 N95 Companion Manual
        </router-link>

        <br>
        <router-link :to="tocPath('installing-probes-to-masks')">
          Installing Probes to Masks
        </router-link>

        <br>
        <router-link :to="tocPath('setting-up-tsi-8020A-with-tsi-8095')">
          Setting up TSI 8020A with TSI 8095 N95 Companion
        </router-link>

        <br>
        <router-link :to="tocPath('setup-alcohol-cartridge')">
          Setting up Alcohol Cartridge
        </router-link>

        <br>
        <router-link :to="tocPath('connecting-the-8020a-and-8095')">
          Connecting the 8020A and the 8095
        </router-link>

        <br>
        <router-link :to="tocPath('setup-n95-companion-pendant')">
          Setting up N95 Companion Pendant
        </router-link>

        <br>
        <router-link :to="tocPath('setup-aerosol-generator')">
          Setting up the Aerosol Generator
        </router-link>

        <br>
        <router-link :to="tocPath('turning-on-the-portacount')">
          Turning on the PortaCount
        </router-link>

        <br>
        <router-link :to="tocPath('daily-checks')">
          Daily Checks
        </router-link>

        <br>
        <router-link :to="tocPath('ready-for-testing')">
          Ready for Testing
        </router-link>

        <br>
        <router-link :to="tocPath('putting-things-back')">
          Putting things back
        </router-link>
      </div>

      <br>

      <router-link :to="tocPath('running-a-qualitative-fit-test')">
        Running a Qualitative Fit Test
      </router-link>

      <div style="margin-left: 2em;">
        <router-link :to="tocPath('running-fit-tests-qlft-setup-equipment')">
          Equipment Setup
        </router-link>
        <br>
        <router-link :to="tocPath('running-fit-tests-qlft-sensitivity-check')">
          Sensitivity Check
        </router-link>
        <br>
        <router-link :to="tocPath('running-fit-tests-qlft-fit-tests')">
          Fit Tests
        </router-link>
      </div>

      <br>

      <router-link :to="tocPath('importing-fit-tests-in-bulk')">
        Importing Fit Tests in Bulk
      </router-link>

      <div style="margin-left: 2em;">
        <router-link :to="tocPath('import-a-file')">
          Import a File
        </router-link>
        <br>
        <router-link :to="tocPath('columns-matching')">
          Columns Matching
        </router-link>
        <br>
        <router-link :to="tocPath('user-matching')">
          User Matching
        </router-link>
        <br>
        <router-link :to="tocPath('mask-matching')">
          Mask Matching
        </router-link>
        <br>
        <router-link :to="tocPath('user-seal-check-matching')">
          User Seal Check Matching
        </router-link>
        <br>
        <router-link :to="tocPath('qlft-values-matching')">
          QLFT Values Matching
        </router-link>
        <br>
        <router-link :to="tocPath('comfort-matching')">
          Comfort Matching
        </router-link>
        <br>
        <router-link :to="tocPath('review-and-import')">
          Review and Import
        </router-link>
      </div>

      <br>
      <br>
      <br>

    </div>

    <div class='margined main' id='onboarding'>
      <br>
      <br>

      <h2>Onboarding for Mask Recommender Based on Facial Features</h2>

      <div>
        <p>Last updated: Dec. 19, 2025</p>
      </div>

      <div class='row'>
        <p>Welcome! This page is intended for people who have volunteered to become fit testing participants to assist in creating a mask recommender based on facial features.</p>
      </div>

        <div id='timeline'>
          <br>
          <br>
          <h4>Timeline</h4>
        </div>

        <p>This is an ongoing project with no definite end-date. You can add fit testing data and facial measurements at any time.</p>

        <div id='expected-time-commitment'>
          <br>
          <br>
          <h4>Time Commitment</h4>
        </div>

        <h5>
          Registration
        </h5>
        <p>
        It might take about a couple of minutes to register, confirm the email, and login.
        </p>
        <h5>
          Creating a respirator user
        </h5>
        <p>
        It takes 30 seconds to create a Respirator User. You could create one for yourself, and for others you'd like to add data for (e.g. your children).
        </p>

        <h5>
          Adding Demographic Information
        </h5>
        <p>
        There are a few questions about race, ethnicity, gender / sex. It should take less than 30 seconds to answer per Respirator User that you've created.
        </p>


        <h5>
          Adding Facial Measurements
        </h5>
        <p>
        To add facial measurements for a Respirator User, use the <router-link :to="{name: 'NewFitTest'}">MasqFit iOS app</router-link> to upload the relevant facial measurements to Breathesafe. It might take a minute to search and download the app from the App Store. Once downloaded, it can take a few seconds to take measurements, and upload the data to Breathesafe to improve the Mask Recommender system.
        </p>


        <h5>
          User Seal Check Results
        </h5>
        <p>
        Some of the masks that you try are going to be too small or too big. For those, you will be able to quickly mark masks as way too small or way too big and would not have to go through the full qualitative or quantitative fit testing procedure. It will take about 30 seconds or less to mark a mask as such in the
        <router-link :to="{name: 'NewFitTest'}">Adding a Fit Test page</router-link>.
        </p>


        <h5>
          Qualitative Fit Testing
        </h5>

        <p>
        If you have access to qualitative fit testing, you will go through the OSHA set of exercises:

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

        <p>Each exercise takes a minute to do. Filling out the fit testing data in <router-link :to="{name: 'NewFitTest'}">Adding a Fit Test page</router-link> takes about a couple of minutes max. So in total that's about 9 minutes per mask.
        </p>
        <h5>
          Quantitative Fit Testing
        </h5>
        <p>
        If you have access to quantitative fit testing, you will go through these smaller number of OSHA exercises (which I dub as the "OSHA Fast Facepiece Respirator" set of exercises)

        </p>

        <ul>
          <li>Bending over</li>
          <li>Turning head side-to-side</li>
          <li>Moving head up-and-down</li>
          <li>Talking</li>
        </ul>

        <p>
        Since each exercise takes a minute to do, and adding in some buffer, let's assume it takes 5 minutes to do one mask.
        </p>
        <h5>
          Uploading Fit Testing Results in Bulk
        </h5>
        <p>
        If you prefer to store your data using spreadsheets instead of the regular UI, or already have fit testing data saved in a spreadsheet, you can upload your data seamlessly using the Bulk Fit Tests Importing tool. It takes about a minute or two to upload data from spreadsheets (CSV). See the <router-link :to="tocPath('importing-fit-tests-in-bulk')">Bulk Fit Tests Import section.</router-link>
        </p>


        <div id='expected-equipment'>
          <br>
          <br>
          <h4>Expected equipment</h4>
        </div>

        <p>
        You can do fit testing on your own set of masks. I also expect that you have access to an iPhone with True Depth camera, along with either a qualitative or quantitative fit testing device:
        </p>


        <div class='grid-images'>

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

          <figure>
            <a href="https://www.verizon.com/smartphones/apple-iphone-14/" target='_blank'>
              <img class='left-pane-image' src="https://ss7.vzw.com/is/image/VerizonWireless/iphone-14-midnight-fall22-a?wid=930&hei=930&fmt=webp" alt='An iPhone'>
            </a>
            <figcaption>An iPhone with True Depth camera</figcaption>
          </figure>

        </div>

        <p>For the <strong>iPhone</strong> requirement, one can tell whether or not the device has True Depth capability is if the particular iPhone model is capable of using FaceID. If an iPhone model is not capable of FaceID, it probably doesn't have a True Depth infrared sensor.</p>

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
          <li>a quantitative fit testing machine with N95-mode capability (e.g. TSI 8020A w/ N95-Mode Companion)</li>
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

        <div id='adding-a-respirator-user'>
          <br>
          <br>
          <h3>Adding a Respirator User</h3>
        </div>

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

        <p>Download the MasqFit app from the App Store on your iPhone with True Depth Camera (i.e. has FaceID capability). You should see a landing screen like this:</p>
        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-landing-page.png" alt='MasqFit landing page' height='400'>
            <figcaption>MasqFit landing page</figcaption>
          </figure>
        </div>

        <p>Click on the "Contribute Facial Measurement Data" button. You should see the sign-in / registration page. Please sign-in with your Breathesafe credentials.</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-login.png" alt='MasqFit sign-in page' height='400'>
            <figcaption>MasqFit sign-in page</figcaption>
          </figure>
        </div>

        <p>You should see a list of Respirator Users associated with your account. You should see at least one entry:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-respirator-users.png" alt='MasqFit Respirator Users View' height='400'>
            <figcaption>MasqFit Respirator Users View</figcaption>
          </figure>
        </div>

        <p>Click on the "Gear" icon with the user you'd like to add facial measurement data for. You should see a list of options:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-respirator-users-list-of-options-for-user.png" alt='MasqFit Respirator User Options' height='400'>
            <figcaption>MasqFit Respirator Options</figcaption>
          </figure>
        </div>


        <p>Click on "Add Facial Measurements". You should see something like so:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-blank.png" alt='MasqFit Facial Measurements for User View' height='400'>
            <figcaption>MasqFit Facial Measurements for User View</figcaption>
          </figure>
        </div>

        <p>Click on "Add Facial Measurements". You'll be taken to this view:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-blank.png" alt='MasqFit Facial Measurements for User View' height='400'>
            <figcaption>MasqFit Facial Measurements for User View</figcaption>
          </figure>
        </div>

        <p>Click on "Add Facial Measurements". You'll be taken to this view:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-ar-view.png" alt='MasqFit Facial Measurements Augmented Reality View' height='400'>
            <figcaption>MasqFit Facial Measurements Augmented Reality View</figcaption>
          </figure>
        </div>

        <p>Position your face close to the camera (less than 12 inches away) in portrait mode. Remove glasses, hats, or anything covering your face. Stay still, then press the "Start Measurement button". After hitting that button, you should see:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-ar-view-complete.png" alt='MasqFit Facial Measurement Points Taken' height='400'>
            <figcaption>MasqFit Facial Measurement Points Taken.</figcaption>
          </figure>
        </div>

        <p>It says: "Measurement complete! You can now export your data." Press the "Save" button. It should show a message:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-ar-view-success.png" alt='MasqFit Facial Measurements Saved' height='400'>
            <figcaption>MasqFit Facial Measurements Saved</figcaption>
          </figure>
        </div>

        <p>Press "OK". It should show you aggregated measurements of the individual:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/masqfit-facial-measurements-aggregated.png" alt='MasqFit Facial Measurements Aggregated' height='400'>
            <figcaption>MasqFit Facial Measurements Aggregated</figcaption>
          </figure>
        </div>

        <p>Going to the
            <router-link :to='{name: "RespiratorUsers"}'>
              Respirator Users
            </router-link> page shows that information for the user has been completed:
        </p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "RespiratorUsers"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/respirator-user-complete.png" alt='Added a new Respirator User. User is ready for fit testing'>
            </router-link>
            <figcaption>Added a new Respirator User. User is ready for fit testing</figcaption>
          </figure>
        </div>

        <div id='adding-a-fit-test'>
          <br>
          <br>
          <h3>Adding a Fit Test</h3>
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

        <p>If the User Seal Check does pass, the user can then add QLFT and/or QNFT data. First, the user will be asked about if they wanna add QLFT testing results:</p>

        <div id='adding-fit-tests-qnft'>
          <br>
          <br>
          <h4> Adding Fit Tests: Quantitative Fit Testing (QNFT) </h4>
        </div>

        <p>You may move onto the next section if you're instead doing qualitative fit testing (QLFT).</p>

        <p>You should be asked about which fit testing procedure you'd like to add data for:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-choose-procedure-1.png" alt='MasqFit Fit Testing - Choose a Procedure' height='400'>
            <figcaption>MasqFit Fit Testing - Choose a Procedure</figcaption>
          </figure>
        </div>

        <p>Here are the options:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-choose-procedure-2.png" alt='MasqFit Fit Testing - Procedure Options' height='400'>
            <figcaption>MasqFit Fit Testing - Procedure Options</figcaption>
          </figure>
        </div>

        <p>I recommend you to select the "OSHA Fast Face Piece Respirators" option as it is the faster option, though the Full OSHA option is available as well. Choosing a procedure will show more questions about the testing mode, and initial count (particles / cm3). Ideally you have N95 mode capability if you are testing N95-certified respirators. Initial counts are also asked for to ensure that the results are valid (i.e. the device might not be sensitive enough to detect up to 200 fit factor if the initial count is too low. Aim for higher than 70, but this number depends on the model of your fit testing device.)</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-qnft.png" alt='MasqFit Fit Testing - Procedure Options' height='400'>
            <figcaption>MasqFit Fit Testing - Procedure Options</figcaption>
          </figure>
        </div>

        <p>Hitting "Save and Continue", you should see a list of exercises:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-qnft-exercises.png" alt='MasqFit Fit Testing - QNFT exercises' height='400'>
            <figcaption>MasqFit Fit Testing - QNFT exercises</figcaption>
          </figure>
        </div>

        <p>Clicking on one of the Help (?) buttons, you should see instructions about how to perform the particular exercise.</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-exercise-instructions.png" alt='MasqFit Fit Testing - QNFT exercise instructions' height='400'>
            <figcaption>MasqFit Fit Testing - QNFT exercise instructions</figcaption>
          </figure>
        </div>

        <p>Do each exercise and write the fit factors you've acquired from the testing device:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-testing-add-fit-factors.png" alt='MasqFit Fit Testing - QNFT Add Fit Factors' height='400'>
            <figcaption>MasqFit Fit Testing - Add Fit Factors</figcaption>
          </figure>
        </div>

        <p>Then hit Save and Continue.</p>

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

        <div id='running-a-quantitative-fit-test'>
          <br>
          <br>
          <h3>Running a Quantitative Fit Test</h3>
        </div>

        <div id='tsi-8020a-with-n95-companion'>
          <br>
          <br>
          <h4>TSI 8020A w/ N95 Companion</h4>
        </div>

        <figure>
          <iframe width="560" height="315" src="https://www.youtube.com/embed/YtGaLMneojA" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          <figcaption>TSI 8020A PortaCount with N95 Companion training</figcaption>
        </figure>

        <div id='tsi-8020-manual'>
          <br>
          <br>
          <h4>TSI 8020A Manual</h4>
        </div>

        <a href='https://www.tttenviro.com/wp-content/uploads/Manual-TSI-Portacount-model-8020.pdf' target='_blank'>Here is a link to the 8020 Manual.</a>

        <div id='tsi-8095-n95-companion-manual'>
          <br>
          <br>
          <h4>TSI 8095 N95 Companion Manual</h4>
        </div>

        <a href='https://tsi.com/getmedia/23133329-810a-45d0-8bdf-145592b592c8/1980308J-8095-N95-Companion?ext=.pdf' target='_blank'>Here is a link to the 8095 N95 Companion Manual.</a>


        <div id='installing-probes-to-masks'>
          <br>
          <br>
          <h4>Installing Probes to Masks</h4>
        </div>

        <p>For quantitative fit testing, we'll need to install a probe on the to-be-tested masks. Quantitative fit testing works by comparing the within-mask particle concentration and the ambient (outside-of-mask) particle concentrations. In this example, I'll be showing you how to insert a reusable probe. You'll need to have access to an X-ACTO knife (which Breathesafe LLC might have provided you):</p>


        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-reusable-probes.png" alt='Reusable Probes'>
            <figcaption>Reusable Probes</figcaption>
          </figure>


          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-xacto-knife-hole.png" alt='Xacto Knife Hole'>
            <figcaption>Xacto Knife Hole</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-xacto-knife-hole-2.png" alt='Xacto Knife Hole 2'>
            <figcaption>Xacto Knife Hole 2</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-xacto-knife-hole-3.png" alt='Xacto Knife Hole 3'>
            <figcaption>Xacto Knife Hole 3</figcaption>
          </figure>

        </div>

        <p>Insert the Probe all the way. You might have to rotate the probe like a screw so that it goes all the way in.</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-probe.png" alt='Probe'>
            <figcaption>Probe</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-insert-probe-through-mask-hole.png" alt='Insert Probe Through Mask Hole'>
            <figcaption>Insert Probe Through Mask Hole</figcaption>
          </figure>
        </div>

        <p>Add the washer</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-rubber.png" alt='Rubber'>
            <figcaption>Rubber</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-probe-rubber-washer.png" alt='Probe Rubber Washer'>
            <figcaption>Probe Rubber Washer</figcaption>
          </figure>
        </div>


        <p>Rotate the nut so that the nut and the probe are sealed together:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-probe-nut-1.png" alt='Probe Nut 1'>
            <figcaption>Probe Nut 1</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-probe-nut-2.png" alt='Probe Nut 2'>
            <figcaption>Probe Nut 2</figcaption>
          </figure>
        </div>

        <div id='setting-up-tsi-8020A-with-tsi-8095'>
          <br>
          <br>
          <h4>Setting up TSI 8020A with TSI 8095 N95 Companion</h4>
        </div>

        <p>If you've borrowed Breathesafe LLC's TSI 8020A and the TSI 8095 N95 Companion, you should see two luggages' worth of equipment.</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-2-luggages.png" alt='2 Luggages containing TSI 8020A and TSI 8095 N95 Companion'>
          <figcaption>2 Luggages containing TSI 8020A and TSI 8095 N95 Companion</figcaption>
        </figure>

        <p>Take out the N95 Companion and place it on some flat surface (e.g. table, floor, etc.):</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-companion.png" alt='Companion'>
          <figcaption>Companion</figcaption>
        </figure>

        <p>Place 8020a on top of the N95 companion.</p>


        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-place-8020a-on-top-of-companion.png" alt='Place 8020a On Top Of Companion'>
            <figcaption>Place 8020a On Top Of the Companion</figcaption>
          </figure>


          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-8020a-with-companion-close-up.png" alt='8020a With Companion Close Up'>
            <figcaption>8020a With Companion Close Up</figcaption>
          </figure>
        </div>

        <div id='setup-alcohol-cartridge'>
          <br>
          <br>
          <h4>Setting up Alcohol Cartridge</h4>
        </div>

        <p>Get the Alcohol Container. Remove Storage Cap from 8020A by turning counter-clockwise.</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-get-alcohol-container.png" alt='Get Alcohol Container'>
            <figcaption>Get Alcohol Container</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-remove-storage-cap.png" alt='Remove Storage Cap'>
            <figcaption>Remove Storage Cap</figcaption>
          </figure>
        </div>

        <p>Remove Alcohol Cartridge from its container by turning counter-clockwise. Then let the excess alcohol drip onto the sides of the container. Then place Alcohol Cartridge Into 8020a. Insert all the way and then turn clockwise to lock it:
        </p>


        <div class='grid even'>


          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-alcohol-cartridge.png" alt='Alcohol Cartridge'>
            <figcaption>Alcohol Cartridge</figcaption>
          </figure>


          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-place-alcohol-cartridge-into-8020a.png" alt='Place Alcohol Cartridge Into 8020a'>
            <figcaption>Alcohol Cartridge Placed Into 8020a</figcaption>
          </figure>

        </div>

        <p>Place the Storage Cap onto the Alcohol container. Rotate clockwise to seal:</p>

        <div class='grid even'>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-place-storage-cap-on-alcohol-container.png" alt='Place Storage Cap On Alcohol Container'>
            <figcaption>Place Storage Cap On Alcohol Container</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-clockwise-seal.png" alt='Clockwise Seal'>
            <figcaption>Clockwise Seal</figcaption>
          </figure>

        </div>

        <div id='connecting-the-8020a-and-8095'>
          <br>
          <br>
          <h4>Connecting the 8020A and the 8095</h4>
        </div>

        <p>Plug the N95 Companion Silver port To the 8020A Silver port:</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-plug-silver-to-silver.png" alt='Plug Silver To Silver'>
          <figcaption>Plug Silver To Silver</figcaption>
        </figure>

        <p>At the back, connect the two devices via the telephone cable. Plug all the way in until you hear a clicking sound:</p>
        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-plug-back.png" alt='Connect the two devices via the telephone cable'>
            <figcaption>Back view, with the two devices connected via telephone cable</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-plug-back-all-the-way.png" alt='Plugged all the way in'>
            <figcaption>Plugged all the way in</figcaption>
          </figure>
        </div>


        <p>Get the power adapter for the TSI 8020A:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-power-adapter.png" alt='Power Adapter'>
            <figcaption>Power Adapter</figcaption>
          </figure>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-connect-power-adapter-and-cord.png" alt='Connect Power Adapter And Cord'>
            <figcaption>Connect Power Adapter And Cord</figcaption>
          </figure>
        </div>

        <p>Plug Barrel Jack of Power Adapter into 8020A</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-plug-barrel-jack.png" alt='Plug Barrel Jack'>
          <figcaption>Plug Barrel Jack</figcaption>
        </figure>

        <div id='setup-n95-companion-pendant'>
          <br>
          <br>
          <h4>Setting up N95 Companion Pendant</h4>
        </div>

        <p>N95 Companion Pendant. Connect the N95 Companion Pendant to the N95 Companion by attaching the blue connector and the sampling tube like so:</p>


        <div class='grid even'>
        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-n95-companion-pendant.png" alt='N95 Companion Pendant'>
          <figcaption>N95 Companion Pendant</figcaption>
        </figure>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-attach-two-plugs-to-n95-companion.png" alt='Attach Two Plugs To N95 Companion'>
          <figcaption>Attach Two Plugs To N95 Companion</figcaption>
        </figure>

        </div>

        <div id='setup-aerosol-generator'>
          <br>
          <br>
          <h4>Setting up the Aerosol Generator</h4>
        </div>

        <p>Extract the Salt Reservoir container and the aerosol generator. Add tap water to the fill line, and then add some salt, preferably kosher salt (just NaCl). Mix the solution so that the salt dissolves. Attach Salt Solution Container To Humidifier and then rotate to seal the two together:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-salt-solution-reservoir.png" alt='Salt Solution Reservoir'>
            <figcaption>Salt Solution Reservoir</figcaption>
          </figure>


          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-attach-salt-solution-container-to-humidifier.png" alt='Attach Salt Solution Container To Humidifier'>
            <figcaption>Attach Salt Solution Container To Humidifier</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-plug-humidifier.png" alt='Plug Humidifier'>
            <figcaption>Plug Humidifier</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-humidifier-plug-to-wall-socket-and-turn-on.png" alt='Humidifier Plug To Wall Socket And Turn On'>
            <figcaption>Humidifier Plug To Wall Socket And Turn On</figcaption>
          </figure>
        </div>

        <div id='turning-on-the-portacount'>
          <br>
          <br>
          <h4>Turning on the PortaCount</h4>
        </div>

        <p>Turn On by pressing the On/Off button. You should see a countdown. After waiting a minute, you should see something like so:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-turn-on.png" alt='Turn On'>
            <figcaption>Turn On</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-after-waiting-a-minute.png" alt='After Waiting A Minute'>
            <figcaption>After Waiting A Minute</figcaption>
          </figure>
        </div>

        <p>Switch to Count Mode by pressing the COUNT button. <strong>If the value on the screen is less than 70 particles per cubic centimeter, then the counts are way too low. You'll need to run the aerosol generator, and wait until the level is way above that limit</strong>.</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-count-mode-low.png" alt='Count Mode Low'>
          <figcaption>Ambient Count Too Low</figcaption>
        </figure>


        <div id='daily-checks'>
          <br>
          <br>
          <h4>Daily Checks</h4>
        </div>

        <p>Once you have way over 70 particles / cubic centimeter, you could run the Daily Checks to ensure that the fit factors that you're getting from the PortaCount are valid.</p>


        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-daily-check-zero-check-filter.png" alt='Daily Check Zero Check Filter'>
            <figcaption>Daily Check Zero Check Filter</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-zero-check-connected-to-mask-sample-tube.png" alt='Zero Check Connected To Mask Sample Tube'>
            <figcaption>Zero Check Connected To Mask Sample Tube</figcaption>
          </figure>
        </div>

        <p>You should get 0.00 particles per cubic centimeter. Switch to the Fit Test mode by clicking on the button. Then press Start. After a minute, you should get a fit factor of 200, the highest that can be detected by the PortaCount:</p>


        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-should-get-0-count-while-using-zero-check-filter.png" alt='Should Get 0 Count While Using Zero Check Filter'>
            <figcaption>Should Get 0 Count While Using Zero Check Filter</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-zero-check-fit-test-waiting.png" alt='Zero Check Fit Test Waiting'>
            <figcaption>Zero Check Fit Test Waiting</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-zero-check-gives-highest-score-possible-of-200.png" alt='Zero Check Gives Highest Score Possible Of 200'>
            <figcaption>Zero Check Gives Highest Score Possible Of 200</figcaption>
          </figure>
        </div>

        <p>Wear N95 Companion Pendant</p>

        <div id='ready-for-testing'>
          <br>
          <br>
          <h4>Ready for Testing</h4>
        </div>

        <p>Once the Daily Checks pass, you are now ready to test masks on your face. Go ahead and wear the N95 Pendant.</p>

        <div class='grid even'>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-wear-n95-companion-pendant.png" alt='Wear N95 Companion Pendant'>
          <figcaption>Wear N95 Companion Pendant</figcaption>
        </figure>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-n95-pendant-tighten.png" alt='N95 Pendant Tighten'>
          <figcaption>N95 Pendant Tighten</figcaption>
        </figure>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-attach-mask-sample-to-mask-probe.png" alt='Attach Mask Sample Tube To Mask Probe'>
          <figcaption>Attach Mask Sample Tube To Mask Probe</figcaption>
        </figure>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-don-respirator.png" alt='Don Respirator'>
          <figcaption>Don Respirator</figcaption>
        </figure>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-n95-pendant-ensure-ambient-sample-tube-unblocked.png" alt='N95 Pendant Ensure Ambient Sample Tube Unblocked'>
          <figcaption>N95 Pendant Ensure Ambient Sample Tube Unblocked</figcaption>
        </figure>
        </div>

        <p>While the PortaCount is on Fit Test mode, press the Start button and then do an exercise from the protocol (e.g. Bend over, Head side-to-side, Head up-and-down, Talking)</p>

        <figure>
          <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-run-fit-test-got-31-ff.png" alt='Run Fit Test Got 31 Ff'>
          <figcaption>Run Fit Test Got 31 Ff</figcaption>
        </figure>

        <p>Repeat for each of the exercises to complete the protocol for one mask. Record each result through the Breathesafe app, either one by one — see <router-link :to="tocPath('adding-a-fit-test')"> Adding a Fit Test </router-link> — or in bulk (see <router-link :to="tocPath('importing-fit-tests-in-bulk')"> Importing Fit Tests in Bulk).</router-link>
        </p>

        <p>Repeat the testing for other masks by first removing the mask sampling tube from the probe:</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-remove-tube-1.png" alt='Remove Tube 1'>
            <figcaption>Remove Tube 1</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-remove-tube-2.png" alt='Remove Tube 2'>
            <figcaption>Remove Tube 2</figcaption>
          </figure>

        </div>


        <div id='putting-things-back'>
          <br>
          <br>
          <h4>Putting things back</h4>
        </div>

        <p>When done, swap the Storage Cap with the Alcohol Cartridge. Make sure they are fastened correctly.</p>

        <div class='grid even'>
          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-when-done-get-ready-to-swap-storage-cap-and-alcohol-cartridge.png" alt='When Done Get Ready To Swap Storage Cap And Alcohol Cartridge'>
            <figcaption>When Done Get Ready To Swap Storage Cap And Alcohol Cartridge</figcaption>
          </figure>

          <figure>
            <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/portacount-setup/portacount-put-items-back-to-luggage.png" alt='Put Items Back To Luggage'>
            <figcaption>Put Items Back To Luggage</figcaption>
          </figure>
        </div>


        <div id='running-a-qualitative-fit-test'>
          <br>
          <br>
          <h3>Running a Qualitative Fit Test</h3>
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

      <p>Each exercise takes a minute. <strong>At the beginning of each exercise, use the same amount of time running the nebulizer as you did in the sensitivity step. On the other hand, at the 30-second mark, you should use half the amount of time of nebulization as in the sensitivity step.</strong>  For example, if it only took you 2 seconds of running the nebulizer to detect the sensitivity solution in the earlier step, you should run the nebulizer for 2 seconds with the fit test solution in the beginning of each exercise, and run the nebulizer for 1 second at the 30-second mark for each exercise. </p>

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

        <div id='importing-fit-tests-in-bulk'>
          <br>
          <br>
          <h4>Importing Fit Tests in Bulk</h4>
        </div>

        <p>This section walks you through importing fit tests via a CSV. For some people, they might be more comfortable writing down their data in spreadsheets than inputting data one-by-one directly in the app. In the Fit tests page, there should be an up-arrow icon, which is meant for importing fit tests in bulk:</p>

        <div id='import-a-file'>
          <h5>Import a File</h5>
        </div>

        <div class='center'>
          <figure>
            <router-link :to='{name: "FitTests"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/fit-test-page-with-bulk-upload-icon-arrow.png" alt='Fit Test Results'>
            </router-link>
            <figcaption>Import Bulk Fit Tests button</figcaption>
          </figure>
        </div>

        <p>Clicking on that should take you to the Bulk Fit Tests page:</p>

        <div class='center'>
          <figure>
            <router-link :to='{name: "BulkFitTestsImportsList"}'>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-none.png" alt='Bulk Fit Tests Imports'>
            </router-link>
            <figcaption>Bulk Fit Tests Imports page</figcaption>
          </figure>
        </div>

        <p>Clicking on the New import button should take you to the Import a File section:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-import-a-file.png" alt='Importing a File'>
            <figcaption>Importing a File</figcaption>
          </figure>
        </div>

        <p>You can click on the Help (?) button to learn more:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-import-a-file-help.png" alt='Importing a File: Help'>
            <figcaption>Importing a File: Help</figcaption>
          </figure>
        </div>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-import-a-file-help-2.png" alt='Importing a File: Help'>
            <figcaption>Importing a File: Help (Part II)</figcaption>
          </figure>
        </div>

        <a href="/sample_fit_tests_import.csv" download>You can download the sample CSV template here.</a>

        <p>Here's a preview of the sample CSV template you could use:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-sample-1.png" alt='Sample Data: Part I'>
            <figcaption>Sample Data: Part I</figcaption>
          </figure>
        </div>

        <p>As you can see some values might be the same thing (e.g. "ok" vs. "OK"). These from-file values will be mapped to the same Breathesafe value later on.</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-sample-2.png" alt='Sample Data: Part II'>
            <figcaption>Sample Data: Part II</figcaption>
          </figure>
        </div>

        <p>Rows representing a fit testing session for an individual-and-mask pair can have different testing modes (e.g. quantitative fit testing with N95/N99 mode vs. qualitative fit testing).</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-sample-3.png" alt='Sample Data: Part III'>
            <figcaption>Sample Data: Part III</figcaption>
          </figure>
        </div>

        <p>You can use that template and fill the spreadsheet with data, and then import that file.
        After choosing a CSV file with the data, you should see some metadata:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-import-a-file-success.png" alt='Importing a File'>
            <figcaption>Importing a File: Success</figcaption>
          </figure>
        </div>

        <div id='columns-matching'>
          <h5>Columns Matching</h5>
        </div>

        <p>After clicking Next, you'll be taken to the Columns Matching section:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-column-matching-1.png" alt='Columns Matching (Part I)'>
            <figcaption>Columns Matching (Part I)</figcaption>
          </figure>
        </div>

        <p>You can click on the Match button to do auto-matching:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-column-matching-2.png" alt='Columns Matching (Part II)'>
            <figcaption>Columns Matching (Part II)</figcaption>
          </figure>
        </div>

        <p>It's based on string matching, works pretty well, but could have errors. Scrolling down some more, you could see some of the exercises from the file being matched to exercises in Breathesafe:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-column-matching-3.png" alt='Columns Matching (Part III)'>
            <figcaption>Columns Matching (Part III)</figcaption>
          </figure>
        </div>

        <div id='user-matching'>
          <h5>User Matching</h5>
        </div>

        <p>Then hitting Next, you should be taken to the User Matching section. Hit the "Match" button:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-users.png" alt='User Matching'>
            <figcaption>User Matching</figcaption>
          </figure>
        </div>

        <div id='mask-matching'>
          <h5>Mask Matching</h5>
        </div>

        <p>Then hitting Next, you should be taken to the Mask Matching section. Hit the "Match" button:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-mask.png" alt='Mask Matching'>
            <figcaption>Mask Matching</figcaption>
          </figure>
        </div>

        <p>Sometimes there are mistakes with the auto-matching (e.g. Zimi 7711 and Zimi ZM100). Please fix.</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-mask-incorrect.png" alt='Mask Matching: Manual Fix'>
            <figcaption>Mask Matching: Manual Fix</figcaption>
          </figure>
        </div>

        <div id='user-seal-check-matching'>
          <h5>User Seal Check Matching</h5>
        </div>

        <p>Moving onto User Seal Check Matching, you might see something like this:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-user-seal-check-matching.png" alt='User Seal Check Matching'>
            <figcaption>User Seal Check Matching</figcaption>
          </figure>
        </div>

        <p>With the Match button and some manual matching:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-user-seal-check-matching-manual.png" alt='User Seal Check Matching: Auto + Manual Matching'>
            <figcaption>User Seal Check: Auto + Manual Matching</figcaption>
          </figure>
        </div>

        <div id='qlft-values-matching'>
          <h5>QLFT Values Matching</h5>
        </div>

        <p>QLFT Values Matching attempts to map pass and fail values to the corresponding Breathesafe values:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-qlft-values-matching.png" alt='QLFT Values Matching'>
            <figcaption>QLFT Values Matching</figcaption>
          </figure>
        </div>

        <div id='comfort-matching'>
          <h5>Comfort Matching</h5>
        </div>

        <p>In Comfort Matching, the Match functionality was successful in some but not for others. Manual fix was needed:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-comfort-matching.png" alt='Comfort Values Matching'>
            <figcaption>Comfort Values Matching</figcaption>
          </figure>
        </div>

        <p>With manual fixing:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-comfort-matching-manual.png" alt='Comfort Values Matching — Manual'>
            <figcaption>Comfort Values Matching — Manual</figcaption>
          </figure>
        </div>

        <div id='review-and-import'>
          <h5>Review and Import</h5>
        </div>

        <p>Then review:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-review-1.png" alt='Comfort Values Matching — Review (Part I)'>
            <figcaption>Review (Part I)</figcaption>
          </figure>
        </div>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-review-2.png" alt='Comfort Values Matching — Review (Part II)'>
            <figcaption>Review (Part II)</figcaption>
          </figure>
        </div>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-review-3.png" alt='Comfort Values Matching — Review (Part III)'>
            <figcaption>Review (Part III)</figcaption>
          </figure>
        </div>

        <p>If everything looks good, please press the "Import" button. That should show you a success message:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-successful.png" alt='Bulk Imports Successful'>
            <figcaption>Bulk Imports Successful</figcaption>
          </figure>
        </div>

        <p>Clicking on the "Go to Bulk Imports" should take you to that page:</p>

        <div class='center'>
          <figure>
              <img src="https://breathesafe.s3.us-east-2.amazonaws.com/images/mask-recommender-onboarding/bulk-imports-page-with-one-row.png" alt='Bulk Imports Successful'>
            <figcaption>Bulk Imports — New Row</figcaption>
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
    margin: 2em;
  }

  .toc {
    width: 27vw;
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
      height: auto;
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

  /* Scroll margin for TOC anchor links */
  #toc,
  #adding-a-respirator-user,
  #adding-a-fit-test,
  #running-a-qualitative-fit-test,
  #import-a-file,
  #columns-matching,
  #user-matching,
  #mask-matching,
  #user-seal-check-matching,
  #qlft-values-matching,
  #comfort-matching,
  #review-and-import {
    scroll-margin-top: 4em;
  }

</style>
