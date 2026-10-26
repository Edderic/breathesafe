# Pilot head asset decision

Selected October 25, 2026: MakeHuman hm08 base mesh, upstream commit
`a8bc2d54ff0ac92e78ff71431b1023eda42bf482`.

Source: https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/makehuman/data/3dobjs/base.obj

Upstream OBJ SHA-256:
`8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c`.

The base mesh is a graphical asset released under CC0-1.0. The upstream
license distinguishes assets from application code:
https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.md

The asset license is preserved in `MAKEHUMAN-LICENSE.ASSETS.md` (SHA-256
`f6089cba01cb570a24712b41ab8a586ccd3cc5ef53dc266ca50b95c288956d2c`).
No upstream application code, learned weights, morph targets, skin textures,
or participant photographs are bundled. The existing 3DDFA wrapper was not used:
its weights, metric conventions and ear coverage are not verified here.

## Derivation and provenance

`makehuman_head.json` includes only faces from the OBJ `body` group with every
vertex at source y >= 5.8. Polygon faces are fan-triangulated. Used vertices
are remapped in ascending upstream index order; `upstream_vertex_indices`
preserves this mapping. The result has 4,311 vertices and 8,572 triangles.

Coordinates retain x subject-left, y superior, z anterior. The cropped y range
is recentered and uniformly scaled to **nominal 240 mm**. This is an explicit
modeling choice, not independent physical calibration or a claim that this is
an average human head. The neck boundary is open and irregular. The face, ears,
jaw and under-chin surface are available for exploratory annotation; anatomical
placement and capture visibility still need human review.

To verify the derivation against a separately downloaded pinned OBJ:

```sh
PYTHONPATH=python python3 -m dimension_pipeline.prepare_head /path/to/base.obj
```

The command checks the upstream hash, repeats the geometry transformation,
and compares the result with the bundle. It does not access the network.

## Variants and limits

`head_variants.json` records five deterministic controls: base, 0.92× scale,
1.08× scale, a smooth +5 mm nasal projection control, and increased face/jaw
width. Gaussian deformation locations are model-space controls, not anatomical
landmark labels. These are custom exploratory deformations, not MakeHuman's
full parameter system or a statistically validated face generator. They do not
guarantee fixed perimeter or realistic anatomical variation. Tests reject
degenerate triangles; full self-intersection and plausibility review remain
pending before using variants for training or printing.

Every variant has the same root identity. They must stay together in any future
dataset split. They are useful for annotation workflow review, not independent
subjects, population coverage, camera-estimator validation, or fit outcomes.

`head_views.json` defines the seven shared orthographic cameras. Positive depth
is nearer the viewer. Rendering centers the base bounding box and uses
1.45 pixels per model millimeter for every variant and view. Projection is the
same yaw-then-pitch transform as `dimension_fixture_geometry.projectPoint`.
No perspective camera or photographic distortion is simulated. Flat opaque
triangles use depth sorting for preview rendering; this is not a photorealistic
renderer, and intersecting geometry can cause depth-sorting artifacts. Surface
picking uses per-click depth intersections, not polygon sort order.
