<template>
  <section v-if="available" class="observed-rate-comparison" aria-labelledby="observed-rates-title">
    <h3 id="observed-rates-title">Pass rates with repeat testing balanced</h3>
    <p>Each person–mask pair contributes once. When tests disagree, we average that pair’s pass/fail outcomes.</p>
    <div class="observed-rate-cards">
      <article><strong>{{ percent(rates.overall.pass_rate) }}</strong><span>Every test counts equally</span><small>{{ rates.overall.total }} labeled tests</small></article>
      <article data-testid="equal-pair-overall"><strong>{{ percent(pairRates.overall.pass_rate) }}</strong><span>Every person–mask pair counts equally</span><small>{{ pairRates.overall.pair_count }} pairs · {{ pairRates.overall.unique_users }} people · {{ pairRates.overall.mixed_pairs }} pairs with mixed outcomes</small></article>
    </div>
    <h4>Style comparison: each family counts equally</h4>
    <p>First average each person’s mask-pair rates within a fit family, then average people for the family rate, then average families within each style. Families with more testers receive no extra weight.</p>
    <div class="observed-rate-table-wrap">
      <table class="observed-rate-table" data-testid="style-rate-comparison">
        <thead><tr><th>Style</th><th>Per test</th><th>Per person–mask pair</th><th>Equal family average</th></tr></thead>
        <tbody><tr v-for="row in styleRows" :key="row.name">
          <th scope="row">{{ row.name }}</th>
          <td>{{ percent(row.test?.pass_rate) }}<small>{{ row.test ? row.test.total + ' tests' : 'Unavailable' }}</small></td>
          <td>{{ percent(row.pair?.pass_rate) }}<small>{{ row.pair ? row.pair.pair_count + ' pairs' : 'No usable pairs' }}</small></td>
          <td>{{ percent(row.family?.pass_rate) }}<small>{{ row.family ? row.family.family_count + ' families · ' + row.family.unique_users + ' people' : 'No usable families' }}</small></td>
        </tr></tbody>
      </table>
    </div>
    <details>
      <summary>Per-mask rates, counting each person once</summary>
      <div class="observed-rate-table-wrap">
        <table class="observed-rate-table" data-testid="equal-pair-mask-rates">
          <thead><tr><th>Mask</th><th>Pair-weighted pass rate</th><th>People / pairs</th><th>Tests</th><th>Mixed pairs</th></tr></thead>
          <tbody><tr v-for="row in maskRows" :key="row.mask_id"><th scope="row">{{ row.name }}</th><td>{{ percent(row.pass_rate) }}</td><td>{{ row.pair_count }}</td><td>{{ row.test_count }}</td><td>{{ row.mixed_pairs }}</td></tr></tbody>
        </table>
      </div>
    </details>
    <p class="observed-rate-note">Rates describe the observed tests and mixed evidence sources. Equal pair weighting balances repeat testing; it does not give every person equal total weight across all masks. Family averages are computed before rounding. A missing family ID is treated as a separate family per mask.</p>
    <p v-if="rates.weighting?.excluded_pair_records" class="observed-rate-note">{{ rates.weighting.excluded_pair_records }} records lack usable person/mask identity or a recognized outcome and are excluded from balanced rates.</p>
  </section>
</template>

<script>
export default {
  name: 'ObservedPassRateComparison',
  props: { rates: { type: Object, default: null } },
  computed: {
    available() { return Boolean(this.rates?.equal_person_mask); },
    pairRates() { return this.rates?.equal_person_mask; },
    styleRows() {
      const index = new Map();
      for (const [key, rows] of Object.entries({ test: this.rates?.by_style || [], pair: this.pairRates?.by_style || [], family: this.rates?.equal_family_by_style || [] })) {
        for (const row of rows) {
          if (!index.has(row.name)) index.set(row.name, { name: row.name });
          index.get(row.name)[key] = row;
        }
      }
      return [...index.values()].sort((a, b) => a.name.localeCompare(b.name));
    },
    maskRows() { return [...(this.pairRates?.by_mask || [])].sort((a, b) => a.name.localeCompare(b.name)); }
  },
  methods: {
    percent(value) { return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(1) + '%' : 'N/A'; }
  }
};
</script>

<style scoped>
.observed-rate-comparison{margin:30px 0;padding:24px;background:#f5faf9;border:1px solid #cadfd9;border-radius:10px;min-width:0}.observed-rate-comparison h3{margin:0 0 12px}.observed-rate-comparison h4{font-size:19px;margin:24px 0 10px}.observed-rate-comparison p{line-height:1.5}.observed-rate-cards{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:20px 0}.observed-rate-cards article{display:flex;flex-direction:column;gap:8px;padding:20px;background:white;border:1px solid #d9e6e2;border-radius:8px}.observed-rate-cards strong{font-size:30px;color:#087f79}.observed-rate-cards span{font-weight:600}.observed-rate-cards small,.observed-rate-note{color:#52646a;font-size:14px}.observed-rate-table-wrap{overflow-x:auto;max-width:100%;margin:15px 0}.observed-rate-table{border-collapse:collapse;width:100%;font-size:15px;background:white}.observed-rate-table th,.observed-rate-table td{text-align:left;padding:12px;border-bottom:1px solid #d6e2dd}.observed-rate-table thead th{background:#e4f0ec}.observed-rate-table td small{display:block;color:#52646a;font-size:13px;margin-top:5px}.observed-rate-comparison summary{cursor:pointer;margin:20px 0 10px;font-weight:600}.observed-rate-note{margin-bottom:0}@media(max-width:760px){.observed-rate-comparison{padding:15px}.observed-rate-cards{grid-template-columns:1fr}.observed-rate-table{font-size:13px;min-width:430px}.observed-rate-table th,.observed-rate-table td{padding:10px 8px}}
</style>
