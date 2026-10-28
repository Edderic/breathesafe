# Continuous shortest paths on the annotated mesh

The default path method in the landmark viewer is now **Continuous surface
shortest path**, provided by a local CGAL service. It crosses triangle interiors
and retains the exact barycentric endpoints. **Mesh-edge approximation** remains
available as an explicit comparison. An unavailable solver is shown as an error;
an edge route is never silently labeled as a continuous result.

## Build and start

Install CGAL and a C++17 compiler/CMake. On macOS with Homebrew:

```sh
brew install cgal cmake
cmake -S native/surface_geodesic -B tmp/surface-geodesic-build -DCMAKE_BUILD_TYPE=Release
cmake --build tmp/surface-geodesic-build -j 2
PYTHONPATH=python python3 -m dimension_pipeline.surface_geodesic
```

On Debian/Ubuntu, install `libcgal-dev`, `cmake` and a C++ compiler. CI builds
the same executable before running the native integration tests. If a macOS
Conda environment injects an incompatible x86 library directory, reconfigure
this build with `-DCMAKE_EXE_LINKER_FLAGS=` to use the native compiler's standard
library and CGAL's imported library targets.

The bridge uses only Python's standard library and binds to `127.0.0.1:5180`.
Only local browser origins are accepted. Mesh requests are limited to 20,000
vertices, 40,000 faces, two endpoint pairs, and 10 MB. At most two solves run
concurrently; each subprocess has a 25-second timeout. There are no network
downloads or external uploads in the solver. The browser waits 180 ms after an
endpoint edit, aborts superseded requests, and ignores stale replies.

Run the existing standalone preview, or use the local Rails/Vite app:

```sh
./node_modules/.bin/vite --config scripts/face_landmarks.vite.config.mjs
```

Open
`http://127.0.0.1:5178/scripts/face_landmarks_preview.html?heads=/tmp/flame-open-pilot/manifest.json`.
Re-import the saved annotations for that mesh. Existing annotations need no
migration, and derived paths are recalculated. The browser calls the loopback
solver directly; remote production pages do not attempt this local service.
Native solver deployment to production is outside this local research change.

## Algorithm and verifiable output

CGAL's Surface Mesh Shortest Path package implements the Xin–Wang extension of
the Chen–Han continuous shortest-path algorithm. Source and target are original
face locations, with their barycentric weights reordered only for CGAL's face
convention. The result is a sequence of vertex and edge-crossing attachments,
mapped back to the original mesh indices. The input mesh is not smoothed,
subdivided, normalized or otherwise changed.

This build uses `Exact_predicates_inexact_constructions_kernel` (EPICK): exact
predicates with floating-point coordinate constructions. "Continuous" describes
the surface-path algorithm, not arbitrary-precision arithmetic or independently
validated anatomical/physical accuracy. The result is the shortest path on the
supplied piecewise-flat mesh, subject to numerical precision.

Before displaying a path, the browser checks that:

* Endpoints match the original annotation positions.
* Attachments are valid and every segment is supported by a mesh triangle.
* Reconstructed length agrees with the solver's reported length.
* Length lies between the straight chord and the mesh-edge route, within the
  documented floating-point tolerance of `1e-6 * max(1, length_mm)`.

Disconnected components remain disconnected. Invalid or inconsistently oriented
meshes are rejected rather than automatically repaired, preserving annotation
indices. Exports include method `cgal_continuous_v1`, CGAL version, arithmetic,
runtime, mesh-edge comparison and reconstructable path attachments. Pending or
unavailable paths retain their status and have no measured length.

References:

* https://doc.cgal.org/latest/Surface_mesh_shortest_path/index.html
* https://doc.cgal.org/latest/Surface_mesh_shortest_path/classSurfaceMeshShortestPathVisitor.html

The installed CGAL package uses GPL-3.0-or-later or a commercial license for
this component; the Breathesafe source repository is GPL-3.0. No binary or CGAL
headers are vendored in Git. See the exact installed CGAL license before any
separately licensed distribution.

## Validation and initial comparison

Analytic tests cover a flat square (continuous distance `sqrt(2)` rather than
the edge graph's `2`), a folded pair of triangles with a known unfolded distance,
same-face interior points, pose/scale changes, disconnected coincident surfaces,
and inconsistent winding. Client tests reject shifted endpoints, off-surface
segments, malformed attachments and fabricated lengths.

For the eight-landmark neutral-head export supplied during this session
(`flame-open-pilot-e75a0990728ba038-neutral-annotations (2).json`), the same
left endpoints produce:

| Method | Model-space length |
| --- | --- |
| Straight chord | 65.65 mm |
| Mesh-edge Dijkstra | 74.46 mm |
| CGAL continuous surface path | 66.11 mm |

CGAL 6.2 took approximately 102 ms locally, including native process startup.
That removes about 8.35 mm of edge-constrained detour for these endpoints.
The source annotation file is not modified. This is geometric evidence on the
given mesh, not confirmation of zygion/gonion placement, a particular physical
tape route, or physical millimeter accuracy.

```sh
PYTHONPATH=python python3 -m unittest discover -s python/dimension_pipeline/tests -p test_surface_geodesic.py -v
node --test scripts/tests/face_continuous_paths.test.cjs
```

If the executable is absent, native integration tests explicitly skip; CI builds
it so those tests are required there. Input-validation tests remain runnable
without CGAL. Build outputs and benchmark artifacts stay under ignored `tmp/`.
