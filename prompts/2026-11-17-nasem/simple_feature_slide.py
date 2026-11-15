"""Appendix feature ablation and child false-positive comparison, frozen evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
METRICS = [('log_loss', 'Log loss ↓', '.3f'), ('precision', 'Precision ↑', '.1%'),
           ('recall', 'Recall ↑', '.1%'), ('negative_predictive_value', 'NPV ↑', '.1%'), ('f1', 'F1 ↑', '.3f')]


def add_slide(add):
    report = json.loads((ROOT/'simple-fixed-range-comparison.json').read_text())
    child = json.loads((ROOT/'child-false-positive-evidence.json').read_text())
    parameters = json.loads((ROOT/'arkit-parameter-counts.json').read_text())
    assert report['people'] == 7 and report['tests'] == 421
    assert child['negative_tests'] == 130 and child['positive_tests'] == 0
    labels = dict(linear_additive='Linear only', quadratic_additive='Linear + squared',
                  shared_perimeter_interactions='Shared perimeter × face', full_interactions='Full category interactions')
    best = {m: (min if m == 'log_loss' else max)([r['test_weighted'][m] for r in report['results']]+[report['production_arkit_reference'][m]]) for m, _, _ in METRICS}
    best_f1 = {arm: max(r['test_weighted']['f1'] for r in report['results'] if r['arm'] == arm)
               for arm in ['traditional_direct', 'traditional_pca3']}

    def metric_cells(values):
        return ''.join(f'<td class="{"metric-gain" if abs(values[m]-best[m]) < 1e-12 else ""}">{values[m]:{fmt}}</td>' for m, _, fmt in METRICS)

    rows = ''
    for row in report['results']:
        arm, recipe = row['arm'], row['recipe']
        selected = row['test_weighted']['f1'] == best_f1[arm]
        label = 'Traditional' if arm == 'traditional_direct' else 'PCA-3'
        fp = row['child_extrapolation_case']['false_positives']
        rows += (f'<tr data-simple-arm="{arm}" data-simple-recipe="{recipe}" class="{"best-recipe" if selected else ""}">'
                 f'<th scope="row">{label}</th><td>{labels[recipe]}</td><td>{row["predictors_min"]+1}–{row["predictors_max"]+1}</td>' +
                 metric_cells(row['test_weighted']) + f'<td class="child-fpr child-fpr-high"><strong>{fp/130:.1%}</strong><small>{fp}/130</small></td></tr>')
    rows += (f'<tr class="arkit-reference" data-simple-arm="production_arkit"><th scope="row">ARKit</th><td>Perimeter + nose deviation</td>'
             f'<td>{parameters["parameter_count_min"]}–{parameters["parameter_count_max"]}</td>'+metric_cells(report['production_arkit_reference'])+
             f'<td class="child-fpr child-fpr-low"><strong>{child["false_positive_rate"]:.1%}</strong><small>{child["mean_false_positives"]:.1f}/130 avg.</small></td></tr>')
    headers = ''.join(f'<th>{label}</th>' for _, label, _ in METRICS)
    add('PAIRED / COMPLEXITY & EXTRAPOLATION', 'ARKit’s deviation model was more robust in this child.',
        '<p class="ablation-context">Same 421 held-out tests · 7 people · fixed-range Traditional/PCA · C = 1 · 50% cutoff<br>'
        'Child extrapolation case: 130 negative tests, no positive labels. Lower false-positive rate (FPR) is better.</p>'
        '<table class="method-table ablation-table"><thead><tr><th>Model</th><th>Feature set</th><th>Coefficients¹</th>'+headers+
        '<th>Child FPR ↓</th></tr></thead><tbody>'+rows+'</tbody></table>'
        '<p class="ablation-legend">Shaded rows: highest F1 within Traditional / PCA. Teal metric values: best across all models. '
        '¹Raw fitted coefficient counts include intercepts / offsets, not independent degrees of freedom.</p>'
        f'<div class="ablation-takeaway"><strong>Child FPR:</strong> ARKit {child["false_positive_rate"]:.1%} '
        'vs Traditional 60.0–63.8% and PCA 49.2–56.2%. ARKit averages 5, 6 and 6 false positives over 3 initializations.</div>'
        '<p class="ablation-boundary">One held-out child; not proof of general outlier robustness. Architectures and training weights differ. '
        'Exploratory point estimates: no new bootstrap intervals. Fully additive models cannot personalize mask rankings.</p>',
        'This feature-ablation comparison uses the same seven people and 421 observations as slides 10 and 12. '
        'Each outer fold trains on six people and tests the seventh. Traditional and PCA retain fixed physical scaling, equal-person training weights, C=1, and a 50 percent decision threshold. '
        'Linear-only removes squares and interactions. Linear-plus-squared retains squared main effects without interactions. Shared perimeter interactions add each linear and squared facial term times mask perimeter, but no category-specific facial terms. The full baseline also includes interactions of facial terms with fit-family, style and strap indicators. '
        'The linear-only rows have the highest F1 within each traditional/PCA family and are shaded; metric-level teal highlights compare all nine rows. Simpler PCA has lower aggregate log loss than ARKit, so this is not a claim that ARKit wins every metric. '
        'For a fair raw-count comparison, traditional/PCA column counts include their additional classifier intercept; ARKit counts already include all learned category offsets and nose parameters. These are not independent degrees of freedom. '
        'The out-of-range child has 130 negative labels and no positive labels. False-positive rate is FP divided by FP plus TN, not one minus precision. '
        'Traditional linear-only gives 78 false positives, or 60 percent, versus 83 for the full fixed-range model. PCA linear-only gives 64, or 49.23 percent, versus 73 for full PCA. '
        'ARKit has 5, 6 and 6 false positives across initializations, a mean of 5.67 and mean FPR 4.36 percent. The seeds do not add independent child tests. Child-specific recall is undefined. '
        'This is consistent with constrained mismatch modeling helping in this specific child extrapolation case, not evidence of general robustness across children or unseen large adults. '
        'No confidence intervals or full-refit bootstrap were computed for these simplified feature sets. Same-cohort exploration, architecture differences and unequal training objectives prevent causal attribution to measurement modality alone. '
        'Fully additive logits f(face)+g(mask) have the same within-model mask ranking for every face. Shared perimeter interactions preserve some mask-size personalization; further tuning should happen inside training-only folds, followed by independent validation.',
        source='Frozen feature ablation + child-fold evidence · Test-weighted aggregate metrics · Same held-out cohort; exploratory, no new CIs.',
        cls='simple-feature-slide')
