<template>
  <section class="probability-metrics" aria-labelledby="probability-title">
    <h3 id="probability-title">Do higher model scores correspond to passing tests?</h3>
    <p v-if="!available" class="metric-note" data-testid="metrics-unavailable">
      This model has no held-out probability report yet. These metrics will appear after training with the updated evaluator.
    </p>
    <template v-else>
      <p class="metric-note">
        {{ evaluation.sample_count }} tested observations from {{ evaluation.user_count ?? 'an unknown number of' }} people;
        {{ evaluation.positive_count }} positive and {{ evaluation.negative_count }} negative fit labels.
        Each person was excluded from the model fit used to score their observations.
        Repeated tests can remain; this is not a count of distinct masks or independent people.
        <span v-if="timestamp">Training run: {{ timestamp }}.</span>
      </p>
      <div class="metric-cards">
        <article><strong>{{ number(evaluation.quality.log_loss) }}</strong><span>Held-out log loss</span><small>Lower is better; confident wrong scores cost more.</small></article>
        <article><strong>{{ percent(selectedMetrics?.precision) }}</strong><span>Precision at {{ percent(threshold) }}</span><small>Of tests scored above the cutoff, how many have positive labels?</small></article>
        <article><strong>{{ percent(selectedMetrics?.recall) }}</strong><span>Recall at {{ percent(threshold) }}</span><small>Of positive tests, how many score above the cutoff?</small></article>
        <article><strong>{{ number(selectedMetrics?.f1) }}</strong><span>F1 at {{ percent(threshold) }}</span><small>Harmonic mean of precision and recall.</small></article>
      </div>
      <p v-if="evaluation.training_prevalence_baseline" class="metric-note">
        Training-prevalence baseline log loss: {{ number(evaluation.training_prevalence_baseline.log_loss) }}.
        This baseline uses each fold's training-label prevalence, not its held-out outcomes.
      </p>
      <div class="threshold-controls">
        <label for="fit-score-threshold">Score cutoff: {{ percent(threshold) }}</label>
        <input id="fit-score-threshold" v-model.number="threshold" type="range" min="0" max="1" step="0.01">
        <button type="button" @click="threshold = 0.5">Use fixed 50% cutoff</button>
        <button v-if="evaluation.exploratory_f1" type="button" @click="useExploratoryThreshold">
          Explore maximum-F1 cutoff ({{ percent(evaluation.exploratory_f1.threshold) }})
        </button>
      </div>
      <p class="metric-note">
        Scores at or above the cutoff count as predicted positive. The maximum-F1 cutoff balances precision and recall
        on these same evaluation observations. It is exploratory and needs a separate validation set before deployment.
        A higher cutoff may favor precision at the expense of missed fitting options.
      </p>
      <div class="metric-charts">
        <figure>
          <figcaption>Precision and recall across cutoffs</figcaption>
          <svg viewBox="0 0 600 230" role="img" aria-label="Precision and recall across model-score thresholds">
            <path d="M40 20V190H580" fill="none" stroke="#8a999a" />
            <polyline :points="metricPoints('precision')" fill="none" stroke="#087f79" stroke-width="3" />
            <polyline :points="metricPoints('recall')" fill="none" stroke="#9b5223" stroke-width="3" />
            <line :x1="40 + threshold * 540" :x2="40 + threshold * 540" y1="20" y2="190" stroke="#52616b" stroke-dasharray="5 4" />
            <text x="40" y="214">0%</text><text x="580" y="214" text-anchor="end">100% cutoff</text>
            <text x="3" y="30">100%</text><text x="8" y="190">0%</text>
          </svg>
          <p class="metric-legend"><span class="precision-color">Precision</span> · <span class="recall-color">Recall</span></p>
        </figure>
        <figure>
          <figcaption>Scores for positive versus negative fit labels</figcaption>
          <svg viewBox="0 0 600 230" role="img" aria-label="Normalized score distributions for positive and negative fit labels">
            <path d="M40 20V190H580" fill="none" stroke="#8a999a" />
            <g v-for="(bin, index) in evaluation.score_histogram" :key="bin.bin_start">
              <rect :x="44 + index * 53" :y="190 - (bin.pass_fraction || 0) * 170" width="21" :height="(bin.pass_fraction || 0) * 170" fill="#087f79">
                <title>{{ percent(bin.bin_start) }}–{{ percent(bin.bin_end) }}: {{ bin.pass_count }} positive labels</title>
              </rect>
              <rect :x="66 + index * 53" :y="190 - (bin.fail_fraction || 0) * 170" width="21" :height="(bin.fail_fraction || 0) * 170" fill="#9b5223">
                <title>{{ percent(bin.bin_start) }}–{{ percent(bin.bin_end) }}: {{ bin.fail_count }} negative labels</title>
              </rect>
            </g>
            <text x="40" y="214">0% score</text><text x="580" y="214" text-anchor="end">100% score</text>
            <text x="3" y="30">100%</text><text x="8" y="190">0%</text>
          </svg>
          <p class="metric-legend"><span class="precision-color">Positive labels</span> · <span class="recall-color">Negative labels</span>. Each outcome group sums to 100%.</p>
        </figure>
      </div>
      <div class="table-scroll">
        <table>
          <caption>How high are the scores when a tested mask passes or fails?</caption>
          <thead><tr><th>Recorded outcome</th><th>Tests</th><th>Mean score</th><th>Median score</th><th>10th–90th percentile</th></tr></thead>
          <tbody><tr v-for="outcome in ['pass', 'fail']" :key="outcome">
            <th>{{ outcome === 'pass' ? 'Positive fit label' : 'Negative fit label' }}</th>
            <td>{{ evaluation.outcome_scores[outcome].sample_count }}</td>
            <td>{{ percent(evaluation.outcome_scores[outcome].mean) }}</td>
            <td>{{ percent(evaluation.outcome_scores[outcome].median) }}</td>
            <td>{{ percent(evaluation.outcome_scores[outcome].p10) }}–{{ percent(evaluation.outcome_scores[outcome].p90) }}</td>
          </tr></tbody>
        </table>
      </div>
      <div v-if="selectedMetrics" class="confusion-counts" aria-live="polite">
        <p><strong>{{ selectedMetrics.true_positive }}</strong> positive tests above cutoff (true positives)</p>
        <p><strong>{{ selectedMetrics.false_positive }}</strong> negative tests above cutoff (false positives)</p>
        <p><strong>{{ selectedMetrics.false_negative }}</strong> positive tests below cutoff (false negatives)</p>
        <p><strong>{{ selectedMetrics.true_negative }}</strong> negative tests below cutoff (true negatives)</p>
      </div>
      <details>
        <summary>Calibration: do the scores match observed positive-label rates?</summary>
        <div class="table-scroll"><table>
          <thead><tr><th>Score range</th><th>Tests</th><th>Mean score</th><th>Positive-label rate</th></tr></thead>
          <tbody><tr v-for="bin in evaluation.calibration_bins" :key="bin.bin_start">
            <td>{{ percent(bin.bin_start) }}–{{ percent(bin.bin_end) }}</td><td>{{ bin.sample_count }}</td>
            <td>{{ percent(bin.mean_predicted_probability) }}</td><td>{{ percent(bin.observed_positive_rate) }}</td>
          </tr></tbody>
        </table></div>
      </details>
      <details v-if="evaluation.user_equal">
        <summary>Give each person equal weight</summary>
        <p>Equal-person-weighted log loss: {{ number(evaluation.user_equal.quality.log_loss) }}.
          At the fixed 50% cutoff, precision is {{ percent(evaluation.user_equal.at_0_5.precision) }}
          and recall is {{ percent(evaluation.user_equal.at_0_5.recall) }}.
          These reduce the influence of people with many test records.</p>
      </details>
      <p class="metric-note">
        Fit labels combine evidence sources and constructed outcomes; they are not exclusively direct formal fit-test results.
        Model scores are not automatically calibrated probabilities. Imputation and preprocessing still need end-to-end validation.
        A missing denominator is shown as “N/A”, not zero.
      </p>
    </template>
  </section>
</template>

<script>
export default {
  name: 'RecommenderProbabilityMetrics',
  props: { evaluation: { type: Object, default: null }, timestamp: { type: String, default: null } },
  data() { return { threshold: 0.5 }; },
  computed: {
    available() { return this.evaluation?.version === 'held_out_probability_evaluation_v1' && this.evaluation.available === true; },
    selectedMetrics() {
      return this.evaluation?.threshold_curve?.find(row => Math.abs(row.threshold - this.threshold) < 0.000001) || null;
    }
  },
  methods: {
    percent(value) { return typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : 'N/A'; },
    number(value) { return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(3) : 'N/A'; },
    useExploratoryThreshold() { if (this.evaluation?.exploratory_f1) this.threshold = this.evaluation.exploratory_f1.threshold; },
    metricPoints(metric) {
      return (this.evaluation?.threshold_curve || []).filter(row => typeof row[metric] === 'number' && Number.isFinite(row[metric]))
        .map(row => `${40 + row.threshold * 540},${190 - row[metric] * 170}`).join(' ');
    }
  }
};
</script>

<style scoped>
.probability-metrics{margin:1.5rem 0;padding:1.5rem;background:#f5f8f7;border:1px solid #d3dfdc;border-radius:8px;color:#243b46}
.metric-note{line-height:1.5;color:#52616b}.metric-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;margin:1.2rem 0}.metric-cards article{background:white;padding:1rem;border-top:4px solid #087f79}.metric-cards strong,.metric-cards span,.metric-cards small{display:block}.metric-cards strong{font-size:2rem;color:#087f79}.metric-cards small{margin-top:.6rem;line-height:1.4;color:#52616b}
.threshold-controls{display:flex;align-items:center;gap:.75rem;flex-wrap:wrap}.threshold-controls button{padding:.6rem;border:1px solid #9bb6af;border-radius:5px;background:white;color:#243b46;cursor:pointer}.metric-charts{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin:1.5rem 0}.metric-charts figure{margin:0;padding:1rem;background:white;min-width:0}.metric-charts figcaption{font-weight:bold}.metric-charts svg{width:100%;font-size:13px}.metric-legend{font-size:.85rem;line-height:1.4}.precision-color{color:#087f79;font-weight:bold}.recall-color{color:#9b5223;font-weight:bold}
.table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;background:white;margin:1rem 0}th,td{text-align:left;padding:.7rem;border-bottom:1px solid #d3dfdc}caption{text-align:left;font-weight:bold;margin-bottom:.6rem}.confusion-counts{display:grid;grid-template-columns:1fr 1fr;gap:0 1rem}details{margin:1rem 0}summary{cursor:pointer;font-weight:bold}
@media(max-width:760px){.probability-metrics{padding:1rem}.metric-cards{grid-template-columns:1fr 1fr}.metric-charts,.confusion-counts{grid-template-columns:1fr}.metric-cards strong{font-size:1.6rem}}
</style>
