<template>
  <div class='row'>
    <div class='col border-showing left-pane'>
      <router-link to="/faqs#faqs" class='link-h1'>
        Frequently Asked Questions
      </router-link>
      <router-link to="/faqs#data-contribution" class='link-h1'>
        How do I contribute data?
      </router-link>
      <router-link to="/faqs#risk-metrics" class='link-h1'>
        Risk Metrics
      </router-link>
      <router-link to="/faqs#one-hr-risk" class='link-h2'>
        What is the 1-hr Risk?
      </router-link>
      <router-link to="/faqs#one-hr-risk-with-infector" class='link-h2'>
        What is the 1-hr Risk w/ Infector?
      </router-link>
      <router-link to="/faqs#one-hr-risk-low-but-one-hr-risk-with-infector-high" class='link-h2'>
        What does it mean if the 1-hr Risk is quite low, but the 1-hr Risk w/ Infector is quite high?
      </router-link>
    </div>

    <div class='col border-showing right-pane'>
      <div class='container'>
        <div class='container'>
          <br id='faqs'>
          <br>
          <br>
          <h3 class='subsection'>Frequently Asked Questions</h3>

          <br id='data-contribution'>
          <br>
          <br>
          <h3>How do I contribute data?</h3>

          <p>
          If you haven't signed up, please do. You will be sent a confirmation email. After
          clicking on the confirmation email, you'll be sent to the Profile page. You can
          add your CO2 monitor(s) in the Profile page. They must be one of the
          following NDIR devices:
          </p>

          <div class='centered'>

            <table>
              <tr>
                <th>Image</th>
                <th>Name</th>
                <th>Cost</th>
              </tr>
              <tr v-for='carbonDioxideMonitor in carbonDioxideMonitors'>
                <td>
                <a :href="carbonDioxideMonitor.website">
                  <img :src="carbonDioxideMonitor.imageLink" :alt="`Image of ${carbonDioxideMonitor.name}`" class='icon-img'>
                </a>
                </td>
                <td>
                <a :href="carbonDioxideMonitor.website">
                  {{ carbonDioxideMonitor.name }}
                </a>
                </td>
                <td>
                  {{ carbonDioxideMonitor.estimatedCost }}
                </td>
              </tr>
            </table>



          </div>

          <p>
          Once you add in one of your models through the Profile, you can
          then go to <router-link to='/'>Events</router-link> and click on the
          <router-link to='/events/new#top'>Add New Event</router-link> link.
          </p>
          <br id='risk-metrics'>
          <br>
          <br>
          <h3 class='subsection'>Risk Metrics</h3>

          <br id='one-hr-risk'>
          <br>
          <br>
          <h3>What is the 1-hr Risk?</h3>

          <p class='bold italic'>
              This risk is useful when you are uncertain about whether or not an
              infector is in the room.
          </p>

          <p>
              It makes use of some notion of a person being infectious, and combines
              that information with occupancy data to see how likely that at
              least one person in the room is infectious.  Then it combines that
              information with the probability that, given someone infectious
              <span class='italic'>is</span> in the room, how likely are they to
              infect, based on their and other people's behavior and the environment.
          </p>

          <p>
              In more detail, this takes into account case rates in the area and
              multiplies it by some factor to account for cases that are
              uncounted. From there, we have an estimate that a randomly sampled one person
              from the population is infectious. Once we have that, we then
              compute the probability that at least someone is infectious in the
              room. Finally, each measurement has different sets of people marked by their
              profiles (e.g. mask usage, aerosol exhalation rates due to
              singing vs. resting). Some profiles are more risky than others. For example,
              those who wear N95 masks or elastomeric masks are likely to transmit less virus
              than those who don't.  We look at how many people are expected to be in that
              group, depending on if the "max occupancy" option is used, or if the "at this
              hour" option is used. We scale accordingly. After scaling, we
              proceed with computing the probability that someone from that group is
              infectious, and multiplying that with the conditional probability "if someone
              were infectious from this group, what's the chance of transmission?"
              We add these products to get the overall risk of transmission, taking into account
              the uncertainty of an infector being present.
          </p>

          <br id='one-hr-risk-with-infector'>
          <br>
          <br>
          <h3>What is the 1-hr Risk w/ Infector?</h3>

          <p class='bold italic'>
              This risk assumes that there is one infector in the room.
          </p>

          <p>
              Unlike the <span class='italic'>1-hr Risk</span>, this metric
              does not take occupancy into account. This metric considers
              environment parameters and worst-case behaviors only.
          </p>

          <p>
              For this risk, we go through the different activity profiles that
              were recorded at the time of measurement.

              Some people are riskier than others. We go through the recorded
              activities for this place. We pick the worst case exhalation activity for an
              infector (e.g. loudly speaking during heavy exercise vs. oral
              breathing at rest), along with the riskiest susceptible inhalation activity
              (e.g. at rest vs. heavy exercise).  We assume that the riskiest behaviors are
              being done. We then compute, for 1 hour, what is the probability of
              transmitting SARS-CoV-2, assuming that the infector stays in the
              room for an hour.
          </p>

          <br id='one-hr-risk-low-but-one-hr-risk-with-infector-high'>
          <br>
          <br>
          <h3>What does it mean if the 1-hr Risk is quite low, but the 1-hr Risk w/ Infector is quite high?</h3>

          <p>
              This means that the environmental protections and individuals'
              behaviors are not good enough, hence the 1-hr Risk w/ Infector being high.
              However, if the prevalence rate of SARS-CoV-2 is low, and if the room has a low
              maximum occupancy, one could still get a low 1-hr Risk score.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { CARBON_DIOXIDE_MONITORS } from './carbon_dioxide_monitors.js'

export default {
  name: 'FAQs',
  computed: {
    carbonDioxideMonitors() {
      return CARBON_DIOXIDE_MONITORS
    }
  }
}

</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: row;
  }
  .container {
    margin: 1em;
  }
  label {
    padding: 1em;
  }
  .subsection {
    text-align: center;
    font-weight: bold;
    margin-left: 1em;
  }

  .wide {
    display: flex;
    flex-direction: row;
  }

  .row {
    display: flex;
    flex-direction: row;
  }

  .textarea-label {
    padding-top: 0;
  }

  textarea {
    width: 30em;
  }

  .border-showing {
    border: 1px solid grey;
  }

  .centered {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .wider-input {
    width: 30em;
  }

  button {
    padding: 1em 3em;
  }

  table {
    text-align: center;
    padding: 2em;
  }

  .scrollable {
    overflow-y: scroll;
    height: 72em;
  }

  .scroll-table {
    height: 40em;

    overflow-y: scroll;
  }


  .col {
    display: flex;
    flex-direction: column;
  }

  .margined {
    margin: 2em;
  }

  .padded {
    padding: 1em;
  }

  th {
    padding: 1em;
  }

  .font-light {
    font-weight: 400;
  }

  td {
    padding: 1em;
  }

  span {
    line-height: 2em;
  }

  .highlight {
    font-style: italic;
    font-weight: bold;
  }

  img {
    width: 4em;
  }

  p {
    line-height: 2em;
  }

  li {
    line-height: 2em;
  }

  .bold {
    font-weight: bold;
  }
  .italic {
    font-style: italic;
  }

  .clicked {
    background-color: #e6e6e6;
  }

  .color-cell {
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px black;
    padding: 1em;
  }

  .quote {
    font-style: italic;
    padding-left: 2em;
  }

  div {
    scroll-behavior: smooth;
  }

  .left-pane {
    width: 20rem;
    height: 50em;
    position: fixed;
    left: 0em;
    border-right: 0px;
    border-top: 0px;
    border-bottom: 0px;
  }

  .right-pane {
    width: 70vw;
    height: auto;
    margin-left: 20rem;
  }

  .link-h1 {
    margin-left: 2em;
    margin-top: 1em;
  }

  .icon-img {
    width: 10rem;
    height: 10rem
  }
  .link-h2 {
    margin-left: 3em;
    margin-top: 1em;
  }

  @media (max-width: 840em) {
    .centered {
      overflow-x: auto;
    }
  }

  @media (max-width: 1080px) {

    .left-pane {
      display: none;
      position: unset;
    }

    .right-pane {
      margin-left: 0;
      width: 100vw;
    }
  }

</style>
