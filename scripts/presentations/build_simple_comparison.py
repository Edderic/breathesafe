"""Render the frozen feature-ablation aggregate as an offline HTML report."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / 'prompts/2026-11-17-nasem'
LABELS = {
    'linear_additive': 'Linear only',
    'quadratic_additive': 'Linear + squared',
    'shared_perimeter_interactions': 'Shared perimeter interactions',
    'full_interactions': 'Full interactions · slide 12 baseline',
}
METRICS = [('log_loss', 'Log loss ↓', '.3f'), ('precision', 'Precision ↑', '.1%'),
           ('recall', 'Recall ↑', '.1%'), ('negative_predictive_value', 'NPV ↑', '.1%'),
           ('f1', 'F1 ↑', '.3f')]


def result_table(rows, weighting):
    best = {m: (min if m == 'log_loss' else max)(r[weighting][m] for r in rows) for m, _, _ in METRICS}
    body = ''
    for row in rows:
        cells = ''.join(f'<td class="{"best" if abs(row[weighting][m]-best[m]) < 1e-12 else ""}">{row[weighting][m]:{fmt}}</td>'
                        for m, _, fmt in METRICS)
        body += f'<tr><th scope="row">{LABELS[row["recipe"]]}</th><td>{row["predictors_min"]}–{row["predictors_max"]}</td>{cells}</tr>'
    headers = ''.join(f'<th scope="col">{label}</th>' for _, label, _ in METRICS)
    return f'<div class="table-scroll"><table><thead><tr><th scope="col">Feature set</th><th scope="col">Predictors</th>{headers}</tr></thead><tbody>{body}</tbody></table></div>'


def build():
    report = json.loads((FOLDER/'simple-fixed-range-comparison.json').read_text())
    arkit_counts = json.loads((FOLDER/'arkit-parameter-counts.json').read_text())
    assert all(r['total_parameters'] == 4*(r['fit_families']+r['styles'])+r['strap_types']+2 for r in arkit_counts['category_count_combinations'])
    arkit_rows = ''.join(f'<tr><td>{r["fold_count"]}</td><td>{r["fit_families"]}</td><td>{r["styles"]}</td><td>{r["strap_types"]}</td><td><strong>{r["total_parameters"]}</strong></td></tr>' for r in arkit_counts['category_count_combinations'])
    direct = [r for r in report['results'] if r['arm'] == 'traditional_direct']
    pca = [r for r in report['results'] if r['arm'] == 'traditional_pca3']
    options = ''
    ranges = json.loads((ROOT/'python/mask_recommender/scripts/fixed_range_scaling.json').read_text())['ranges']
    range_labels = {'face_width':'Face width', 'face_length':'Face length', 'bitragion_subnasale_arc':'Bitragion–subnasale arc', 'nose_protrusion':'Nose protrusion', 'nasal_root_breadth':'Nasal root breadth', 'nose_bridge_height':'Nose bridge height', 'mask_perimeter_mm':'Mask perimeter'}
    range_rows = ''.join(f'<tr><th scope="row">{range_labels[k]}</th><td>{v[0]}–{v[1]} mm</td></tr>' for k, v in ranges.items())
    descriptions = {
        'linear_additive': ('No squares or interactions.', 'Same mask ranking for everyone'),
        'quadratic_additive': ('Adds squared face/PC terms and squared mask perimeter; no interactions.', 'Same mask ranking for everyone'),
        'shared_perimeter_interactions': ('Adds face/PC terms × mask perimeter; removes face × mask-category terms.', 'Allows some mask-size personalization'),
        'full_interactions': ('Keeps squares, perimeter interactions and category-specific facial interactions.', 'Most flexible; hundreds of terms'),
    }
    for a, b in zip(direct, pca):
        description, tradeoff = descriptions[a['recipe']]
        options += f'<tr><th scope="row">{LABELS[a["recipe"]]}</th><td>{description}</td><td>{a["predictors_min"]}–{a["predictors_max"]}</td><td>{b["predictors_min"]}–{b["predictors_max"]}</td><td>{tradeoff}</td></tr>'
    sections = ''
    for weighting in ['test_weighted', 'equal_person']:
        sections += f'<div data-weighting="{weighting}" {"hidden" if weighting == "equal_person" else ""}><h3>Traditional dimensions</h3>{result_table(direct, weighting)}<h3>Traditional → PCA-3</h3>{result_table(pca, weighting)}</div>'
    reference = ''.join(f'<div><span>{label.replace(" ↑", "").replace(" ↓", "")}</span><strong>{report["production_arkit_reference"][m]:{fmt}}</strong></div>' for m, label, fmt in METRICS)
    child = ''.join(f'<tr><th scope="row">{LABELS[a["recipe"]]}</th><td>{a["child_extrapolation_case"]["false_positives"]} / 130</td><td>{b["child_extrapolation_case"]["false_positives"]} / 130</td></tr>' for a, b in zip(direct, pca))
    html = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simpler facial-measurement models · MasqFit</title><style>
:root{--ink:#153b40;--teal:#087f79;--muted:#55696b;--paper:#f5f4ed;--line:#d9e1dc}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 Arial,Helvetica,sans-serif}main{max-width:1180px;margin:auto;padding:44px 30px 60px}header{border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:30px}.eyebrow{color:var(--teal);font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}h1{font-size:clamp(30px,4.2vw,48px);line-height:1.12;letter-spacing:-.035em;margin:14px 0}h2{font-size:27px;margin:0 0 14px}h3{font-size:21px;margin:24px 0 10px}p{margin:10px 0 18px}.lede{max-width:880px;font-size:21px}.meta{color:var(--muted);font-size:15px}section{margin:32px 0;padding:24px;background:white;border:1px solid var(--line);border-radius:10px}.callout{padding:18px 22px;background:#dcebe7;border-left:4px solid var(--teal);border-radius:4px}.caution{background:#fff2cf;border-left-color:#ae7000}.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:15px;text-align:left}th,td{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}thead th{background:#e4eeea;font-size:13px}tbody th{font-weight:600}td{font-variant-numeric:tabular-nums}.best{color:var(--teal);font-weight:700;background:#edf6f2}.term-card{border-top:1px solid var(--line);padding:18px 0 4px}.term-card h3{margin:0 0 12px}.equation{background:#edf3ef;padding:14px 16px;border-radius:5px;font-size:18px;line-height:1.7;overflow-wrap:anywhere}.equation span{display:block}.term-definitions dt{font-weight:700;margin-top:12px}.term-definitions dd{margin:4px 0 12px}.count-formula{font-size:14px;color:var(--muted)}.ranges-table{max-width:580px}.table-note{font-size:14px;color:var(--muted);margin:12px 0 0}.reference{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:16px 0}.reference div{background:var(--paper);padding:12px;border-radius:5px}.reference span{display:block;font-size:13px;color:var(--muted)}.reference strong{font-size:25px;color:var(--teal)}select{font:inherit;color:var(--ink);background:white;padding:8px;border:1px solid #69837f;border-radius:5px;margin-left:8px}a{color:var(--teal);text-underline-offset:3px}button:focus-visible,select:focus-visible,a:focus-visible{outline:3px solid #ae7000;outline-offset:3px}footer{border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:14px}code{background:#edf1ee;padding:2px 5px;border-radius:3px}li{margin:8px 0}[hidden]{display:none!important}
@media(max-width:650px){main{padding:26px 16px}section{padding:16px}.lede{font-size:19px}table{min-width:620px}.reference{grid-template-columns:repeat(2,1fr)}select{display:block;margin:8px 0 0;max-width:100%}}
@media print{body{font-size:12px}main{max-width:none;padding:0}section{padding:14px;break-inside:avoid}header{margin-bottom:16px}.lede{font-size:16px}h1{font-size:30px}h2{font-size:21px}h3{font-size:17px}table{font-size:11px;min-width:0}th,td{padding:7px}select{display:none}.table-scroll{overflow:visible}a{color:inherit}}
</style></head><body><main>
<header><div class="eyebrow">MasqFit · Exploratory model comparison · November 15, 2026</div>
<h1>Fewer predictors. What changes?</h1>
<p class="lede">Removing most interactions cuts hundreds of fitted terms. It improves some initial metrics, but removing <em>all</em> face–mask interactions also removes personalized mask ordering.</p>
<p class="meta">7 people · 421 held-out observations · train on 6, test on the 7th · same fixed scaling ranges · C = 1 · 50% cutoff</p></header>
<div class="callout"><strong>Recommended compact candidate:</strong> retain shared face-by-mask-perimeter interactions, while removing category-specific facial interactions. This preserves some mask-size personalization with far fewer coefficients. It is a candidate for further validation, not an established winning model.</div>
<section><h2>Four feature sets</h2><p>Every version includes mask-family, style and strap indicators. Traditional uses six facial dimensions; PCA uses three components fitted on training people.</p>
<div class="table-scroll"><table><thead><tr><th scope="col">Feature set</th><th scope="col">What it includes</th><th scope="col">Traditional predictors</th><th scope="col">PCA predictors</th><th scope="col">Main tradeoff</th></tr></thead><tbody>OPTIONS</tbody></table></div>
<p class="table-note">Counts vary by training fold because the available categories vary. Add one intercept to each count. Fixed min–max scaling changes magnitudes, not the number of predictors.</p></section>
<section id="feature-terms"><h2>Exact terms in each feature set</h2>
<p>All four versions are logistic regressions: <strong>predicted fit probability = sigmoid(L) = 1 / (1 + exp(−L))</strong>. The terms below form the logit L, before that probability transformation.</p>
<dl class="term-definitions">
<dt>z₁, …, z<sub>d</sub> · facial predictors</dt><dd>Traditional: d = 6, in this order: face width, face length, bitragion–subnasale arc, nose protrusion, nasal root breadth and nose bridge height. PCA: d = 3, the first three components of those same six fixed-range-scaled measurements, fitted on training people and rescaled using analytic component bounds. Both versions use facial predictors bounded to [0, 1] for in-range measurements.</dd>
<dt>p · mask perimeter</dt><dd>The observed mask perimeter, scaled as (perimeter in mm − 100) / 700.</dd>
<dt>c₁, …, c<sub>K</sub> · mask-category indicators</dt><dd>One-hot indicators for fit family, style and strap type, concatenated into one vector. For example, a Bifold style contributes a 1 in the Bifold indicator and 0 in the other style indicators. Categories are learned from training data; an unseen category contributes zeros in its block. K = 57–61 indicator columns across the original training folds. These are category main effects, not facial measurements.</dd>
<dt>B · intercept and category main effects</dt><dd>B = β₀ + Σ<sub>k=1…K</sub> γ<sub>k</sub>c<sub>k</sub>. Every feature set includes this block. β₀ is the intercept; each γ is a fitted category coefficient.</dd>
</dl>
<article class="term-card" data-feature-recipe="linear_additive"><h3>1 · Linear only</h3>
<div class="equation">L = B + αp + Σ<sub>j=1…d</sub> β<sub>j</sub>z<sub>j</sub></div>
<p>Terms: category indicators, mask perimeter, and each facial measurement or PC. No squares and no products between predictors.</p>
<p class="count-formula">Predictors: K + d + 1, plus one intercept.</p></article>
<article class="term-card" data-feature-recipe="quadratic_additive"><h3>2 · Linear + squared, without interactions</h3>
<div class="equation"><span>L = B + α₁p + α₂p²</span><span>+ Σ<sub>j=1…d</sub> (β<sub>j</sub>z<sub>j</sub> + δ<sub>j</sub>z<sub>j</sub>²)</span></div>
<p>Adds each facial measurement/PC squared and mask perimeter squared. A square such as z₁² allows curvature in that predictor’s effect, but it does not couple the face to a mask.</p>
<p class="count-formula">Predictors: K + 2d + 2, plus one intercept.</p></article>
<article class="term-card" data-feature-recipe="shared_perimeter_interactions"><h3>3 · Shared perimeter interactions</h3>
<div class="equation"><span>L = [all terms in feature set 2]</span><span>+ Σ<sub>j=1…d</sub> (η<sub>j</sub>z<sub>j</sub>p + θ<sub>j</sub>z<sub>j</sub>²p)</span></div>
<p>Adds two products per facial predictor: its linear term × mask perimeter and its squared term × mask perimeter. For example: scaled face width × scaled mask perimeter, and scaled face width² × scaled mask perimeter.</p>
<p>The interaction coefficients are shared across mask categories. These products allow the effect of mask perimeter to change with facial geometry; no category gets its own facial slope.</p>
<p class="count-formula">Predictors: K + 4d + 2, plus one intercept.</p></article>
<article class="term-card" data-feature-recipe="full_interactions"><h3>4 · Full interactions · slide 12 baseline</h3>
<div class="equation"><span>L = [all terms in feature set 3]</span><span>+ Σ<sub>k=1…K</sub> Σ<sub>j=1…d</sub> (κ<sub>kj</sub>c<sub>k</sub>z<sub>j</sub> + λ<sub>kj</sub>c<sub>k</sub>z<sub>j</sub>²)</span></div>
<p>Adds each category indicator × each linear and squared facial predictor. Examples: Bifold indicator × face width, fit-family indicator × nose protrusion², or Headstrap indicator × PC₁. Each fit family, style and strap category can therefore have its own facial coefficients.</p>
<p class="count-formula">Predictors: K + 4d + 2 + 2dK = (2d + 1)K + 4d + 2, plus one intercept. The 2dK category-by-face terms explain most of the expansion.</p></article>
<p class="table-note"><strong>Each feature set is fitted independently.</strong> “All terms in feature set 2/3” describes included columns, not reuse of previously fitted coefficient values. Coefficient signs are unconstrained; all versions use the existing L2 regularization setting C = 1. None includes face-to-face products zᵢzⱼ for i ≠ j, p² × facial terms, products between category indicators, or a prescribed face-minus-mask deviation feature. Predictor counts are raw design columns, not independent degrees of freedom; the one-hot blocks and intercept contain redundant columns. PCA loadings are preprocessing parameters and are not included in these classifier counts.</p>
<details><summary>Fixed scaling ranges and PCA score bounds</summary><p>Each physical value x is transformed as (x − minimum) / (maximum − minimum). Out-of-range measurements raise an error; they are not silently clipped. These bounds are provisional engineering assumptions, not validated population limits.</p>
<div class="table-scroll"><table class="ranges-table"><thead><tr><th scope="col">Physical input</th><th scope="col">Fixed range</th></tr></thead><tbody>RANGES</tbody></table></div>
<p>For PCA component loadings v, define a = Σ min(vᵢ, 0) and w = Σ |vᵢ|. Its bounded score is z = (x<sub>scaled</sub> · v − a) / w. These are analytic extrema over the fixed input unit cube, rather than extrema estimated from held-out people. PCA is fitted without whitening.</p></details>
</section>
<section id="arkit-complexity"><h2>ARKit + nose: how many predictors?</h2>
<p class="lede"><strong>Four measured facial paths → two geometric summaries → ARKITMIN–ARKITMAX learned parameters</strong> across the original seven leave-one-person-out folds.</p>
<p>The four facial measurements are the <strong>nose, upper-cheek, mid-cheek and chin paths</strong>. Their sum is the total facial perimeter; the nose path is also used separately. The model additionally receives observed mask perimeter and fit-family, style and strap-type categories. The facial strap-path measurement is not used by this logit; strap <em>type</em> is categorical.</p>
<p>Thus “two geometric summaries” does not mean two fitted coefficients. The model learns family/style-specific perimeter coefficients and preferred nose distances.</p>
<div class="equation"><span>ΔP = (P<sub>face</sub> − P<sub>mask</sub>) / 10; &nbsp; N = nose path in mm / 10</span><span>L = (a<sub>f</sub> + a<sub>s</sub>)ΔP² + (b<sub>f</sub> + b<sub>s</sub>)ΔP + c<sub>f</sub> + c<sub>s</sub> + t<sub>r</sub></span><span>− softplus(q)[N − exp(u₀ + u<sub>f</sub> + u<sub>s</sub>)]²</span></div>
<p>Here f is fit family, s is style, and r is strap type. The a coefficients are constrained negative via a = −exp(α). Nose mismatch strength softplus(q) is positive and shared across styles in this model; the preferred nose distance exp(u₀ + u<sub>f</sub> + u<sub>s</sub>) is learned. Lengths enter in centimeters, rather than the fixed [0, 1] ranges used for the traditional/PCA comparisons. Fit probability is sigmoid(L).</p>
<div class="table-scroll"><table id="arkit-parameter-breakdown"><thead><tr><th scope="col">Learned parameter block</th><th scope="col">Count formula</th><th scope="col">Original fold range</th></tr></thead><tbody>
<tr><th scope="row">Perimeter quadratic, linear and constant coefficients for each family and style</th><td>3(F + S)</td><td>156–168</td></tr>
<tr><th scope="row">Strap-type offsets</th><td>T</td><td>4–5</td></tr>
<tr><th scope="row">Preferred-nose offsets for each family and style</th><td>F + S</td><td>52–56</td></tr>
<tr><th scope="row">Global preferred-nose center</th><td>1</td><td>1</td></tr>
<tr><th scope="row">Shared nose-mismatch strength</th><td>1</td><td>1</td></tr>
<tr><th scope="row">Total learned parameters</th><td><strong>4(F + S) + T + 2</strong></td><td><strong>ARKITMIN–ARKITMAX</strong></td></tr>
</tbody></table></div>
<p class="table-note">F = number of fit families, S = styles, T = strap types in training. These are raw trainable scalar counts, not independent degrees of freedom. There is no additional standalone intercept to add: category constant terms already provide offsets. Shared family/style terms can be redundant; constraints and regularization also affect effective complexity.</p>
<details><summary>Counts in the seven original training folds</summary><div class="table-scroll"><table id="arkit-fold-counts"><thead><tr><th scope="col">Number of folds</th><th scope="col">Families F</th><th scope="col">Styles S</th><th scope="col">Strap types T</th><th scope="col">Parameters</th></tr></thead><tbody>ARKITROWS</tbody></table></div></details>
<p><strong>Comparison:</strong> ARKit has fewer learned scalars than the full traditional/PCA models, but more than any of the three simplified alternatives. Traditional/PCA tables count classifier columns and exclude one intercept; ARKit’s total above already includes all learned offsets. Its distinction is the constrained mismatch structure, not simply having the fewest parameters.</p>
<p class="table-note">Counts apply to the original seven-person comparison, not necessarily to every bootstrap resample or the deployed model trained on a larger category catalog. <a href="arkit-parameter-counts.json">Parameter-count evidence and source hashes</a>.</p>
</section>
<section><h2>Held-out results</h2><label for="weighting">Evaluation weighting <select id="weighting"><option value="test_weighted">Test-weighted — every observation counts equally</option><option value="equal_person">Equal-person — every participant has equal weight</option></select></label>
<p id="weighting-note" class="table-note">Two people contribute 296 of 421 observations (70.3%), so test weighting emphasizes their results.</p>
SECTIONS
<p class="table-note">Teal cells mark the best value within each model family and selected weighting, including ties. Lower log loss is better; higher precision, recall, NPV and F1 are better. These are point estimates, without new bootstrap intervals.</p>
<h3>Production ARKit reference · test-weighted</h3><div class="reference">REFERENCE</div>
<p class="table-note">This reference uses the same original seven-person cohort. It is test-weighted even when the tables above show equal-person metrics. Architecture and training weights differ: this is a pipeline comparison, not an isolated causal test of measurement modality.</p></section>
<section><h2>Why keep a few interactions?</h2><p>Without interactions, the logit is <code>f(face) + g(mask)</code>. When comparing two masks for the same person, <code>f(face)</code> cancels. Everyone therefore receives the same relative mask ranking within one fitted model, even if squared main effects are included.</p>
<p>Shared face-by-perimeter interactions let the effect of mask size depend on the face. They preserve some personalization without estimating a separate facial relationship for every mask family or style.</p></section>
<section><h2>The child extrapolation problem remains</h2><p>All 130 labels in this held-out child’s fold are negative. Below are the numbers incorrectly predicted to fit; lower is better.</p>
<div class="table-scroll"><table><thead><tr><th scope="col">Feature set</th><th scope="col">Traditional false positives</th><th scope="col">PCA false positives</th></tr></thead><tbody>CHILD</tbody></table></div>
<p><strong>Production ARKit: approximately 5.7 false positives</strong>, averaged over three initializations. The simpler linear models reduce errors relative to the full fixed-range models, but do not resolve the gap. Child-specific recall cannot be measured because this fold contains no positive labels.</p></section>
<div class="callout caution"><strong>Interpretation boundary:</strong> seven people remain seven independent people. These are exploratory comparisons on the same cohort. Selecting a recipe because it looks best here would give an optimistic estimate; previous bootstrap intervals do not apply to these new feature sets.</div>
<section><h2>What to test next</h2><ol><li>Keep the compact shared-perimeter interaction model as a personalized candidate, and the additive models as comparison cases.</li><li>Select regularization inside training-person-only folds, then evaluate the complete selection procedure on held-out people.</li><li>Bootstrap the chosen procedure with refitting, and validate on additional independent people, particularly children and larger faces.</li></ol>
<p class="table-note">Preprocessing and PCA were fitted on training people only. Regularization strength and the decision threshold were fixed in this experiment; no new nested selection or bootstrap was performed. The full-interaction baseline reproduces slide 12’s frozen metrics within 1e−12.</p></section>
<footer><a href="simple-fixed-range-comparison.json">Aggregate data and provenance (JSON)</a> · <a href="simple-fixed-range-comparison.txt">Plain-text report</a> · <a href="presentation.html#slide-12">Presentation slide 12</a><p>The presentation is unchanged by this report. The comparison uses local snapshots; no production model was deployed.</p></footer>
</main><script>
const select=document.querySelector('#weighting');select.addEventListener('change',()=>{for(const panel of document.querySelectorAll('[data-weighting]'))panel.hidden=panel.dataset.weighting!==select.value;document.querySelector('#weighting-note').textContent=select.value==='test_weighted'?'Two people contribute 296 of 421 observations (70.3%), so test weighting emphasizes their results.':'Each person’s confusion counts and log-loss totals are normalized by their observation count before pooling metrics. Training weights are unchanged.'});
</script></body></html>'''
    for key, value in [('ARKITMIN', str(arkit_counts['parameter_count_min'])), ('ARKITMAX', str(arkit_counts['parameter_count_max'])), ('ARKITROWS', arkit_rows), ('RANGES', range_rows), ('OPTIONS', options), ('SECTIONS', sections), ('REFERENCE', reference), ('CHILD', child)]:
        html = html.replace(key, value)
    output = FOLDER/'simple-fixed-range-comparison.html'
    output.write_text(html)
    print(output)


if __name__ == '__main__':
    build()
