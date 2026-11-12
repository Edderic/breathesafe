# BRE-17 frozen-depth experiments

The bounded November 5 development experiment does not justify changing the raw
reconstruction defaults: two-view fusion, two geometric-consistency passes and
depth postprocessing disabled. All tested variants retain visible facial grain.
They remain read-only research artifacts, with no anatomical-accuracy claim.

## Running and inspecting

Resume a locally reconstructed session with 61 approved captures and select
**Run depth filtering experiments**. The frozen undistorted turn images, masks,
camera model and depth cache must still exist locally. A reconstruction imported
from an inspection-only ZIP may lack the cache; the processor fails explicitly
instead of inventing geometry or silently recomputing a different camera model.

The five fixed profiles are defined in `depth_quality_policy.json`, version
`webcam_depth_quality_v1`. The pinned CPU pipeline's fresh baseline now records
explicit defaults and quality-version provenance; its behavior is retained.

| Profile | Fusion views | Speckle flag | Added consistency passes |
| --- | --- | --- | --- |
| `fusion2` | 2 | 0 | 0 |
| `fusion3` | 3 | 0 | 0 |
| `fusion4` | 4 | 0 | 0 |
| `speckles` | 2 | 1: remove segments below 100 pixels | 0 |
| `extra_geom2` | 2 | 0 | 2 |

Each starts from identical frozen maps produced with two consistency passes.
`--geometric-iters 0` reuses those maps without further geometric refinement;
it does **not** mean that the source maps lacked consistency processing. The last
profile adds two passes to that same cache. It is an incremental experiment,
not an independently re-estimated four-iteration reconstruction. The speckle
size is verified from the effective native config. Depth gap filling, mesh hole
filling, geometry smoothing, spike removal, spurious-component removal, coordinate
normalization and ROI/tower additions are disabled throughout.

Native semantics were checked against the pinned [OpenMVS 2.4.0 CLI source](https://github.com/cdcseacave/openMVS/blob/v2.4.0/apps/DensifyPointCloud/DensifyPointCloud.cpp),
[cached-map processing](https://github.com/cdcseacave/openMVS/blob/v2.4.0/libs/MVS/SceneDensify.cpp)
and [depth defaults](https://github.com/cdcseacave/openMVS/blob/v2.4.0/libs/MVS/DepthMap.cpp).

Open **Compare full and analysis meshes**, then choose an experiment variant.
Filtered variants default to comparison with the original full reconstruction;
the reference selector can also use the original bounded analysis mesh. Both
panes share coordinates, fit, orientation, zoom and lighting. Annotations stay on
the original SVG analysis topology. No variant triangle indices, tape routes or
landmarks are transferred. Where calibration exists, the same raw uniform scale
is used for display; independent check arcs require new variant routes rather than
reusing old attachments. This development capture had no tape calibration/check.

## Persistence, inputs and failures

The processor runs one reconstruction/experiment job at a time. Cancel processing
terminates the active process group and preserves the raw session and finished
variants. On restart, unfinished experiment runs become interrupted. Each new run
has an immutable directory; earlier failures remain recorded. The checkpoint-resume
action validates prior parameters, tool hashes, original input hashes and saved
point-cloud hashes before reusing completed fusion output for meshing.

Only the 60 reconstruction slots are accepted. Turn-only COLMAP text is validated
and converted into an isolated model; the held-out frontal image is excluded from
all geometry/filtering inputs. Its existing camera/detections serve only the
post-reconstruction evaluation. Inputs are independent copies or APFS copy-on-write
clones, never hard links. Disposable depth copies are removed after fusion; the
original cache is retained. Source-file hashes are rechecked after the batch.

Session records preserve versioned settings, full input manifests, binary/tool
hashes, exact commands, effective config hashes, elapsed times, point counts,
meshes, metrics and failures. Original images/masks, cameras and geometry stay
unchanged. Variant artifacts and provenance round-trip in the versioned session
ZIP; large source depth caches are represented by hashes rather than bundled.
Export refuses changed artifact hashes. Inspection and checkpoint data remain
private under the ignored run directory, outside Vite/Rails file serving.

Initial instrumentation failures are retained: the neighbor-export CLI option
exits before densification when neighbors are absent, and generic trimesh cannot
read OpenMVS's per-point visibility lists. The corrected workflow counts the
native point header and recovered saved fusion checkpoints instead of rerunning
those completed jobs. Those failures are not filtering results.

## Defined screening metrics

All native metrics remain in reconstruction coordinates. The fixed scale reference
is the raw mesh's Y extent after transformation into the registered frontal camera,
including reconstruction boundary artifacts; it is not measured anatomical height.

Local-plane roughness uses 2,000 area-weighted surface samples (seed 17) and a
30,000-point area-weighted neighborhood cloud (seed 18). Neighborhood radius is
1.5% of that fixed raw extent, with at least 10 neighbors. The square root of the
smallest centered covariance eigenvalue is the local orthogonal plane RMS. The
report gives assessed count, mean/RMS/median/p95/maximum and values normalized by
the fixed extent. Curvature, density, coverage and genuine detail affect this
measure; lower residuals alone are not an improvement. Some neighborhoods lack
sufficient samples, and this one-capture test does not quantify metric uncertainty.

Displacement uses 5,000 area-weighted samples in each direction to nearest triangle
surfaces, with raw samples at seed 0 and variant samples at seed 1. The raw samples
are common across variants and the raw-reference viewer report. These are sampled
disagreements, not exact Hausdorff bounds or physical error.

Raw proximity is the fraction of raw samples within 1% of the fixed extent from
the candidate. It is a coverage/disagreement proxy, not proof of complete coverage:
moving a surface can reduce proximity without creating a hole. Nose/chin detector
proxies use neighborhoods of existing unvalidated raw predictions; lateral-head
proxies use image-side bands and do not establish tragion/ear anatomy. Provisional
gates flag low global/regional proximity. Finite empty/degenerate output and very
low point counts fail explicitly. Components, boundary edges and nonmanifold edges
are reported; exact hole counts are not inferred from open surfaces. No defects
are automatically repaired. Front/±35° views provide limited manual detail/coverage
inspection, not complete ear/underside or anatomical validation.

## Results and recommendations

The existing 20-second capture used 60/60 registered turn views. The recovered
two-view control full PLY is byte-for-byte identical to the original, confirming
the frozen-input/coordinate baseline. Defaults remain unchanged.

| Setting | Retained points | Faces | Roughness change vs control | Raw proximity | Cached-depth seconds | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 2 views, control | 1,337,106 | 532,359 | reference | 100.00% | 46.7 | Retain baseline |
| 3 views | 1,337,101 | 532,532 | +0.88% | 100.00% | 45.4 | Reject default change |
| 4 views | 1,257,236 | 523,043 | −0.26% | 93.74% | 44.9 | Reject default change |
| Remove 100-pixel speckles | 1,332,404 | 531,833 | +0.08% | 96.22% | 47.0 | Adjust / further test only |
| Two added consistency passes | 1,333,706 | 528,782 | −2.70% | 95.56% | 91.6 | Adjust / further test only |

Times include successful checkpoint creation plus resumed meshing/metrics. They
exclude the original shared SfM/depth-estimation run and initial neighbor-option
failures; they are not fresh reconstruction benchmarks. The raw pipeline originally
took about 208.9 seconds. The control's normalized local-plane RMS was 0.001680
of raw mesh height; 1,295 of 2,000 neighborhoods were assessed.

Three-view agreement removes only five points and does not visibly fix central
grain. Four-view agreement removes about 6% of points, with essentially unchanged
roughness and only 83.78% raw proximity in the chin proxy. Some neck/boundary shape
changes, but this cannot establish a physical improvement. Speckle removal reduces
connected face components from 291 to 275 while leaving central grain and boundary
artifacts. Extra passes reduce the roughness metric slightly at roughly twice the
cached-depth compute cost; substantial lower-edge triangles remain. Neither result
justifies automatic promotion. Fine eye/ear detail remains unresolved in all views.

| Setting | Connected face components | Boundary edges |
| --- | --- | --- |
| Control | 291 | 191 |
| 3 views | 316 | 180 |
| 4 views | 298 | 153 |
| Speckles | 275 | 141 |
| Added consistency passes | 276 | 146 |

Every variant is open and has zero counted nonmanifold edges. These topology
summaries do not establish complete ear/chin surfaces. No independent scan, tape
check or anatomical reference was available. Recommendations are bounded to this
capture and recorded separately from the immutable execution reports. No outputs
enter recommender training/scoring or ARKit records.

## Verification and private evidence

Python tests cover one-factor parameter propagation, zero hole filling, held-out
exclusion, low-roughness/lost-coverage fixtures, native visibility lists, checkpoint
reuse, process cancellation, single-job execution, interrupted recovery, variant
isolation and artifact-hashed export/reload. Browser tests exercise raw/analysis
reference switching, calibration and read-only full-resolution variant inspection.

The actual completed session was exported privately (942,083,559 bytes, within
the browser upload limit) and restored into an isolated temporary store. All five
variants, review records, original captures and base geometry matched, and a
restored full/raw comparison loaded successfully. The temporary reload store was
removed after verification; the original session remained intact.

Private evidence includes input manifests, failed attempts, point-cloud checkpoints,
full meshes, reports, review notes and front/side screenshots under
`.private-webcam-runs/`. No source capture or raw geometry was replaced.
