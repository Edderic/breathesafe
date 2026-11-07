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
apply; smoothing never joins separate strokes. Calibration's named-point routes
continue to use their existing mesh-edge method.

Older imported perimeter drafts without a smoothing field retain edge routing.
Enable the checkbox to recalculate them with triangle-interior routing. Changing
the route method resets review to Pending and is undoable. Existing raw control
attachments are preserved. Exports distinguish the routing methods so lengths
from different methods are not silently treated as identical measurements.

Analytic tests cover planar shortcuts and folded triangles where the correct
surface length differs from the 3D chord. Browser tests exercise Cmd+Z, Ctrl+Z,
native text undo, mid-drag cancellation, smoothing toggle undo, surface shortening
on the actual fitted mesh, and persistence of the routing setting.
