# FLAME 2023 Open evaluation and viewer adapter

## Interactive shape generator

Run the local preview server and generator service in separate terminals from
the repository root (NumPy is required; see `requirements-flame.txt`):

```sh
./node_modules/.bin/vite --config scripts/face_landmarks.vite.config.mjs
PYTHONPATH=python python3 -m dimension_pipeline.flame_playground \
  --model ~/Downloads/FLAME2023Open.zip --source-units m
```

Open <http://127.0.0.1:5178/scripts/flame_face_generator.html>. All 300 identity
shape coefficients can be combined using sliders or numeric fields, in pages
of 20. The coefficient range is −2 to +2, not a guarantee of plausible shape
or population coverage. Expression and all articulated poses remain zero.
Previews are debounced, superseded replies cannot replace newer settings, and
the camera stays fixed as shape changes. Drag/arrow keys rotate and scroll
zooms. Invalid values leave the last successful preview visible and disable
saving; reset individual components or all components to return toward neutral.

Give the face a name and choose **Save face to library**. Saved runs live in
`tmp/flame-face-library/<record_id>/` and contain:

- `face.json`: millimeter mesh, all 300 coefficients, model/archive hashes,
  source-unit and axis choices, friendly name, and pending review status.
- `manifest.json`: a single-head run accepted by `face_landmarks_preview.html`.
- `metadata.json`: library entry, parameters, geometry report and viewer link.

**Open for annotation** loads the saved mesh directly into the existing viewer.
**Download face JSON** also allows manual import through its top file picker.
The generator's **Edit parameters** and file restore controls regenerate the
shape from the local model. A changed vector saves a new record with a new
identity; an identical vector reuses the existing saved face without overwriting
its name, geometry or annotation compatibility. Saving the same settings after
a service restart is deterministic. The saved manifests remain usable while the
generator service is stopped, provided the Vite preview server is running.

The API binds only to `127.0.0.1:5181`; writes require JSON and the exact local
preview origin. It accepts parameter vectors, never uploaded pickle files or
output paths. `--model`, `--source-units`, optional `--source-x`, and `--library`
are explicit service-start settings. Libraries must live under the repository's
`tmp/` directory with URL-safe names. Model weights are not sent to the browser
or copied into saved runs. Library files are local and Git-ignored; keep a copy
elsewhere before clearing `tmp/`.

Degenerate triangles reject a preview. Normal reversals relative to neutral are
shown as conservative review flags. The playground permits saving flagged
faces for review, retaining the report in both the mesh record and library
metadata with review status pending. The batch pilot still rejects flagged
runs. These flags do not establish intersections; self-intersections and
anatomical quality still require review. Full poses,
semantic nose/jaw controls, demographic/child labels and population sampling are
not implemented by this shape-only playground.

Status, October 25, 2026: the supplied official ZIP was inspected and its actual
model was loaded, rendered, and exercised in the existing viewer. The bounded
pilot can proceed to manual landmark review. Anatomical sign-off, physical
metric validation and comparison with the complete articulated runtime remain
pending. The separate toy-geometry tests are not counted as FLAME evidence.

## First actual model evaluation

Archive SHA-256:
`a6b4c3dc15d569d98136a1e548b6fe532eb2830ca12a4f0d4b3a5dba8ee87a91`.

`flame2023_Open.pkl` SHA-256:
`e75a0990728ba038c7da2a420ae4396f7ddd7781366c13026066c5b24f127623`.

The archive's `FLAME2023_Open Readme.pdf` identifies an attribution 4.0 license
and refers to the official terms. It does not document units or axes. The run
explicitly assumes source meters and y-up/z-anterior/x-subject-left. Extents
are plausible and front/profile orientation looks correct; these observations
are not independent unit/side verification or physical calibration.

The model contains 5,023 vertices and 9,976 triangles: a 3,931-vertex head/neck
component and two 546-vertex eye components. There are 62 boundary edges and
zero nonmanifold edges; it is not a watertight print-ready solid. Five-joint
skinning weights sum to one within 2.3e-16, consistent with the neutral-pose
shape equation, but the independent runtime comparison remains open.

| Pilot shape | RMS vertex change from neutral | Degenerate triangles | Normal reversal flags |
| --- | --- | --- | --- |
| Neutral | 0 mm | 0 | 0 |
| PC1 -0.5 / +0.5 | 1.908 mm each | 0 | 0 |
| PC2 -0.5 / +0.5 | 1.053 mm each | 0 | 0 |

At magnitude 1, PC1 -1, PC1 +1 and PC2 +1 each trigger one normal reversal flag
near an ear. PC2 -1 has none. The pattern persists at 0.75; at 0.5 and 0.25 all
four pass. A normal turning over 90 degrees relative to neutral is a conservative
review flag, not proof of self-intersection or topological inversion. The report
key `flipped_triangles_vs_neutral` counts those flags. Flagged runs remain
rejected; the accepted pilot records magnitude 0.5 explicitly.

Inspection of all seven neutral views and front/profile views of the variants
finds nose, ears, jaw, chin and under-chin surfaces available for exploratory
annotation. Exact tragion/gonion placement and extra nasal points still need
review. Ear and jaw regions have relatively coarse facets. PC1/PC2 change broad
shape, not isolated nasal geometry at fixed perimeter.

Actual FLAME browser checks passed: five imports, shared framing, surface
placement, annotation round trip, cross-shape rejection, seven-view PNG export
and mobile layout. Local run artifacts are in Git-ignored `tmp/flame-open-pilot/`,
with a separate `review.json` recording this inspection. Automated click-test
annotations are not anatomical labels and are not included in that directory.
Original weights and generated meshes are not committed or bundled in the app.

With the standalone Vite preview running, open this local link to load all five
saved pilot heads automatically:
`http://127.0.0.1:5178/scripts/face_landmarks_preview.html?heads=/tmp/flame-open-pilot/manifest.json`.
This preview-only option reads explicitly requested local run files, without
uploading them or embedding weights in the application.

## Source and scope

Official project: https://flame.is.tue.mpg.de/

Exact Open release download:
https://download.is.tue.mpg.de/download.php?domain=flame&sfile=FLAME2023Open.zip

Exact release terms: https://flame.is.tue.mpg.de/modellicense.html

The site distinguishes FLAME 2023 Open from FLAME 2017/2019/2020/2023. Its Open
section identifies an attribution license and permits commercial adaptation;
retain the complete accompanying terms and attribution for the actual download.
This decision does not cover separate textures, scan datasets, model-fitting
code, or older model releases. None of those are downloaded or bundled here.

Attribution: Li, Bolkart, Black, Li and Romero, *Learning a model of facial shape
and expression from 4D scans*, ACM TOG / SIGGRAPH Asia 2017,
DOI https://doi.org/10.1145/3130800.3130813.

The proposal calls for correlated facial variation rather than unrestricted
stretching. FLAME's learned shape basis is a stronger candidate for that goal
than the current one-template MakeHuman perturbation pilot. This remains a
candidate selection, not a finding of sufficient anatomical diversity or metric
accuracy. The initial mean/PC1/PC2 experiment samples a tiny part of its space.

## Run locally

Install the isolated optional dependency with Python 3.11–3.13 (the pinned NumPy
version does not supply Python 3.14 wheels):

```sh
python3.11 -m venv /tmp/masqfit-flame-env
/tmp/masqfit-flame-env/bin/pip install -r python/dimension_pipeline/requirements-flame.txt
```

Download the official Open ZIP through your account. Keep it outside the public
repository. Use a new output directory:

```sh
PYTHONPATH=python /tmp/masqfit-flame-env/bin/python -m dimension_pipeline.flame_open \
  --model ~/Downloads/FLAME2023Open.zip \
  --source-units m \
  --coefficient 0.5 \
  --out /tmp/masqfit-flame-open-pilot
```

`--source-units` must match the supplied model's documentation. The example uses
meters; that assumption must be confirmed against the actual release. The
adapter checks the resulting head extent and never rescales to an average head.
It assumes source y superior and z anterior, and defaults to x subject-left.
`--source-x subject_right` reflects x and reverses triangle winding if required
by the actual source coordinate convention. Confirm axes visually before
accepting annotations; bbox plausibility is not coordinate-system validation.

The ZIP is read without extracting arbitrary paths. It must contain one
`flame2023_Open.pkl`; that exact basename can also be provided directly.
Older-release filenames are rejected. Pickle globals are restricted to supported
NumPy array construction and inert placeholders for unused sparse joint arrays.
Unsupported Chumpy/custom serialized objects fail explicitly; no automatic
fallback to other model assets occurs.

## What the first adapter evaluates

For neutral expression and zero joint/global pose, compute
`vertices = template + sum(shape_direction[i] * coefficient[i])` using the first
300 shape directions. The five outputs are neutral, coefficient 1 at
-magnitude/+magnitude, and coefficient 2 at -magnitude/+magnitude. The CLI
defaults to magnitude 1; the inspected real pilot uses `--coefficient 0.5`.
These are **coefficient settings**, not named nose,
jaw or ear controls. No expression directions, pose correctives, skinning under
articulation, texture fitting, or automatic anatomical landmarks are evaluated.

The outputs include five JSON/OBJ meshes, 35 orthographic SVG captures, a contact
sheet, shared camera metadata, source/archive hashes, full shape coefficients,
and `evaluation.json`. The geometry report records bounds, minimum triangle
area, flipped/degenerate triangles, boundary/nonmanifold edge counts, and RMS
vertex displacement from neutral. Degenerate or reversed regions stop a run.
The report explicitly leaves self-intersection and anatomical review pending.

All five samples share a conservative pilot lineage and must remain in one
evaluation partition. They are not five independent subjects. Model units are
not independently measured human or printed dimensions. Neither a nominal mm
conversion nor a good-looking mesh establishes camera measurement accuracy.

## Connect to the existing viewer

Open `/#/research/face-landmarks` or the standalone preview documented in
`README.md`. Use **Open generated heads** and select `neutral.json` plus the four
`pc*.json` meshes. Do not select `manifest.json` or `evaluation.json` as meshes.

The importer validates the surface format, units/frame, provenance, triangle
indices, finite coordinates and nondegenerate geometry. The run's shared
framing preserves differences in model size. Each imported mesh has its own
drafts; geometry fingerprints prevent carrying MakeHuman annotations or another
FLAME shape's annotations onto it accidentally. Export sidecars before leaving,
and reopen the same mesh before resuming its annotations.

## Review before choosing a research generator

1. Check front, profiles, oblique, underside and top views for plausible neutral
   shape, nasal-root detail, tragion/ear coverage, gonion and under-chin access.
2. Confirm units, subject sides and head orientation against the release docs.
3. Label the four pilot landmarks and unresolved nasal/ear/jaw points. Inspect
   whether the supplied resolution supports reproducible placement.
4. Compare selected vertices with an independently run full FLAME implementation
   at the same zero pose/expression and coefficients.
5. Review self-intersections and extreme shapes before sampling more components.
   Test fixed-perimeter nasal controls separately; PCA variation alone does not
   enforce that constraint.

The generator initially records `pending_visual_and_anatomical_review`; the
separate first inspection supports proceeding to manual landmark review while
the remaining checks above stay open. Owned tetrahedron tests check array
loading, neutral shape math, explicit unit conversion, reflected winding,
provenance and file output only.
