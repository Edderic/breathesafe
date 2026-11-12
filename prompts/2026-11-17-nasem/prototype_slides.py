"""November camera-prototype slides, using frozen evidence and actual surface views."""
import json
import math
from pathlib import Path


def add_slides(add, screenshot):
    evidence=json.loads((Path(__file__).parent/'prototype-evidence.json').read_text())
    assert evidence['participants']==1 and evidence['reconstruction_captures']==1
    for row in evidence['linear_checks']:
        assert math.isclose(row['estimated_mm']-row['median_mm'],row['signed_difference_mm'])
    add('NEW / CAMERA PROTOTYPE', 'Photos now produce a physically scaled digital headform.',
        '<div class="prototype-figures"><figure>'+screenshot('prototype/raw-headform.jpg','Actual neck-inclusive photogrammetry reconstruction.','prototype-image')+
        '<figcaption>Raw photogrammetry reconstruction</figcaption></figure><figure>'+screenshot('prototype/smoothed-headform.jpg','Same reconstructed head after Gaussian smoothing, including the jaw and upper neck.','prototype-image')+
        '<figcaption>Smoothed surface · same coordinates</figcaption></figure></div>'+
        '<p class="takeaway">61 ordinary-camera photos → registered 3D surface → supported smoothing → tape-based scale in millimeters.</p>'+
        '<p class="muted">Head still, camera moving; eye-level and lower views retain upper-neck coverage. Laptop prototype demonstrated; Android workflow validation remains ahead.</p>',
        'Since the October draft, the camera-only path has become a working local prototype. This is an actual reconstructed head, not a fitted FLAME shape. '
        'The same 61-photo capture includes the jaw and upper neck. Gaussian volume smoothing reduces graininess while source-photo checks remain available. '
        'A measured bitragion–subnasale tape arc sets physical scale; it is not inferred from an average model face. '
        'This is a digital headform, not a fabricated or uniformly validated surface. Smoothing does not establish anatomy where source coverage is missing. '
        'The complete updated workflow has not been benchmarked for speed or validated on Android.',
        40,'November 11 prototype update · One participant, one capture · Digital headform; no fabricated-headform or population-accuracy claim.', 'prototype')
    add('NEW / LANDMARKS & DISTANCES', 'Landmarks support chords and surface routes.',
        '<div class="prototype-figures"><figure>'+screenshot('prototype/landmark-widths.jpg','Nose-wing and cheekbone contact candidates on the actual reconstructed head, joined by straight width chords.','prototype-image')+
        '<figcaption>Straight chords · nose and cheekbone widths</figcaption></figure><figure>'+screenshot('prototype/under-chin-route.jpg','Trifold or duckbill surface-route draft on the reconstructed head, seen from below.','prototype-image')+
        '<figcaption>Surface-route draft · inspect below the jaw</figcaption></figure></div>'+
        '<p class="takeaway">Dense multi-photo correspondences propose surface-attached points. Original-photo overlays support anatomical review.</p>'+
        '<p class="muted">A chord joins two 3D endpoints. A surface arc follows the mesh through controls. Named landmarks and route controls retain their attachments.</p>',
        'The prototype now proposes points using existing dense multi-photo correspondences, triangulates them with the registered cameras, and checks support on the raw surface before attaching them to the smoothed one. '
        'Source-photo overlays let us inspect whether the coordinates match the anatomical contact intended. The presenter visually approved the proposed nasal-wing and cheekbone contacts for this capture. '
        'Straight widths use Euclidean 3D endpoint chords. Surface routes use local triangle-strip shortcuts through controls; these are not exact global geodesics or physical tape simulations. '
        'The upper-neck coverage supports inspection of under-menton routes for trifold and duckbill styles. These points are not a direct ARKit-to-FLAME equivalence claim, and the full perimeter is still exploratory.',
        40,'Actual prototype views · Width contacts visually approved for this capture · Route overlays may show through the mesh; no seal-pressure prediction.', 'prototype')
    rows=''.join(f'<tr><td>{r["name"]}</td><td>{r["median_mm"]:.1f} mm</td><td>{r["estimated_mm"]:.1f} mm</td><td>{r["signed_difference_mm"]:+.1f} mm</td></tr>' for r in evidence['linear_checks'])
    add('NEW / INITIAL PHYSICAL CHECKS', 'Three linear checks agree within 2.3 mm in one pilot.',
        '<div class="prototype-scale"><strong>Scale reference: 284 mm</strong><span>Median bitragion–subnasale tape arc: 288, 280, 284 mm.</span></div>'+
        '<table class="method-table prototype-results"><thead><tr><th>Dimension</th><th>Caliper median</th><th>Headform</th><th>Headform − caliper</th></tr></thead><tbody>'+rows+'</tbody></table>'+
        '<div class="callout">Caliper dimensions check the tape-derived scale; they do not adjust it.</div>'+
        '<p class="muted">One person, one capture; three caliper readings per dimension. Method and endpoint choices were inspected during development—not a blinded accuracy or capture-repeatability study.</p>',
        'The scale anchor is the median of three bitragion–subnasale tape readings: 288, 280 and 284 millimeters. '
        'With that scale fixed, the headform gives nose width 35.2 versus a 35.0 millimeter caliper median, face length 112.3 versus 114.6, and face width 153.0 versus 150.9. '
        'These are separate dimensions from the calibration arc, with repeated caliper readings but only one reconstruction capture. '
        'The endpoints and methods were inspected during development, so these are initial agreement checks, not a blinded validation set. '
        'Next steps are independent repeated captures, predefined landmarks and reference protocols, and more people, devices and lighting conditions. '
        'Perimeter work remains separate: a future experiment may photograph a suitable bifold mask while worn, reconstruct/register it and trace its contact arc. The exploratory perimeter discrepancy is omitted from this presentation.',
        40,'Frozen November pilot reports · Three readings per caliper dimension, not three captures · Rounded to 0.1 mm; no population-accuracy claim.', 'prototype')
