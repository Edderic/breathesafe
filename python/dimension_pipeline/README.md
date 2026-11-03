# Camera dimension pipeline: measurement foundation (BRE-6)

This isolated experiment implements a versioned reference-geometry contract,
surface attachments, measurement extraction, analytic fixtures, and a small
synthetic head generation/rendering/annotation workflow. It does not train an
estimator or establish camera accuracy. No production
fit scoring or training code imports this package.

The [production proposal](https://www.breathesafe.xyz/reviews/masqfit-kanro-2026-10-981030707f76ec2a.html)
is the canonical research context (updated October 22, 2026), especially A and
B1/B2. The fetched HTML SHA-256 is
`0c8de909bec6ed8dda00a650eccbf564833c198eee0fe3894dff87883aa409ca`.
Local proposal drafts are not the source of truth.

## Run the foundation

From the repository root, with Python 3.10 or later:

```sh
PYTHONPATH=python python3 -m dimension_pipeline
PYTHONPATH=python python3 -m dimension_pipeline python/dimension_pipeline/fixtures/larger_m.json
PYTHONPATH=python python3 -m unittest discover -s python/dimension_pipeline/tests -v
```

Only the Python standard library is used, with no assets, model downloads, GPU,
network, or random sampling. The tiny smoke check takes well under one second
locally. The fixture manifest records seed 0 and deterministic construction; no
dependency installation is required. This is not the eventual BRE-9 image-to-report
command. It deliberately exercises geometry before asset selection.

## Visualize fixtures in Breathesafe

Run Rails and Vite as usual (`rails s` and `./bin/vite dev`), then open
`http://localhost:3000/#/research/dimension-fixtures`. The admin navigation also
links to **Fixture Viewer**. The page contains only project-owned analytic demo
geometry and does not require an admin account to view.

Choose a fixture, drag to rotate, scroll to zoom, or use the view buttons and
rotation sliders. Select a measurement to highlight its path and inspect its
definition and value. Landmark labels include the barycentric base midpoint.
The base overlay and a shared viewing scale make the global/local changes
visible. **Fit geometry** recenters and rescales the current view.

**Open fixture JSON** reads a reference record directly in the browser; it does
not upload or save the file. The page bundles the same three fixture JSON files
used by Python rather than separate copies. Display validation checks geometry,
units, attachments and measurement operators, but does not replace anatomical
review or dataset validation. The lightweight SVG viewer is intended for small
fixtures, with a 5 MB file limit and limits of 20,000 vertices/40,000 triangles.

Browser geometry checks:

```sh
node --test scripts/tests/dimension_fixture_geometry.test.cjs
```

## Generate heads, capture views, and annotate landmarks

For the next candidate generator, see [FLAME 2023 Open](FLAME_OPEN.md). Its local
adapter produces meshes that can be opened by the same labeling page; the
official model asset is required for actual FLAME evaluation. The
[interactive shape generator](FLAME_OPEN.md#interactive-shape-generator) lets
you combine all 300 shape parameters, save faces locally and open them directly
for annotation. Its page is `scripts/flame_face_generator.html`.

Generate five head variants, OBJ/JSON meshes, 35 fixed-view SVG images, a
camera/source manifest, and an HTML contact sheet with no network or GPU:

```sh
PYTHONPATH=python python3 -m dimension_pipeline.generate_heads --out /tmp/masqfit-heads
```

Choose a new output directory for each run; existing runs are never overwritten.
Keep run outputs outside Git. All five variants derive from one CC0 MakeHuman
template, with ears/jaw coverage and stable topology. See
[`assets/README.md`](assets/README.md) for the pinned source, asset license,
crop/nominal scale, control definitions, and known limitations. This is a bounded
pilot generator for annotation review; full BRE-7 realism/self-intersection gates
and BRE-8 perspective rendering/dataset validation remain subsequent work.

With Rails/Vite running, open `/#/research/face-landmarks`, also linked from the
fixture viewer. For a standalone preview without Rails or a database:

```sh
./node_modules/.bin/vite --config scripts/face_landmarks.vite.config.mjs
```

Open `http://127.0.0.1:5178/scripts/face_landmarks_preview.html`.

1. Choose a head and enter your name. Use fixed views or drag without Ctrl to rotate.
   **Open heads or annotations** can load up to ten compatible surface JSON files
   (including local FLAME adapter outputs) without external uploads. Selecting a
   single annotation export there automatically finds its exact matching loaded
   head and resumes it. Load the head first if it is not already available.
2. Choose a landmark, enter an optional placement note, and **Ctrl-click** its
   visible surface; switch views to inspect the same point. Unmodified clicks
   do not place points. Unmodified drags always rotate, with no mode switching.
   Ctrl-drags and gestures whose modifier changes mid-drag do not place points.
   The viewport suppresses macOS's Ctrl-click context menu while preserving the
   ordinary right-click menu. Enable **Tap to place (touch/pen)** for touch or
   pen taps; dragging still rotates. This checkbox does not affect mouse clicks.
   **[** selects the previous landmark, and **]** selects the next (wrapping
   through the list). They work across the page except while a form control or
   editable field has focus. Browser modifier shortcuts and held-key repeats
   are left alone. Arrow keys rotate when the geometry viewport has focus.
   The previous R/L mode shortcuts are superseded by modifier-based interaction.
3. Use **Undo last edit**, **Remove point**, or place again to correct it.
   **Save note** updates a note without moving the point.
   Choose one of the five **Measurements** to see its computed value and
   highlighted geometry. Mark its required points to calculate it automatically.
   Left/right results stay separate. Surface paths have a separate chord
   comparison; ear height shows a vertical drop and menton reference plane.
4. **Download annotations** for each edited head. **Resume annotations** loads
   a saved sidecar for the currently selected exact mesh. Drafts remain in memory
   between variant switches; export before leaving. Navigation warns about edits
   that have not been exported. There is no server upload or browser persistence.
5. **Download view sheet** exports seven fixed views in one PNG; camera metadata
   is available separately. Offline generation provides individual SVG captures.

Annotations store triangle indices/barycentric weights, annotator, timestamp,
placement view, notes, topology, source identity, nominal units, definition
version, and a SHA-256 fingerprint of the actual mesh/frame. Import rejects
different variants/geometry, unknown landmark names, invalid attachments, and
unsupported versions. Left/right always means the subject's side. Hidden markers
are suppressed using surface-depth checks; clicks attach to the nearest surface.

The nasal midpoint, lateral mid-nose root, zygion mapping, and ear-top orientation
remain provisional and are identified as such in the UI. Initial sidecars have
their own `annotation_version`, rather than pretending to be complete reference
records: candidate routes are computed explicitly, and anatomical approval is
not inferred from a successful calculation.
`ready_for_review` is a workflow status, not anatomical sign-off. Each derivative
is labeled independently in this first workflow; cross-variant propagation and
multi-reviewer adjudication remain future work.

The four surface measurement types use `cgal_continuous_v1`, which crosses
triangle interiors through the local solver. See [SURFACE_GEODESICS.md](SURFACE_GEODESICS.md)
for build/start commands, validation and the comparison on saved annotations.
The viewer retains `mesh_edge_dijkstra_v1` as an explicit comparison: a shortest path
along the triangle edge graph, connecting exact barycentric endpoints to their
own triangle vertices. Endpoints within one triangle use the direct on-surface
segment. Edge directions/resolution can overestimate the continuous geodesic;
the chosen route is not automatically a physical tape route. Missing endpoints
or disconnected components produce no distance. Model units do not establish
independent physical millimeter accuracy.

| Measurement | Annotated endpoints / construction |
| --- | --- |
| Nose protrusion | Pronasale–subnasale continuous surface length; the FFR-specific candidate, distinct from the traditional chord. |
| Mid-nose slope | Nasal midpoint–mid-nose root on each side, as a surface length in mm; both endpoint placement and route equivalence remain provisional. |
| Lateral zygomatic–gonion | Candidate zygion–gonion surface route on each side. |
| Ear height; top | Model +Y height from each upper-ear point to the plane through menton. The dashed drop and plane are constructions in space, not surface paths. |
| Gonion–menton | Continuous surface length from each gonion to midline menton. |

All seven surface pairs can be solved together. The two ear heights are computed
locally using `model_y_height_v1`; each export retains the up vector, plane
anchor, projected foot point and unreviewed alignment status. View rotation
changes only the display. Negative heights are rejected as invalid references
rather than silently taking their absolute values. Confirm anatomical head
alignment before treating model-Y ear heights as the published measure.

Annotation exports include all nine `derived_measurements` (including missing
statuses), with endpoint names, methods, surface paths or height constructions.
Surface results retain length, chord and reconstructable vertex/barycentric
path attachments. Import
recalculates these values from the landmarks and mesh rather than trusting
previously exported numbers. Published equivalence remains unverified: S1 row
14 describes a lateral cheekbone endpoint without explicitly naming zygion.
The candidate mapping is recorded in `target_registry.json` separately from the
source definition. Older `lateral_zygomatic_edge_left/right` labels are retained
as optional **Legacy cheekbone point** entries for review; they are never
silently renamed or used as zygion in the calculation.

To review repeated placements, load the matching head, then use **Compare
annotation sets → Load comparison files** to select the original and repeat
exports together. Up to 10 sets (5 MB per file, 20 MB per batch) are supported.
Selecting multiple annotation exports in the top **Open heads or annotations**
picker opens the same comparison overlay on the selected head. Selecting one
annotation export there resumes the editable draft. Load head meshes separately
from annotation exports.
Every file must match the selected head's record, topology, scale and exact mesh
fingerprint. An invalid batch adds no sets; duplicate landmark bundles are
skipped. Sets remain in memory per head until cleared or the page is closed.

The numbered colors identify each set. Choose a landmark with the selector or
`[` / `]`, toggle sets, and switch **Selected landmark only** off for context.
**Use placement view** restores a set's recorded yaw, tilt and zoom. Occluded
points are hidden by default; **Show points through the head** reveals them.
Dashed connectors and the pairwise table report straight-line 3D displacement,
not surface distance. Median and maximum use all pairs of checked sets that
contain the landmark, including placements currently hidden by the surface.
They measure agreement rather than anatomical correctness.

While the overlay is enabled, draft markers and measurement routes are hidden
and placement is disabled. Turn **Show comparison overlay** off to resume
editing the existing draft. Loading, toggling and removing comparison sets
never imports them into the draft, its undo history or annotation exports.

Geometry/annotation checks:

```sh
node --test scripts/tests/dimension_fixture_geometry.test.cjs scripts/tests/face_annotation_geometry.test.cjs scripts/tests/face_surface_paths.test.cjs scripts/tests/face_continuous_paths.test.cjs scripts/tests/face_annotation_comparison.test.cjs
PYTHONPATH=python python3 -m unittest discover -s python/dimension_pipeline/tests -v
```

## MediaPipe image-to-surface pilot

Install the local experiment assets once (requires internet for the versioned
Google model; subsequent inference stays local):

```sh
node scripts/setup_face_landmarker.cjs
./node_modules/.bin/vite --config scripts/face_landmarks.vite.config.mjs
```

Open `scripts/face_landmarks_preview.html` with the desired head, then select
**MediaPipe experiment**. The workspace preserves your editable draft and has
no annotation-writing actions. It uses the same untextured, faceted shading,
720 × 480 orthographic image geometry, and seven presets as the viewer. Choose
**Run selected view** or **Run all seven views**. Capture framing is shared
across that head's views; rotating/zooming the inspection pane does not change
inference images or calculated distances. All seven attempts remain visible,
including no-detection, failed, and cancelled captures. A new run replaces the
previous run; download results before starting another run you want to retain.

The pinned model is Google's float16 Face Landmarker bundle, version 1:
<https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task>.
Its SHA-256 is
`64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff`.
Setup checks that digest and copies the installed SDK (currently 0.10.18) and
matching WASM files into Git-ignored `public/mediapipe/experiment/`. The worker
checks every asset against its manifest before initialization. Existing webcam
recommendation flows and their model URL are unchanged.

Inference uses CPU delegation in IMAGE mode, one face, detection/presence
thresholds 0.5, no blendshapes or transformation matrices, and a classic worker
because this SDK loads WASM glue through `importScripts`. WebGL 2 is still
required for MediaPipe's image preprocessing, even with CPU inference. Missing
assets and unavailable WebGL produce explicit setup errors. Initialization and
per-image requests time out, Cancel terminates the worker, and changing heads
invalidates stale work. The experiment records SDK/model/runtime hashes,
configuration, browser user agent, camera, renderer version and capture checksum.

Click a dot in the 2D image or enter its MediaPipe index to highlight the same
point in 3D. Each normalized `(x, y)` is converted to capture coordinates and
intersected with the nearest visible triangle, retaining its barycentric
attachment. MediaPipe `z` is retained for inspection but never interpreted as
model millimeters. Invalid/out-of-image coordinates and missed rays remain
statuses; there is no snapping fallback. Successful ray hits do not establish
anatomical correspondence: far-side inferred features can intersect the wrong
visible facial surface.

Candidate correspondences start empty. Select a named research landmark and
assign an index only after inspecting it. Unmap unsupported landmarks rather
than substituting nearby points, especially for ears. Mapping files can be
exported and reused across faces. Load exact-mesh annotation exports as manual
references; the current draft and existing comparison sets are also available.
References stay separate, can be toggled, and are never averaged or declared
ground truth. The selected reference is purple in the 3D pane. Per-view comparison
rows show Euclidean model-mm displacement only when the manual reference is
visible in that capture; otherwise they explicitly report occlusion, missing
reference, detection failure, or projection failure. Summary statistics describe
pairwise displacement across successful views of each raw index, not anatomical
accuracy or independent repeats. Repeated inference of identical images is not
used to estimate variation.

**Download experiment JSON** retains mesh fingerprint, all raw predictions,
projection statuses/attachments, candidate mappings, reference snapshots,
per-index coverage/dispersion summaries and per-reference comparisons. Its
`experiment_version` is `1.1.0`, separate from annotation exports; the loader also accepts earlier `1.0.0` raw pilot reports. Reload rejects
other meshes/unsupported cameras, recomputes projections and errors, and does
not trust exported derived points or distances. Individual original PNGs can be
downloaded for every captured view. Reload regenerates only images whose PNG
checksum matches the original; when rasterization differs, **Restore original
PNG** accepts the previously exported capture only after verifying its checksum
and dimensions. Keep PNGs with the experiment JSON for reproducible inspection.

### Experimental view-dependent filtering

The workspace defaults to **Conservative view filter**. It keeps a raw ray-hit
status separate from an observation-acceptance status. A ray can hit the mesh
while the associated observation is rejected. Select **Raw baseline (no
filtering)** to compare the identical predictions with the filter disabled;
changing this selection never reruns MediaPipe or alters raw coordinates or
attachments. **Show excluded predictions in gray** reveals removed predictions
in both panes, independently of **Show points through head**, which remains a
display-only depth toggle.

The fixed v1 policy uses capture cameras (not the rotatable inspection pane):

- Absolute yaw at most 15 degrees and tilt at most 20 degrees: keep successful
  projections on both sides and the central region.
- Absolute yaw greater than 15 and at most 60 degrees, with tilt at most 20:
  keep only the subject's near-side region. Negative yaw exposes subject left;
  positive yaw exposes subject right. Exclude opposite-side observations as
  `far_side` and central observations as `central_requires_frontal`.
- Tilt over 20 degrees or yaw over 60 degrees: exclude as `tilt_outside_policy`
  or `yaw_outside_policy`. Unknown indices are excluded. Invalid coordinates
  and missed rays remain geometry failures, never accepted observations.

Index regions are derived from the MediaPipe v0.10.18 canonical face model,
with a central band of 6% of its maximum absolute X coordinate. The bundled
`assets/mediapipe_regions.json` records its pinned source URL, SHA-256,
Apache-2.0 attribution, side convention, and the iris-region extension. Eye
indices 33 (right) and 263 (left) anchor the convention. The rule never reads
manual placements, predicted image X, MediaPipe depth or the projected point's
position to infer side. This is a region/view heuristic, not an occlusion mask.
For example, index 423 belongs to the left region and remains accepted in a
left-oblique view even if that particular prediction is inaccurate.

The selected-index summary reports accepted coverage and dispersion beside the
raw baseline. Rejected observations do not contribute to accepted summaries,
and one accepted view yields no pairwise estimate. Reducing the number of
observations can reduce dispersion without improving anatomical accuracy. The
manual comparison table likewise shows filtered status/error and raw-baseline
status/error together. Manual-reference visibility still determines evaluation
eligibility only; it never determines which predictions the filter accepts.
No predictions are averaged, moved, triangulated or fused by this policy.

Exports retain the filter configuration/canonical-source hash, raw detections,
geometry attachments, per-observation region/status/rejection reason, both
summary baselines and both manual comparison tables. Reload recomputes these
from raw detections and rejects modified or unknown filter policies. Earlier
reports without filter metadata reopen in raw-baseline mode so filtering is
not silently applied to old results. Select the conservative mode explicitly
to experiment on those same captures.

The pilot deliberately adds no photorealistic textures, automated head batches,
view fusion, consensus ground truth or anatomical measurement-error estimates.
A poor detection rate on current shading is an experiment result, not a reason
to invent landmarks. Rendering improvements can be assessed in a later protocol.

## Reference schema 1.0.0

`geometry.validate_reference` is the executable validator. JSON fixtures are
examples; this table defines the record contract. Unsupported schema versions,
unknown length units, invalid references, nonfinite coordinates, degenerate
triangles, and ambiguous measurement kinds fail validation.

| Field | Meaning |
| --- | --- |
| `schema_version` | Exact supported format version, currently `1.0.0`. |
| `record_id`, `topology_id` | Stable record and topology identifiers. A vertex index is meaningful only within its topology. |
| `units` | `mm` or `m`; applies to every mesh coordinate. Output lengths are always millimeters. Pixels, canonical units, and normalized detector coordinates are not accepted as metric reference geometry. |
| `coordinate_frame` | Right handed; +x subject left, +y superior, +z anterior. Importers must explicitly convert other conventions first. |
| `source` | Root `identity_id`, `asset_id`, `license`, `provenance`, `domain` (`analytic`, `synthetic`, `printed`, `human`), and ordered `parent_record_ids`. |
| `mesh` | Finite 3D `vertices` and nondegenerate indexed `triangles`. This format represents a triangular surface, not a requirement for watertight printable geometry. |
| `landmarks` | Named vertex attachments (`vertex_index`) or barycentric surface attachments (`triangle_index`, three nonnegative `weights` summing to 1). These names require a reviewed anatomical atlas before use on people. |
| `measurements` | Unique `id`, `kind`, ordered `landmarks`, `role`, `definition`, and `definition_status`. Roles: `target`, `scale_anchor`, `diagnostic`. Statuses: `analytic_only`, `pending_review`, `reviewed`. |
| `camera` | `null` for reference-only geometry. An optional metadata object is reserved for BRE-8; its projection, intrinsics, distortion, and extrinsics contract is not implemented or validated yet. Do not use that object for projection until BRE-8 defines it. |
| `review` | `pending` or `approved`; approved records must name a `reviewer`. Fixture records remain pending and are never approved for anatomical use. |

Lineage is recorded, but this validator does not resolve a dataset-wide lineage
graph or enforce train/test splits. The future dataset stage must check missing
parents/cycles and group all descendants, prints and captures of a root identity
in the same partition. All three current fixtures share one root: they cannot
serve as independent train/test identities.

Measurement operators are deliberately separate:

* `straight_distance`: Euclidean chord between exactly two landmarks.
* `surface_polyline`: sum of ordered short chords on the triangular surface.
  Every consecutive attachment pair must lie on a common triangle. This is an
  explicitly chosen mesh route, not an inferred smooth arc or shortest geodesic.
  A physical tape route needs independent correspondence validation.
* `angle`: unsigned interior 3D angle at the middle of exactly three points,
  exported in degrees. This generic operator does not define any published slope.

Exports include schema/measurement versions, `model_version: null`, source
provenance, label origin, unit, role, and separate geometry/anatomical validity.
`valid_geometry` means the calculation is defined; it says nothing about image
accuracy, anatomical semantics, source asset suitability, or physical validation.

## Fixtures and analytical expectations

The project-owned tent mesh has five vertices and three triangles. It represents
a mathematical local nasal ridge and an independent lower span; it is not an
anatomically plausible face or a licensed human scan.

| Fixture | Local tip-to-base midpoint | Independent lower span | Ridge polyline | Ridge chord |
| --- | --- | --- | --- | --- |
| `base_mm.json` | 4 mm | 12 mm | 10 mm | 6 mm |
| `larger_m.json` | 6 mm | 18 mm | 15 mm | 9 mm |
| `local_nose_mm.json` | 6 mm | 12 mm | 2√45 mm | 6 mm |

The larger fixture is a uniform 1.5× transform, stored in meters. The local
variant changes only tip height, preserving the independent span and base chord.
Tests additionally apply proper rotation/translation and verify angle invariance
under scale. Expected values are recorded in the manifest from these formulas.
The analytic ridge anchor is **not** a bitragion–subnasale arc and is not a
validated alternative for physical calibration.

## Target atlas and remaining review

`target_registry.json` records two provisional physical pilot targets (a locally
defined pronasale–subnasale chord and a sellion–menton chord), all five Yu 2024
compact candidates, the distinct Yu/Griffin 2026 lateral nose slope, objective
bridge height, and the proposed bitragion–subnasale tape arc. The pilot nasal
chord has the endpoint/operator construct of traditional nose protrusion (S2
row 15); anatomical equivalence still requires reviewed landmark placement.

[Yu et al. (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10941723/)
points to supplementary S1/S2 for measurement definitions. On October 24, 2026,
the user supplied `wxae005_suppl_supplementary_appendix.pdf`, resolving the earlier
download blocker. Its SHA-256 is
`f2418d004eefe05e8726647268adc275eb39cc7eec665f96669ec5436b8ff60f`.
S1/S2 were text-extracted and visually checked on PDF pages 2/3. The registry
records source rows and paraphrased definitions; the publisher PDF is not copied
into the repository.

| Compact candidate | Retrieved construction (S1, PDF page 2) |
| --- | --- |
| Mid-nose slope, row 9 | Surface length joining nasal midpoint and mid-nose root; not an angle or ratio. |
| Nose protrusion, row 11 | Surface length between pronasale and subnasale; distinct from the traditional straight chord in S2 row 15. |
| Lateral zygomatic–gonion length, row 14 | Surface length joining the lateral zygomatic boundary to gonion. |
| Gonion–menton length, row 16 | Surface length joining gonion to menton. |
| Ear height–top, row 7 | Vertical separation of the upper ear boundary from a horizontal plane through menton; not an ear-to-chin chord. |

All five are lengths, represented in mm in the registry. S3 groups the first
four as surface measures and ear height as linear; the main article explicitly
discusses mid-nose slope and ear height-top increments in mm. S1/S3 themselves
have no unit column. These semantic kinds are not new executable operators:
surface lengths need reviewed routes for the existing `surface_polyline`
operator; ear height has a provisional model-Y operator and still needs an
approved anatomical frame.
The supplement does not supply a complete annotation atlas, side/aggregation
convention, intermediate surface route, or operational head-orientation protocol.
In particular, nasal midpoint/root must not silently be replaced by sellion or
other familiar landmarks. Visibility requirements remain recorded per feature;
ear/jaw coverage cannot be assumed on frontal-only meshes. The 2026 lateral
nose slope and objective bridge-height definitions remain separately blocked.

S2 row 18 (PDF page 3) confirms the proposed tape arc's surface construction
from left tragion via subnasale to right tragion. Its intermediate contact route,
side-view acquisition, ear coverage,
annotation rules, and repeated/self-versus-assisted measurement protocol still
need review and validation. No physical alternative anchor has been validated.
Scaling a reconstruction to match the entered arc cannot validate that same arc;
assess independently measured dimensions and independently scaled references.

Before annotating or rendering anatomical faces, a human reviewer must sign off
the target definitions, landmark placements, and tape contact route. Keep BRE-6
open until that review and remaining operational definition blockers are resolved. The mathematical
fixture work can proceed without pretending that review has occurred.

## Legacy ARKit comparison

`legacy_arkit_paths.json` snapshots the current Python/Rails segment keys. The
four scoring paths have 46 segments across 46 distinct vertex IDs. `strap` is a
separate legacy aggregate. The existing Python helper sums available entries;
Rails returns null for incomplete aggregates. A future adapter must preserve
missingness explicitly and avoid treating a partial sum as a complete path.

These aggregates are sums of short chords. They are not automatically physical
tape surface arcs, bridge heights, or slope measures. The Rails output names
declare millimeters; source capture units still require an independent check.
There is no cross-topology ARKit mapping in this fixture. That requires measured
registration and surface/barycentric attachments with correspondence error, not
renumbering another mesh to match ARKit. Compatibility accuracy remains untested.

## Inputs and label separation

| Stage | Allowed data |
| --- | --- |
| Reference labeling/training/evaluation | Source meshes, physical reference measurements, attachments, camera metadata, identity/lineage and derived labels. |
| Future deployed estimator | Unmarked RGB capture and optional independently entered, validated tape measurement; no reference mesh, target labels, source identity, or known camera extrinsics. |
| Evaluation partitioning | Root identity and lineage metadata for separation; never estimator features. |

Keep analytic, rendered, printed and human evidence separate. No synthetic shape
or derivative inherits a person's respirator fit outcome. Next work is operational
landmark/route review and anatomical target approval, followed by BRE-7/BRE-8 assets
and labeled rendering, and BRE-9's small end-to-end experiment.
