<template>
  <div class='row'>
    <div class='col border-showing left-pane'>
      <router-link to="/faqs#faqs" class='link-h1'>
        Frequently Asked Questions
      </router-link>

      <router-link to="/faqs#data-contribution" class='link-h2'>
        How do I contribute data?
      </router-link>

      <router-link to="/faqs#why-should-we-care-about-covid-risk" class='link-h2'>
        Why should we care about covid risk?
      </router-link>
      <router-link to="/faqs#how-to-improve-indoor-air-quality" class='link-h2'>
        Is there a succinct video I can watch to learn about indoor air quality?
      </router-link>

      <router-link to="/faqs#modeling" class='link-h1'>
        How are risk calculations done in general?
      </router-link>

      <router-link to="/faqs#risky-behaviors-and-environments" class='link-h2'>
        Risky Behaviors and Environments
      </router-link>

      <router-link to="/faqs#safer-behaviors-and-environments" class='link-h2'>
        Safer Behaviors and Environments
      </router-link>

      <router-link to="/faqs#risk-metrics" class='link-h1'>
        Risk Metrics in more detail
      </router-link>

      <router-link to="/faqs#one-hr-risk-with-infector" class='link-h2'>
        What is the 1-hr Risk w/ Infector?
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
          In order to contribute data, you must be in possession of one of these
          carbon dioxide monitors. They must be one of the
          following NDIR devices. Note that the Aranet4 is preferred for its long battery life, portability, and data storage.

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
          If you don't have any of the devices and find it financially difficult to purchase one, please email us at <a href="mailto:info@breathesafe.xyz?subject=CO2 monitors&body=Hello,I'm interested in helping log data into the app. I would like to borrow a CO2 monitor.">info@breathesafe.xyz</a>. We cannot guarantee that we will be able to loan one, but we will keep you in mind.
          </p>

          <p>
          Once you have one of the models, you can <router-link :to='{ name: "SignIn"}'>sign up</router-link>.
          You will be sent a confirmation email. After
          clicking on the confirmation email, you'll be sent to the
          <router-link to="/profile">Profile</router-link> page. Please fill out
          your <router-link :to='{ name: "SignIn"}'>Profile</router-link>, especially the
          <router-link :to='{name: "Profile", query: { section: "ventilation"}}'>ventilation section, which asks about the CO2 monitor</router-link>.
          Once that is filled out, one can click on the
          <router-link to='/events/new'>Add Measurements</router-link> link.
          </p>

          <br id='why-should-we-care-about-covid-risk'>
          <br>
          <br>
          <h4 >Why should we care about covid risk?</h4>
          <p>
            While vaccines prevent deaths and hospitalizations to a great degree, they by themselves are not so great at
            <a href="https://www.nejm.org/doi/full/10.1056/NEJMoa2119451">
            preventing symptomatic infections
            </a>
            and
            <a href="https://www.nature.com/articles/d41586-022-01453-0#:~:text=The%20researchers%20found%20that%20vaccination,found%20much%20higher%20protection%20rates."
            >
            long COVID
            </a>.
            As of August 2022, it is estimated that
            <a
            href="https://www.npr.org/2022/07/31/1114375163/long-covid-longhaulers-disability-labor-ada"
            >
            4 million employees in the U.S. are out of work due to long-COVID.
            </a>

            Decreasing the risk of transmission will decrease the
            likelihood of contracting COVID, and therefore,
            <a href="https://www.science.org/content/article/what-causes-long-covid-three-leading-theories"
            >
            long-COVID</a>.

            Doing so will also make spaces become more
            accessible to
            <a href="https://www.theatlantic.com/health/archive/2022/02/covid-pandemic-immunocompromised-risk-vaccines/622094/"
            >the millions of immunocompromised people in the U.S.</a>
            We need a "vaccines-plus" strategy, not just a "vaccines-only" strategy, using non-pharmaceutical interventions such as cleaning the air, masking, and rapid testing.

            Investing in infrastructure to clean the air will make the spaces
            we inhabit <a href="https://www.science.org/doi/10.1126/science.abd9149">be
            more resilient not just to COVID-19, but also to other respiratory viruses</a>.
          </p>

          <p class='bold'>For more up-to-date information about COVID-19, check out <a href="https://peoplescdc.org/">People's CDC</a>.
          </p>

          <br id='how-to-improve-indoor-air-quality'>
          <br>
          <br>

          <h4>Is there a succinct video I can watch to learn about indoor air quality?</h4>
          <p>This one by Scientific American is pretty good.</p>

          <div class='centered'>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/djnie-h6Bn8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>

          <br id='modeling'>
          <br>
          <br>

          <h4>How are risk calculations done in general?</h4>

          <p>The model used here is a variant of
          <a href="https://pubs.acs.org/doi/full/10.1021/acs.est.1c06531">
          Peng et.al.'s Practical Indicators for Risk of Airborne Transmission in Shared Indoor Environments and Their Application to COVID-19 Outbreaks
          </a>. We assume that an infector is present as it allows us to test the resiliency of environmental
            and behavioral interventions in decreasing the risk
            of transmission of respiratory viruses.
          </p>
          <p>
          Put simply, the risk of transmission is proportional to the generation rate of
          infectious aerosols from infector(s) and is inversely related to the removal rate of said
          aerosols. The faster the generation rate of infectious aerosols from infectors,
          the higher the risk. On the other hand, the faster the rate of air cleaning in
          the air, the lower the risk.
          </p>
          <br id='risky-behaviors-and-environments'>
          <br>
          <br>
          <h4>Risky behaviors and environments</h4>
          <p>Actions that increase risk:
            <ul>
              <li>
              infector not wearing a mask with high filtration efficiency. N95
              and Elastomeric masks block a lot more particles of aerosols that contain the
              virus than cloth and surgical.
              </li>
              <li>
              aerosol activity. Singing produces more aerosols than talking,
              which in turn produces more aerosols than oral breathing.
              </li>
              <li>
              exercise. Exercise encourages more exhalation. If there's an
              infector doing exercise, they will generate more respiratory particles in the
              air more so than someone who is at rest.
              </li>
              <li>inherent infectiousness of the virus. Alpha &lt; Delta &lt; Omicron. </li>
            </ul>

          </p>

          <br id='safer-behaviors-and-environments'>
          <br>
          <br>
          <h4>Safer behaviors and environments</h4>
            <p>
            In contrast, cleaning the air efficiently and quickly lowers the
            probability of infection. Air is cleaner when:

            <ul>
              <li>
              air is filtered through masking.
              If an infector is wearing a tight-fitting mask with a high
              filtration efficiency (e.g. N95 and Elastomeric masks), then there are less
              infectious particles in the air for susceptibles to breathe in.
              Likewise, if susceptibles are wearing such masks, they can significantly reduce
              their inhalation dose.
               </li>
              <li>
              HEPA or MERV 13 filtration with powerful fans are used. Portable
              air cleaning technologies like the DIY Corsi-Rosenthal box or commercial ones
              with comparable or higher clean air delivery rates (CADR) could quickly remove
              particles from the air that contain the virus.
              </li>
              <li>
              ventilation is increased. Increasing the amount of air exchanged
              from outside to inside (e.g. by opening windows) discourages build up of
              infectious aerosols in a room. Outdoors generally have high ventilation rates.
              </li>
              <li>
              Irradiation technologies are put in place to deactivate the virus while
              in the air (e.g. Upper-room UV).
              </li>
              <li>
              susceptibles inhale more slowly (e.g. through resting instead of
              doing heavy exercise while an infector is present). The less breaths a
              susceptible takes, the less infectious dose one can receive.
              </li>
            </ul>
          </p>

          <p>
              We assume that the air is well-mixed (i.e. COVID particles are
              spread evenly throughout the space) and that people are far apart
              (6 ft or more). If people are far apart, then they are less likely to breathe
              in a jet of aerosols from an infector, and increases the effectiveness of
              the environment (e.g. air cleaning through ventilation, filtration, deactivation).
              <span class='bold'>
                If this assumption does not hold in practice for this space, then the estimates of risk can be thought of as lower-bound risks.
              </span>
          </p>
          <br id='risk-metrics'>
          <br>
          <br>
          <h3 class='subsection'>Risk Metrics</h3>

          <br id='one-hr-risk-with-infector'>
          <br>
          <br>
          <h3>What is the 1-hr Risk w/ Infector?</h3>

          <p class='bold italic'>
              This risk assumes that there is one infector in the room.
          </p>

          <p>
              This metric considers environment parameters and worst-case behaviors only.
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
