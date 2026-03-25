<template>
  <router-link to="/introduction#toc-mobile">
    <CircularButton text="TOC" class='toc-button'/>
  </router-link>

  <div class="container">
    <div class='toc toc-mobile margined' id='toc-mobile'>
      <h2><strong>Table of Contents</strong></h2>

      <router-link to="/introduction#top">
        Introduction
      </router-link>

      <router-link to="/introduction#why-this-matters">
        Why This Matters
      </router-link>

      <router-link to="/introduction#what-came-before">
        What Came Before
      </router-link>

      <router-link to="/introduction#what-we-do-differently">
        What We Do Differently
      </router-link>

      <router-link to="/introduction#how-it-works">
        How It Works
      </router-link>

      <router-link to="/introduction#why-failed-results-matter">
        Why Failed Results Matter
      </router-link>

      <router-link to="/introduction#quality-and-accessibility">
        Quality and Accessibility
      </router-link>

      <router-link to="/introduction#contribute">
        Contribute
      </router-link>

      <router-link to="/introduction#deep-dives">
        Deep Dives
      </router-link>

      <router-link to="/introduction#current-limitations">
        Current Limitations
      </router-link>

      <router-link to="/introduction#references">
        References
      </router-link>
    </div>

    <div class="grid">
      <div class='toc toc-desktop margined overflow' id='toc'>
        <br>
        <br>
        <br>
        <div><br></div><h2><strong>Table of Contents</strong></h2><div><br></div>

        <router-link to="/introduction#top">
          Introduction
        </router-link>

        <router-link to="/introduction#why-this-matters">
          Why This Matters
        </router-link>

        <router-link to="/introduction#what-came-before">
          What Came Before
        </router-link>

        <router-link to="/introduction#what-we-do-differently">
          What We Do Differently
        </router-link>

        <router-link to="/introduction#how-it-works">
          How It Works
        </router-link>

        <router-link to="/introduction#why-failed-results-matter">
          Why Failed Results Matter
        </router-link>

        <router-link to="/introduction#quality-and-accessibility">
          Quality and Accessibility
        </router-link>

        <router-link to="/introduction#contribute">
          Contribute
        </router-link>

        <router-link to="/introduction#deep-dives">
          Deep Dives
        </router-link>

        <router-link to="/introduction#current-limitations">
          Current Limitations
        </router-link>

        <router-link to="/introduction#references">
          References
        </router-link>
      </div>

      <div class='main margined'>
        <div id='top'>
          <div class='hero-grid'>
            <div class='hero-copy'>
              <p class='eyebrow'>Introduction</p>
              <h1>MasqFit is now available in the iOS App Store.</h1>
              <p class='hero-lede'>
                Breathesafe and MasqFit are designed around a simple public-interest idea:
                high-quality mask fit information should not be limited to people who already
                have easy access to formal fit testing.
              </p>
              <p>
                <strong>MasqFit</strong> makes it easier to capture facial measurements using
                an iPhone. <strong>Breathesafe</strong> connects those measurements with mask
                data and contributed outcomes, including fit tests and failed user seal checks,
                to estimate which masks are more likely to fit a particular face.
              </p>
              <p>
                The goal is not to replace fit testing. The goal is to make better starting
                points, better transparency, and better public knowledge available to more people.
              </p>

              <div class='cta-row'>
                <a
                  class='cta primary'
                  href="https://apps.apple.com/ca/app/masqfit/id6756614276"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Download MasqFit
                </a>
                <router-link class='cta secondary' to="/onboarding">
                  Contribute Your Results
                </router-link>
              </div>
            </div>

            <div class='hero-visual'>
              <img :src="masqfitLaunchHero" alt="MasqFit App Store launch graphic showing the app interface and app availability announcement.">
            </div>
          </div>

          <p><strong>Last updated:</strong> March 24, 2026</p>
        </div>

        <hr>

        <div id='why-this-matters'>
          <br>
          <br>
          <h2>Why This Matters</h2>
          <p>
            The best way to know whether a mask fits a specific person is still direct fit
            testing on that person with that mask. But formal fit testing takes time,
            equipment, training, and access that many people do not have.
          </p>
          <p>
            Without that access, people often rely on trial and error, generic sizing advice,
            or whatever mask seems popular online. That can work sometimes, but it is not the
            same as evidence tied to a real face and a real outcome.
          </p>
          <p>
            Breathesafe and MasqFit try to narrow that gap: more accessible than formal fit
            testing for everyone, but more evidence-based and more transparent than closed,
            black-box matching tools.
          </p>
        </div>

        <hr>

        <div id='what-came-before'>
          <br>
          <br>
          <h2>What Came Before</h2>
          <p>
            Earlier work helped move the field forward, but each approach comes with limits.
          </p>
          <p>
            <strong>Fit Mask</strong> and <strong>MaskFit AR</strong> both pushed toward a
            more accessible experience by using face scans or facial matching. That direction
            matters. But those apps are closed systems: the code is not publicly auditable,
            the data collection and update processes are not fully transparent, and the public
            cannot easily inspect how their recommendations improve over time.
          </p>
          <p>
            <strong>Fit Test the Planet</strong> has done valuable public-interest work by
            surfacing adversarial quantitative fit test results and showing which masks have
            worked for many adults. That helps people discover strong candidates. But it does
            not primarily solve the personalization problem of estimating which masks are more
            likely to fit one specific face.
          </p>
          <p>
            Existing literature on respirator anthropometry is also important. It shows that
            facial dimensions matter, but it also shows why static panels and limited study
            populations are not enough for everyone. The 2007 National Academies review noted
            weaknesses in older respirator panel development strategies and called for better
            representation and stronger methods. More recent work continues to show that facial
            dimensions are relevant to respirator fit while also highlighting the limits of
            small or uneven datasets.
          </p>
        </div>

        <hr>

        <div id='what-we-do-differently'>
          <br>
          <br>
          <h2>What We Do Differently</h2>
          <p>
            The main difference is not that Breathesafe and MasqFit claim perfect
            personalization. The main difference is that this project is designed to be
            <strong>open, inspectable, and improvable</strong>.
          </p>
          <ul>
            <li>The code is open source.</li>
            <li>The recommendations are tied to crowd-sourced outcomes, not just geometric matching.</li>
            <li>The project is meant to improve as more people contribute fit tests and seal check data.</li>
            <li>The public can inspect the infrastructure rather than relying on a closed promise.</li>
          </ul>
          <p>
            That matters because personalized recommendations should not depend on a private,
            unaccountable black box if the goal is public trust and long-term improvement.
          </p>
        </div>

        <hr>

        <div id='how-it-works'>
          <br>
          <br>
          <h2>How It Works</h2>
          <p>
            At a high level, the workflow is:
          </p>
          <ol>
            <li>MasqFit captures facial measurements using an iPhone-compatible workflow.</li>
            <li>Breathesafe stores mask information and fit-related outcomes.</li>
            <li>Contributed outcomes can include quantitative fit tests, qualitative fit tests, and failed user seal check data.</li>
            <li>The system uses those inputs to estimate which masks are more likely to fit a given face.</li>
          </ol>
          <p>
            These recommendations are <strong>probabilistic</strong>. They are meant to help
            people narrow the field and make better choices about what to try next, not to
            guarantee that a mask will seal correctly.
          </p>
        </div>

        <hr>

        <div id='why-failed-results-matter'>
          <br>
          <br>
          <h2>Why Failed Results Matter</h2>
          <p>
            Negative outcomes are not throwaway data. They are part of the methodology.
          </p>
          <p>
            If a user seal check fails, that is evidence that a particular mask-face pairing
            may be a poor match. If a fit test fails, that is even stronger evidence. A living
            recommendation system improves not only by learning what worked, but also by
            learning what did <strong>not</strong> work.
          </p>
          <p>
            This is why failed user seal check data is treated as a first-class contribution
            alongside fit-test data. A mask that looks promising from geometry alone may still
            fail in real use. Capturing that failure helps prevent false confidence.
          </p>
        </div>

        <hr>

        <div id='quality-and-accessibility'>
          <br>
          <br>
          <h2>Quality and Accessibility</h2>
          <p>
            The project is built around an explicit tradeoff:
          </p>
          <ul>
            <li><strong>Direct fit testing</strong> offers the highest confidence, but it is the least accessible.</li>
            <li><strong>Scan-only matching</strong> is more accessible, but often less transparent and less tied to real outcomes.</li>
            <li><strong>Breathesafe + MasqFit</strong> aim for a middle path: accessible measurement capture plus real-world contributed outcomes.</li>
          </ul>
          <p>
            In other words, the system is trying to raise the floor on mask-fit guidance
            without pretending it has reached the ceiling.
          </p>
        </div>

        <hr>

        <div id='contribute'>
          <br>
          <br>
          <h2>Contribute</h2>
          <p>
            This project gets better when people contribute outcomes, especially outcomes that
            would otherwise never become part of the public record.
          </p>
          <p>Examples of useful contributions include:</p>
          <ul>
            <li>a quantitative fit test that passed or failed,</li>
            <li>a qualitative fit test that passed or failed,</li>
            <li>a failed user seal check on a mask that initially seemed promising,</li>
            <li>results on masks that are underrepresented in current public datasets, and</li>
            <li>results from face types and age groups that are currently underserved.</li>
          </ul>
          <p>
            If you already have fit testing data or failed user seal check data, you can help
            improve future recommendations for other people by contributing it through the
            onboarding flow.
          </p>
          <div class='cta-row'>
            <router-link class='cta secondary' to="/onboarding">
              Go To Onboarding
            </router-link>
          </div>
        </div>

        <hr>

        <div id='deep-dives'>
          <br>
          <br>
          <h2>Deep Dives</h2>

          <h3>What “probability of fit” means</h3>
          <p>
            A probability of fit is an estimate based on available measurements and available
            outcome data. It does not mean certainty. Two people with similar measurements may
            still get different real-world results because fit is affected by mask construction,
            donning technique, strap tension, facial movement, facial hair, and other factors.
          </p>

          <h3>What kinds of evidence are used</h3>
          <p>
            The project combines multiple evidence types rather than relying on only one.
            Breathesafe currently works with outcome data that can include quantitative fit
            testing, qualitative fit testing, and failed user seal checks, together with facial
            measurements and mask-related attributes.
          </p>

          <h3>Why openness matters</h3>
          <p>
            Openness does not automatically make a project correct, but it does make it more
            accountable. People can inspect the code, question assumptions, contribute data,
            and improve the system over time. That is a meaningful difference from closed apps
            that ask the public to trust a recommendation pipeline they cannot examine.
          </p>

          <h3>Why existing literature still matters</h3>
          <p>
            The literature matters because it establishes two important points at once:
            facial dimensions do matter for fit, and current methods still have limitations.
            The National Academies review raised concerns about representativeness and method
            quality in respirator panel development, while more recent research has continued
            exploring the relationship between face shape and respirator fit using newer
            measurement approaches.
          </p>
        </div>

        <hr>

        <div id='current-limitations'>
          <br>
          <br>
          <h2>Current Limitations</h2>
          <p>
            This project is useful now, but it is still incomplete. Current limitations include:
          </p>
          <ul>
            <li>not enough data yet on toddlers and young children,</li>
            <li>not enough data yet on people with larger faces, including people who fit masks like the Zimi B95-XL,</li>
            <li>uneven coverage across masks, face types, and demographics, and</li>
            <li>the fact that some contribution types, especially self-reported seal check data, are noisier than formal fit tests.</li>
          </ul>
          <p>
            That is one reason the project is framed as a living system. With broader and more
            representative participation, recommendations should become more useful and more
            correct over time.
          </p>
        </div>

        <hr>

        <div id='references'>
          <br>
          <br>
          <h2>References and Transparency</h2>
          <ul class='link-list'>
            <li><a href="https://apps.apple.com/ca/app/masqfit/id6756614276" target="_blank" rel="noopener noreferrer">MasqFit on the App Store</a></li>
            <li><a href="https://github.com/edderic/breathesafe" target="_blank" rel="noopener noreferrer">Breathesafe source code</a></li>
            <li><a href="https://github.com/edderic/masqfit" target="_blank" rel="noopener noreferrer">MasqFit source code</a></li>
            <li><a href="https://apps.apple.com/us/app/fit-mask/id1578496578" target="_blank" rel="noopener noreferrer">Fit Mask on the App Store</a></li>
            <li><a href="https://apps.apple.com/us/app/maskfit-ar/id1492746281" target="_blank" rel="noopener noreferrer">MaskFit AR on the App Store</a></li>
            <li><a href="https://www.testtheplanet.org/" target="_blank" rel="noopener noreferrer">Fit Test the Planet</a></li>
            <li><a href="https://www.nationalacademies.org/read/11815/chapter/1" target="_blank" rel="noopener noreferrer">National Academies: Assessment of the NIOSH Head-and-Face Anthropometric Survey of U.S. Respirator Users</a></li>
            <li><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10941723" target="_blank" rel="noopener noreferrer">Face anthropometry for filtering facepiece respirators: analysis of the association between facial dimensions and respirator fit</a></li>
          </ul>
        </div>

        <br>
        <br>
        <br>
      </div>
    </div>
  </div>
</template>

<script>
import CircularButton from './circular_button.vue'
import masqfitLaunchHero from '../assets/images/masqfit-launch-hero.jpg'

export default {
  name: 'Introduction',
  components: {
    CircularButton
  },
  data() {
    return {
      masqfitLaunchHero
    }
  },
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
    max-width: 52em;
  }

  .hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.05fr) minmax(18em, 0.95fr);
    gap: 1.5em;
    align-items: center;
    margin-bottom: 1.5em;
  }

  .eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.8em;
    font-weight: 700;
    color: #666;
    margin-bottom: 0.4em;
  }

  .hero-copy h1 {
    font-size: 2.4em;
    line-height: 1.05;
    margin: 0 0 0.4em 0;
  }

  .hero-lede {
    font-size: 1.15em;
    line-height: 1.5;
  }

  .hero-visual img {
    width: 100%;
    display: block;
    border-radius: 0.75em;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.16);
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

  .cta-row {
    display: flex;
    gap: 1em;
    flex-wrap: wrap;
    margin-top: 1.5em;
  }

  .cta {
    padding: 0.9em 1.3em;
    border-radius: 0.35em;
    text-decoration: none;
    font-weight: 600;
  }

  .primary {
    background-color: #111;
    color: #fff;
  }

  .secondary {
    background-color: #f1f1f1;
    color: #111;
    border: 1px solid #ccc;
  }

  .link-list a {
    word-break: break-word;
  }

  .toc-button {
    position: fixed;
    top: 4em;
    right: 1em;
    z-index: 1000;
    display: none;
  }

  .toc-mobile {
    display: none;
  }

  #top,
  #why-this-matters,
  #what-came-before,
  #what-we-do-differently,
  #how-it-works,
  #why-failed-results-matter,
  #quality-and-accessibility,
  #contribute,
  #deep-dives,
  #current-limitations,
  #references,
  #toc-mobile {
    scroll-margin-top: 3.25em;
  }

  @media(max-width: 700px) {
    .grid {
      grid-template-columns: 100%;
    }

    .hero-grid {
      grid-template-columns: 100%;
    }

    .hero-copy h1 {
      font-size: 1.9em;
    }

    .toc-desktop {
      display: none;
    }

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

    .toc-button {
      display: block;
    }

    .cta-row {
      flex-direction: column;
    }
  }
</style>
