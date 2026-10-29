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
    '06 / ANDROID DEVELOPMENT': 80,
    '07 / LESSONS FOR NPPTL APPS': 90,
    '08 / TAKEAWAY': 30,
}


def chart(name, alt):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="chart result-chart" src="data:image/svg+xml;base64,{encoded}" alt="{escape(alt)}">'


def screenshot(name, alt, cls='reference-image'):
    encoded = base64.b64encode((ROOT / 'assets' / name).read_bytes()).decode()
    return f'<img class="{cls}" src="data:image/png;base64,{encoded}" alt="{escape(alt)}">'


personal = json.loads((ROOT / 'data/personal-recommendations-2026-10-29.json').read_text())
recommendation_cards = '<div class="personal-recommendations">' + ''.join(
    '<article><h3>' + escape(item['name']) + '</h3>'
    '<p class="personal-score">' + str(item['predicted_fit_percent']) + '% <span>predicted fit</span></p>'
    '<p class="observed-result" hidden>Observed Fit: ' + escape(item['observed_fit']) + '</p></article>'
    for item in personal['recommendations']
) + '</div>'


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

add('01 / THE APPLICATION', 'From my facial measurements to recommendations.',
    '<div class="capture-demo"><figure>' +
    screenshot('masqfit-capture.png', 'MasqFit app showing selected measurement points overlaid on a face.', 'demo-phone') +
    '<figcaption>ARKit in the current app</figcaption></figure><figure>' +
    screenshot('masqfit-measurements.png', 'MasqFit five aggregate measurements: nose 45.1 mm, strap 129.0 mm, top cheek 99.1 mm, mid cheek 94.0 mm, chin 128.8 mm.', 'demo-phone') +
    '<figcaption>Five paths in millimeters</figcaption></figure><div><div class="recommendation-heading">'
    '<h2>Recommendations for Edderic</h2><button id="toggle-observed" aria-expanded="false" aria-controls="sample-recommendations">Show observed fit</button></div>'
    '<div id="sample-recommendations">' + recommendation_cards + '</div>'
    '<p class="personal-caption"><a href="' + escape(personal['source_url'], quote=True) + '">Open live recommendations</a>'
    ' · Oct 29 screenshot<br>Model: custom_lr · Oct 25, 2026</p>'
    '<p class="personal-caption">Nose + top cheek + mid cheek + chin → perimeter proxy. Strap path collected separately.</p></div></div>',
    'Here is ARKit in the current MasqFit app. The dots mark selected facial measurement paths. '
    'The next screen shows five aggregates in millimeters: nose, strap, top cheek, mid cheek, and chin. '
    'Four paths form the perimeter proxy used for ranking masks. The strap path is collected but does not directly enter this model. '
    'The cards at right show four recommendations for me from the October 29 screenshot, using the October 25 model. '
    'Observed Fit starts hidden; the slide button can reveal the values from the screenshot. '
    'The displayed predicted percentages are model outputs, not calibrated individual success probabilities or independent validation. '
    'This personal example is separate from the held-out ranking results on slide 4.',
    30, 'Presenter screenshots and personal example · Predicted percentages are model outputs; calibration is not established.')

add('02 / GEOMETRY → FIT SCORE', 'A preferred perimeter difference, learned from outcomes.',
    '<div class="equation compact-equation">Δ = (P<sub>face, mm</sub> − P<sub>mask, mm</sub>) / 10 &nbsp; [cm]<br>'
    'Fit score = sigmoid[c − κ(Δ − Δ*)²], &nbsp; κ &gt; 0</div>' +
    chart('model-response.svg', 'Schematic curves with invented coefficients peak at perimeter differences of zero and minus two centimeters, then decline on either side.') +
    '<p class="takeaway">Δ* is the learned optimum; it need not be zero. Moving away lowers the modeled fit score.<br>'
    'Facial perimeter proxy = nose + upper cheek + mid-cheek + chin paths, measured in mm.</p>',
    'The face measurement enters the recommender as a perimeter proxy: four selected facial paths added together. '
    'Subtract the mask perimeter and convert millimeters to centimeters. This is a signed difference of lengths, not a physical gap between the face and mask. '
    'A quadratic in that difference feeds a logistic function. In this centered form, delta star is the preferred difference, '
    'kappa controls how quickly the score falls away, and c sets the peak logit. '
    'The optimum need not be zero: the model can learn that a family and style work best at a nonzero difference. '
    'Family and style supply the quadratic coefficients; strap type supplies an offset. New training constrains curvature to be negative. '
    'The plotted curves use invented coefficients to explain the shape; they are not measured mask response curves. '
    'The sigmoid gives a probability-like fit score for ranking, but calibration needs separate evaluation. '
    'A limitation is geometry compression: for the same mask, two faces with the same summed perimeter get the same score.',
    75, 'Source: custom_lr calc_preds and parameterization · Curve is schematic; invented coefficients, not fitted probabilities.')

performance = json.loads((ROOT / 'data/dashboard-2026-09-24.json').read_text())['recommender_performance']
rates = [performance[f'cross_validation_top_{k}_hit_rate_mean'] for k in (1, 3, 5)]
assert all(0 <= rate <= 1 for rate in rates) and rates == sorted(rates)
add('03 / RECOMMENDER RELEVANCE', 'How often was a fitting result near the top?',
    chart('current-top-k.svg', 'Five-fold conditional mean hit rates: top one 64.2 percent, top three 90.3 percent, top five 92.8 percent.') +
    '<div class="callout">Top 1: '+f'{rates[0]:.1%}'+ ' &nbsp; · &nbsp; Top 3: '+f'{rates[1]:.1%}'+
    ' &nbsp; · &nbsp; Top 5: '+f'{rates[2]:.1%}'+'</div>' +
    '<p class="takeaway">Held-out users with ≥1 positive fit label; ranks previously tested observations.<br>'
    'Retrospective relevance evidence. Prospective success with newly recommended masks remains to be tested.</p>',
    'These are the saved September dashboard results: top one 64.2 percent, top three 90.3 percent, and top five 92.8 percent. '
    'The question is whether at least one positive fit label appears among the first k ranked held-out test observations. '
    'The reported percentages are unweighted means across five user-grouped folds. Only users with a positive held-out result contribute. '
    'The candidate set is their observed test rows, not the entire catalog, and repeated observations can remain. '
    'For example, top three is a hit if one of the first three ranked observations has a positive label. '
    'It is not a claim that sending three new masks to an arbitrary new user will yield a 90.3 percent chance of a fit. '
    'The labels combine formal test sources and constructed outcomes, so this is internal relevance evidence rather than a formal-test-only prospective trial. '
    'Fold counts and uncertainty were not exposed by this snapshot. The transferable lesson is to evaluate ranking relevance explicitly, '
    'then test the user decision prospectively.',
    75, 'Frozen dashboard retrieved Sept 24, 2026 · Model Sept 20, 2026 · Five-fold means · Fold denominators / uncertainty unavailable.')

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

add('03 / WHAT WORKED', 'ARKit made the measurement experience simpler.',
    '<div class="reference-layout"><figure>' +
    screenshot('arkit-reference.png', 'Apple Developer video screenshot illustrating the ARFaceAnchor triangular face mesh.') +
    '<figcaption>Apple Developer: ARFaceAnchor mesh</figcaption></figure><div>'
    '<h2>Metric face geometry</h2><p>Our TrueDepth path uses infrared depth sensing and a fitted face mesh.</p>'
    '<h2>Real-time feedback</h2><p>No separate pixel-to-millimeter step in this workflow.</p>'
    '<p class="muted">Millimeter units do not establish millimeter accuracy.</p></div></div>',
    'ARKit felt more seamless because I did not need to ask the user to supply a conversion between pixels and physical size. '
    'On the TrueDepth devices used by this workflow, Apple combines its camera system and infrared depth sensing with a face model. '
    'The mesh supports real-time distance calculations, which helps make the capture interaction immediate. '
    'That is an implementation advantage rather than a measurement validation result. A model can report millimeters and still be biased at a particular facial region. '
    'Also, ARKit face tracking availability is broader than TrueDepth on some newer devices; I am describing our TrueDepth measurement path, '
    'not asserting that every ARKit-compatible device has the same depth hardware or metrology performance.',
    60, f'<a href="{APPLE}">ARFaceGeometry</a> · <a href="https://developer.apple.com/documentation/arkit/arfacetrackingconfiguration">Apple device support</a> · Experience: presenter report.')

add('04 / WHAT DID NOT TRANSFER DIRECTLY', 'A mesh vertex is not an anatomical definition.',
    '<div class="reference-layout"><figure>' +
    screenshot('mediapipe-reference.png', 'Presenter-supplied MediaPipe example showing a face with and without a landmark mesh overlay.') +
    '<figcaption>MediaPipe example supplied by presenter</figcaption></figure><div>'
    '<h2>Anatomical correspondence</h2><p>Mesh vertices may not coincide with the traditional landmarks used by NIOSH.</p>'
    '<h2>Occluded points</h2><p>Face models can infer hidden points. An estimated coordinate is not a direct observation.</p></div></div>' +
    callout('Open question for ARKit and MediaPipe: how accurate are occluded-point estimates from one viewing angle?'),
    'A mesh vertex is not automatically the anatomical point we want. Both systems fit or predict facial geometry, '
    'so a returned coordinate may be inferred even where the surface is not visible from that angle. '
    'That is useful for tracking, but I have not established the accuracy of these hidden points from a single view. '
    'We should compare visible and occluded landmarks against an independent reference, across head angles and single-view versus multi-view capture. '
    'More frames from one angle do not necessarily reveal the hidden surface. Multi-view capture adds observations, but its benefit still needs testing.',
    40, f'<a href="{GOOGLE}">Google: predicted mesh</a> · <a href="{APPLE}">Apple: fitted face geometry</a> · Single-angle accuracy: not yet established by this project.')

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

add('06 / ANDROID DEVELOPMENT', 'Separate reconstruction from landmarking.',
    '''<div class="pipeline"><article><b>1</b><h2>3D face</h2><p>Synthetic geometry<br>or a captured human face</p></article>
    <span>→</span><article><b>2</b><h2>2D landmarks</h2><p>Detect target points in rendered or captured views</p></article>
    <span>→</span><article><b>3</b><h2>3D projection</h2><p>Map detections onto the matching surface</p></article>
    <span>→</span><article><b>4</b><h2>Dimensions</h2><p>Establish physical scale; calculate defined distances</p></article>
    <span>→</span><article><b>5</b><h2>Predict fit</h2><p>Evaluate the measured features in the ranking pipeline</p></article></div>''' +
    callout('Current development direction for Android; synthetic faces provide geometry labels, not fit outcomes.'),
    'This is the pipeline I am working toward. Begin with a 3D face, either synthetic or from an actual captured person. '
    'Use rendered or captured 2D views to detect the target landmarks, then project those detections back onto the matching 3D surface. '
    'Projection requires the camera-to-surface relationship: for a rendered view it is known; for a captured view it must be recovered or calibrated. '
    'A point on the image does not select the correct surface point without that relationship and visibility checks. '
    'Once the landmarks are on a scaled surface, calculate the defined dimensions and pass them into the fit-prediction pipeline. '
    'Synthetic models let us generate known geometry labels and controlled views. They do not tell us whether a respirator fits a real person. '
    'The difficult transfer is from synthetic rendering to real cameras and faces, which needs independent evaluation.',
    90, 'Development direction described by presenter · Pipeline is not presented as a validated Android release.')

add('07 / LESSONS FOR NPPTL APPS', 'Validate the handoffs, not only the final score.',
    cards([('Capture → geometry', 'Measure scale error, repeatability, failed scans, and variation across devices.'),
           ('Geometry → dimensions', 'Compare defined landmarks and distances with an independent reference.'),
           ('Dimensions → fit', 'Use held-out people and formal fit-test outcomes; evaluate practical selection benefit.')]) +
    callout('Use one measurement definition across platforms.<br>Track units, landmark definitions, capture method, and version with every result.'),
    'For your iOS and Android apps, I would start with a common measurement contract. Specify the landmarks, units, and distance definitions '
    'independently of the camera library. Record the capture method and version so that a change in reconstruction is traceable. '
    'Then validate the handoffs. At capture, count failures and repeated-scan variability across devices and conditions. '
    'At measurement, compare each dimension to an independent reference and report bias and repeatability, not just correlation. '
    'At prediction, hold out people and use fit-test outcomes to evaluate whether the measurements improve selection. '
    'Keep synthetic, printed-face, and real-human evidence separate. If the camera route changes a feature’s meaning or distribution, '
    'do not assume a model trained on the old route will transfer unchanged. The useful collaboration is agreeing on definitions and reference measurements before optimizing the interface.',
    90, 'Proposed evaluation priorities; not completed validation results.')

add('08 / TAKEAWAY', 'Choose the capture route.<br>Keep the measurement contract.',
    '<p class="lead">ARKit reduced calibration friction.<br>MediaPipe helped with real-time landmarks.<br>'
    'Photogrammetry offers a path to broader camera access.</p>' +
    callout('Shared research question: which landmarks and reference protocol should both apps use?') +
    '<p class="muted credits">Thank you: Kanro · Aaron Collins / OpenAeros · Gerard Hughes · Nukit · anonymous contributors</p>',
    'My main lesson is to separate the capture technology from the scientific definition of the measurement. '
    'ARKit simplified the first iOS experience. Moving toward Android means making scale, landmark placement, and reconstruction explicit. '
    'I would welcome discussion about a shared set of anatomical definitions and an independent reference protocol that could help both projects. Thank you.',
    30, 'MasqFit · Breathesafe · Main talk ends at 10:00')

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
    'Technical references checked October 29, 2026. Recommender results come from the frozen September 24 dashboard, '
    'model timestamp September 20, 2026. They are historical internal ranking results, not a fresh evaluation. '
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
