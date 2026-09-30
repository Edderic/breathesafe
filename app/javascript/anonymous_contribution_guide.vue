<template>
  <section id="anonymous-fit-tests" class="anonymous-guide" aria-labelledby="anonymous-guide-title">
    <h3 id="anonymous-guide-title">Add fit tests anonymously with MasqFit</h3>
    <p>You can contribute facial measurements and fit-test results without creating a Breathesafe account or providing a name or email. Use <a href="https://apps.apple.com/ca/app/masqfit/id6756614276" target="_blank" rel="noopener noreferrer">MasqFit on a supported iPhone</a>, then import your results from Mark’s Fit Test Console (MFTC).</p>
    <p>You’ll need MasqFit with the <strong>Contribute anonymously</strong> option, a face scan or saved measurements for the person being tested, and their MFTC results. You can also contribute measurements alone; importing fit tests is optional.</p>

    <ol class="anonymous-steps">
      <li>
        <h4>Choose anonymous contribution</h4>
        <p>On the MasqFit home screen, tap <strong>Contribute Facial Measurement Data</strong>, then <strong>Contribute anonymously</strong>. Choose <strong>New participant</strong> for someone contributing for the first time.</p>
        <div class="anonymous-screenshots">
          <figure v-for="shot in startScreens" :key="shot.file">
            <a :href="imagePath(shot.file)" target="_blank" rel="noopener noreferrer" :aria-label="`Open full-size screenshot: ${shot.alt}`">
              <img :src="imagePath(shot.file)" :alt="shot.alt" width="945" height="2048" loading="lazy" decoding="async">
            </a>
            <figcaption>{{ shot.caption }}</figcaption>
          </figure>
        </div>
      </li>
      <li>
        <h4>Save your participant code and measure your face</h4>
        <p>Tap <strong>Save participant code</strong> and keep your own copy. This code links future visits to the same anonymous participant. Keep it private: anyone with the code can access and reuse your saved measurements. A lost code cannot be recovered by name or email.</p>
        <p>Tap <strong>Scan face</strong> and follow the on-screen instructions. Check the five measurements shown after the scan. On a later visit, choose <strong>Scan saved participant code</strong> or <strong>Enter saved participant code</strong> to load your previous measurements, or scan again if they have changed.</p>
        <p>Use a separate participant code and the correct measurements for each person. Choose <strong>Next participant</strong> when moving to someone else.</p>
      </li>
      <li id="anonymous-mftc-import">
        <h4>Export MFTC results and import them into MasqFit</h4>
        <p><a href="https://emcee5601.github.io/fit-test-console/" target="_blank" rel="noopener noreferrer">Open Mark’s Fit Test Console (MFTC)</a> on the device where you recorded the fit tests. MFTC works with fit-testing equipment; the phone’s face scan alone does not perform a fit test.</p>
        <ol>
          <li>In MFTC’s results table, filter to the participant and results you want to share, then use <strong>QR Code</strong> to display the results export.</li>
          <li>In MasqFit, tap <strong>Import MFTC results</strong>. Point the rear camera at the results QR code on the other device. If you saved an image instead, choose <strong>Import image</strong> and select it from Files.</li>
          <li>Select only tests belonging to the person whose measurements you’re contributing. You can select individual tests or all tests in their group, up to 100 per contribution. Tap <strong>Review</strong>.</li>
        </ol>
        <p>The MFTC results QR code transfers test results. Your saved MasqFit participant code identifies the returning participant; these are two different codes.</p>
        <GuideScreenshot file="select-tests" alt="MasqFit Select tests screen with three tests selected and the Review button enabled" caption="Select the correct person’s tests before continuing." />
      </li>
      <li id="anonymous-privacy-review">
        <h4>Review the labels and testing mode</h4>
        <p>On <strong>Review shared text</strong>, tap the mask and protocol labels to remove names, event details, or other identifying text. Keep enough mask information for a reviewer to identify the model and size. Repeated labels are grouped so you can review them together.</p>
        <p>Confirm the instrument’s <strong>testing mode</strong>: N99, N95, or Unknown. N99 is selected by default, so check it. This is the mode used by the fit tester, not the mask’s filtration rating. Choose Unknown if you’re unsure or the batch contains different modes; you can change each test’s mode afterward.</p>
        <p>Select <strong>I checked these labels and removed identifying details</strong>, then tap <strong>Add tests</strong>. Named masks are sent for admin catalog matching after you consent to submit. Adding tests here does not upload them yet.</p>
        <GuideScreenshot file="review-labels" alt="Review shared text screen showing the testing mode, grouped mask label, and checked privacy confirmation" caption="Review the mode and identifying text, then add the tests to your contribution." />
      </li>
      <li>
        <h4>Review the contribution and give consent</h4>
        <p>Back on the contribution screen, check the imported results. Use <strong>Change testing mode for fit test</strong> or <strong>Remove fit test</strong> if needed. Tap <strong>Review and submit</strong>, read the measurements, tests, and consent text, then choose <strong>I agree — submit</strong> when ready.</p>
        <p>The contribution includes the five facial measurements and the reviewed fit-test fields. MFTC participant labels stay on the phone and are discarded after review; notes and original MFTC identifiers are not included in the contribution. Check the mask and protocol text yourself before sharing.</p>
        <GuideScreenshot file="review-contribution" alt="Review contribution dialog displaying facial measurements and imported fit-test results above the I agree — submit button" caption="Submission happens only after your final review and consent." />
      </li>
      <li id="anonymous-submission-queue">
        <h4>Check that your submission arrived</h4>
        <p>Open <strong>Queue</strong> or <strong>Submission queue</strong>. <strong>Submitted · Received by BreatheSafe</strong> confirms delivery. “Submission saved” means it was saved to the phone’s queue; it does not by itself confirm that the server received it.</p>
        <p>If delivery is pending or failed, reconnect to the internet and tap <strong>Retry</strong>. Keep the queued item until it is delivered. Removing a submitted receipt from the phone does not delete data already received by Breathesafe.</p>
        <GuideScreenshot file="submission-queue" alt="Submission queue with two entries marked Submitted and Received by BreatheSafe" caption="Check for Submitted to confirm your contribution reached Breathesafe." />
      </li>
    </ol>

    <details class="anonymous-help">
      <summary>Trouble importing or returning for another visit?</summary>
      <ul>
        <li><strong>QR code won’t import:</strong> use MFTC’s results QR export, try a clearer image, or export fewer tests at a time. MasqFit supports results exports from emcee5601.github.io and algorhythmical.github.io.</li>
        <li><strong>Camera unavailable:</strong> enable camera access in iPhone Settings, or use Import image with a results QR image saved in Files.</li>
        <li><strong>Add tests is disabled:</strong> finish the shared-text privacy review and select its confirmation.</li>
        <li><strong>Returning participant:</strong> restore the saved participant code before adding results. Wait for previous measurements to load, or take a new scan. A new code starts a separate anonymous participant.</li>
      </ul>
    </details>
    <p class="anonymous-caption">Screenshots show the MasqFit contribution flow. Tap an image to open it at full size.</p>
  </section>
</template>

<script>
import { defineComponent, h } from 'vue'

const imagePath = file => `/images/onboarding/anonymous-contributions/${file}.png`
const GuideScreenshot = defineComponent({
  props: { file: String, alt: String, caption: String },
  setup(props) {
    return () => h('figure', { class: 'anonymous-screenshot' }, [
      h('a', { href: imagePath(props.file), target: '_blank', rel: 'noopener noreferrer', 'aria-label': `Open full-size screenshot: ${props.alt}` }, [
        h('img', { src: imagePath(props.file), alt: props.alt, width: 945, height: 2048, loading: 'lazy', decoding: 'async' })
      ]),
      h('figcaption', props.caption)
    ])
  }
})

export default {
  components: { GuideScreenshot },
  data() {
    return { startScreens: [
      { file: 'choose-anonymous', alt: 'MasqFit contribution menu with Measure only, Contribute anonymously, and Use an account', caption: 'Choose Contribute anonymously from the home screen.' },
      { file: 'new-participant', alt: 'Anonymous contribution screen with New participant and saved participant code options', caption: 'Create a participant or restore your saved code.' }
    ] }
  },
  methods: { imagePath }
}
</script>

<style scoped>
.anonymous-guide { margin: 2rem 0 3rem; line-height: 1.6; }
.anonymous-guide, .anonymous-guide li[id] { scroll-margin-top: 5rem; }
.anonymous-guide h3 { font-size: 1.6rem; }
.anonymous-guide h4 { font-size: 1.2rem; margin: 0 0 .75rem; }
.anonymous-steps { padding-left: 1.5rem; }
.anonymous-steps > li { padding-left: .5rem; margin: 2rem 0; }
.anonymous-steps > li::marker { font-weight: bold; color: #087f79; }
.anonymous-steps ol { padding-left: 1.5rem; }
.anonymous-steps ol li { margin: .75rem 0; }
.anonymous-screenshots { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.anonymous-screenshots figure, :deep(.anonymous-screenshot) { margin: 1rem 0; width: min(100%, 280px); }
.anonymous-screenshots img, :deep(.anonymous-screenshot img) { display: block; width: 100%; height: auto; border: 1px solid #d7e1e5; border-radius: 12px; }
.anonymous-screenshots figcaption, :deep(.anonymous-screenshot figcaption), .anonymous-caption { font-size: .9rem; line-height: 1.5; color: #475569; margin-top: .75rem; }
.anonymous-help { padding: 1rem; background: #f0f7f7; border: 1px solid #c9dedd; border-radius: 8px; }
.anonymous-help summary { cursor: pointer; font-weight: bold; }
.anonymous-guide a { text-decoration: underline; text-underline-offset: .15em; }
.anonymous-guide a:focus-visible, summary:focus-visible { outline: 3px solid #087f79; outline-offset: 4px; }
</style>
