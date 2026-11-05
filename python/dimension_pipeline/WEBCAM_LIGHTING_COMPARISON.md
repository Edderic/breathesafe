# November 5 webcam lighting comparison

Four distinct new 20-second captures completed with 60/60 registered turn views
and no provisional capture-quality flags. No clear improvement was demonstrated
by adding ceiling-bounced orange light. Preserve the raw pipeline and investigate
refinement budgets on identical saved inputs before promoting a setting.

The participant confirmed that captures 3 and 4 added **soft orange light pointed
at the ceiling**. This was indirect ceiling lighting, not direct frontal lighting.
Initial session labels described the planned condition; the separate study record
preserves this clarification without rewriting the captured provenance.

## Protocol and results

Captures 1–2 used current room lighting. Captures 3–4 added the ceiling-bounced
orange light. Intended controls were camera position, framing, native 1920×1080
resolution, a designated held-out frontal and a continuous 60-frame right-to-left
sweep. Recorded durations were 20.0011, 20.0015, 19.9998 and 20.0007 seconds. All
four used the pinned unrefined pipeline; no refinement or geometry smoothing
was applied to these raw meshes.

| Capture | Lighting | Median sharpness proxy | Normalized plane RMS | Frontal sparse reprojection RMS (px) | Analysis ray hits / 478 |
| --- | --- | --- | --- | --- | --- |
| 1 | Room | 706.8 | 0.001768 | 3.596 | 469 |
| 2 | Room | 740.2 | 0.001603 | 2.638 | 470 |
| 3 | Room + ceiling-bounced orange | 670.0 | 0.001920 | 3.282 | 459 |
| 4 | Room + ceiling-bounced orange | 539.9 | 0.001843 | 4.196 | 466 |

Mean normalized plane RMS was 0.001685 for captures 1–2 and 0.001881 for 3–4,
an 11.63% increase in this roughness screening metric. Definitions, fixed sampling
seeds and limitations are those of the
[depth study](WEBCAM_DEPTH_EXPERIMENTS.md#defined-screening-metrics). Normalization
uses raw reconstructed camera-Y extent, including boundary artifacts, and does
not establish physical dimensions or anatomical accuracy. Sharpness is the
mask-interior Laplacian variance proxy, affected by texture/noise as well as blur.
Reprojection is sparse camera-alignment evidence; ray hits establish intersections.
None alone validates anatomy or ranks a capture as the most accurate one.

The raw meshes contain 529,235 / 575,398 / 558,774 / 470,207 triangles. Face-connected
components are 199 / 167 / 178 / 182; boundary edges are 131 / 140 / 132 / 163, with
zero counted nonmanifold edges. Surfaces remain open. Read-only full-resolution
front and ±35° inspection shows substantial grain in all four, flat jaw/neck sheets
particularly in 2–3, and crown/boundary gaps. These artifacts affect normalized
roughness; the lowest score is not proof of a better face surface. Matching viewer
controls and fit-to-view support appearance inspection, not cross-capture geometric
alignment. No source sessions or geometry changed during inspection.

Two captures per condition, one participant, fixed order and unverified ambient
stability do not establish statistical significance or a general lighting effect.
Manual exposure, focus and white balance are unavailable through this camera/browser,
so settings could not be verified as fixed across conditions. There is no paired
reference scan, calibrated tape scale or independent check arc. The bounded
conclusion is **no demonstrated benefit of this added light in these captures**.

## Follow-up requested for later

Compare the same soft orange light aimed directly at the face with an iPhone 16
flashlight aimed at the face. Take two captures per source, preferably alternating
orange / phone / phone / orange to reduce order effects. Keep ambient room lighting,
camera position, face framing, 20-second timing and source position/distance/angle
as consistent as possible; use one test source at a time. Record source placement
and any brightness setting. Equal settings do not establish equal illumination,
and automatic exposure/white balance remain potential confounders. This compares
the practical setups; it does not isolate lamp spectrum or device hardware.

This follow-up has not started. It requires participant-operated captures after
the saved-input iteration comparison. No additional recruitment or recommender
changes are involved.

## Private evidence

Raw images/masks, full geometry and native diagnostics remain in the ignored
private run directory. `capture-comparisons/bre18-lighting-20261105/` contains
per-capture baseline JSON, a summary with the lighting clarification,
full-resolution front/side screenshots and iteration-study snapshots. Participant
assets are not published or committed.
