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

      <router-link :to="tocPath('how-long-study')">
        How long will you be in this study?
      </router-link>

      <router-link :to="tocPath('study-procedures')">
        What are the study procedures?
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

      <router-link :to="tocPath('confidentiality')">
        How will participants' information be kept confidential?
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
        involved.

        Existing approaches of testing masks like the <a
          href="https://www.armbrustusa.com/pages/mask-testing/">Armbrust</a>
        and <a
                href="https://docs.google.com/spreadsheets/d/1M0mdNLpTWEGcluK6hh5LjjcFixwmOG853Ff45d3O-L0/edit?gid=1976839763#gid=1976839763">MaskNerd</a>
        mask testing
        databases focus on filtration efficiency and breathability, but do not
        provide an easy way for people to find masks that would fit their face.
        On the other hand, <a
          href="https://www.testtheplanet.org/">TestThePlanet</a> focuses on
        fit testing of masks on some sample of testers, but also does not help people find masks that fit their individual faces. Fit is highly individual.
        Amanda Abbott <a href="">has created the PDX respirator repository</a>
        which has elastomeric respirators and disposable masks, and has a
        functional recommender system. However, the performance of it is
        quantitatively unknown. There is an iPhone app called <a
          href="https://apps.apple.com/us/app/fit-mask/id1578496578">Fit
          Mask</a> that uses the iPhone camera to do 3D scanning of the face.
        It estimates two measurements and then makes some mask recommendations.
        However, some users have said that they’ve gotten very inaccurate
        results, since the app rounds to the nearest inch.  The hope for this
        project is that using facial features, a diverse sample of faces, and a
        large enough sample size, we can create "fit profiles" for a bunch of
        masks, so that when someone does come to the app with the intention of
        finding a mask that fits their face, they can do so in an easy way. We
        envision doing this project in two phases.


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
              <td>10 minutes</td>
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
        <div id='study-procedures'>
          <br>
          <br>
          <h4>What are the study procedures?</h4>
        </div>


        <h5>Phase 1: manual measurements of facial features (using caliper/tape) </h5>

        <p>
        You will be asked to give information about demographics and facial measurements <router-link :to='{name: "RespiratorUsers"}'>here</router-link>.
        Once that is filled out, you can add the following fit testing data <router-link :to='{name: "NewFitTest"}'> here</router-link>:
        </p>

        <ul>
          <li>user seal check</li>
          <li>qualitative fit testing</li>
          <li>quantitative fit testing</li>
          <li>comfort</li>
        </ul>

        <p>
        You will be guided by the UI. Clicking on the "Save and Continue" button will validate the information being saved and will show helpful error messages and general messages. For example, if a user fails the user seal check section, they don't need to add qualitative or quantitative fit testing data (as it is assumed that they will most likely fail either of those more stringent tests).
        </p>

        <h5>Phase 2: automated inference of facial measurements via selfies </h5>

        <p>Getting facial measurements via caliper and tape can be a bit tedious and could deter adoption of said recommender system. Breathesafe LLC will attempt to simplify this process by inferring facial measurements via selfies. You will be given the opportunity to share selfies to this project to assess and improve the performance of a facial measurement system based on selfies. Given your facial measurements that were taken from phase 1 using caliper and tape, we will assess and improve the accuracy of said inference system.
        </p>

        <div id='leave-study'>
          <br>
          <br>
          <h4>Can participants choose to leave the study?</h4>
        </div>
        <p>Participants may be able to delete their data anytime using this button (TODO). That will delete user information such as email, password, demographics, and fit testing data.</p>

        <div id='risks-harms'>
          <br>
          <br>
          <h4>What are the risks and harms of participating in the study?</h4>
        </div>
        <p>Sensitive data like facial measurements will be stored in a database. Breathesafe LLC will follow best security practices to prevent malicious actors from accessing said database. Example of such actions are:
        <ul>
          <li>using https to prevent man-in-the-middle attacks.</li>
          <li>admins will be using password managers and two factor authentication</li>
          <li>number of admins will be as small as possible to limit risk</li>
        </ul>
        </p>

        <div id='benefits'>
          <br>
          <br>
          <h4>What are the benefits of participating in this study?</h4>
        </div>

        <p>One direct benefit is one might be able to find a mask that has overall high protection (combination of fit and high filtration efficiency), if they haven't aready. Another benefit is gaining a sense of accomplishment in helping others find masks that offer high protection for their faces by providing data that will be used to improve performance of a personalized recommender system.</p>

        <div id='confidentiality'>
          <br>
          <br>
          <h4>How will participants' information be kept confidential?</h4>
        </div>

        <p> In terms
        of data publicly displayed on this web app, we will only show
        aggregate data about users, such as demographic information and fit
        test results for each mask. We will maintain privacy of individual fit
        testing information along with demographics. We will preserve privacy
        of individuals in the aggregation of the data: if a demographic has
        less than 5 people in it, they will be grouped in the "Prefer not to
        disclose / too small sample size" group.
        </p>

        <p>This study may go on indefinitely. If for any reason you want your data deleted, you may do so. See data deletion section above.</p>

        <div id='compensation'>
          <br>
          <br>
          <h4>Are participants compensated in this study?</h4>
        </div>

        <p>Breathesafe LLC applied for a grant for this project. If that goes
        through, it is possible that some volunteers with qualitative and
        quantitative fit testing devices may get some compensation for testing
        equipment and labor.</p>

        <div id='participant-rights'>
          <br>
          <br>
          <h4> What are the rights of the participants? </h4>
        </div>

        <p>Your participation in this study is voluntary. You may decide not to
        be in this study. Even if you consent to participate, you have the
        right to withdraw and delete your data at any time. See the <router-link :to="tocPath('leave-study')">
        Can participants choose to leave the study?
      </router-link> section for details.
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

      <div></div>
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
      return `/consent_form#${suffix}`
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

  @media(min-width: 750px) {
    .toc-button {
      display: none;
    }

  }
  @media(max-width: 750px) {
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
