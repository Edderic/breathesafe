"""Fixed-range comparison, using completed full-refit bootstrap aggregates only."""
import json
from pathlib import Path


def add_slides(add):
    evidence = json.loads((Path(__file__).parent/'fixed-range-bootstrap-evidence.json').read_text())
    assert evidence['attempted_replicates'] == 10000
    arms = ('production_arkit', 'traditional_direct', 'traditional_pca3')
    metrics = [('Log loss ↓', 'log_loss', '.3f'), ('Precision ↑', 'precision', '.1%'),
               ('F1 ↑', 'f1', '.3f'), ('NPV ↑', 'negative_predictive_value', '.1%'),
               ('Recall ↑', 'recall', '.1%')]
    results = evidence['results']['test_weighted']
    rows = []
    for label, metric, fmt in metrics:
        result = results[metric]
        assert sum(r['strict_best_count'] for r in result['arms'].values())+result['tie_count'] == result['valid_paired_replicates']
        best_estimate = (min if metric == 'log_loss' else max)(
            result['arms'][arm]['estimate'] for arm in arms)
        best_frequency = max(result['arms'][arm]['strict_best_count'] for arm in arms)
        cells = ''.join(
            f'<td><strong class="{("metric-gain" if result["arms"][arm]["estimate"] == best_estimate else "")}">{result["arms"][arm]["estimate"]:{fmt}}</strong>'
            f'<span class="{("metric-gain" if result["arms"][arm]["strict_best_count"] == best_frequency else "")}">{result["arms"][arm]["strict_best_fraction"]:.2%} best '
            f'({result["arms"][arm]["strict_best_count"]:,})</span></td>' for arm in arms)
        rows.append(f'<tr data-refit-metric="{metric}"><td>{label}</td>{cells}'
                    f'<td>{result["tie_count"]:,}</td><td>{result["valid_paired_replicates"]:,}</td></tr>')
    valid = evidence['pca_evaluable_replicates']
    excluded = evidence['insufficient_pca_rank_replicates']
    add('FIXED / RANGE SENSITIVITY', 'Fixed-range inputs: which model wins after refitting?',
        '<p class="refit-intro">Traditional inputs and PCA scores bounded to [0, 1] using fixed engineering ranges; ARKit retains its deviation model.</p>'
        '<table class="method-table refit-table"><thead><tr><th>Held-out metric</th><th>ARKit: perimeter + nose</th>'
        '<th>Traditional</th><th>Traditional → PCA</th><th>Ties</th><th>Evaluable draws</th></tr></thead><tbody>' +
        ''.join(rows) + '</tbody></table>'
        '<p class="refit-legend"><strong>Bold:</strong> metric on the original seven-person cohort. '
        '<strong>Below:</strong> strict-best frequency (count) among paired evaluable draws. Teal highlights the best metric / highest win frequency.</p>'
        f'<div class="refit-denominator"><strong>10,000 participant resamples with full refitting:</strong> {valid:,} PCA-valid draws; '
        f'{excluded:,} cannot fit PCA-3 reliably. Percentages use the metric-specific evaluable denominator above.</div>'
        '<p class="refit-boundary">Scaling, PCA and classifiers are refitted within each draw; duplicate copies of a person stay together. '
        'Fixed C = 1 and 50% cutoff. Seven original people; these are bootstrap frequencies, not posterior probabilities.</p>',
        'This is a new sensitivity comparison rather than a replacement for slide 10. The traditional models use prespecified physical ranges rather than training-sample z-scores. '
        'Each predictor is mapped by x minus fixed lower bound divided by the fixed range. Input values outside the bounds raise an error; they are not silently clipped. '
        'PCA is refitted within each training fold on scaled participant copies without whitening. Its component extrema are computed analytically over the fixed input cube and used to bound PC predictors too. '
        'That keeps input squares and interactions bounded, but it does not bound the learned logistic score or guarantee reliable extrapolation. Fixed scaling also changes effective L2 regularization; C remains 1, without tuning. '
        'For each of 10,000 paired bootstrap draws, sample seven people with replacement. Keep all copies of an original person in the same held-out group. Refit the three pipelines on the remaining resampled people and evaluate the held-out group, with bootstrap multiplicity in both training and evaluation. '
        'Production ARKit is refitted for the same three initialization seeds as the original comparison, plus the original held-person fold offset. Metrics are computed per initialization then averaged, not by averaging probabilities first. '
        'Traditional models retain equal-person training weights; duplicate participant copies each receive weight. ARKit retains its original row-weighted objective. All arms use the same held-out observations per draw. '
        f'Only {valid} of the 10,000 draws allow all PCA-3 folds to have at least four distinct training faces with rank three. The remaining {excluded} draws are explicitly unevaluable for the paired three-way comparison. '
        'Individual metrics can have additional undefined ratios; their common evaluable denominator is displayed. Strict ties within 1e-12 receive no unique winner and are counted separately. '
        'Identical deterministic training inputs and seeds are cached, which is equivalent to repeating the same refit. No original fixed held-out prediction file is substituted for retraining. '
        'The percentages condition on PCA-evaluable draws and are not Bayesian probabilities of population superiority. The full report also provides counts divided by all 10,000 attempts, and pointwise percentile intervals. '
        'Only seven original participants underlie these results, with earlier exploratory analysis of this same cohort. More resamples do not add independent children or large faces.',
        45, 'Same 7-person cohort · New fixed-range sensitivity experiment · Full refit bootstrap; conditional PCA-valid denominators · Methods in appendix.',
        'fixed-range-refit-slide')
    labels = {'face_width': 'Face width', 'face_length': 'Face length',
              'bitragion_subnasale_arc': 'Bitragion–subnasale arc', 'nose_protrusion': 'Nose protrusion',
              'nasal_root_breadth': 'Nasal root breadth', 'nose_bridge_height': 'Nose bridge height',
              'mask_perimeter_mm': 'Mask perimeter'}
    ranges = ''.join(f'<tr><td>{labels[key]}</td><td>{bounds[0]}–{bounds[1]} mm</td></tr>'
                     for key, bounds in evidence['ranges']['ranges'].items())
    add('BACKUP / FIXED RANGE & REFIT', 'How the fixed-range, full-refit comparison works.',
        '<div class="refit-method-layout"><article><h2>Provisional engineering bounds</h2>'
        '<table class="method-table refit-range-table"><thead><tr><th>Predictor</th><th>Fixed range</th></tr></thead><tbody>' +
        ranges + '</tbody></table>'
        '<p><strong>Transform:</strong> (x − min) / (max − min). No data-derived extrema or silent clipping.</p></article>'
        '<article><h2>Paired training-pipeline bootstrap</h2>'
        '<p><strong>1 · Resample people.</strong> Draw 7 with replacement; retain all observations and copies. Hold out each original person as one group.</p>'
        '<p><strong>2 · Refit everything.</strong> Fit categories, PCA, and models on the other people. PCA components use analytic cube bounds to keep scores in [0, 1].</p>'
        '<p><strong>3 · Compare on the same draw.</strong> Compute held-out metrics, average the 3 ARKit initialization metrics, and count strict winners / ties.</p>'
        f'<p><strong>PCA-3 limitation:</strong> {excluded:,} / 10,000 draws have too few distinct training faces. '
        'Undefined metric ratios are excluded from their paired comparison too.</p></article></div>'
        '<p class="refit-method-note">Fixed C = 1; original feature recipe and training weights retained. Bounds are assumptions, not validated child/adult population limits. '
        'Results remain conditional on the seven-person cohort and on evaluable bootstrap draws.</p>',
        'The fixed facial ranges were recorded before model outcomes were examined in this experiment. They are broad engineering assumptions, not externally validated percentiles. '
        'The mask upper limit was broadened from the initially proposed 650 mm to 800 mm after a predictor-only range check found two existing rows at 699 mm; no outcome was used to select limits. '
        'For PCA, a component with loadings v has a unit-cube minimum equal to the sum of negative loadings, and a width equal to the sum of their absolute values. '
        'Map the uncentered projection using those extrema; the learned PCA centering cancels when subtracting the component lower bound. This bounds scores for in-range inputs without fitting a score range to held-out faces. '
        'C=1 and all linear/quadratic interaction terms remain fixed, so changes relative to z-scaling include changes in the effective regularization penalty. '
        'All duplicated observations from one original person are excluded from its fitting folds together; participant clones never leak across training and test. '
        'PCA-3 requires at least four distinct training faces with sufficient rank. A bootstrap draw that cannot support every held-person fold is not assigned a three-model winner. '
        'The same resampled data and initialization bank can appear repeatedly; exact deterministic fit caching avoids redundant work without reusing the original fixed OOF model predictions. '
        'This is full refitting of the fixed comparison recipe, not nested hyperparameter selection and not a prospective confirmation study.',
        source='fixed_range_scaling.json · bootstrap_fixed_range_comparison.py · All source hashes and denominators in fixed-range-bootstrap-evidence.json.',
        cls='fixed-range-method-slide')
