# FLAME 2023 Open evaluation and viewer adapter

Status, October 25, 2026: the official model download requires login. The model
was not found locally when implementation started. The importer and viewer
connection can be tested using owned geometry, but anatomical coverage, actual
FLAME shape quality, and comparison with the complete model runtime remain
pending until the official asset is supplied. No substitute model is presented
as FLAME evidence.

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
300 shape directions. The five outputs are neutral, coefficient 1 at -1/+1,
and coefficient 2 at -1/+1. These are **coefficient settings**, not named nose,
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

Until those checks use the actual release, the decision stays
`pending_visual_and_anatomical_review`. Owned tetrahedron tests check array
loading, neutral shape math, explicit unit conversion, reflected winding,
provenance and file output only.
