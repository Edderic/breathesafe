"""Build the local November draft. Never writes to public/ or deploys anything."""
from html import escape
from pathlib import Path
import base64
import json
import re
from prototype_slides import add_slides as add_prototype_slides
from fixed_range_slides import add_slides as add_fixed_range_slides
from simple_feature_slide import add_slide as add_simple_feature_slide

ROOT = Path(__file__).resolve().parent
APPLE = 'https://developer.apple.com/documentation/arkit/arfacegeometry'
GOOGLE = 'https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md'
PHOTO = 'https://pubmed.ncbi.nlm.nih.gov/15352857/'


def cards(items):
    return '<div class="cards">' + ''.join(
        f'<article><h2>{title}</h2><p>{body}</p></article>' for title, body in items
    ) + '</div>'


def callout(text):
    return f'<div class="callout">{text}</div>'


slides = []
notes = []
durations = []
budgets = {
    'NASEM / NOVEMBER 17, 2026': 20,
    '02 / GEOMETRY → FIT SCORE': 50,
    'PAIRED / TEST-WEIGHTED': 35,
    'PAIRED / COMPLEXITY & EXTRAPOLATION': 30,
    'FIXED / RANGE SENSITIVITY': 35,
    'NEW / CAMERA PROTOTYPE': 30,
    'NEW / LANDMARKS & DISTANCES': 30,
    'NEW / INITIAL PHYSICAL CHECKS': 35,
    'NEXT / VALIDATION PLAN': 20,
    '01 / THE APPLICATION': 30,
    '02 / THREE APPROACHES': 35,
    '03 / WHAT WORKED': 30,
    '04 / WHAT DID NOT TRANSFER DIRECTLY': 30,
    '07 / OBSERVED FIT': 30,
    '08 / WHO IS REPRESENTED': 20,
    '08 / COMPLEMENTARY SCOPE': 30,
    '09 / ACKNOWLEDGEMENTS': 30,
}


def chart(name, alt):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="chart result-chart" src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt)}">'


def screenshot(name, alt, cls='reference-image'):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    mime = 'image/jpeg' if Path(name).suffix.lower() in ('.jpg', '.jpeg') else 'image/png'
    return f'<img class="{cls}" src="data:{mime};base64,{encoded}" alt="{escape(alt)}">'


def svg_icon(name, alt, cls):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="{cls}" src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt)}">'


def rate_rows(rows):
    return ''.join(
        f'<div class="dashboard-row"><div class="dashboard-row-head"><strong>{escape(row["name"])}</strong>'
        f'<span>{row["pass_rate"]:.1f}% <small>({row["passed"]}/{row["total"]})</small></span></div>'
        f'<div class="dashboard-track"><span style="width:{row["pass_rate"]:.2f}%"></span></div></div>'
        for row in rows if row['total'] >= 10
    )


def demographic_card(title, rows):
    assert sum(row['unique_users'] for row in rows) == 55
    return f'<article><h2>{escape(title)}</h2>' + ''.join(
        f'<div class="demographic-row"><span>{escape(row["name"])}</span>'
        f'<strong>{row["unique_users"]} <small>({row["unique_users"]/55:.1%})</small></strong></div>'
        for row in rows
    ) + '</article>'


def add(tag, title, body, note, seconds=0, source='', cls=''):
    index = len(slides) + 1
    seconds = budgets.get(tag, seconds)
    durations.append(seconds)
    if seconds and index > 1:
        tag = re.sub(r'^\d{2} /', f'{index - 1:02d} /', tag)
    timing = f' · {seconds // 60}:{seconds % 60:02d}' if seconds else ' · Backup'
    slides.append(f'<section class="slide {cls}" aria-label="{escape(re.sub("<[^>]+>", " ", title))}">'
                  f'<div class="eyebrow">{tag}{timing}</div><h1>{title}</h1>'
                  f'<div class="body">{body}</div><footer>{source}</footer></section>')
    notes.append(f'{index}. {re.sub("<[^>]+>", " ", title)}{timing}\n{note}\n')


add('NASEM / NOVEMBER 17, 2026', 'From face capture<br>to useful measurements.',
    '<p class="lead">Lessons from building MasqFit and Breathesafe</p>'
    '<div class="accent-line"></div><p>Edderic Ugaddan · Breathesafe LLC</p>'
    '<p class="muted">For NPPTL researchers developing iOS and Android apps</p>',
    'My goal today is to share implementation lessons you can use in your own apps. '
    'The practical challenge is getting from a camera image to a facial dimension that is meaningful for respirator selection. '
    'I will connect capture choices to our perimeter-based fit model, show the ranking results, and outline the Android pipeline.',
    30, '10-minute presentation · Local review draft', 'cover')

add('01 / THE PUBLIC GOAL', 'Better-fitting respirators for the <em>general public</em>.',
    '<div class="goal-layout"><div class="goal-copy">'
    '<article class="goal-scope"><h2>NIOSH app direction</h2><p>NIOSH-approved respirators<br>Adult-worker fit panels</p></article>'
    '<article class="goal-scope our-goal"><h2>Our project goal</h2><p><strong>Adults + kids</strong><br>N95 · KN95 · FFP2 / FFP3</p></article>'
    '<p class="goal-validation">Broader intended reach; pediatric fit prediction still needs validation.</p></div>'
    '<figure class="goal-figure">' +
    screenshot('public-fit-family-flo-mask.jpg', 'A family outdoors wearing Flo Mask respirators in adult and child sizes.', 'goal-family-photo') +
    '<figcaption>A family wearing Flo Mask respirators.<br>Photo: <strong>Flo Mask</strong>, via '
    '<a href="https://newatlas.com/health-wellbeing/n95-flo-mask-reusable-elastomeric-respirator/">New Atlas · July 27, 2022</a>.</figcaption></figure></div>',
    'The goal is to help the general public find better-fitting respirators. '
    'A loose surgical mask leaves gaps where air can bypass the filter; both filtration and fit matter. '
    'NIOSH’s published app direction focuses on NIOSH-approved respirators and worker fit panels. '
    'Our intended reach includes adults and children, with N95, KN95 and FFP2 or FFP3 options. '
    'The photo is the user-selected family image, sourced at original resolution from New Atlas and credited there to Flo Mask. It illustrates the public and family scope; it is not a measurement of anyone’s fit or an endorsement of one product. '
    'This is complementary scope, not a claim of validated pediatric predictions or a guarantee of fit.',
    30, '<a href="https://www.cdc.gov/niosh/docs/2024-107/pdfs/2024-107.pdf">NIOSH app targets</a> · '
    '<a href="https://www.cdc.gov/niosh/bulletin/2021/astm-rfc-standard.html">Worker fit panels</a> · '
    '<a href="https://www.cdc.gov/niosh/ppe/php/community-respirators-masks/">CDC: fit and protection</a>.', 'goal-slide')

add('01 / THE APPLICATION', 'ARKit in MasqFit: five facial paths.',
    '<div class="capture-demo"><figure>' +
    screenshot('masqfit-capture.png', 'MasqFit app showing selected measurement points overlaid on a face.', 'demo-phone') +
    '<figcaption>ARKit in the current app</figcaption></figure><figure>' +
    screenshot('masqfit-measurements.png', 'MasqFit five aggregate measurements: nose 45.1 mm, strap 129.0 mm, top cheek 99.1 mm, mid cheek 94.0 mm, chin 128.8 mm.', 'demo-phone') +
    '<figcaption>Five paths in millimeters</figcaption></figure><div class="measurement-summary">'
    '<h2>Five measured paths</h2><p>Nose · Strap · Top cheek<br>Mid cheek · Chin</p>'
    '<p class="muted">Nose, top cheek, mid cheek, and chin form the perimeter proxy used for ranking.</p></div></div>',
    'Here is ARKit in the current MasqFit app. The dots mark selected facial measurement paths. '
    'The next screen shows five aggregates in millimeters: nose, strap, top cheek, mid cheek, and chin. '
    'Four paths form the perimeter proxy used for ranking masks. The strap path is collected but does not directly enter this model.',
    30, 'Presenter-supplied MasqFit screenshots · These images illustrate the workflow, not measurement accuracy.', 'visual-slide')

add('02 / PERSONAL RECOMMENDATIONS', 'What the model recommends for my face.',
    '<figure class="full-recommendations"><div class="recommendations-window">' +
    screenshot('personal-recommendations-hidden-observed-fit.png',
               'Breathesafe recommendations for Edderic, sorted by predicted fit, with Observed Fit hidden. The first four listed respirators each show a 98 percent model fit score.',
               'recommendations-image') +
    '</div><figcaption>October 29 screenshot · October 25 custom_lr model · Observed Fit hidden</figcaption></figure>',
    'These are my recommendations in Breathesafe, sorted by the model’s fit score. This is an October 29 screenshot of the October 25 model, with Observed Fit hidden. '
    'The displayed predicted percentages are model outputs, not calibrated individual success probabilities or independent validation. '
    'This personal example is separate from the held-out ranking results that follow.',
    20, 'Presenter screenshot · Individual scores are model outputs; calibration is not established.', 'visual-slide recommendation-slide')

dashboard = json.loads((ROOT / 'data/dashboard-2026-10-29.json').read_text())

fit_stats = dashboard['fit_tests']
pass_rates = fit_stats['pass_rates']
assert pass_rates['overall']['total'] == fit_stats['total_unique'] == 1145
assert pass_rates['overall']['passed'] == 296
demographic_user_count = sum(row['unique_users'] for row in fit_stats['demographics']['gender_and_sex'])
add('08 / COMMUNITY CONTEXT', 'A convenience sample seeking protection.',
    f'<p class="sample-intro"><strong>{demographic_user_count} unique users</strong> · Members of the general public seeking protection for themselves and others.</p>'
    '<div class="sample-grid">'
    '<article><h2>Immunocompromised or disabled people</h2><p>Seeking protection from respiratory infections.</p></article>'
    '<article><h2>People who cannot afford to get sick</h2><p>Health issues and the personal costs of illness make protection a priority.</p></article>'
    '<article><h2>Disability justice advocates</h2><p>Seeking to avoid infection and transmission to help keep public spaces accessible to others.</p></article>'
    '<article><h2>Family members</h2><p>Seeking to protect relatives with these concerns.</p></article>'
    '</div><p class="sample-caveat">Convenience sample · Overlapping groups · Not population-representative</p>',
    'The October 29 demographic snapshot has 55 unique users. This is not the denominator for the newer November 13 source counts. '
    'This is the presenter’s description of the contributor community, not a survey of diagnoses or motivations. '
    'These overlapping groups include immunocompromised or disabled people, people with health issues who cannot afford to get sick, '
    'disability justice advocates seeking to keep public spaces accessible, and family members. '
    'Health status and motivations were not quantified in this analysis, and no category proportions are implied. '
    'This community context should not be interpreted as a classification of every person in the seven-person or 49-person modeling cohorts. '
    'A motivated convenience sample may differ from the wider general public.',
    30, '55-user demographic snapshot: Oct 29, 2026 · Community description supplied by presenter; health status and motivations not quantified.', 'sample-slide')

demographics = fit_stats['demographics']
add('08 / WHO IS REPRESENTED', 'Demographic breakdown',
    '<p class="dashboard-subtitle">55 unique participants · count (% of people), not tests</p>' +
    '<div class="demographic-grid">' +
    demographic_card('Gender / sex', demographics['gender_and_sex']) +
    demographic_card('Race / ethnicity', demographics['race_ethnicity']) +
    demographic_card('Age', demographics['age']) + '</div>' +
    '<div class="demographic-takeaway">Representation and repeat testing matter when interpreting a dashboard rate.</div>',
    'This is the composition of the same filtered dashboard dataset. It contains 55 unique participants and 1,145 tests. '
    'The columns show unique users within each demographic field, so a participant is counted once per column. '
    'Each percentage divides that category’s count by all 55 participants, including the privacy-pooled or nonresponse group. '
    'For example, 26 cisgender female participants are 47.3 percent, and 41 White or Caucasian participants are 74.5 percent. '
    'Percentages are rounded to one decimal place, so a column may not sum to exactly 100 percent. '
    'For example, 41 participants are in the White or Caucasian category, and 29 are in the age category labeled Prefer not to say. '
    'The dashboard pools some small demographic groups into that label for privacy, so the label must not be read as all explicit nonresponse. '
    'These counts describe who is represented; they are not demographic-specific pass rates. Repeated tests and uneven coverage make subgroup comparisons especially sensitive. '
    'For app evaluation, track participant counts as well as test counts and assess performance across groups with suitable privacy safeguards.',
    30, '<a href="https://www.breathesafe.xyz/#/dashboard">Breathesafe dashboard</a> snapshot Oct 29, 2026 · Small groups may be pooled into “Prefer not to say.”', 'dashboard-slide')

fit_sources = json.loads((ROOT / 'fit-evidence-source-counts.json').read_text())
fit_source_total = fit_sources['total_analyzed_records']
assert sum(fit_sources['by_type'].values()) == fit_source_total
fit_source_rows = ''.join(
    f'<tr data-fit-source="{key}"><td>{label}</td>'
    f'<td class="fit-source-count">{fit_sources["by_type"][key]:,}<span>{fit_sources["by_type"][key]/fit_source_total:.1%}</span></td>'
    f'<td>{rule}</td></tr>'
    for key, label, rule in [
        ('n95_mode', 'Direct N95-mode', 'Harmonic mean ≥100.'),
        ('n99_mode', 'N99 → estimated N95', 'Filtration-adjusted estimate; harmonic mean ×2 ≥100.'),
        ('qlft', 'Qualitative fit testing', 'All nonblank answers pass; ≥1 explicit pass.'),
        ('user_seal_check', 'User seal-check reports', 'Failure → negative only; no positive fit label.'),
    ]
)
fit_testing_photos = json.loads((ROOT / 'fit-testing-photo-sources.json').read_text())
fit_testing_gallery = '<div class="fit-testing-gallery" aria-label="Qualitative and quantitative testing equipment">' + ''.join(
    '<figure>' + screenshot(image['file'].removeprefix('assets/'), image['alt'], 'fit-testing-photo') +
    f'<figcaption>{escape(image["caption"])}</figcaption></figure>'
    for image in fit_testing_photos['images']
) + '</div>'

add('FIT / OUTCOME DEFINITION', 'What does “fit” mean in this dataset?',
    f'<p class="fit-data-summary"><strong>{fit_source_total:,} fit tests</strong> · '
    f'<strong>{fit_sources["unique_user_mask_pairs"]:,} unique user–mask pairs</strong> · Nov 13 snapshot</p>'
    '<p class="fit-definition-intro">Access varies: some participants have only N99-mode or qualitative testing. '
    '<strong>Ideally, we would have direct N95-mode results.</strong></p>'
    '<p class="fit-conversion-intuition"><strong>Intuition:</strong> if a mask scores 25 when sealed (96% filtration) and nearly 25 when worn under comparable conditions, '
    'that suggests little leakage—and a much higher estimated N95-mode score after accounting for filter penetration.</p>'
    '<div class="fit-definition-layout"><div class="fit-definition-rules"><table class="fit-definition-table"><thead><tr><th>Evidence source</th><th>n (%)</th>'
    '<th>Project’s positive-label rule</th></tr></thead><tbody>' + fit_source_rows +
    '</tbody></table><div class="fit-definition-boundary">×2 is a project adjustment; seal-check pass ≠ fit-test pass.</div></div>' + fit_testing_gallery + '</div>'
    '<p class="fit-definition-note">Shares describe records, not people; rounding may exceed 100%. '
    'Negative overrides conflicting labels.</p>',
    'Participant access to fit-testing equipment varies. Some have access only to standard/N99-mode particle counting or qualitative testing. '
    'Ideally this project would have direct N95-mode quantitative outcomes, but it uses the available sources with distinct interpretations. '
    'The November 13 public dashboard snapshot contains 1,157 analyzed fit-test records and 769 distinct user-mask pairs across 57 users. '
    'Multiple tests of the same mask by the same person count as one user-mask pair; these are not independent participants. '
    'The source counts are 136 direct N95-mode, 150 N99-derived, '
    '119 qualitative and 752 user-seal-check reports. Their proportions are 11.8, 13.0, 10.3 and 65.0 percent. '
    'These are record-level source categories after consolidation, not percentages of people who own each tool; '
    'repeat testing varies, and a participant may use multiple methods. The counts are not denominators for the separate 49-person or seven-person CV experiments. '
    'Other descriptive slides retain the explicitly dated October 29 snapshot of 1,145 records. '
    'Here fit means the project’s binary training outcome, not a claim that every source is an equivalent formal fit test. '
    'Direct N95-mode exercise factors are aggregated using a harmonic mean, with 100 or above labeled positive; the optional sealed exercise is excluded. '
    'For N99-mode records, broad-particle counts can reflect filter penetration as well as leakage. '
    'For intuition, a sealed N99-mode factor of 25 corresponds to 4 percent penetration, or 96 percent filtration. If the worn result is nearly 25 under comparable conditions, most measured penetration can be explained by the filter rather than seal leakage, yielding a higher estimated leakage-only N95-mode factor. This is a model-based inference, not a guaranteed fit pass; estimates become sensitive to reference uncertainty near the sealed limit. '
    'The project estimates leakage using filtration data, including Aaron Collins’s MaskNerd spreadsheet and contributed sealed-breathing observations. '
    'It pools sealed references per mask, adjusts an incompatible reference to the largest retained exercise factor plus one, '
    'excludes talking and sealed breathing, then multiplies the harmonic estimate by two. '
    'That factor is a sensitivity-oriented project adjustment, not an instrument-standard correction, and does not apply to direct N95-mode results. '
    'The appendix contains the equations and source attribution. '
    'The qualitative pathway requires all recorded nonblank results to pass and at least one explicit pass; '
    'this permissive completeness policy is not a claim of a fully completed OSHA protocol. An all-fail qualitative record without any explicit pass currently becomes unknown. '
    'Failed seal checks contribute proxy negatives; passing checks establish no positives. Negative overrides positive, then unknown. Unknown records are excluded by default. '
    'Incomplete exercises and mixed sources warrant label-quality review and formal-test-only sensitivity analysis. '
    'Mode names describe measurement methods, not a respirator’s certification class. '
    'The photos come from the presenter’s existing Breathesafe onboarding materials. They show a respirator inside a DIY bag hood, '
    'the hood opening, a nebulizer held at the opening during sensitivity screening, and the 8020A with N95 Companion. '
    'These are illustrations of equipment access, not a complete testing protocol or a demonstration that this DIY setup meets formal protocol requirements.',
    30, '<a href="https://www.breathesafe.xyz/dashboard/stats">Public dashboard</a>, Nov 13, 2026 · '
    'Photos: presenter’s Breathesafe onboarding materials · <a href="https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.134AppB1">OSHA: seal checks ≠ fit tests</a>.',
    'fit-definition-slide')

observed = json.loads((ROOT / 'observed-pass-rate-evidence.json').read_text())
observed_rates = observed['pass_rates']
observed_pairs = observed_rates['equal_person_mask']
observed_tests = {row['name']: row for row in observed_rates['by_style']}
observed_pair_styles = {row['name']: row for row in observed_pairs['by_style']}
observed_style_rows = ''.join(
    f'<tr data-style="{escape(row["name"])}"><td>{escape(row["name"])}</td>'
    f'<td>{observed_tests[row["name"]]["pass_rate"]:.1f}%</td>'
    f'<td>{observed_pair_styles[row["name"]]["pass_rate"]:.1f}% <small>({row["pair_count"]} pairs)</small></td>'
    f'<td>{row["pass_rate"]:.1f}%</td><td>{row["family_count"]}</td></tr>'
    for row in observed_rates['equal_family_by_style']
    if row['name'] in observed_tests and observed_tests[row['name']]['total'] >= 10
)
mask_coverage = json.loads((ROOT / 'mask-coverage-evidence.json').read_text())
assert sum(row['test_count'] for row in mask_coverage['masks']) == mask_coverage['total_tests']
coverage_top = mask_coverage['masks'][:mask_coverage['top_n']]
coverage_top_tests = sum(row['test_count'] for row in coverage_top)
coverage_display_names = {
    'Makrite 9500S Surgical NIOSH N95 Size Small headstraps': 'Makrite 9500S · Small · headstraps',
    'Makrite 9500-N95, M/L Size, NIOSH 84A-5411, FDA 510(k) cleared as a surgical N95': 'Makrite 9500-N95 · M/L',
}
coverage_rows = [
    f'<tr data-rank="{rank}"><td>{rank}</td>'
    f'<td data-mask-name="{escape(row["name"])}" title="{escape(row["name"])}">'
    f'{escape(coverage_display_names.get(row["name"], row["name"]))}</td>'
    f'<td><strong>{row["test_count"]}</strong></td>'
    f'<td>{row["test_count"]/mask_coverage["total_tests"]:.1%}</td></tr>'
    for rank, row in enumerate(coverage_top, 1)
]
coverage_tables = '<div class="coverage-columns">' + ''.join(
    f'<table class="coverage-table" aria-label="Most-tested mask entries, ranks {offset+1}–{offset+10}">'
    '<thead><tr><th>#</th><th>Mask entry</th><th>Tests</th><th>Share</th></tr></thead><tbody>' +
    ''.join(coverage_rows[offset:offset+10]) + '</tbody></table>'
    for offset in range(0, len(coverage_rows), 10)
) + '</div>'
add('07 / MASK COVERAGE', 'Which masks are most represented? · Top 30',
    '<div class="coverage-stats">' + ''.join(
        f'<article><strong>{number:,}</strong><span>{label}</span></article>'
        for number, label in [
            (mask_coverage['total_tests'], 'fit-test records'),
            (mask_coverage['mask_entries'], 'mask entries'),
            (mask_coverage['unique_users'], 'unique people'),
            (mask_coverage['unique_user_mask_pairs'], 'user–mask pairs'),
        ]
    ) + '</div>'
    + coverage_tables +
    f'<p class="coverage-context">The top 30 entries account for {coverage_top_tests:,} of {mask_coverage["total_tests"]:,} records '
    f'({coverage_top_tests/mask_coverage["total_tests"]:.1%}). Counts include repeat tests of the same person–mask pair.</p>'
    '<p class="coverage-note">Coverage of the analyzed dataset, not a ranking of fit. Entries distinguish sizes / strap variants; '
    'evidence sources include seal-check reports.</p>',
    'This provides context for the mask coverage in the observed dataset. It uses the same frozen November 13 public dashboard snapshot as the preceding fit-definition slide: '
    '1,157 canonical analyzed fit-test records, 77 mask entries, 57 unique people and 769 unique user-mask pairs. '
    'The demographics on slides 5 and 6 remain explicitly based on the October 29 snapshot of 55 people. '
    'This dataset is broader than the separate seven-person paired measurement experiment or 49-person model experiment. '
    'The table ranks mask entries by number of fit-test records, descending, with alphabetical ordering for equal counts. '
    'Zimi ZM9233 with headstraps has 54 records; Zimi 7711 with headband has 49; 3M Aura 9205+ has 46; Shawmut small has 38. '
    f'The thirty entries together account for {coverage_top_tests} of {mask_coverage["total_tests"]:,} records, '
    f'about {coverage_top_tests/mask_coverage["total_tests"]:.1%}. The three tables show ranks one through ten, eleven through twenty, and twenty-one through thirty. '
    'Records include repeated tests of the same person and mask, and the mixed evidence sources defined on slide 7. '
    'These are not necessarily complete formal fit-test protocols or independent people per row. '
    'Per-mask unique-person counts are not available in this frozen public aggregate, so they are not inferred from the test counts. '
    'The global unique-person and pair totals are displayed separately. '
    'Different sizes and strap variants can be separate mask entries and can belong to the same fit family. '
    'Coverage reflects participant access and choices; it is not a balanced mask catalog, a popularity survey, or a best-fitting-mask ranking. '
    'The repeat-balanced rates have moved to the appendix for optional discussion. '
    'All mask names and counts are stored in mask-coverage-evidence.json with the public-response hash.',
    30, '<a href="https://www.breathesafe.xyz/dashboard/stats">Public dashboard</a> snapshot Nov 13, 2026 · '
    'Same analyzed subset as slide 7 · Most-tested entries; not fit-performance estimates.',
    'mask-coverage-slide')

evidence = json.loads((ROOT / 'recommender-evidence.json').read_text())
base = evidence['variants']['none']
nose = evidence['variants']['latent_nose_v1']
bootstrap = json.loads((ROOT / 'recommender-bootstrap-evidence.json').read_text())
assert bootstrap['people'] == 49 and bootstrap['replicates'] == 10000
assert bootstrap['independent_bootstrap_model_fits'] == 300000
assert all(row['low'] <= 0 <= row['high'] for row in bootstrap['differences'].values())


def metric_interval(variant, key, fmt):
    row = bootstrap['variants'][variant][key]
    # Batched independent production refits can differ at float32 rounding level.
    assert abs(row['estimate'] - evidence['variants'][variant][key]) < 1e-6
    bound_fmt = '.1f' if fmt.endswith('%') else fmt
    multiplier = 100 if fmt.endswith('%') else 1
    return (f'{format(row["estimate"], fmt)} <span class="metric-ci">'
            f'[{format(row["low"]*multiplier, bound_fmt)}, {format(row["high"]*multiplier, bound_fmt)}]</span>')


classification_metrics = sorted(
    [('Log loss ↓', 'log_loss', '.3f'), ('Precision ↑', 'precision', '.1%'),
     ('Recall ↑', 'recall', '.1%'), ('Negative predictive value ↑', 'negative_predictive_value', '.1%'), ('F1 ↑', 'f1', '.3f')],
    key=lambda metric: bootstrap['superiority'][metric[1]]['better_frequency'], reverse=True)
classification_rows = ''.join(
    f'<tr data-metric="{key}"><td>{label}</td><td>{metric_interval("none", key, fmt)}</td>'
    f'<td class="metric-gain">{metric_interval("latent_nose_v1", key, fmt)}</td>'
    f'<td class="nose-win-frequency">{bootstrap["superiority"][key]["better_frequency"]:.2%}</td></tr>'
    for label, key, fmt in classification_metrics
)
add('02 / GEOMETRY → FIT SCORE', 'Keep the nose path separate from total perimeter.',
    '<div class="equation compact-equation defined-logit">'
    '<div>L<sub>perimeter</sub> = aΔP² + bΔP + c + s<sub>strap</sub>, &nbsp; ΔP = (P<sub>face</sub> − P<sub>mask</sub>) / 10</div>'
    '<div>L<sub>new</sub> = L<sub>perimeter</sub> − λ[(N<sub>face</sub> − μ<sub>mask/style</sub>) / 10]²; &nbsp; fit score = sigmoid(L<sub>new</sub>)</div></div>' +
    '<p class="logit-definition">a, b, c: learned fit-family + style coefficients (a &lt; 0); s<sub>strap</sub>: strap offset; μ: learned nose preference; λ &gt; 0.<br>'
    'P<sub>face</sub> = nose + upper-cheek + mid-cheek + chin paths. All input lengths in mm; division by 10 gives cm.</p>' +
    '<div class="model-context-grid"><aside class="inline-coefficients" aria-label="Where a, b and c come from">'
    '<article><h2>a · Curvature</h2><div class="inline-coefficient-formula">a = −exp(α<sub>family</sub>) − exp(α<sub>style</sub>)</div>'
    '<p>Always negative; larger |a| gives a sharper mismatch penalty.</p></article>'
    '<article><h2>b · Preferred difference</h2><div class="inline-coefficient-formula">b = b<sub>family</sub> + b<sub>style</sub></div>'
    '<p>With a, sets the perimeter-term peak: ΔP* = −b / (2a), not necessarily zero.</p></article>'
    '<article><h2>c · Baseline logit</h2><div class="inline-coefficient-formula">c = c<sub>family</sub> + c<sub>style</sub></div>'
    '<p>Logit at ΔP = 0, before the strap offset and nose penalty.</p></article>'
    '<p class="inline-coefficient-note"><strong>Learned jointly from fit outcomes;</strong> facial measurements enter through ΔP, rather than directly determining a, b or c.</p></aside>'
    '<div class="model-results"><table class="method-table metric-comparison"><thead><tr><th>Held-out metric</th><th>Perimeter deviation</th><th>+ Nose deviation</th><th>Nose better¹</th></tr></thead><tbody>' +
    classification_rows + '</tbody></table>' +
    '<p class="metric-context">1,086 tests · 49 people · 50% cutoff · 5 user-grouped folds · mean of 3 initializations<br>'
    'Estimate [95% CI] · ¹These percentages show how often the nose model performed better when we resampled these same 49 people '
    'and retrained both models 10,000 times.</p>' +
    callout('With retraining, every paired 95% difference interval includes zero.') + '</div></div>',
    'Previously, nose, upper cheek, mid-cheek and chin paths were summed into a single perimeter proxy. '
    'Two people with the same total could receive the same score despite different nose shapes. '
    'The perimeter-model logit is a times the squared signed perimeter difference, plus b times the difference, plus c and a strap-type offset. '
    'The signed difference is face perimeter minus mask perimeter, divided by ten to convert millimeters to centimeters. '
    'Face perimeter sums the nose, upper-cheek, mid-cheek and chin paths. Coefficients a, b and c combine learned fit-family and style terms; a is constrained negative. '
    'A logit is the model score before the sigmoid transformation; the displayed fit score is sigmoid of the new logit, not an independently calibrated probability. '
    'The new model retains the total-perimeter term and adds a separate squared nose mismatch. The face nose path is an input; '
    'the mask and style preferred nose distance is inferred from fit labels, not measured mask geometry. '
    f"Across three initializations on the same five user-grouped folds, precision rose from {base['precision']:.1%} to {nose['precision']:.1%}, "
    f"recall rose from {base['recall']:.1%} to {nose['recall']:.1%}, and log loss fell from {base['log_loss']:.3f} to {nose['log_loss']:.3f}. "
    'Precision asks: among tests called fitting, how many had positive labels? Recall asks: among positive labels, how many were found? '
    f"NPV asks: among observations predicted not to fit, how many have negative labels? It rises from {base['negative_predictive_value']:.1%} to {nose['negative_predictive_value']:.1%} at the fixed 50 percent cutoff. "
    'It is true negatives divided by true negatives plus false negatives; no predicted negatives makes it undefined. '
    'Log loss penalizes confident mistakes using the original continuous scores, not their binarized versions. Lower log loss means better overall probabilistic scoring but can reflect changes in discrimination or calibration; it does not establish calibration improvement alone. Higher precision at the fixed cutoff means a smaller false-positive fraction among predicted fits. It does not prove that scores fell for every nonfit, rose for every fit, or improved the absolute number of false positives or true positives; a more selective predictor can also improve precision. A recall interval including zero leaves the direction uncertain, rather than establishing equal recall. All classification metrics use the fixed 50 percent cutoff except log loss, which uses the scores directly. '
    'These are averages of pooled held-out metrics from each initialization, not training scores or independent replicated datasets. '
    'Brackets show pointwise 95 percent percentile intervals from 10,000 paired participant-cluster bootstrap samples: sample 49 people with replacement and retain all their tests, using identical draws for models and initializations. Retrain both classifiers from scratch in each original grouped-user fold with sampled participant multiplicities in the objective. Keep all copies of a person in the same fold. Compute each metric per initialization then average; do not average probabilities. These intervals include classifier training-population variation, conditional on fixed prepared inputs, category catalog, folds, hyperparameters and initialization bank. All five paired 95 percent difference intervals include zero. Log-loss strict wins are 86.41 percent and precision wins 84.71 percent, substantially less decisive than the earlier fixed-prediction bootstrap. See the appendix for paired difference intervals; separate model intervals cannot establish a difference. '
    'The mixed cohort contains measured and imputed ARKit paths. The regression used for imputation was fitted before CV, so full-pipeline generalization is not independently established. '
    'Measured-only training on 615 tests from 18 people did not reproduce the gain: average F1 fell from .620 to .578. '
    'The new log loss remains worse than the prevalence-only baseline of approximately .588; calibration needs separate reliability assessment. '
    'Labels mix evidence sources and repeated user-mask tests can remain. This is exploratory internal evidence. '
    'Shared nose sensitivity is now the training default in code; style-specific sensitivity remains experimental.',
    65, 'Exploratory mixed measured/imputed inputs · Gain did not reproduce with measured-only training · Recall improvement remains uncertain.', 'metrics-slide')

ranking_rows = ''.join(
    f'<tr><td>Top-{k}</td><td>{base[f"top_{k}"]:.1%}</td><td>{nose[f"top_{k}"]:.1%}</td>'
    f'<td class="{("metric-gain" if nose[f"top_{k}"] >= base[f"top_{k}"] else "metric-drop")}">{100 * (nose[f"top_{k}"] - base[f"top_{k}"]):+.1f} pp</td></tr>'
    for k in [1, 3, 5]
)
paired = json.loads((ROOT / 'paired-measurement-evidence.json').read_text())
assert paired['population']['people'] == 7 and paired['population']['test_observations'] == 421
model_labels = {'production_arkit': 'ARKit: perimeter + nose',
                'traditional_direct': 'Traditional dimensions', 'traditional_pca3': 'Traditional → PCA-3'}


def paired_table(weighting):
    rows = [row for row in paired['metrics'] if row['weighting'] == weighting]
    best = {key: (min if key == 'log_loss' else max)(row[key] for row in rows)
            for key in ['precision', 'recall', 'negative_predictive_value', 'f1', 'log_loss']}
    cells = []
    for row in rows:
        metrics = ''.join(
            f'<td class="{("metric-gain" if row[key] == best[key] else "")}">{format(row[key], fmt)}</td>'
            for key, fmt in [('precision', '.1%'), ('recall', '.1%'), ('negative_predictive_value', '.1%'), ('f1', '.3f'), ('log_loss', '.3f')])
        cells.append(f'<tr><td>{model_labels[row["arm"]]}</td>{metrics}</tr>')
    return '<table class="method-table paired-metrics"><thead><tr><th>Model</th><th>Precision ↑</th><th>Recall ↑</th><th>NPV ↑</th><th>F1 ↑</th><th>Log loss ↓</th></tr></thead><tbody>' + ''.join(cells) + '</tbody></table>'


add('PAIRED / TEST-WEIGHTED', 'ARKit vs. Traditional (Tape/Caliper)',
    '<p class="paired-context">421 held-out observations · 7 people · train on 6, test on the 7th · fixed 50% cutoff</p>' +
    paired_table('test_weighted') +
    '<div class="paired-detail-grid"><div class="paired-explanation"><div class="paired-dimensions"><strong>Traditional dimensions · mm:</strong> face width, face length, bitragion–subnasale arc, nose protrusion, nasal root breadth, and nose bridge height.'
    '<span><strong>PCA-3:</strong> first three components of those same six standardized dimensions.</span></div>' +
    callout('<strong>Highlighted child ★:</strong> traditional/PCA models extrapolated from larger training faces to a held-out child. Deviation-based ARKit made fewer false-positive predictions in that fold.') +
    '<p class="paired-note"><strong>Test-weighted:</strong> each test counts equally. Two people contributed 296 of 421 observations (70.3%); this evaluates the collected test mix.</p></div><!-- PAIRED COHORT --></div>',
    'Now a separate comparison: seven people with both measurement types, training on six and testing the seventh. '
    'The ARKit arm uses our actual perimeter-plus-nose architecture; the other models use traditional dimensions directly or through PCA. '
    'The six traditional dimensions, all in millimeters, are face width, face length, bitragion-subnasale arc, nose protrusion, nasal root breadth and nose bridge height. PCA-3 uses the first three components of these same six standardized dimensions. '
    'Here each test counts equally. ARKit reaches 55.9 percent precision and 46.7 percent recall, but two people supplied 70 percent of the tests. '
    'NPV is the negative-label fraction among observations predicted not to fit, using the same test weighting and fixed cutoff. '
    'The held-out child has face length 77 mm, compared with 112 to 127 mm for the six training people: 8.77 training standard deviations below the mean. The presenter confirmed this is a child with a substantially smaller face, not an identified data-entry error. '
    'In that child’s 130 held-out tests, all labels are negative. Traditional dimensions yield 58 false positives, PCA yields 53, and production ARKit averages 5.7 over three initializations. There are no positive labels in that fold, so child-specific recall cannot be evaluated. '
    'This illustrates an extrapolation limitation of these traditional/PCA fits and is consistent with deviation modeling providing a useful inductive bias: assess face-to-mask mismatch rather than learning unconstrained effects of absolute face dimensions. It is not proof of general robustness on unseen children. '
    'Architecture, feature capacity and person weighting differ, and there is only one such child fold. The models were trained on the same six people, without the held-out child. More child measurements and matched-architecture validation are required. Traditional dimensions already receive training-fold z-score scaling. '
    'Geometry constraints are useful; repeated tests still do not add independent faces.',
    50, 'One child extrapolation case · Consistent with benefit from mismatch constraints; not proof of general robustness · Architecture / training weights differ.', 'paired-slide')

add('02 / THREE APPROACHES', 'The tradeoff: metric scale, speed, and reach.',
    '''<table class="method-table capture-table"><thead><tr><th>Approach</th><th>Geometry & scale</th><th>Experience</th><th>Main constraint</th></tr></thead><tbody>
    <tr><td>ARKit + TrueDepth<br><small>Our iOS path</small></td><td>Metric 3D mesh;<br>meters → millimeters</td><td>Real-time</td><td>Apple hardware path; anatomical mapping still needed</td></tr>
    <tr><td>Google MediaPipe</td><td>Normalized image coordinates + relative depth;<br>physical scale needs calibration</td><td>Real-time</td><td>A landmark mesh is not a subject-specific metric measurement</td></tr>
    <tr><td>Photogrammetry</td><td>Multi-view 3D surface;<br>physical scale must be established</td><td>~45 s raw reconstruction<br><small>Earlier developer report</small></td><td>Slower reconstruction; anatomical landmarking is a separate step</td></tr>
    </tbody></table>''' + callout('Standard-camera capture offers a path toward iOS, Android, and webcams.'),
    'These are three different starting points. In our TrueDepth-based ARKit workflow, the mesh has metric coordinates, '
    'so I can calculate a distance in meters and convert to millimeters. MediaPipe is very useful for real-time landmark detection across camera platforms, '
    'but its standard output is normalized image coordinates and relative depth. Converting normalized coordinates to pixels does not tell me the physical size of the face. '
    'Google also offers a Face Geometry representation with canonical metric units; that is not an independent measurement of the particular person’s absolute size. '
    'Photogrammetry reconstructs a surface from multiple images. It supports ordinary cameras, but still needs physical scale and anatomical landmarks. '
    'The roughly 45 seconds here is an earlier report for raw reconstruction, not a benchmark of the updated capture, reconstruction, smoothing and landmarking workflow.',
    90, f'<a href="{APPLE}">Apple geometry</a> · <a href="{GOOGLE}">Google coordinate conventions</a> · Timing: presenter report, not a controlled comparison.')

accuracy_rows = [
    ('Face width', '142', '137.0', '5.0', '3.6%'),
    ('Face length', '125', '112.0', '13.0', '11.6%'),
    ('Nose breadth', '36', '30.0', '6.0', '20.0%'),
    ('Lower face length', '74', '64.7', '9.3', '14.4%'),
    ('Nose protrusion', '16', '14.0', '2.0', '14.3%'),
    ('Lip width', '47', '52.0', '5.0', '9.6%'),
]
accuracy_table = '<table class="method-table accuracy-table"><thead><tr><th>Measurement</th><th>ARKit (mm)</th><th>Caliper (mm)</th><th>|Difference| (mm)</th><th>Relative difference*</th></tr></thead><tbody>' + ''.join(
    '<tr><td>' + '</td><td>'.join(row) + '</td></tr>' for row in accuracy_rows
) + '</tbody></table>'
add('03 / WHAT WORKED', 'ARKit vs. caliper: an exploratory self-check.',
    '<p class="accuracy-intro">Real-time metric output made capture easy. Agreement varied across six measurements on my face.</p>' +
    accuracy_table +
    '<p class="accuracy-note">* Absolute difference ÷ caliper value. One person, one comparison; causes of the differences have not been isolated.</p>',
    'ARKit simplified capture because it gave me metric coordinates in real time, without a separate pixel-to-millimeter conversion. '
    'I also compared six ARKit-derived dimensions of my own face with digital caliper measurements. '
    'The absolute differences ranged from 2 to 13 millimeters, or 3.6 to 20 percent of the caliper values. '
    'Nose breadth had the largest relative difference, 20 percent. This is an exploratory one-person comparison, not an accuracy study or a reference standard. '
    'Landmark definitions, caliper technique, device behavior, and repeated-capture variability still need to be evaluated. '
    'The published 2023 ARKit study measured eye-to-phone distance at different angles and reported errors from 0.88 to 9.07 percent under its tested conditions. '
    'It did not test distances between facial landmarks or validate MasqFit’s nose, cheek, and chin paths.',
    60, 'Presenter self-measurement: ARKit vs. digital caliper · <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10181530/">ARKit eye-to-phone study (2023)</a> tests a different distance.')

add('04 / WHAT DID NOT TRANSFER DIRECTLY', 'A mesh vertex is not an anatomical definition.',
    '<div class="reference-layout"><figure><div class="mediapipe-frame">' +
    screenshot('mediapipe-masqfit-demo.png', 'MasqFit web app showing a Google MediaPipe face mesh over the presenter’s face.', 'reference-image mediapipe-image') +
    '</div><figcaption>MediaPipe mesh in a MasqFit prototype</figcaption></figure><div>'
    '<h2>Anatomical correspondence</h2><p>Mesh vertices may not coincide with the traditional landmarks used by NIOSH.</p>'
    '<h2>Occluded points</h2><p>Face models can infer hidden points. An estimated coordinate is not a direct observation.</p>' +
    callout('Open question: how accurate are hidden points inferred from one viewing angle?') + '</div></div>',
    'This screenshot shows the MediaPipe mesh running in a MasqFit web prototype. A mesh vertex is not automatically the anatomical point we want. Both systems fit or predict facial geometry, '
    'so a returned coordinate may be inferred even where the surface is not visible from that angle. '
    'That is useful for tracking, but I have not established the accuracy of these hidden points from a single view. '
    'We should compare visible and occluded landmarks against an independent reference, across head angles and single-view versus multi-view capture. '
    'More frames from one angle do not necessarily reveal the hidden surface. Multi-view capture adds observations, but its benefit still needs testing.',
    40, f'<a href="{GOOGLE}">Google: predicted mesh</a> · <a href="{APPLE}">Apple: fitted face geometry</a> · Single-angle accuracy: not yet established by this project.', 'mediapipe-slide')

add_prototype_slides(add, screenshot)

acknowledgements = [
    ('Wayne', 'Community fit testing and training'),
    ('Mish', 'Initial mask recommendations and Masks for Kids'),
    ('Lisa Foreman', 'Community fit testing and the Readimask Dental Nose Hack'),
    ('Gerard Hughes', 'Breathability and fit-testing data'),
    ('Amanda Abbott', 'PDX Respirator Repository'),
    ('Nukit', 'Fit-testing probes'),
]
add('09 / ACKNOWLEDGEMENTS', 'Acknowledgements.',
    '<div class="ack-grid">' + ''.join(
        f'<article><strong>{name}</strong><span>{contribution}</span></article>'
        for name, contribution in acknowledgements
    ) + '</div>' +
    '<div class="ack-support"><strong>With thanks to Kanro</strong> for early support, and to Aaron Collins / OpenAeros, research participants, and anonymous contributors.</div>' +
    '<div class="ack-contact"><strong>Seeking funding to continue this research · Open to work and consulting</strong>' +
    '<span><a href="mailto:info@breathesafe.xyz">info@breathesafe.xyz</a> · <a href="https://www.linkedin.com/in/edderic/">LinkedIn: Edderic Ugaddan</a></span></div>',
    'Thank you to Wayne, Mish, Lisa Foreman, Gerard Hughes, and Amanda Abbott for their community fit-testing, mask-selection, and data contributions. '
    'Thank you to Nukit for fit-testing probes, Kanro for early support, and Aaron Collins, OpenAeros, research participants, and anonymous contributors. '
    'I am seeking funding to continue this research and am open to work and consulting. You can reach me at info@breathesafe.xyz or on LinkedIn.',
    30, 'Community contributor descriptions: October 2026 Kanro proposal · Nukit probe credit: presenter.')

add('BACKUP / COMPLEMENTARY SCOPE', 'A complementary scope for respirator research.',
    '<p class="complement-intro">MasqFit and Breathesafe add community-use questions alongside NIOSH’s facial-measurement work.</p>'
    '<div class="complement-grid">'
    '<article><span class="complement-number">01</span><h2>More mask standards</h2>'
    '<p>Catalog options include KN95 and FFP2/FFP3, alongside NIOSH-approved respirators.</p></article>'
    '<article><span class="complement-number">02</span><h2>Children included</h2>'
    '<p>Contributed data include children and child-sized masks. Pediatric prediction accuracy still needs evaluation.</p></article>'
    '<article><span class="complement-number">03</span><h2>Open methods</h2>'
    '<p>GPLv3 code lets researchers inspect, run, and extend methods—supporting reproducible science.</p></article></div>'
    '<div class="complement-close">Shared opportunity: comparable measurements and fit outcomes across platforms and populations.</div>',
    'NIOSH’s published face-measuring app description focuses on facial dimensions and fit-panel classification. '
    'MasqFit and Breathesafe can complement that work through a broader mask catalog, child-inclusive contributed data, and open GPLv3 code. '
    'Our catalog includes KN95 and FFP2 or FFP3 options as well as NIOSH-approved respirators. '
    'The dataset includes children and child-sized masks, but pediatric prediction accuracy has not yet been established. '
    'Open code allows method inspection and reproduction where data access permits; participant data require appropriate consent and privacy controls. '
    'These are scope differences, not a head-to-head accuracy claim or a statement about the final features of NIOSH’s apps.',
    0, '<a href="https://www.cdc.gov/niosh/docket/archive/pdfs/niosh-278/2_DirectorsTalkingPointsApril2023_508.pdf">NIOSH face-measuring app description</a> · <a href="https://www.cdc.gov/wildfires/safety/how-to-safely-stay-safe-during-a-wildfire.html">CDC on child-sized respirators</a> · <a href="https://github.com/Edderic/breathesafe">Breathesafe GPLv3 source</a>.', 'complement-slide')

add('BACKUP / SYNTHETIC LANDMARKING', 'Synthetic faces remain a complementary research path.',
    '<div class="android-gallery"><figure><div class="android-shot generator">' +
    screenshot('android-flame-generator.png', 'MasqFit research tool generating a synthetic FLAME face with adjustable shape parameters.', 'android-screen') +
    '</div><figcaption>Generate controlled 3D faces</figcaption></figure><figure><div class="android-shot landmarks">' +
    screenshot('android-landmark-labeling.png', 'MasqFit research tool showing labeled facial landmarks on a synthetic FLAME face.', 'android-screen') +
    '</div><figcaption>Label anatomical points on the 3D surface</figcaption></figure></div>' +
    '<div class="android-flow"><span>3D face → 2D views</span><span class="android-arrow">→</span>' +
    '<span class="cnn-step">' + svg_icon('cnn-local-features.svg', 'CNN diagram: local facial features pass through a convolution grid.', 'cnn-icon') +
    '<span><strong>CNN detector · planned</strong><small>eyes · nose · ears · other landmarks</small></span></span>' +
    '<span class="android-arrow">→</span><span>3D projection → dimensions → fit</span></div>',
    'This is complementary research, separate from the working multi-photo correspondence prototype shown in the main talk. Begin with a 3D face, either synthetic or from an actual captured person. '
    'Use rendered or captured 2D views to detect the target landmarks, then project those detections back onto the matching 3D surface. '
    'A planned CNN detector would learn local visual patterns around features such as eyes, nose, ears, and other landmarks in those 2D views. The screenshot shows hand-labeled landmarks that can support training and evaluation; it does not show a trained CNN result. '
    'Projection requires the camera-to-surface relationship: for a rendered view it is known; for a captured view it must be recovered or calibrated. '
    'A point on the image does not select the correct surface point without that relationship and visibility checks. '
    'Once the landmarks are on a scaled surface, calculate the defined dimensions and pass them into the fit-prediction pipeline. '
    'These screenshots show the current FLAME synthetic-face generator and anatomical landmark labeling tool. They are research tools for the Android path, not Android app screens. '
    'Synthetic models let us generate known geometry labels and controlled views. They do not tell us whether a respirator fits a real person. '
    'The difficult transfer is from synthetic rendering to real cameras and faces, which needs independent evaluation.',
    source='October research-tool screenshots · Complementary synthetic-landmark work; not the current prototype output or Android app screens.', cls='android-slide')

add('BACKUP / SCALE & PROJECTION', 'The prototype uses one physical scale anchor.',
    '<div class="two-col"><div><h2>Absolute scale</h2><p>The prototype uses a 284 mm bitragion–subnasale tape arc to establish scale.</p>'
    '<p>A canonical average face is a model prior, not an independent ruler for this person.</p></div>'
    '<div><h2>Surface correspondence</h2><p>Use the matching camera intrinsics and pose to project a 2D detection onto the mesh.</p>'
    '<p>Check occlusion, multiple intersections, missing surface regions, and agreement across views.</p></div></div>' +
    callout('Evaluate absolute millimeter errors without fitting scale to the reference target.'),
    'Use this only if asked about implementation. Rendered geometry provides known cameras for development. Captured geometry requires estimated or calibrated cameras. '
    'A known reference dimension must be independent of the target used for accuracy evaluation; otherwise calibration can conceal the error being tested.',
    source='Working prototype scale: 284 mm / 4.28220 reconstruction units ≈ 66.3211 mm per unit. Caliper checks do not change scale.')

add('BACKUP / 49-PERSON RANKING', 'A stronger shortlist, with a Top-1 tradeoff.',
    '<table class="method-table metric-comparison ranking-comparison"><thead><tr><th>CV hit rate</th><th>Perimeter deviation</th><th>+ Nose deviation</th><th>Change</th></tr></thead><tbody>' +
    ranking_rows + '</tbody></table>' +
    callout('Top-3 and Top-5 improve; the first-ranked result is slightly worse.') +
    '<p class="takeaway">Ranks previously tested observations for the 32 people with ≥1 positive fit label.<br>'
    'Retrospective relevance; prospective success with newly recommended masks remains untested.</p>',
    'This compares the same two models and the same mixed-input dataset as the preceding slide. '
    'Each rate is the unweighted mean across five user-grouped folds, then averaged across three initializations. '
    f"Top one changes from {base['top_1']:.1%} to {nose['top_1']:.1%}, top three from {base['top_3']:.1%} to {nose['top_3']:.1%}, "
    f"and top five from {base['top_5']:.1%} to {nose['top_5']:.1%}. "
    'Top three means at least one of the first three ranked held-out observations had a positive fit label. '
    'The denominator includes 32 people with at least one positive held-out label; eligible fold counts were 5, 4, 5, 8 and 10. '
    'Candidates are their existing test observations, not the entire catalog; repeated user-mask tests can remain. '
    'These rates are conditional ranking relevance, not the chance that sending three new masks to any new person succeeds. '
    'The three initializations share the same folds and are not confidence intervals. '
    'Measured-only training does not show the same gains: top one fell from 91.7 to 87.5 percent, top three from 95.8 to 93.1 percent, and top five remained 95.8 percent. '
    'That smaller cohort has a different population and test mix, so its absolute rates should not be compared with the mixed cohort.',
    0, 'Nov 12 local trial · Means across 5 folds × 3 initializations · Positive-label users only · Full-catalog prospective fit remains unvalidated.')

traditional_labels = {
    'face_width': 'Face width', 'face_length': 'Face length',
    'bitragion_subnasale_arc': 'Bitragion–subnasale arc',
    'nose_protrusion': 'Nose protrusion', 'nasal_root_breadth': 'Nasal root breadth',
    'nose_bridge_height': 'Nose bridge height',
}
assert len(paired['traditional_predictors_mm']) == 6
add('BACKUP / TRADITIONAL PREDICTORS', 'Which predictors enter the traditional models?',
    '<div class="predictor-layout"><article><h2>Six facial dimensions · mm</h2><ul class="predictor-list">' +
    ''.join(f'<li data-predictor="{key}">{traditional_labels[key]}</li>' for key in paired['traditional_predictors_mm']) +
    '</ul></article><article><h2>Mask predictors in both models</h2>'
    '<p>Fit family · style · strap type<br>Observed mask perimeter</p>'
    '<h2>Direct vs. PCA inputs</h2><p><strong>Direct:</strong> all six standardized dimensions.<br>'
    '<strong>PCA-3:</strong> first three components of those same six standardized dimensions.</p>'
    '<p class="predictor-small">Our PCA transformation—not the NIOSH PCA fit panel.</p></article></div>' +
    '<div class="predictor-method"><strong>Fit model:</strong> L2 logistic regression (C = 1), linear + squared geometry terms, '
    'and geometry × mask-category / perimeter interactions.</div>' +
    '<p class="predictor-small">Scaling and PCA fit only on the 6 training people in each fold. No conversion into ARKit paths.</p>',
    'This is the input list used by both traditional comparison arms: face width, face length, bitragion-subnasale arc, '
    'nose protrusion, nasal root breadth, and nose bridge height, entered in millimeters. '
    'No age, sex, ethnicity or inferred ARKit measurements enter these classifiers. '
    'The direct model uses all six standardized dimensions. The PCA model uses the first three components of the same six standardized dimensions, '
    'without whitening. Three components were selected before outcome evaluation, not by choosing the best held-out score. '
    'This is a project-specific PCA, not the NIOSH PCA panel. The three components retained about 83.6 to 98.5 percent of training-person variance across folds. '
    'Both traditional models also receive mask fit-family, style, strap type and observed perimeter. Categories are one-hot encoded. '
    'The mask-perimeter scaler fits the distinct training mask/perimeter combinations; the perimeter and its square are included. '
    'The classifier includes shared linear and squared face or PC terms, those geometry terms interacting with each mask-category indicator, '
    'and geometry terms interacting with mask perimeter. Interactions allow mask rankings to vary with the face. '
    'These are not merely six dimensions entered into an otherwise face-independent mask ranking. '
    'L2 logistic regression uses C=1, deterministic lbfgs and at most 2,000 iterations. Each training person has equal total weight. '
    'Face scaling and PCA fit once per unique training person; repeated fit rows do not overweight the PCA. '
    'All preprocessing excludes the held-out person. In each fold only six paired people train the model. '
    'Feature counts and training recipes differ from production ARKit, so this compares pipelines rather than isolating a causal measurement-modality effect. '
    'Precise anatomical endpoint definitions and collection procedures still need harmonization for a formal measurement-accuracy comparison.',
    source='Implementation: compare_direct_measurements.py · Production comparison: compare_production_measurements.py · Frozen predictor list: paired-measurement-evidence.json.',
    cls='predictor-slide')

coefficient_notes = 'The displayed coefficients combine a fit-family component and a mask-style component. The internal names alpha_mask_raw and beta_gamma_mask refer to fit-family categories in the current training pipeline. For the current constrained parameterization, the two raw alpha parameters are exponentiated and negated, then added, so the effective quadratic coefficient a is negative. The linear and intercept coefficients each add family and style values. Training learns all these underlying parameters jointly by minimizing binary cross-entropy on observed fit outcomes. The strap category contributes a separate additive offset. The with-nose model also subtracts a separately learned nose-mismatch penalty. The peak minus b over two a refers to the perimeter term with categories fixed; it is not a claim about the best physical mask geometry or the optimum of the full model when the nose term changes. The coefficients are learned associations, not physical constants. Legacy parameter files can bypass the newer negative-curvature transformation; the equation describes the current training parameterization.'
notes[8] += '\nCoefficient context: ' + coefficient_notes

add('BACKUP / TRADITIONAL MODEL TERMS', 'Both traditional models include squared terms.',
    '<div class="terms-models">'
    '<article><h2>Traditional dimensions</h2><p>6 standardized measurements</p>'
    '<div class="terms-equation">x₁, …, x₆ &nbsp; and &nbsp; x₁², …, x₆²</div></article>'
    '<article><h2>Traditional → PCA-3</h2><p>3 component scores from standardized measurements</p>'
    '<div class="terms-equation">PC₁, PC₂, PC₃ &nbsp; and &nbsp; PC₁², PC₂², PC₃²</div></article>'
    '</div><div class="terms-shared"><h2>Shared additions in both classifiers</h2>'
    '<p>Mask perimeter p and p², with p standardized; fit-family, style and strap indicators.</p>'
    '<p>Each linear or squared facial term × p, and × each mask-category indicator.</p>'
    '<p>No explicit pairwise facial cross-products, such as face width × face length.</p></div>'
    '<p class="terms-contrast"><strong>Difference from ARKit:</strong> L2 logistic regression learns unconstrained coefficient signs. '
    'These terms do not enforce ARKit’s negative-curvature perimeter-mismatch penalty.</p>',
    'Both traditional comparison models use linear and squared geometry terms. For the direct model, '
    'the six dimensions are standardized before squaring. For PCA, the same standardized dimensions are '
    'projected into three components, and those component scores are squared. This is not PCA applied to squared raw dimensions. '
    'The shared design includes one-hot fit-family, style and strap categories, standardized mask perimeter p and its square, '
    'each geometry basis term multiplied by p, and each geometry basis term multiplied by every category indicator. '
    'Thus the squared geometry terms also interact with perimeter and categories; this is not simply a full degree-two polynomial expansion. '
    'There are no explicit cross-products between different facial dimensions or different PCs. '
    'Squared PCs can nevertheless encode combinations of the original dimensions, because each PC is a linear combination. '
    'Both models are L2 logistic regression with C=1; coefficient signs are not constrained. '
    'This differs from the production ARKit architecture, which explicitly uses a concave quadratic in signed perimeter difference '
    'and a separate negative squared nose mismatch. Standardization and PCA are fitted using training people only.',
    source='Implementation: python/mask_recommender/scripts/compare_direct_measurements.py · FaceMaskClassifier.geometry, design and fit · Used unchanged by compare_production_measurements.py.',
    cls='traditional-terms-slide')

conversion = json.loads((ROOT / 'n95-conversion-evidence.json').read_text())
assert conversion['mask_aggregates'] == 24 and conversion['people'] == 1
slope_low, slope_median, slope_high = conversion['log10_slope_quantiles_2_5_50_97_5']
add('BACKUP / N95 CONVERSION CHECK', 'A positive trend, with substantial scatter.',
    '<p class="conversion-context">N99 + filtration → N95 estimate, compared with measured N95 · 1 wearer · 24 mask aggregates</p>' +
    svg_icon('n95-conversion-uncertainty.svg',
             'Scatter plot of capped N95-mode estimates on the horizontal axis versus measured N95-mode factors on the vertical axis. '
             'A Bayesian log-linear fit shows a positive trend, a 95 percent credible band for the median trend, and a wider 95 percent predictive interval. '
             'Triangles at 200 indicate right-censored measured scores; seven aggregates overlap at estimate 200 and measured at least 200.',
             'conversion-chart') +
    '<p class="conversion-legend">Dark band: 95% credible interval for median trend. Light band: 95% predictive interval for another aggregate.</p>'
    '<p class="conversion-caveat">Triangles: measured ≥200; bands extend above the instrument ceiling. '
    '12 assigned-score aggregates excluded. Historical comparison—not current-converter or recommender validation.</p>',
    'This revisits the saved table behind the earlier actual-versus-predicted N95-mode scatter plot in the conversion notebook. '
    'Predicted here means a conversion estimate from N99-mode results and filtration, not a fit-factor prediction from the perimeter recommender. '
    'The original scatter included 36 mask aggregates. We exclude 12 aggregates containing assigned score-one observations: '
    '11 are entirely assigned, and one pools assigned values with measured exercises. The remaining 24 are mask-level aggregates for one author. '
    'Earlier test exclusions were chosen by the author after interpreting low or inconsistent results, and repeated tests/exercises are pooled by mask; '
    'these are not 24 independent people or prospective validation data. '
    'Both axes are logarithmic. The gray dashed line denotes exact agreement; orange dotted lines mark the 100 cutoff. '
    'Conversion estimates were clipped at exercise level to 200 before harmonic aggregation. The capped aggregate is treated as a fixed predictor. '
    'Eight measured aggregates reach 200 and are modeled as right-censored lower bounds, shown as triangles; seven overlap at the upper-right point. '
    'The model is log10 measured score equals alpha plus beta times log10 conversion estimate over 100 plus Gaussian residual noise. '
    'The priors are alpha Normal(2,1), beta Normal(0,1), sigma HalfNormal(.75). '
    f'The posterior log-log slope median is {slope_median:.2f}, with a 95 percent credible interval from {slope_low:.2f} to {slope_high:.2f}. '
    'The dark band describes uncertainty in the conditional median trend; the lighter band adds residual variation for another mask aggregate in this same modeled setting. '
    'The bands do not cover all sources of uncertainty: predictor measurement error, filtration uncertainty, dependence among tests, selection, '
    'and transfer to other people are not modeled. A positive association does not establish agreement or an accurate binary label near 100. '
    'The historical notebook documents a factor-two bias adjustment, but its exact runtime state cannot be reconstructed solely from the stored outputs. '
    'The current production converter pools filtration references differently, so this plot must not be presented as validation of that exact implementation. '
    'Saved data hashes, anonymous paired values, priors and four-chain sampling diagnostics are retained in n95-conversion-evidence.json. '
    'The raw records were not re-fetched and the converter was not changed.',
    source='Historical source: inferring-n95-mode-fit-factors.ipynb, saved April 2025 comparison · '
    'Reanalysis: analyze_n95_conversion.py · Censored log-linear Bayesian association; conditional uncertainty, not population validation.',
    cls='conversion-slide')

add('BACKUP / N99 → N95 EQUATIONS', 'From N99 counts to an estimated N95 fit factor.',
    '<p class="conversion-equation-key">Fᵢ = observed N99 exercise factor · E = filtration fraction (0–1) · Lᵢ = inferred leakage fraction</p>'
    '<div class="conversion-equation-grid"><article><h2>1 · Separate penetration and leakage</h2>'
    '<div class="conversion-formula">1/Fᵢ = Lᵢ + (1 − Lᵢ)(1 − E)</div>'
    '<div class="conversion-formula">Lᵢ = 1 − (1 − 1/Fᵢ)/E</div>'
    '<div class="conversion-formula">F̂ᵢ = 1/Lᵢ</div>'
    '<p>Assumes unfiltered leakage and comparable aerosol / flow conditions. This is a model, not an instrument equivalence.</p>'
    '</article><article><h2>2 · Apply the project’s implementation</h2>'
    '<div class="conversion-formula">Sⱼ = 1/(1 − Eⱼ); &nbsp; S̄ = mean(Sⱼ)</div>'
    '<div class="conversion-formula">M = max(Fᵢ); &nbsp; S* = S̄ if S̄ &gt; M,<br>otherwise S* = M + 1; &nbsp; E = 1 − 1/S*</div>'
    '<div class="conversion-formula">Estimated N95 = 2 × n / Σᵢ(1/F̂ᵢ)</div>'
    '<p>Pool spreadsheet-derived and contributed sealed ratios. Exclude talking / sealed exercises; label positive at ≥100. '
    'The reference adjustment and ×2 require validation.</p></article></div>'
    '<div class="conversion-example"><strong>Example · one retained exercise</strong> '
    'N99 factor F = 50; filtration E = 0.99 (99%).<br>'
    'L = 1 − (1 − 1/50)/0.99 = 0.01010 → F̂ = 99 → project-adjusted estimate = 2 × 99 = <strong>198</strong>.'
    '<small>Assumes the final sealed reference S* = 100. With several exercises, use their harmonic mean before ×2.</small></div>'
    '<div class="conversion-credit"><strong>Credit: Aaron Collins (“MaskNerd”)</strong> — filtration-efficiency data at normal breathing rates, '
    'via his <a href="https://docs.google.com/spreadsheets/d/1M0mdNLpTWEGcluK6hh5LjjcFixwmOG853Ff45d3O-L0/edit">MaskNerd spreadsheet</a>.</div>',
    'Worked example: use final sealed reference 100, giving filtration efficiency 99 percent. An N99 exercise factor of 50 gives leakage 1 minus 0.98 divided by 0.99, or 0.010101. Its reciprocal is 99. For one retained exercise, the harmonic mean is 99, and the project multiplier gives 198. This is illustrative, not an observed participant result or direct N95 measurement. '
    'This is the equation used for the project’s N99-to-N95 estimate. F_i is the outside-to-inside particle ratio for an N99-mode exercise. '
    'E is the filtration fraction, not a percent; L_i is the inferred fraction of incoming flow that bypasses the filter. '
    'The simplified mixture gives one over F_i equals L_i plus one minus L_i times one minus E. '
    'Solving gives L_i equals one minus one minus one over F_i divided by E; its reciprocal is the exercise-level leakage estimate. '
    'Credit Aaron Collins, MaskNerd, for providing filtration-efficiency data at normal breathing rates through his Master Mask Testing Data Set spreadsheet. '
    'The repository selects imported entries identified as Aaron’s data; contributed Normal breathing SEALED measurements are a second source. '
    'For each imported E_j, compute an equivalent sealed ratio S_j equals one over one minus E_j. '
    'Contributed sealed ratios enter directly. Pool by mask using SQL UNION, which removes identical selected rows, then average the ratios, not efficiencies. '
    'For retained exercise maximum M, use mean sealed ratio if it exceeds M; otherwise replace with M plus one. '
    'This explicit conditional matters: it is not simply max(mean sealed ratio, M plus one). Convert the final ratio back to E. '
    'Apply the inverse leakage formula per exercise and aggregate harmonically, excluding Talking and Normal breathing SEALED. '
    'The code multiplies the result by two and uses 100 as its positive-label threshold. '
    'The two multiplier is a project bias adjustment intended to improve sensitivity, not part of the physical derivation or a correction applied to direct N95-mode tests. '
    'The formula is unstable when the observed ratio approaches the sealed reference, and filtration measured under other conditions may not transfer. '
    'Normal-breathing observations are not certification tests at a standardized test flow or proof of another wearer’s fit. '
    'This credits the data contribution, not endorsement of our conversion, multiplier or recommender. '
    'No spreadsheet measurements are reproduced on this slide; the source is linked. '
    'Implementation: N99ModeToN95ModeConverterService.avg_sealed_ffs_sql, n95_mode_sql and call. '
    'The historical scatter elsewhere uses saved notebook outputs and does not validate this exact production pooling pipeline.',
    source='<a href="https://github.com/Edderic/breathesafe/blob/main/python/mask_recommender/notebooks/inferring-n95-mode-fit-factors.ipynb">Breathesafe Jupyter notebook: inferring N95 fit factors from N99 mode results</a><br>'
    'Project converter: N99ModeToN95ModeConverterService · '
    '<a href="https://docs.google.com/spreadsheets/d/1M0mdNLpTWEGcluK6hh5LjjcFixwmOG853Ff45d3O-L0/edit">Aaron Collins: Master Mask Testing Data Set</a> · '
    'E is a fraction; inferred score is not a direct N95-mode measurement.',
    cls='conversion-equations-slide')

add('BACKUP / SEAL-CHECK LABELS', 'Which questionnaire answers become a failure?',
    '<p class="seal-rule-intro">Current training rule reads <strong>mask sizing</strong> and '
    '<strong>air movement along the seal during a positive-pressure check</strong>.</p>'
    '<div class="seal-rule-grid"><article class="seal-rule-fail"><h2>Fail → negative label</h2>'
    '<ul><li>Sizing: <strong>“Too big”</strong> or <strong>“Too small”</strong>.<br>'
    '<span>This fails even if the air-movement answer is missing.</span></li>'
    '<li>Sizing is answered, and air movement is <strong>“A lot of air movement”</strong>.</li></ul>'
    '</article><article><h2>Not-a-fail → no positive label</h2>'
    '<p>Sizing: <strong>“Somewhere in-between too small and too big”</strong></p>'
    '<p><strong>AND</strong> air movement: <strong>“Some air movement”</strong> or <strong>“No air movement”</strong>.</p>'
    '<p class="seal-rule-detail">The questionnaire calls this “pass”; the training label remains unknown (NULL).</p>'
    '</article></div><div class="seal-rule-incomplete"><strong>Incomplete → no label:</strong> missing required answers or '
    'unrecognized combinations, unless an earlier failure rule applies. “A lot” with missing sizing is incomplete.</div>'
    '<p class="seal-rule-boundary">Negative-pressure answers do not enter this label rule. Neither “not-a-fail” nor “incomplete” establishes a passing fit test.</p>',
    'This slide describes UserSealCheckService, the backend rule used to create recommender labels, rather than a formal fit-test protocol. '
    'The sizing question asks: What do you think about the sizing of this mask relative to your face? '
    'Its choices are Too big, Somewhere in-between too small and too big, and Too small. '
    'The second question asks, while performing a positive-pressure user seal check, how much air movement on your face along the seal of the mask did you feel? '
    'Its choices are A lot of air movement, Some air movement, and No air movement. '
    'Evaluation order matters. First, Too big or Too small returns fail immediately, even if the air answer is absent or contradicts it. '
    'Next, a blank or missing sizing or air answer returns incomplete. This means A lot of air movement without a sizing answer is incomplete, not fail. '
    'With both answers present, A lot of air movement returns fail, including when the nonblank sizing value is unrecognized. '
    'Middle sizing plus Some air movement or No air movement returns questionnaire pass. Other nonblank combinations return incomplete. '
    'Missing, empty or invalid JSON data is also incomplete. '
    'qlft_pass_value maps fail to false and both pass and incomplete to NULL. '
    'The label is therefore asymmetric: a failed self-report can contribute a proxy negative, but passing questions cannot contribute a positive fit label. '
    'Another source on the same test record may still supply a label; consolidation favors negative over positive over unknown. '
    'The interface also has negative-pressure questions, but those answers are not read by this backend label service. '
    'Some air movement being accepted here is a permissive project classification rule, not guidance that a leaking respirator passes a formal fit test. '
    'User seal checks are not substitutes for qualitative or quantitative fit tests. No questionnaire, service or training-label behavior is changed by this slide.',
    source='Implementation: UserSealCheckService.evaluate / qlft_pass_value; UserSealCheckFacialMeasurementsService · '
    '<a href="https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.134AppB1">OSHA: seal checks are not fit tests</a>.',
    cls='seal-rule-slide')

add('BACKUP / BALANCED PASS RATES', 'Pass rates depend on how observations are weighted.',
    '<div class="balanced-overall"><article><span>Each test counts equally</span>'
    f'<strong>{observed_rates["overall"]["pass_rate"]:.1f}%</strong>'
    f'<small>{observed_rates["overall"]["passed"]} passes / {observed_rates["overall"]["total"]:,} tests</small></article>'
    '<article><span>Each person–mask pair counts equally</span>'
    f'<strong>{observed_pairs["overall"]["pass_rate"]:.1f}%</strong>'
    f'<small>{observed_pairs["overall"]["pair_count"]} pairs · {observed_pairs["overall"]["unique_users"]} people · '
    f'{observed_pairs["overall"]["mixed_pairs"]} pairs with mixed outcomes</small></article></div>'
    '<table class="balanced-style-table"><thead><tr><th>Style</th><th>Per test</th><th>Per person–mask pair</th>'
    '<th>Equal family mean</th><th>Families</th></tr></thead><tbody>' + observed_style_rows + '</tbody></table>'
    '<p class="balanced-method"><strong>Mixed tests:</strong> average within each person–mask pair. '
    '<strong>Family mean:</strong> average people within each family, then average families within style.</p>'
    '<p class="balanced-note">Descriptive local snapshot · Same records for all columns · Styles with ≥10 tests shown · '
    'The preceding slides use separately dated public snapshots.</p>',
    'This slide compares weighting approaches on the same canonical local development snapshot: 1,142 labeled tests, '
    '756 unique person-mask pairs and 54 people. These totals differ from the older public snapshots on preceding slides. '
    'Every test weighted equally gives 293 of 1,142 passes, or 25.66 percent. '
    'For the new pair-weighted measure, take the mean of all observed pass/fail outcomes within each person-mask pair, '
    'then give every pair equal weight. That gives 16.75 percent. Fourteen pairs have both passing and failing tests. '
    'There is no selected latest test or any-pass rule. A person with one pass and one fail contributes 50 percent, not a binary pass. '
    'A person may contribute several different masks, so this is not equal total influence per person across all masks. '
    'For the family-weighted style average, first average pair rates within each person and fit family, '
    'so variants do not give one person extra influence within the family. Then average people to obtain the family rate; '
    'finally average family rates equally within each style. All calculations retain full precision until final rounding. '
    'Families with no observations are excluded rather than assigned a zero. Missing family IDs use a distinct fallback family per mask. '
    'The table shows styles with at least ten source tests. Elastomeric, adhesive and unknown styles are retained in the evidence and dashboard '
    'but omitted here due to small denominators. Pair/family denominators are shown; small samples remain descriptive. '
    'Family means are conditional on the observed people and tested families, not causal effects of mask design or population success probabilities. '
    'The raw record data remain private. The same DashboardPassRatesService calculates the web dashboard and the frozen slide evidence. '
    'The dashboard additionally retains per-mask pair-weighted rates, per-strap rates and the original per-test charts. '
    'Mixed outcome sources, self-selection, repeated donning and test procedure differences remain in all three views.',
    0, 'Local development DB snapshot, Nov 13, 2026 · DashboardPassRatesService · '
    'Frozen aggregates: observed-pass-rate-evidence.json · Mixed evidence sources; descriptive, not causal.',
    'balanced-pass-slide')

add('BACKUP / LANDMARKS & CURVE PROJECTION', 'From photo landmarks to surface-attached curves.',
    '<div class="projection-walkthrough"><article><h2>Landmark proposals</h2>'
    '<p><b>1 · Match across photos.</b> RealDenseFace predicts corresponding face points in each registered source photo; template regions identify nose-wing / cheekbone candidates.</p>'
    '<p><b>2 · Recover a 3D point.</b> Triangulate camera rays from multiple views; reject inconsistent image matches and observations outside the skin mask.</p>'
    '<p><b>3 · Attach and review.</b> Check raw-surface proximity and visibility; attach to the smoothed mesh by triangle + within-triangle weights. Review source-photo overlays.</p>' +
    screenshot('prototype/landmark-widths.jpg','Automated width-endpoint proposals and chords on the reconstructed head.','projection-step-image') +
    '</article><article><h2>Bifold / trifold / duckbill curves</h2>'
    '<p><b>1 · Start with a saved guide.</b> Previously drawn FLAME curves define candidate contact paths: bifold/cup around the chin; trifold/duckbill extend under the jaw.</p>'
    '<p><b>2 · Project and connect.</b> Align coordinate frames using matched camera positions. Project controls onto nearby eligible reconstructed triangles; route over the surface between controls.</p>'
    '<p><b>3 · Audit the whole route.</b> Sample along each segment; check skin-mask views, visibility and raw-depth agreement. Keep unsupported gaps flagged rather than bridging them.</p>' +
    screenshot('prototype/bifold-cup-route.jpg','Saved bifold guide projected and routed on the reconstructed face.','projection-step-image') +
    '</article></div>'
    '<p class="projection-result"><strong>Measurements:</strong> straight endpoint chords or supported surface-route lengths × tape-derived mm scale.</p>'
    '<p class="projection-boundary">Automated proposals still need anatomical review. Saved curve guides are not automatically detected mask seals; source-photo agreement is not independent accuracy validation.</p>',
    'The two columns describe related but distinct procedures in the current prototype. RealDenseFace supplies dense per-photo correspondences. '
    'Its template vertex identities identify candidate regions, but metric-like 3D coordinates come from registered multi-photo triangulation and the reconstructed surface, not from accepting a fitted FLAME nose shape. '
    'Observation gates reject points outside the image, prediction crop or skin mask. Bounded pair hypotheses reject reprojection outliers; raw-surface proximity and at least three visible views are required before attachment. '
    'For nose-wing and cheekbone widths, fixed template regions propose supported, height-matched lateral endpoints; visual anatomical review remains necessary. '
    'A barycentric attachment stores the mesh triangle and three weights summing to one, so a point can lie inside a triangle rather than snapping to a vertex. '
    'The style curves begin with saved, previously hand-drawn FLAME perimeter drafts; the current pipeline does not infer the mask contact curve from images of a worn mask. '
    'A proper similarity transform from matched camera centers aligns the old guide frame to the neck-inclusive reconstruction. There is no independent per-route alignment. '
    'Guide controls are projected to eligible smoothed-mesh triangles, with maximum shift 0.15 eye-proxy spans. Surface routing uses local triangle-strip shortcuts with mesh-edge fallbacks, not exact global geodesics or a physical tape simulation. '
    'Disconnected surfaces and excessive detours are rejected. Route samples are spaced at most 0.01 eye-proxy spans; source checks require at least three skin-mask views with at least three degrees of angular spread, visibility, and raw-depth agreement within 0.02 eye-proxy spans. '
    'Bifold/cup and trifold/duckbill are proposed style groupings. Duckbill currently shares the trifold guide rather than receiving a separately validated curve. '
    'Unsupported portions remain unknown; they are not silently turned into complete measurements. The independently recorded tape arc sets scale for supported lengths. '
    'The pictures show actual prototype outputs from the same single capture. They do not establish true seal locations, contact pressure or population accuracy.',
    source='Implementation: all_photo_evaluate.py · width_endpoints.py · mask_route_review.py · Saved guide → reconstructed surface; no seal prediction.',
    cls='projection-walkthrough-slide')

bootstrap_labels = [('Precision', 'precision', True), ('Recall', 'recall', True),
                    ('NPV', 'negative_predictive_value', True), ('F1', 'f1', False),
                    ('Log loss ↓', 'log_loss', False)]
bootstrap_difference_rows = ''
for label, key, percentage in bootstrap_labels:
    row = bootstrap['differences'][key]
    scale = 100 if percentage else 1
    fmt = '+.1f' if percentage else '+.3f'
    unit = ' pp' if percentage else ''
    bounds = f'[{row["low"]*scale:{fmt}}, {row["high"]*scale:{fmt}}]{unit}'
    wins = bootstrap['superiority'][key]
    assert wins['better_replicates'] + wins['tied_replicates'] + wins['worse_replicates'] == wins['valid_replicates']
    frequency = (f'<strong>{wins["better_frequency"]:.2%}</strong> '
                 f'<small>({wins["better_replicates"]:,}/{wins["valid_replicates"]:,})</small>')
    bootstrap_difference_rows += (f'<tr data-bootstrap-metric="{key}"><td>{label}</td>'
                                 f'<td>{row["estimate"]*scale:{fmt}}{unit}</td><td>{bounds}</td><td class="bootstrap-frequency">{frequency}</td></tr>')
add('BACKUP / BOOTSTRAP UNCERTAINTY', 'How uncertain is the added-nose improvement?',
    '<p class="bootstrap-intro">Paired differences: nose model − perimeter-only model · same held-out tests</p>'
    '<table class="method-table bootstrap-differences"><thead><tr><th>Metric</th><th>Difference</th><th>95% bootstrap CI</th><th>Nose model better</th></tr></thead><tbody>' +
    bootstrap_difference_rows + '</tbody></table>'
    '<div class="bootstrap-method"><strong>10,000 samples:</strong> draw 49 people with replacement, retaining all their tests. '
    'Retrain both models in each original grouped-user fold, with copies of a person kept together. Same draws and 3 initializations; average metrics.</div>'
    '<p class="bootstrap-note">Pointwise percentile intervals (2.5th–97.5th percentiles). Precision, recall and NPV differences use percentage points; lower log loss is better. All 10,000 replicates were valid for every metric.</p>'
    '<p class="bootstrap-note"><strong>300,000 classifier fits; frequencies are not posterior probabilities or p-values.</strong> Prepared inputs, category catalog and folds stay fixed; imputation is not refitted. Sampling and label limitations remain.</p>',
    'This appendix gives paired model-difference intervals, which cannot be inferred from overlap between separate model intervals. '
    'For each of 10,000 draws with RNG seed 20261114, sample 49 participant clusters with replacement. A person selected twice contributes all their tests twice. '
    'The same cluster multiplicities apply to both models and all three initializations. Each model is retrained from its prescribed seed in each original grouped-user fold, using 200 Adam epochs, learning rate .01, and row-weighted binary cross entropy. Bootstrap multiplicity weights both training and held-out evaluation. All copies of an original person stay in that persons original fold. '
    'Compute the test-weighted pooled confusion ratios and log loss per seed, average the three metrics, and subtract perimeter-only from nose. '
    'Report the 2.5 and 97.5 percentiles without normality assumptions or multiple-comparison adjustment. All 10,000 replicates have defined denominators for each metric. '
    'The table gives the completed refit-bootstrap differences, intervals and strict-win counts. Ties within absolute tolerance 1e-12 count as neither wins nor losses. These are empirical frequencies under the participant bootstrap, not Bayesian posterior probabilities that the nose model is truly better or calibrated hypothesis-test p-values. '
    'All five paired 95 percent difference intervals include zero after classifier retraining. Precision difference is +7.57 percentage points with interval -7.43 to +16.86; log-loss difference is -0.1773 with interval -0.3698 to +0.1015. Strict-win frequencies are log loss 86.41 percent, precision 84.71 percent, F1 60.03 percent, NPV 50.64 percent and recall 35.66 percent. Recall has 106 ties; other metrics have no ties. This is substantially weaker evidence than the earlier fixed-prediction bootstrap. Inspect the paired intervals rather than inferring improvement from the separate model intervals; prospective validation remains necessary. '
    'Intervals now include classifier refitting variability from different training-person multiplicities. They do not include fold-selection or imputation variability. CV models share training data; bootstrap clusters cannot remove that dependence. '
    'Masks remain as observed rather than resampled across mask families. This targets the test-weighted experiment, not equal-person accuracy or unseen-mask performance. '
    'The three seeds are not three independent datasets. The 10,000 resamples require 300,000 independent classifier fits. Computational batching keeps separate parameters, Adam states and losses for every fit; tests verify agreement with explicit production training on repeated observations. Source hashes and exact interval construction are frozen in recommender-bootstrap-evidence.json.',
    source='49 people · 1,086 tests · 5 fixed user-grouped folds · 3 initializations · 200 epochs · bootstrap_nose_refit.py',
    cls='bootstrap-slide')

cohort = json.loads((ROOT / 'paired-cohort-evidence.json').read_text())
assert cohort['people'] == 7 and sum(row['test_count'] for row in cohort['participants']) == 421
assert sum(row['positive_labels'] for row in cohort['participants']) == 115
cohort_rows = ''.join(
    f'<tr data-participant="{row["study_uuid"]}" class="{("child-case" if row["study_uuid"].startswith("4e4ea719-") else "")}"><td><code>{row["study_uuid"][:8]}</code>{(" ★" if row["study_uuid"].startswith("4e4ea719-") else "")}</td>'
    f'<td>{escape(row["age_band"])}</td><td>{escape(row["gender_group"])}</td><td>{escape(row["race_ethnicity"])}</td>'
    f'<td>{row["test_count"]}</td><td>{row["positive_labels"]}</td><td>{row["negative_labels"]}</td></tr>'
    for row in cohort['participants'])
cohort_panel = (
    '<article class="paired-cohort-panel"><h2>Seven-person sample</h2>'
    '<p class="cohort-summary">421 tests · 115 positive / 306 negative labels</p>'
    '<table class="method-table cohort-table"><thead><tr><th>Study ID</th><th>Age¹</th><th>Gender²</th><th>Race / ethnicity</th><th>Tests</th><th>Positive</th><th>Negative</th></tr></thead><tbody>' +
    cohort_rows + '</tbody></table>'
    '<p class="cohort-footnote">¹Approximate 2026 age, not age at testing. ²Broad reported gender. UUIDs are study pseudonyms; demographics are not predictors.</p></article>')
cohort_notes = 'This is the exact seven-person paired cohort used on slide 10, not the 49-person experiment or the broader dashboard sample. There are five adults and two people under 18 by approximate 2026 age band. Local profile demographics were read November 14; birth-year bands do not establish age at a historical measurement or fit test. Random UUIDs were generated independently of database IDs; the local identity lookup is excluded from the deck and repository. UUIDs are pseudonyms rather than a guarantee against re-identification in a small convenience sample. Reported gender categories are broadly grouped; names, database IDs, exact birth years, contact details and cis/trans status are not displayed. Test and label counts come from the same 421 held-out prediction observations across all three models; the three initializations do not triple counts. The two most active participants contribute 166 and 130 observations, respectively. The young child has 130 negative labels and no positives, so this fold measures false-positive behavior but cannot estimate child-specific recall. The traditional/PCA models fail to extrapolate adequately in this case. Production ARKit uses deviations between facial path lengths and observed/learned mask preferences. Negative-curvature mismatch penalties can lower scores as a face becomes too large or too small relative to a mask, even outside observed absolute face sizes. This describes the inductive bias, not an empirical guarantee for unseen large faces. The evidence here is primarily the smaller-child case, and model architecture and training weights differ. Neither demographics nor study UUIDs enter any compared model. More paired children and a matched architecture comparison are needed.'
slides[9] = slides[9].replace('<!-- PAIRED COHORT -->', cohort_panel)
notes[9] += '\nParticipant context: ' + cohort_notes

add('BACKUP / SOURCES', 'Sources and boundaries of the claims.',
    f'<div class="two-col sources"><div><h2>Technical references</h2><p><a href="{APPLE}">Apple: ARFaceGeometry</a></p>'
    f'<p><a href="https://developer.apple.com/documentation/arkit/arfacetrackingconfiguration">Apple: face tracking configuration and device support</a></p>'
    f'<p><a href="{GOOGLE}">Google: Face Mesh coordinate systems and canonical model</a></p></div>'
    f'<div><h2>Photogrammetry evidence</h2><p><a href="{PHOTO}">Aldridge et al. (2005), Digital three-dimensional photogrammetry: evaluation of anthropometric precision and accuracy using a Genex 3D camera system</a></p>'
    '<p>Evidence concerns the tested system and protocol; it does not validate our camera-only pipeline.</p></div></div>' +
    '<p class="muted">Earlier ~45-second raw reconstruction is presenter-reported, not a full-workflow benchmark. The new one-capture caliper checks are not a blinded or multi-person accuracy study.</p>',
    'Prototype evidence updated November 11, 2026; source hashes retained in the frozen pilot summary. Technical references checked October 29, 2026. Recommender comparison results come from the November 12 paired local experiment, '
    'with frozen aggregates and source hashes in recommender-evidence.json and paired-measurement-evidence.json. The seven-person pipeline comparison is separate from the 49-person nose-feature experiment. The personal recommendation screenshot remains the October 25 model. They are internal retrospective ranking results, not a prospective evaluation. '
    'Model architecture is traced to python/mask_recommender/train.py, especially calc_preds and _resolve_custom_lr_parameter_views. '
    'For fixed family, style, and strap type, A = a_family + a_style < 0, B = b_family + b_style, '
    'C = c_family + c_style + s_strap. The centered equation uses kappa = -A, delta_star = -B/(2A), '
    'and c = C - B²/(4A). Legacy parameter files can bypass the newer negative-curvature parameterization; '
    'the historical dashboard snapshot does not independently establish its saved parameter constraints. '
    'Mixed labels and preprocessing/imputation also need an end-to-end validation audit. '
    'For the separate paired experiment, each of seven folds excludes the held-out person from all fitting. '
    'Traditional inputs are face width, face length, bitragion-subnasale arc, nose protrusion, nasal root breadth and nose bridge height. '
    'Traditional/PCA classifiers predict fit directly with L2 logistic regression, C=1, and equal-person training weights; scalers/PCA fit only on six training people. '
    'Production ARKit uses Adam 200 epochs, learning rate .01, original row-weighted BCE, the total-perimeter quadratic and shared latent nose mismatch. '
    'It is retrained per fold, never evaluated using already-deployed weights that could include these people. '
    'All arms score the same 421 observations at fixed 50 percent cutoff, without imputation or conversion into ARKit. '
    'The ARKit metrics average seeds 42/43/44 on the same folds; traditional/PCA are deterministic. '
    'Only six people have positive labels for top-k. Two people supply 296/421 tests. '
    'Equal-person evaluation weights each observation by 1/n for that person; it changes confusion counts, not model predictions or top-k. '
    'Different model architectures and training weights mean this does not isolate measurement modality causally. '
    'Perimeter constraints are an inductive bias, not a guarantee against overfitting or a proof of new-person generalization. '
    'Latest measurements and test dates can differ, labels mix sources, repeated user-mask tests can remain, and prospective full-catalog fit is untested.',
    source='Technical sources reviewed October 29; prototype evidence updated November 11; presentation date November 17, 2026.')

add('NEXT / VALIDATION PLAN', 'Next: validate measurements, then recommendation usefulness.',
    '<p class="validation-intro">Proposed staged study · Freeze the automated pipeline before independent evaluation.</p>'
    '<div class="validation-stages"><article><span class="validation-number">1</span><h2>Protocol & repeatability</h2>'
    '<strong class="validation-size">20-adult pilot</strong>'
    '<p>Define landmarks, routes, tape scaling and capture rules. Repeat captures; compare with independent tape/caliper readings and reference scans where available.</p>'
    '<p>Test raw, remeshed and Gaussian-smoothed surfaces; quantify scale and landmark uncertainty.</p></article>'
    '<article><span class="validation-number">2</span><h2>Locked geometry benchmark</h2>'
    '<strong class="validation-size">120 adults total</strong>'
    '<p>60 development participants, including the pilot; <strong>60 untouched test participants</strong>. Keep every session from one person together.</p>'
    '<p>Compare photogrammetry, direct-photo FLAME and ARKit where available. Report mm error, tail errors, repeatability and failed captures across devices.</p></article>'
    '<article><span class="validation-number">3</span><h2>Prospective fit usefulness</h2>'
    '<strong class="validation-size">60 separate adults</strong>'
    '<p>If geometry passes its gate, freeze recommendations before quantitative fit testing. Compare the first camera recommendation with each person’s initial choice.</p>'
    '<p>Also track top-three success, completion, time, staff burden and cost per usable recommendation / verified fit pass.</p></article></div>'
    '<div class="validation-gate"><strong>Provisional measurement targets:</strong> critical spans ≤2 mm MAE and ≤5 mm 95th-percentile absolute error; aggregate paths ≤5 mm MAE.</div>'
    '<p class="validation-boundary">Android/web research beta only within validated conditions. Adult-first proposal; pediatric validation requires separate scope. Publish negative findings and narrow or stop if gates are missed.</p>',
    'This summary draws on the November 9 Blueprint Biosecurity detailed discussion draft, sections 5 and 6, plus the concept note. It describes proposed work; funding, recruitment and results are not established. '
    'The immediate priority is to freeze landmark and curve definitions, independent reference procedures, capture rules and the tape-derived scale process. A 20-adult geometry pilot tests repeatability and feasibility before expanding. '
    'The geometry cohort has 120 adults total: 60 development participants, including the 20 pilot participants, and 60 untouched test participants. All images, repeated sessions and derivatives of a participant remain in one partition. '
    'References are separately acquired physical measurements and independent scans where available; reconstruction source-photo agreement is not the sole validation reference. Use a second rater on a prespecified subset. '
    'Benchmark raw photogrammetry, zero-filter remeshing and smoothing, direct-photo-to-FLAME fitting, and ARKit where supported. Separately test style-specific features so capture improvements are not confounded with a new feature set. '
    'Report signed bias, mean and 95th-percentile absolute error in millimeters, repeatability, Bland-Altman agreement, reference uncertainty and complete capture/abstention denominators. Use participant-level resampling for repeated observations. '
    'Provisional geometry gates are at most 2 mm mean absolute error and 5 mm 95th-percentile absolute error for critical spans, and at most 5 mm mean absolute error for aggregate paths. These are engineering targets, to be finalized before opening the test set, not achieved accuracy claims. '
    'Evaluate about six Android devices, webcams and an iPhone reference, reserving at least one device model from development; target at least 90 percent capture completion within two attempts in supported conditions. Measure turnaround and processing cost rather than assuming the existing 61-photo workflow is acceptable for end users. '
    'If measurement validation succeeds, recruit 60 separate adults for a prospective quantitative fit-testing pilot. Freeze the recommender before outcomes, randomize testing order and blind the operator to recommendation source where practicable. '
    'Primary outcome is the paired difference in quantitative pass rate between the first camera recommendation and initial choice; secondary outcomes include at least one top-three pass and operational burden. This is a feasibility/effect-estimation pilot, not a powered equivalence or infection-prevention trial. '
    'The proposal begins with adults. Pediatric validation needs a separately scoped protocol; this summary does not claim that the planned adult cohort establishes child performance. '
    'Release a research beta only within validated conditions, with supported devices and explicit failure feedback. Publish methods, aggregate results, negative findings and proceed/narrow/stop decisions.',
    30, 'Blueprint Biosecurity discussion draft · Nov 9, 2026 · Work plan / decision gates · Proposed studies and targets; not completed validation.',
    'validation-plan-slide')

# Insert the fixed-range comparison after slide 10 and its methods before sources.

validation_index = len(slides)-1
fixed_range_index = len(slides)
add_fixed_range_slides(add)
simple_feature_index = len(slides)
add_simple_feature_slide(add)
slide_order = (list(range(10)) + [simple_feature_index, fixed_range_index] + list(range(13, 16)) +
               [validation_index, 16] + list(range(10, 13)) +
               list(range(17, validation_index-1)) + [fixed_range_index+1, validation_index-1])
slides = [slides[index] for index in slide_order]
notes = [notes[index] for index in slide_order]
durations = [durations[index] for index in slide_order]
for index in range(len(slides)):
    notes[index] = re.sub(r'^\d+\.', f'{index + 1}.', notes[index])
    if durations[index] and index > 0:
        slides[index] = re.sub(r'(<div class="eyebrow">)\d{2} /',
                               lambda match: f'{match[1]}{index:02d} /', slides[index])

# Retain the established deck design and controls, frozen into a local template.
template = (ROOT / 'template.html').read_text()
html = template.replace('<!-- SLIDES -->', '\n'.join(slides))
(ROOT / 'presentation.html').write_text(html)
assert sum(durations) == 600
main_count = sum(seconds > 0 for seconds in durations)
elapsed = 0
checkpoints = []
for index, seconds in enumerate(durations):
    if seconds:
        checkpoints.append(f'Slide {index + 1}: {elapsed // 60}:{elapsed % 60:02d}')
        elapsed += seconds
(ROOT / 'speaker-notes.txt').write_text(
    'NASEM · November 17, 2026 · NPPTL researchers\n'
    f'Main talk: slides 1–{main_count}, 600 seconds total. Remaining slides are optional backups.\n'
    'Slide start times: ' + ' · '.join(checkpoints) + ' · close at 10:00.\n\n' + '\n'.join(notes))
print(f'Built {len(slides)} slides ({main_count} main + {len(slides)-main_count} backup); main talk: 10:00.')
