# FLAME Open fitting to the analysis mesh

This offline CPU experiment fits neutral FLAME 2023 Open identity directions to
`result.surface.mesh`. It uses no Pixel3DMM code or weights. The original full
reconstruction is only hashed to validate an optional diagnostic point export;
it supplies no fitting correspondences.

From the repository root, using the existing webcam Python environment:

```sh
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.flame_fit \
  --session .private-webcam-runs/SESSION_ID \
  --model ~/Downloads/FLAME2023Open.zip \
  --exclude-probe ~/Downloads/nose-point-SESSION_ID.json \
  --out .private-webcam-runs/flame-fits/SESSION_ID-trial-1 \
  --iterations 40
```

The output directory must be new and outside the source session. Keep it in the
ignored private run tree, which Vite does not serve. Open `comparison.html`
directly in a browser: it embeds geometry and requires no network or processor.
Choose 50, 100 or 300 components; drag either panel to rotate both; use the
profile buttons and zoom to inspect the nose. The amber circle overlays the
exclusion sphere's projected radius and is not depth-tested. The left panel
defaults to the actual fitting target, with the excluded patch removed. Uncheck
**Show only fitting target on left** for the intact analysis mesh.

Outputs:

- `report.json`: source session/analysis/model/code hashes, coefficients,
  transforms, exclusions, settings, iteration history, timing, vertex residuals,
  reverse sampled triangle residuals and geometry flags.
- `analysis.ply`: copy of the bounded input surface; `fitting-target.ply`: its
  visible facial crop with exclusion-touching triangles removed.
- `flame-{50,100,300}.ply`: complete fitted FLAME topology in reconstruction
  units, including the unfitted scalp, ears, eyes and neck.
- `flame-{50,100,300}-face.ply`: fixed face crop used for display and residuals.
  Its open crop boundaries do not represent missing reconstruction coverage.
- `comparison.html`: self-contained local comparison and report download.

Each component count starts independently from the neutral template. Eye proxies
are re-intersected on the exact analysis topology for initial scale/translation;
the frontal camera supplies initial axes. Template eye components supply initial
eye positions. Shape parameters and proper global rotation/translation/uniform
scale are then optimized alternately. Expressions and articulated pose stay zero.

The target is restricted to the detector face-oval convex hull and nearest visible
frontal triangles. A fixed template crop excludes eyeballs, ears, scalp and neck.
Source vertex quadrature is weighted by incident neutral triangle area. Nearest
triangle correspondences use 90% trimming, maximum distance 0.15 eye-center proxy
span, Cauchy influence scale 0.025 span, coefficient L2 regularity 0.0001 and
bounds ±3. Both query and matched points inside an exclusion sphere are rejected;
target triangles whose bounding spheres touch the exclusion are conservatively
removed. These experimental settings and crop policies are recorded in the report.

An exported raw-full diagnostic point must match the session and original full
mesh hash. It defines a sphere of radius 0.12 eye-center proxy span. Without an
export, the default is a broader 0.15-span sphere at unreviewed detector index 4.
This eye-center span differs from the outer-eye normalizer in regional inspection.
The defective patch does not contribute to the loss; its result is inferred from
the FLAME prior and surrounding geometry.

The optimizer normalizes internally by eye span for numerical stability, then
converts geometry, translations, scale and distances back to reconstruction units.
The model's native numerical units do not establish physical scale. There is no
millimeter claim or calibration transfer. Source annotations, routes, cameras and
session state are never changed. No smoothing, hole filling, local blending or
recommender update is performed. Partial artifacts remain after interruption;
rerun in a fresh output directory. A completed solve can stop at its iteration
budget without converging; inspect `optimization_stop` and the history.

Decimation can introduce errors beyond the nose. Lower scan residuals alone do
not identify a better anatomical face. Inspect nose width/protrusion, bridge,
cheeks and chin against source photos before using a candidate for mask-contact
measurements. Normal reversals are review flags, not self-intersection tests.
Existing landmark attachments do not apply to the new topology.

Reports include Open model provenance and attribution for CC BY 4.0. Older FLAME
files are rejected by the existing Open loader. Model weights are not committed.

Verification:

```sh
env PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m unittest \
  dimension_pipeline.tests.test_flame_fit dimension_pipeline.tests.test_flame_open
node scripts/tests/webcam_flame_fit_smoke.cjs .private-webcam-runs/flame-fits/TRIAL
```

Tests cover proper similarity and shape recovery, unit propagation, coefficient
bounds, missing/excluded coverage and overwrite protection. The browser check
uses the generated local comparison and verifies rendering, profiles, variant
selection, source toggle, report download and absence of network requests.

## Reviewed ARKit counterparts and regional weighting

The standalone comparison now includes **Review approximate ARKit counterparts
on FLAME**. The point list is the unique indices from the repository's four
legacy scoring paths: nose, top cheek, mid cheek and chin. Shared path endpoints
appear once and show all their path memberships. Strap indices are not included.
No anatomical correspondence is pre-populated.

1. Choose a path and ARKit point. Enable **Click to place selected counterpart**.
2. Click the right-hand FLAME surface. Choose either a vertex or a point on a
   triangle; drag still rotates. A click picks the nearest visible triangle
   under the current shared orthographic view. Numeric vertex entry is also
   available for original indices inside the displayed crop.
3. Inspect frontal, profile and underside views. Select **Reviewed** only when
   satisfied; Pending, Uncertain and Unavailable rows do not contribute weights.
   Replacing a point resets its review status. Notes and radius/weight settings
   are saved per row in the in-tab draft. Gold is the selected row; cyan markers
   show other placements. Dashed markers are behind the visible surface.
4. Start with a radius of 0.12 neutral model eye spans and a maximum weight of 4.
   These are adjustable (radius 0.03–0.5, multiplier 1–10). Weight 1 contributes
   no additional emphasis. Download the mapping draft before closing the tab.
5. Reload its JSON to resume. Files from another model, topology, session or
   source analysis mesh are rejected, as are duplicate/unknown ARKit indices
   and invalid attachments. Invalid form fields block export until corrected.

Mapping files use `flame-arkit-analogs-v1`. Each row stores the ARKit index,
review status, notes, radius, multiplier, and either an original FLAME vertex
index or an original triangle index with three barycentric weights. Placement
provenance records which fitted mesh was used for inspection. These are
experimental approximate analogs, not validated anatomical equivalences or
ARKit measurements. They never modify `legacy_arkit_paths.json` or ARKit records.

`face-topology.json` records the original vertex/triangle IDs for the cropped
viewer. Before creating the comparison, the full fitted mesh hash and original
triangle order are checked. The display crop is built from the full mesh using
that explicit mapping. Markers follow the same original attachment across
component counts and ordinary/regional variants without nearest-point transfer.

To run the matched comparison after reviewing at least one placement:

```sh
env PYTHONPATH=python OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  tmp/webcam-pilot-venv/bin/python -m dimension_pipeline.flame_fit \
  --session .private-webcam-runs/SESSION_ID \
  --model ~/Downloads/FLAME2023Open.zip \
  --exclude-probe ~/Downloads/nose-point-SESSION_ID.json \
  --mapping ~/Downloads/flame-arkit-mapping-SESSION_ID.json \
  --components 100 --iterations 40 \
  --out .private-webcam-runs/flame-fits/SESSION_ID-regional-1
```

This generates both `flame-100.ply` and `flame-100-regional.ply`, with matching
face crops, in a new directory. Both fits start independently from the same
neutral face and alignment, use identical target triangles, regularity and
iteration budgets, and retain the nose exclusion. The mapping and its hash are
included in the report. The ordinary fit is not a continuation of an earlier fit.

Regions use shortest paths along neutral FLAME mesh edges within the fixed face
crop. A barycentric center starts at its three triangle corners with their
point-to-corner distances. Distances are fixed before optimization, avoiding
changes of membership as the face deforms or leakage across disconnected parts.
For d < radius, weight is `1 + (multiplier-1)*(1-(d/radius)^2)^2`; outside, it is 1.
Overlapping regions use their maximum weight, not their sum. Both alignment and
shape residuals receive the importance factor. The prior retains its base-weight
normalization. Priority vertices bypass global 90% trimming but retain the same
0.15-span hard distance gate and Cauchy influence function. Exclusion tests apply
before regional weights, including to the matched target point.

The report includes ordinary and regional per-region vertex residuals on the
same fixed vertex sets; regions wholly excluded or outside the crop are explicit.
No reviewed in-crop weighted placement produces an error rather than an implied
weighted result. The comparison's **Left comparison** selector can display the
ordinary FLAME fit on the left and regional fit on the right, with shared view
controls. Global and regional residuals remain scan agreement, not anatomical
accuracy. No reviewed mapping has been assumed for the participant.

Additional verification:

```sh
env PYTHONPATH=python tmp/webcam-pilot-venv/bin/python -m unittest \
  dimension_pipeline.tests.test_flame_mapping
node --test scripts/tests/webcam_flame_mapping.test.cjs
node scripts/tests/webcam_flame_analog_smoke.cjs PRIVATE_COMPARISON_DIRECTORY
```

Tests cover original-index picking, frontmost intersections, barycentric
attachments, mapping identity checks, review statuses, geodesic falloff,
overlapping regions, disconnected surfaces, a synthetic priority-fit improvement,
and matched ordinary/regional exports without changing the source session.
Browser placements are automated interaction fixtures, not participant reviews.

## Direct FLAME measurements and the expanded head

**Direct FLAME points, routes and tape calibration** is now the primary workflow.
On desktop, the point editor occupies the left half of the workspace and the
FLAME viewer stays visible on the right while the controls scroll. Analysis
geometry is hidden by default; **Show analysis / comparison mesh** restores it
below the editor. View presets, zoom and lighting remain beside the FLAME surface.
Enter a new point name and press Enter (or click **Add named point**); placement
is enabled automatically, ready for a click on the right. Routes/calibration and
the landmark guide expand separately, keeping repeated point placement compact.
No ARKit correspondence is required. The prior mapping editor remains optional
in a collapsed section. **Show full FLAME head, ears and lower chin** defaults
on and displays all 5,023 original vertices and 9,976 original triangles, rather
than the face fitting crop. The fitted geometry has not changed: ears, scalp,
neck and portions of the lower chin outside the original crop remain largely
prior-driven. Point status and exports identify whether an attachment lies
within the fitting crop. Use **Fit displayed FLAME head**, zoom, and profile
views to inspect the added geometry.

Select a named direct point (left/right tragion, subnasale, menton, pronasale,
sellion) or add your own name. Enable direct placement and click the right-hand
surface. Choose a vertex or a triangle point. Review from several views; changing
a placement resets its status. Direct placement and legacy mapping placement
are mutually exclusive. Green is selected, blue is another point, and dashed
markers are occluded. Named points are manual anatomical identifications, not
automatic FLAME labels.

Three editable ordered routes are available: scale, independent check, and a
custom arc. Edit the comma-separated control names or append a selected point.
Add intermediate points along the tape-contact path and reorder them explicitly;
an endpoint-only shortest path can take an unintended route. The magenta overlay
shows the actual edge path and is not depth-tested. Route lengths are piecewise
Dijkstra paths along the full mesh edges, with barycentric endpoint-to-corner
links and direct segments within a shared triangle. They are mesh-edge
approximations, not exact continuous geodesics or a physical tape-contact model.
Disconnected components, unavailable controls, unplaced controls and zero-length
arcs fail explicitly. Straight-line measurements use the Euclidean chord between
the chosen endpoints, independently of surface routes.

The scale route must start at left_tragion, pass subnasale once, and end at
right_tragion. Every control on it must be reviewed before calibration. Enter
three tape readings in millimeters and apply them: their median divided by the
mesh arc length gives a uniform mm/reconstruction-unit scale. The check route
passes left_tragion → menton → right_tragion. Its three readings produce a
separate mesh-versus-tape discrepancy and reading spread and never alter scale.
Invalid or incomplete check input is reported separately. Uncalibrated lengths
remain reconstruction units; reviewed calibration adds millimeter values.

**Download direct measurements** exports `flame-direct-measurements-v1` with
original-index attachments, review statuses, notes, routes, readings, computed
values, source model/topology/mesh hashes and fit identity. **Reload direct
measurements** requires the exact fitted mesh and recomputes all quantities;
it never trusts an imported scale result. Drafts are separate for each fit,
so changing component count does not transfer calibration. Download before
closing/reloading the page. The exported file is private research data.

**Download calibrated FLAME mesh** exports a separate full mesh in original
COLMAP world coordinates multiplied by the tape scale. The registered frontal
camera's translation receives the same scale; rotation and intrinsics stay
unchanged. It includes the annotation/calibration record and model attribution.
It does not replace source files or recommender/ARKit records. Calibration sets
scale; it does not validate the inferred ears or other prior-dominated regions.

Verification includes analytic edge-path/chord and barycentric examples,
missing/unavailable/disconnected coverage, median and spread, independent-check
isolation, unit propagation, strict per-mesh reload, and a browser interaction
using explicit automated fixture placements and tape values. Those fixtures are
not participant measurements:

```sh
node --test scripts/tests/webcam_flame_measurements.test.cjs
node scripts/tests/webcam_flame_direct_smoke.cjs PRIVATE_COMPARISON_DIRECTORY
```

## Drag-traced mask perimeters

Create separate named drafts under **Mask-style perimeter drafts** for bifold,
bifold with gasket, cup, trifold, duckbill, or custom styles. These style labels
provide starting guides from the participant's proposed contact patterns; they
do not generate anatomical routes or establish a seal. Several drafts can use
the same style for different mask models. Each stores its own name, notes,
review status, open/closed state and original FLAME barycentric controls.

Click **Add perimeter**, then drag over the FLAME surface. The tool samples the
nearest visible triangles at the chosen pixel spacing without rotating the head.
Hold Alt at the start of a drag to rotate instead, or use the view presets. To
continue around a side, rotate and begin the next stroke near its existing final
endpoint. Direct-point placement, legacy mapping and perimeter tracing modes are
mutually exclusive. Use the expanded head for under-jaw and possible neck contact;
those locations can be prior-dominated rather than constrained by the scan fit.

After release, nearby sampled controls are connected by mesh-edge surface paths
using heap-based Dijkstra. During drawing, the overlay is a preview through picked
surface points. Endpoint proximity joins successive drags only within 0.06 eye
proxy spans. A miss, a sample jump exceeding 0.12 spans, or a switch to another
connected mesh component splits the trace; separate strokes are not silently
bridged. Measuring any segment with a gap exceeding 0.15 spans fails explicitly.
Separate strokes report **partial length**, never a closed perimeter. All these
spans use the fitted experiment's recorded reconstruction eye proxy span.

**Undo last drag** restores the previous trace edit; **Remove last control**
trims its endpoint; **Clear active perimeter** clears that draft only. Geometry
edits reset review to Pending. **Close perimeter loop** explicitly adds the
closing surface path only when one continuous stroke has at least three controls
and its endpoints pass the gap check. The same button reopens a closed loop.
Review open arcs or completed loops after inspecting several views. Invalid
surface paths cannot be marked reviewed. Routes are visual overlays, not
depth-tested contact simulations. Several colors distinguish the mask styles;
**Show all perimeter drafts** compares them against the same fitted head.

Up to 20 drafts are retained per fit, with at most 20 strokes, 200 controls per
stroke and 500 controls per draft. Increase pixel spacing for longer traces.
These bounds keep interactive picking, rendering and surface routing manageable.
Pointer cancellation discards only the unfinished drag. Trace edits have a
20-step in-tab undo history; importing a saved draft resets that history.

Perimeters are included in **Download direct measurements** and in the calibrated
mesh's annotations. The measurements export includes per-draft surface lengths,
method, style, review status, stroke count and closure state; calibrated lengths
are added only when the existing tape calibration is valid. Perimeters never
change tape calibration. Reload validates their styles, control attachments,
resource limits and exact parent fit identity. Old direct-measurement files
without perimeter drafts remain supported. Drafts and calibration remain
isolated between component-count variants.

Verification uses analytic open/closed edge routes, gaps, disconnected surfaces,
review reset, transactional control limits and browser traces with explicit test
names. Browser checks cover fixed-view sampling, Alt rotation, style isolation,
undo, deliberately missed surfaces, export/reload, and fit isolation:

```sh
node --test scripts/tests/webcam_flame_perimeters.test.cjs
node scripts/tests/webcam_flame_perimeter_smoke.cjs PRIVATE_COMPARISON_DIRECTORY
```

### Undo shortcuts and smoother surface routes

Cmd+Z (or Ctrl+Z) invokes the same active-perimeter undo history as **Undo last
drag**. It also undoes trimming, closure, clearing and smoothing changes. During
an unfinished drag it cancels only the current preview; further pointer movement
is suppressed until release, preventing accidental rotation or commitment. Text
inputs, selects and editable text retain their native undo behavior. Shift+Z is
not handled as redo.

New perimeter drafts enable **Smooth surface route** by default. Instead of
forcing each sampled-control pair through mesh vertices, the algorithm finds a
local connected triangle strip, unfolds adjacent triangles across their shared
edges into a plane, and intersects the straight route with those edges in order.
Each resulting 3D segment lies within an actual triangle. This removes many of
the mesh-edge zigzags while preserving the original picked controls and keeping
length calculation on the surface. It does not change or cosmetically smooth the
FLAME head, fit a free-space spline, or smooth away intentional anatomical turns.

If a valid straight crossing of a local strip cannot be found, that pair retains
its mesh-edge path. The number of fallback pairs is displayed and exported,
along with the method and smoothing setting. Surface length is computed from
exactly the same polyline shown in the viewer. Gap and component checks still
apply; smoothing never joins separate strokes. Calibration's named-point routes have an independent smoothing setting, described below.

Older imported perimeter drafts without a smoothing field retain edge routing.
Enable the checkbox to recalculate them with triangle-interior routing. Changing
the route method resets review to Pending and is undoable. Existing raw control
attachments are preserved. Exports distinguish the routing methods so lengths
from different methods are not silently treated as identical measurements.

Analytic tests cover planar shortcuts and folded triangles where the correct
surface length differs from the 3D chord. Browser tests exercise Cmd+Z, Ctrl+Z,
native text undo, mid-drag cancellation, smoothing toggle undo, surface shortening
on the actual fitted mesh, and persistence of the routing setting.

### Mirror a half arc

**Mirror half to opposite side** creates a new open perimeter draft containing
the reflected half. **Build mirrored full perimeter** creates another new draft
joining the original half and the reversed reflected half as one closed loop.
The original source draft remains unchanged. The generated copy starts Pending,
retains the source style and route method, can be trimmed or extended, and has
its own undo history. Cmd+Z immediately after generation clears the copy's trace
without clearing the source half.

Draw an open half entirely on one side, starting near the model midline at the
nose and ending near the midline at the chin or neck. Full-loop generation
requires exactly one continuous stroke with at least three controls and both
endpoints within 0.08 of the recorded eye proxy span from the mirror plane.
A half that significantly spans both sides, has gaps, or exceeds existing
control limits fails explicitly instead of generating a purported complete loop.
Use the open-copy action when the endpoints are intentionally away from midline.

The plane is model X=0 transformed by the selected fit's recorded FLAME rotation
and translation. It is the model's nominal symmetry plane, not the viewer's
screen center or a separately reviewed anatomical midsagittal plane. Reflected
world points are projected to nearest triangle surfaces on the opposite side
and within the original connected mesh component. This prevents an off-surface
reflection or a jump to an eyeball component. Projection offsets exceeding 0.08
eye proxy spans fail. Off-midline controls require an opposite-side projection with a 0.005-span
plane tolerance. Controls initially within that tolerance use the nearest
surface in their component. The full loop retains both halves' actual endpoint attachments;
small joins near midline use the same checked surface routing as other controls.

Each derived draft records source perimeter ID/name, reflection plane, method,
projection maximum/mean distances and symmetry-assumption status under
`mirror_provenance`. Those records and the generated surface attachments persist
through the direct-measurement export/reload. Lengths are calculated on the
projected fitted surface; they are not assumed to equal twice the original
half's length on an asymmetric fit. Inspect both sides before marking the draft
Reviewed. Inferred symmetry is an editing aid, not an independent measurement.

Tests cover exact symmetric reflection, closed-loop joining, rotated/translated
model frames, source preservation, explicit failures for wrong-side/midline or
projection coverage, and generation/export using an automated half arc drawn on
the actual saved fitted surface. These interaction fixtures are not participant
perimeter reviews.


Mirror operation v2 ignores an 0.08-eye-span band when classifying a stroke as
one-sided. Small endpoint overshoots across the nominal model midline therefore
do not invalidate a cheek-side half arc. Controls extending substantially beyond
that band on both sides are still rejected, as are centerline-only arcs whose
mirror would overlap. Full-loop endpoint tolerance uses the same 0.08-span band;
the existing surface-gap and projection-distance checks remain in place.

Mirror feedback is displayed immediately beside the two action buttons, with a
visible busy message before computation and a success or error message afterward.
The buttons are disabled during computation; changing fit/perimeter selection
before it starts aborts without changing the source. Successful feedback names
the newly selected draft. Failure scrolls the nearby message into view rather
than placing it below the perimeter notes. An optional private draft path passed
as the browser smoke test's second argument reproduces a participant-specific
half arc without committing its coordinates to the repository.


### Smooth bitragion calibration and named-point arcs

Expand **Routes, distances and tape calibration**, select the scale/check/custom
route, and enable **Smooth selected measurement arc**. New measurement drafts
start with smoothing enabled for all three routes. Older imported drafts retain
edge routing until explicitly changed, preserving their previous calibration.
Each route's choice is stored in optional `route_methods` settings and exported.

The original named controls, including subnasale or menton, are preserved exactly.
The algorithm starts with the original edge route as a surface corridor and
shortcuts bounded local windows by unfolding triangle strips. Only valid
triangle-interior crossings no longer than the replaced edge path are accepted;
remaining edges are explicit fallbacks. This removes edge zigzags on long arcs
without drawing an off-surface spline or altering the head. The displayed
polyline and measured polyline are identical, including fallback segments.

Changing the scale route method recalculates the tape scale from its new length.
The independent check uses its own selected method and never adjusts that scale.
All derived millimeter lengths and calibrated camera translations still receive
the same uniform factor. Exports record the route method in the scale/check
reports and include surface-shortcut and fallback counts. Smoothing does not
change anatomical point placements or their review status.

Tests cover planar shortening through a fixed named intermediate control,
calibration using the displayed route length, invalid method rejection, method
switching/reload and an optional private named-arc browser regression. No private
control coordinates are committed to tests.

### Style-specific arc fitting experiment

`python -m dimension_pipeline.flame_arc_experiments` accepts `--session`,
`--model`, `--seed` (the original fit directory), `--annotations` (an exported
direct-measurements draft), `--exclude-probe`, and a fresh `--out` directory.
It validates session, analysis mesh, model, topology and exact annotated seed
mesh identities. The saved FLAME lengths are never treated as measured truth.
Named tape-calibration arcs are not targets without independent tape readings.

Only complete closed style perimeters are used, avoiding duplicate evidence
from their source and mirrored halves. Pending perimeter definitions remain
explicitly exploratory. The original local JavaScript routing implementation
evaluates each guide, then fixed barycentric samples preserve its locations
across fitted FLAME meshes. No point review or calibration transfers.

Reconstruction targets use frozen nearest-triangle projections of the seed
samples onto the cropped analysis surface outside the unchanged nose exclusion.
Distance, normal compatibility, adjacent projection-length ratios and minimum
contiguous-run checks reject unsupported samples and gaps. At least 20% of
edges must survive to use a partial length target; only 98% support is labeled
full. The report retains edge indices and coverage, never extrapolating a
partial target into a full perimeter measurement. Samples use 0.025 eye-span
spacing and the reported lengths sum sample chords, not exact geodesics.

Four trials share initialization, 100 components, 40 iterations, coefficient
bounds and shape prior: baseline, up to 4× importance near supported arc samples,
and the same importance plus relative squared arc-length penalties of 0.01 or
0.05. Arc gradients affect shape coefficients and similarity scale. Region
weights remain fixed from the seed. Loss normalization and policy thresholds
are recorded in the report, along with hashes and geometric checks.

The private comparison shows read-only guide overlays, per-style coverage,
supported length errors, regional surface residuals and overall surface metrics.
These measure agreement with the fitting reconstruction, not independent anatomy.
Inspect global tradeoffs and the excluded nose before selecting a candidate.
Unsupported lower jaw, neck and ears remain dominated by the FLAME prior.

### Diagnose arc coverage before expanding the fitting target

Run `python -m dimension_pipeline.flame_arc_coverage --fit <arc-trial-directory>
--seed <annotated-original-fit-directory> --session <source-session-directory>
--out <fresh-private-directory>` to create `coverage.html` and `report.json`.
This reuses the exact annotated seed mesh and fixed barycentric guide samples;
it does not rerun fitting, change measurements or loosen support thresholds.
Session/analysis and seed identities are checked, and cropped support must match
the original experiment (at most one edge may change at a float32 PLY boundary).

The comparison uses the original cropped target and the broader bounded analysis
mesh after the same conservative nose-triangle exclusion. The latter removes
the face-oval/frontal-visibility filters, not the original capture segmentation.
It is not the full dense reconstruction and may still lack neck geometry.

Each edge retains all failed checks: exclusion, endpoint distance, endpoint
normal compatibility, negligible source step, projected-step shrink/stretch,
and minimum contiguous-run support. Exclusive primary colors follow that order;
the JSON records overlapping flags, distances, normals and projected locations.
The unchanged `supported_edges` implementation determines accepted edges.

Shared rotation, zoom and view presets show reasons on both the original FLAME
and the selected target. Hover reports individual edge flags. A second color
mode distinguishes recovered, lost, supported-on-both and rejected-on-both
edges. Overlays are not depth-tested and retain the original FLAME positions.
Coverage counts sampled edges, not surface area or anatomical accuracy. Changes
in nearest surfaces can lose support even when the target mesh is expanded.

Tests verify rejection precedence without dropping overlapping flags, exact
agreement with the fitting support policy, short-run and exclusion behavior,
conservative triangle removal, output isolation, view controls, hover details,
report downloads and absence of browser network requests.

### Isolated upper-neck mask trial

`python -m dimension_pipeline.webcam_neck_masks --source <approved-session>
--root <private-session-root> --model <cached-selfie-multiclass-model>` prepares
new capture masks from the same 61 source PNGs. It verifies the pinned model
and source image/mask hashes, copies images (no hard links), preserves every
original approved foreground pixel, and adds only category-2 body-skin within
the original head bounding-box width, from 40% of its height down to 15% below
its bottom. Added components must connect to the original mask. This is a
bounded proposal, not a semantic neck guarantee; hands, collars and boundaries
still require review. A green/orange contact sheet shows original/added pixels.

The fresh session has no reconstruction, calibration, annotations or inherited
mask approvals. Its provenance records source hashes, ROI, policy and added
pixel counts. Resume it in the existing webcam pilot, review/correct every mask,
and use A to approve and advance. Bulk acceptance is disabled for this trial.
The UI counts only explicitly approved captures, reloads stored proposals for
editing, and blocks reconstruction until all are saved. The processor also
rejects submission if any stored mask is unapproved. Native MediaPipe image
preprocessing may require macOS graphics access even with the CPU delegate.

After review, reconstruct the separate session and compare under-jaw/neck
coverage using the broader analysis target. Reconstruction coordinates can
change between runs; comparisons need explicit registration, and FLAME points,
tape scale and acceptance decisions must be reviewed afresh.

### Compare a completed neck-mask reconstruction

`python -m dimension_pipeline.webcam_neck_compare --original <original-session>
--trial <reviewed-neck-session> --coverage <original-coverage-directory>
--seed <annotated-FLAME-ply> --fit <original-arc-experiment-directory>
--out <fresh-directory>` creates a read-only before/after `coverage.html`.
It verifies all 61 RGB images match pixel-for-pixel after PNG decoding and that
all trial masks are approved. The original seed and guide report hashes must
match the frozen coverage diagnostic.

A proper similarity fitted to all common registered turn-camera centers maps
the trial into original reconstruction units. At least 54 common views are
required; camera-center RMS above the arc-distance threshold rejects comparison.
Center residuals and orientation differences are reported. This alignment uses
neither surfaces nor arcs, but its uncertainty still affects coverage thresholds.
Both targets are broader bounded analysis meshes with the same original-world
nose exclusion. FLAME samples/normals and all support thresholds stay fixed.

Recovered/lost sections describe support against the fixed original FLAME fit,
not anatomical improvement or a new FLAME fit. Mesh decimation, reconstruction
changes and registration error can reduce support on an expanded-mask run.
Original captures, reconstructions, annotations and calibration remain separate.
