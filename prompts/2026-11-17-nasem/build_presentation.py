"""Build the local November draft. Never writes to public/ or deploys anything."""
from html import escape
from pathlib import Path
import base64
import json
import re

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
    '01 / THE APPLICATION': 30,
    '02 / THREE APPROACHES': 60,
    '03 / WHAT WORKED': 40,
    '04 / WHAT DID NOT TRANSFER DIRECTLY': 40,
    '05 / WHY PHOTOGRAMMETRY': 60,
    '06 / ANDROID DEVELOPMENT': 70,
    '07 / OBSERVED FIT': 40,
    '08 / WHO IS REPRESENTED': 30,
    '09 / ACKNOWLEDGEMENTS': 30,
}


def chart(name, alt):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="chart result-chart" src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt)}">'


def screenshot(name, alt, cls='reference-image'):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="{cls}" src="data:image/png;base64,{encoded}" alt="{escape(alt)}">'


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
        f'<div class="demographic-row"><span>{escape(row["name"])}</span><strong>{row["unique_users"]}</strong></div>'
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
    30, 'Presenter screenshot · Individual scores are model outputs; calibration is not established.', 'visual-slide recommendation-slide')

add('02 / GEOMETRY → FIT SCORE', 'A preferred perimeter difference, learned from outcomes.',
    '<div class="equation compact-equation">Δ = (P<sub>face, mm</sub> − P<sub>mask, mm</sub>) / 10 &nbsp; [cm]<br>'
    'Fit score = sigmoid[c − κ(Δ − Δ*)²], &nbsp; κ &gt; 0</div>' +
    chart('model-response.svg', 'Schematic curves with invented coefficients peak at perimeter differences of zero and minus two centimeters, then decline on either side.') +
    '<p class="takeaway">Δ* is the learned optimum; it need not be zero. Moving away lowers the modeled fit score.<br>'
    'Facial perimeter proxy = nose + upper cheek + mid-cheek + chin paths, measured in mm.</p>' +
    '<div class="next-feature"><strong>Next feature to test:</strong> compare the face’s nose path with a matching mask nose perimeter, then evaluate whether it improves held-out fit prediction.</div>',
    'The face measurement enters the recommender as a perimeter proxy: four selected facial paths added together. '
    'Subtract the mask perimeter and convert millimeters to centimeters. This is a signed difference of lengths, not a physical gap between the face and mask. '
    'A quadratic in that difference feeds a logistic function. In this centered form, delta star is the preferred difference, '
    'kappa controls how quickly the score falls away, and c sets the peak logit. '
    'The optimum need not be zero: the model can learn that a family and style work best at a nonzero difference. '
    'Family and style supply the quadratic coefficients; strap type supplies an offset. New training constrains curvature to be negative. '
    'The plotted curves use invented coefficients to explain the shape; they are not measured mask response curves. '
    'The sigmoid gives a probability-like fit score for ranking, but calibration needs separate evaluation. '
    'A limitation is geometry compression: for the same mask, two faces with the same summed perimeter get the same score. '
    'A future improvement is to retain the nose path as its own feature and measure a corresponding nose perimeter on each mask. '
    'We could model their difference separately from the whole-face perimeter and test whether it improves held-out predictions. '
    'This is a proposal, not a measured improvement. Yu and Griffin’s 2024 study used respirator-specific face measurements, including the nose and chin, to examine associations with fit. '
    'Their study does not validate the particular face-to-mask nose perimeter feature proposed here.',
    75, 'Source: custom_lr calc_preds · Schematic curve uses invented coefficients · <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC10941723/">Yu &amp; Griffin et al. (2024): FFR-specific face anthropometry and fit</a>.', 'geometry-slide')

dashboard = json.loads((ROOT / 'data/dashboard-2026-10-29.json').read_text())
performance = dashboard['recommender_performance']
rates = [performance[f'cross_validation_top_{k}_hit_rate_mean'] for k in (1, 3, 5)]
assert all(0 <= rate <= 1 for rate in rates) and rates == sorted(rates)
add('03 / RECOMMENDER RELEVANCE', 'How often was a fitting result near the top?',
    '<div class="topk-bars">' + ''.join(
        f'<div class="topk-row"><strong>Top {k}</strong><div class="topk-track"><span style="width:{rate:.2%}"></span></div><b>{rate:.1%}</b></div>'
        for k, rate in zip((1, 3, 5), rates)
    ) + '</div>' +
    '<div class="callout">Top 1: '+f'{rates[0]:.1%}'+ ' &nbsp; · &nbsp; Top 3: '+f'{rates[1]:.1%}'+
    ' &nbsp; · &nbsp; Top 5: '+f'{rates[2]:.1%}'+'</div>' +
    '<p class="takeaway">Held-out users with ≥1 positive fit label; ranks previously tested observations.<br>'
    'Retrospective relevance evidence. Prospective success with newly recommended masks remains to be tested.</p>',
    f'These are the October 29 dashboard results for the October 25 model: top one {rates[0]:.1%}, top three {rates[1]:.1%}, and top five {rates[2]:.1%}. '
    'The question is whether at least one positive fit label appears among the first k ranked held-out test observations. '
    'The reported percentages are unweighted means across five user-grouped folds. Only users with a positive held-out result contribute. '
    'The candidate set is their observed test rows, not the entire catalog, and repeated observations can remain. '
    'For example, top three is a hit if one of the first three ranked observations has a positive label. '
    'It is not a claim that sending three new masks to an arbitrary new user will yield the displayed top-three rate of fit. '
    'The labels combine formal test sources and constructed outcomes, so this is internal relevance evidence rather than a formal-test-only prospective trial. '
    'Fold counts and uncertainty were not exposed by this snapshot. The transferable lesson is to evaluate ranking relevance explicitly, '
    'then test the user decision prospectively.',
    75, 'Dashboard snapshot Oct 29, 2026 · Model Oct 25, 2026 · Five-fold means · Fold denominators / uncertainty unavailable.')

add('02 / THREE APPROACHES', 'The tradeoff: metric scale, speed, and reach.',
    '''<table class="method-table capture-table"><thead><tr><th>Approach</th><th>Geometry & scale</th><th>Experience</th><th>Main constraint</th></tr></thead><tbody>
    <tr><td>ARKit + TrueDepth<br><small>Our iOS path</small></td><td>Metric 3D mesh;<br>meters → millimeters</td><td>Real-time</td><td>Apple hardware path; anatomical mapping still needed</td></tr>
    <tr><td>Google MediaPipe</td><td>Normalized image coordinates + relative depth;<br>physical scale needs calibration</td><td>Real-time</td><td>A landmark mesh is not a subject-specific metric measurement</td></tr>
    <tr><td>Photogrammetry</td><td>Multi-view 3D surface;<br>physical scale must be established</td><td>~45 s processing<br><small>Developer-reported workflow</small></td><td>Slower reconstruction; anatomical landmarking is a separate step</td></tr>
    </tbody></table>''' + callout('Standard-camera capture offers a path toward iOS, Android, and webcams.'),
    'These are three different starting points. In our TrueDepth-based ARKit workflow, the mesh has metric coordinates, '
    'so I can calculate a distance in meters and convert to millimeters. MediaPipe is very useful for real-time landmark detection across camera platforms, '
    'but its standard output is normalized image coordinates and relative depth. Converting normalized coordinates to pixels does not tell me the physical size of the face. '
    'Google also offers a Face Geometry representation with canonical metric units; that is not an independent measurement of the particular person’s absolute size. '
    'Photogrammetry reconstructs a surface from multiple images. It supports ordinary cameras, but still needs physical scale and anatomical landmarks. '
    'The roughly 45 seconds here is my reported processing experience, not a benchmark across implementations, devices, capture time, or uploads.',
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

add('05 / WHY PHOTOGRAMMETRY', 'Broader camera support adds new work.',
    cards([('Why pursue it', 'Reconstruct a 3D surface from standard-camera images; a plausible common capture route across platforms.'),
           ('What it costs', 'Multi-view capture and a processing wait; motion, coverage, and lighting need attention.'),
           ('What to add', 'Physical scale, automatic anatomical landmark detection, and capture-quality checks.')]) +
    callout('Published facial photogrammetry studies support its potential.<br>Our camera-only pipeline still needs its own accuracy and repeatability study.'),
    'Photogrammetry is attractive because it can use ordinary cameras rather than relying on a particular depth sensor. '
    'Published work has shown good facial anthropometric performance for specific photogrammetric systems. '
    'That is motivation to investigate, not evidence that all smartphone or webcam implementations achieve the same accuracy. '
    'The cost is a slower experience: multiple views and reconstruction rather than an immediate mesh. In my workflow, processing has been around 45 seconds. '
    'That changes the interface: users need capture instructions, a clear waiting state, and a useful way to recover from failure. '
    'Reconstruction itself does not provide the anatomical labels I need. Scale and landmark detection remain separate engineering and validation steps.',
    90, f'<a href="{PHOTO}">Aldridge et al., 2005: facial photogrammetry vs. direct anthropometry</a> · ~45 s: presenter-reported processing time.')

add('06 / ANDROID DEVELOPMENT', 'Building the Android path: faces and landmarks.',
    '<div class="android-gallery"><figure><div class="android-shot generator">' +
    screenshot('android-flame-generator.png', 'MasqFit research tool generating a synthetic FLAME face with adjustable shape parameters.', 'android-screen') +
    '</div><figcaption>Generate controlled 3D faces</figcaption></figure><figure><div class="android-shot landmarks">' +
    screenshot('android-landmark-labeling.png', 'MasqFit research tool showing labeled facial landmarks on a synthetic FLAME face.', 'android-screen') +
    '</div><figcaption>Label anatomical points on the 3D surface</figcaption></figure></div>' +
    '<div class="android-flow"><span>3D face → 2D views</span><span class="android-arrow">→</span>' +
    '<span class="cnn-step">' + svg_icon('cnn-local-features.svg', 'CNN diagram: local facial features pass through a convolution grid.', 'cnn-icon') +
    '<span><strong>CNN detector · planned</strong><small>eyes · nose · ears · other landmarks</small></span></span>' +
    '<span class="android-arrow">→</span><span>3D projection → dimensions → fit</span></div>',
    'This is the pipeline I am working toward. Begin with a 3D face, either synthetic or from an actual captured person. '
    'Use rendered or captured 2D views to detect the target landmarks, then project those detections back onto the matching 3D surface. '
    'A planned CNN detector would learn local visual patterns around features such as eyes, nose, ears, and other landmarks in those 2D views. The screenshot shows hand-labeled landmarks that can support training and evaluation; it does not show a trained CNN result. '
    'Projection requires the camera-to-surface relationship: for a rendered view it is known; for a captured view it must be recovered or calibrated. '
    'A point on the image does not select the correct surface point without that relationship and visibility checks. '
    'Once the landmarks are on a scaled surface, calculate the defined dimensions and pass them into the fit-prediction pipeline. '
    'These screenshots show the current FLAME synthetic-face generator and anatomical landmark labeling tool. They are research tools for the Android path, not Android app screens. '
    'Synthetic models let us generate known geometry labels and controlled views. They do not tell us whether a respirator fits a real person. '
    'The difficult transfer is from synthetic rendering to real cameras and faces, which needs independent evaluation.',
    90, 'Presenter screenshots of research tools · Synthetic geometry and landmarks need anatomical, scale, and real-camera validation.', 'android-slide')

fit_stats = dashboard['fit_tests']
pass_rates = fit_stats['pass_rates']
assert pass_rates['overall']['total'] == fit_stats['total_unique'] == 1145
assert pass_rates['overall']['passed'] == 296
add('07 / OBSERVED FIT', 'Observed pass rates vary by strap and style.',
    '<div class="dashboard-overall"><strong>296 of 1,145 tests passed</strong><span>25.9% overall in the dashboard’s filtered dataset</span></div>'
    '<div class="dashboard-panels"><article><h2>Strap type</h2>' + rate_rows(pass_rates['by_strap_type']) +
    '</article><article><h2>Mask style</h2>' + rate_rows(pass_rates['by_style']) + '</article></div>' +
    '<p class="dashboard-note">Descriptive test-level rates; multiple tests can come from one person. Groups with fewer than 10 tests omitted.</p>',
    'The dashboard currently includes 1,145 distinct test records with usable pass outcomes and linked facial measurements; 296 pass. '
    'The adjustable headstrap group has 120 passes in 283 tests, or 42.4 percent. Headstraps have 162 in 477, or 34.0 percent. '
    'Earloop groups are much lower in this dataset. By style, bifold and gasket has 91 in 265, boat 136 in 510, and bifold 30 in 206. '
    'These are observed associations across different products and participants, not randomized comparisons or estimates of what changing a strap would do. '
    'Test counts vary substantially, and participants can contribute repeated tests. Groups with fewer than ten tests are left off the chart: '
    'strapless 0 of 2, elastomeric 5 of 7, and adhesive 0 of 2. For an app, display denominators with every rate.',
    40, '<a href="https://www.breathesafe.xyz/#/dashboard">Breathesafe dashboard</a> snapshot Oct 29, 2026 · Filtered fit tests · Descriptive only.', 'dashboard-slide')

demographics = fit_stats['demographics']
add('08 / WHO IS REPRESENTED', 'Who contributed the 1,145 fit tests?',
    '<p class="dashboard-subtitle">55 unique participants · counts below are people, not tests</p>' +
    '<div class="demographic-grid">' +
    demographic_card('Gender / sex', demographics['gender_and_sex']) +
    demographic_card('Race / ethnicity', demographics['race_ethnicity']) +
    demographic_card('Age', demographics['age']) + '</div>' +
    '<div class="demographic-takeaway">Representation and repeat testing matter when interpreting a dashboard rate.</div>',
    'This is the composition of the same filtered dashboard dataset. It contains 55 unique participants and 1,145 tests. '
    'The columns show unique users within each demographic field, so a participant is counted once per column. '
    'For example, 41 participants are in the White or Caucasian category, and 29 are in the age category labeled Prefer not to say. '
    'The dashboard pools some small demographic groups into that label for privacy, so the label must not be read as all explicit nonresponse. '
    'These counts describe who is represented; they are not demographic-specific pass rates. Repeated tests and uneven coverage make subgroup comparisons especially sensitive. '
    'For app evaluation, track participant counts as well as test counts and assess performance across groups with suitable privacy safeguards.',
    30, '<a href="https://www.breathesafe.xyz/#/dashboard">Breathesafe dashboard</a> snapshot Oct 29, 2026 · Small groups may be pooled into “Prefer not to say.”', 'dashboard-slide')

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

add('BACKUP / SCALE & PROJECTION', 'The camera-only path needs a scale anchor.',
    '<div class="two-col"><div><h2>Absolute scale</h2><p>Use an independently known dimension or calibrated capture system.</p>'
    '<p>A canonical average face is a model prior, not an independent ruler for this person.</p></div>'
    '<div><h2>Surface correspondence</h2><p>Use the matching camera intrinsics and pose to project a 2D detection onto the mesh.</p>'
    '<p>Check occlusion, multiple intersections, missing surface regions, and agreement across views.</p></div></div>' +
    callout('Evaluate absolute millimeter errors without fitting scale to the reference target.'),
    'Use this only if asked about implementation. Rendered geometry provides known cameras for development. Captured geometry requires estimated or calibrated cameras. '
    'A known reference dimension must be independent of the target used for accuracy evaluation; otherwise calibration can conceal the error being tested.',
    source='Design considerations for the proposed pipeline.')

add('BACKUP / SOURCES', 'Sources and boundaries of the claims.',
    f'<div class="two-col sources"><div><h2>Technical references</h2><p><a href="{APPLE}">Apple: ARFaceGeometry</a></p>'
    f'<p><a href="https://developer.apple.com/documentation/arkit/arfacetrackingconfiguration">Apple: face tracking configuration and device support</a></p>'
    f'<p><a href="{GOOGLE}">Google: Face Mesh coordinate systems and canonical model</a></p></div>'
    f'<div><h2>Photogrammetry evidence</h2><p><a href="{PHOTO}">Aldridge et al. (2005), Digital three-dimensional photogrammetry: evaluation of anthropometric precision and accuracy using a Genex 3D camera system</a></p>'
    '<p>Evidence concerns the tested system and protocol; it does not validate our camera-only pipeline.</p></div></div>' +
    '<p class="muted">Real-time usability, seamlessness, and ~45-second processing are presenter-reported experience. No controlled speed comparison or new measurement-accuracy result is claimed.</p>',
    'Technical references checked October 29, 2026. Recommender results come from the October 29 dashboard snapshot, '
    'model timestamp October 25, 2026. They are internal retrospective ranking results, not a prospective evaluation. '
    'Model architecture is traced to python/mask_recommender/train.py, especially calc_preds and _resolve_custom_lr_parameter_views. '
    'For fixed family, style, and strap type, A = a_family + a_style < 0, B = b_family + b_style, '
    'C = c_family + c_style + s_strap. The centered equation uses kappa = -A, delta_star = -B/(2A), '
    'and c = C - B²/(4A). Legacy parameter files can bypass the newer negative-curvature parameterization; '
    'the historical dashboard snapshot does not independently establish its saved parameter constraints. '
    'Mixed labels and preprocessing/imputation also need an end-to-end validation audit.',
    source='Technical sources reviewed October 29, 2026; presentation date November 17, 2026.')

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
