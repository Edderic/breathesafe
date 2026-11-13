# NASEM presentation rendering

The active deck is `prompts/2026-11-17-nasem/presentation.html`, built by its native `build_presentation.py`. It has 22 slides: 16 main slides within 10 minutes, plus six backups. The September public presentation is unchanged.

Run `python3 prompts/2026-11-17-nasem/build_presentation.py` to rebuild HTML and timed notes. Run `node scripts/presentations/render_nasem_prototype.cjs` to check frozen paired metrics, desktop/mobile layout, navigation and print bounds, and export the PDF. The renderer uses local Chrome and Playwright; set `NASEM_PLAYWRIGHT_ROOT` if needed. Preview screenshots go to ignored `tmp/nasem-preview/`.

Slide 5 retains the 49-person nose-feature experiment. Slide 6 shows test-weighted results for the separate seven-person comparison: actual production ARKit architecture versus direct traditional/PCA models. The older 49-person top-k comparison moves to backup slide 20. Methods, source hashes and aggregate values live in `recommender-evidence.json` and `paired-measurement-evidence.json`. Participant-level inputs and predictions stay private.

Prototype slides 10–12 retain actual raw/smoothed neck-inclusive headforms, landmarks, routes and caliper checks. Evidence is in `prototype-evidence.json`; images are in `assets/prototype/`. The unresolved bifold discrepancy remains omitted. The complementary synthetic detector plan remains a backup.

To refresh source screenshots, set `NASEM_SOURCE_ROOT` to the workspace containing `.private-webcam-runs` and run the renderer with `--capture-sources`. This reads local surfaces without modifying annotations or reconstruction. Rebuild the deck afterward. No deployment is performed.

Slide 2 now establishes the general-public goal, adults-and-kids intended reach and broader respirator standards. Its generated fit illustration and exact prompt are stored in the deck assets. The detailed complementary-scope slide moves to backup 17, keeping the main talk at 600 seconds. Published NIOSH scope and general fit principles are linked in the slide footer; the illustration is not fit-test evidence.

The NPV update adds negative predictive value to slide 5 using saved held-out confusion counts (mean across seeds, fixed 50% cutoff). The former equal-person slide 7 is removed; its frozen evidence is retained. The renderer verifies both NPV cells and absence of that slide. The talk remains 600 seconds, with more time for the NPV explanation and paired test-weighted results.

Backup slide 21 describes the direct traditional/PCA predictors for Q&A: six recorded facial dimensions, shared mask fields, standardization, PCA-3 and the nonlinear interaction recipe. It explicitly distinguishes this project-specific PCA from the NIOSH panel. The frozen feature list is checked against the slide. Main-slide timing is unchanged.

Slide 14 describes the convenience sample before slide 15’s demographic counts. The overlapping community groups are presenter-described; health status and motivations were not quantified. The main talk remains 600 seconds.
