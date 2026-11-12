# Manual anatomical landmark review

Resume a surface-ready session, then click **Review anatomical landmarks**.
Choose the raw full mesh or a completed image-refinement full mesh. Each source
has its own review; a placement is never silently copied between topologies.

1. Select nose tip (pronasale), nose base (subnasale) or nasal root (sellion).
   The panel gives a short placement guide. These are review labels rather than
   claims that the reconstructed surface resolves those anatomical locations.
2. Enable **Click to place selected landmark**, then click the full mesh. Drag
   rotates, including while placement is enabled; scrolling changes zoom.
   A click selects the nearest positive intersection within the renderer's clip
   volume, retaining the source triangle index and barycentric coordinates.
   Clicking background leaves the prior placement untouched.
3. Inspect front, both profiles and **From below**, changing lighting and zoom as
   needed. The selected point is also projected onto the undistorted frontal
   reference using the original registered camera. The marker on the mesh is a
   screen overlay, so it can represent a point behind the surface after rotation;
   inspect several views rather than using overlay visibility as a coverage test.
4. Choose Pending, Accepted, Uncertain or Unavailable, add notes, and **Save
   landmark review**. Acceptance requires an attached point. Uncertain may retain
   a provisional point or have none. Unavailable clears the current attachment
   while retaining previous versions in history. Repositioning or choosing a
   suggestion returns the draft to Pending and requires another explicit save.
5. Save or discard unsaved edits before changing source or landmark. Export the
   session ZIP to include the review. Resuming or reloading that ZIP restores it.
   Closing the panel or leaving the page discards unsaved edits.

**Use detector suggestion for review** ray-projects original frontal detector
indices 4, 2 and 168 onto the selected full surface. These are optional starting
positions, not verified anatomical correspondence. A missed suggestion remains
unavailable; it does not fabricate a point. Refined surfaces use the original
frontal camera and detector pixels in shared reconstruction coordinates for this
initial suggestion and image overlay, rather than transferring analysis-mesh
attachments or acceptance decisions.

The `webcam-landmark-review-v1` records are stored in `session.json` under
`landmark_review.sources`, keyed by raw or completed variant ID. Each source has
its exact full-PLY SHA-256 and a revision counter. Each point has status, source
triangle/weights, reconstructed world point, notes, provenance, timestamp and
previous review history. Source changes and stale revisions reject saves. The
processor reconstructs world points from validated attachments; it never trusts
client-supplied world coordinates. Full-mesh browser downloads are size bounded
and hash checked before rendering. Existing session Origin/Host and artifact-path
guards apply to GET/POST `landmark-review` endpoints. Review is blocked while that
session's reconstruction or experiment job is active.

This changes only the new review record. Full/analysis geometry, detector output
and acceptance, calibration, tape routes, ARKit data and recommender inputs remain
unchanged. All stored points are in reconstruction units. This first version does
not calculate anatomical protrusion, surface arcs, path correspondences or
cross-capture repeatability: those need explicit measurement definitions and
reviewed routes. There is no independent accuracy claim from clicking a mesh.

Verification: 89 Python tests passed, including rotated-view nearest-surface
picking with overlapping depth layers, barycentric reconstruction, missed hits,
invalid attachments, revision/hash failures, unavailable history and session ZIP
reload. The Vite production build passed. A live Chrome workflow on an isolated
copy of an existing capture verified manual placement, misses retaining the point,
raw/refined isolation, detector suggestion review, notes, statuses and unchanged
original session bytes. Browser workflow test placements are not anatomical reviews
and exist only in the ignored private test copy.
