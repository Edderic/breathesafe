# Camera dimension pipeline: measurement foundation (BRE-6)

This isolated experiment implements a versioned reference-geometry contract,
surface attachments, measurement extraction, and analytic fixtures. It does not
yet render faces, train an estimator, or establish camera accuracy. No production
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
bridge height, and the proposed bitragion–subnasale tape arc. No pilot label is
claimed to reproduce a published nasal construct.

[Yu et al. (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10941723/)
points to supplementary S1/S2 for measurement definitions. The supplementary PDF
was located, but on October 22 the browser fetch returned HTTP 403 and curl
returned an HTML challenge instead of a PDF. Consequently the five published
features remain blocked by definition. Their units/operators are unset rather
than guessed from a name or figure. Visibility requirements are recorded per
feature; ear/jaw landmarks cannot be assumed available on frontal-only meshes.

The proposed tape arc runs from left tragion via subnasale to right tragion along
the face. Its intermediate contact route, side-view acquisition, ear coverage,
annotation rules, and repeated/self-versus-assisted measurement protocol still
need review and validation. No physical alternative anchor has been validated.
Scaling a reconstruction to match the entered arc cannot validate that same arc;
assess independently measured dimensions and independently scaled references.

Before annotating or rendering anatomical faces, a human reviewer must sign off
the target definitions, landmark placements, and tape contact route. Keep BRE-6
open until that review and the definition blockers are resolved. The mathematical
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
or derivative inherits a person's respirator fit outcome. Next work is source
definition review and anatomical target approval, followed by BRE-7/BRE-8 assets
and labeled rendering, and BRE-9's small end-to-end experiment.
