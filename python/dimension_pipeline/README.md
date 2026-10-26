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

1. Choose a head and enter your name. Use fixed views or drag in **Rotate** mode.
2. Choose a landmark, enter an optional placement note, and select **Place
   landmark**. Click its visible surface; switch views to inspect the same point.
3. Use **Undo last edit**, **Remove point**, or place again to correct it.
   **Save note** updates a note without moving the point.
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

The nasal midpoint, lateral mid-nose root, zygomatic edge, and ear-top orientation
remain provisional and are identified as such in the UI. Initial sidecars have
their own `annotation_version`, rather than pretending to be complete reference
records: no surface measurement route or approved anatomical labels are invented.
`ready_for_review` is a workflow status, not anatomical sign-off. Each derivative
is labeled independently in this first workflow; cross-variant propagation and
multi-reviewer adjudication remain future work.

Geometry/annotation checks:

```sh
node --test scripts/tests/dimension_fixture_geometry.test.cjs scripts/tests/face_annotation_geometry.test.cjs
PYTHONPATH=python python3 -m unittest discover -s python/dimension_pipeline/tests -v
```

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
operator; ear height needs an anatomical frame and a future height operator.
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
