NASEM presentation — November 17, 2026

Local review draft for NPPTL researchers building iOS and Android apps.
Eleven main slides with a 10-minute speaking budget, followed by two backups.

Preview:
  http://127.0.0.1:8765/presentation.html

To restart the local preview from the repository root:
  python3 -m http.server 8765 --bind 127.0.0.1 --directory prompts/2026-11-17-nasem

presentation.html also opens directly in a browser without a server or internet.
Use arrow keys, Home/End, or the visible controls. All slides provides an overview.
presentation.pdf is the local PDF export. speaker-notes.txt contains the timed script.

Rebuild HTML and notes:
  python3 prompts/2026-11-17-nasem/build_presentation.py

To refresh the PDF after rebuilding, open the HTML and choose Print / PDF.
Use background graphics, the CSS landscape page size, and no browser headers/footers.

Scope:
This draft replaces the September planning-meeting narrative with practical capture,
scale, landmarking, and cross-platform development lessons. Historical September top-1/3/5 conditional hit rates are included with
their evaluation population. The quadratic perimeter-difference slide explains
the learned optimum using a schematic with invented coefficients. The 45-second processing figure is presenter-reported,
not a controlled benchmark. The Android pipeline is work in progress.
Technical references are linked on the relevant slides and in the source backup.
Slide 2 also includes four personal recommendation cards transcribed from the
presenter’s October 29 screenshot (October 25 model). Observed Fit is hidden
initially; use Show observed fit to reveal it, or Hide observed fit before
printing. This presentation toggle does not change the live application.
The live recommendation link requires the appropriate account access.

Four presenter-supplied images show the current MasqFit capture and five aggregates,
Apple face geometry, and a MediaPipe mesh. Originals are preserved in assets/
and embedded in the HTML for offline use. Occluded-point accuracy from one
viewing angle is identified as an open project validation question.

Validation:
Checked all 13 slides at 1366x768 for viewport fit, mobile width at 390px for
horizontal overflow, next-slide navigation, all-slides mode, and print layout.
All print slides fit their 16:9 pages. Visually inspected comparison and pipeline.

Publication:
No production files, public/ copies, routes, or existing September artifacts changed.
This folder is the review draft; publication is a separate step after review.
