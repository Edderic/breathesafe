# NASEM prototype rendering

The active deck is `prompts/2026-11-17-nasem/presentation.html`, built by that folder’s native `build_presentation.py`. The November 11 prototype update replaces the outdated photogrammetry plan with three working-prototype slides (9–11), and retains the synthetic-landmark research slide as a backup. There are 18 slides: 15 main slides within the existing 10-minute budget, plus three backups. The September public presentation is unchanged.

Run `python3 prompts/2026-11-17-nasem/build_presentation.py` to regenerate HTML and timed speaker notes. Run `node scripts/presentations/render_nasem_prototype.cjs` to verify the deck and export its PDF. The renderer uses local Chrome and the existing Playwright installation; set `NASEM_PLAYWRIGHT_ROOT` to the research repository if needed. Preview screenshots go to ignored `tmp/nasem-preview/`.

Actual prototype views are retained in `prompts/2026-11-17-nasem/assets/prototype/` and embedded for offline use. Frozen single-capture measurements and private-source report hashes are in `prototype-evidence.json` within that deck folder. The experimental bifold discrepancy remains omitted from the slides, as requested. Future worn-mask photogrammetry and contact-route tracing remain in speaker notes.

To refresh the surface screenshots, set `NASEM_SOURCE_ROOT` to the research workspace containing `.private-webcam-runs`, and run the renderer with `--capture-sources`. This reads local surfaces without modifying annotations or reconstructing geometry. Rebuild the deck afterward. No raw source photos or private meeting material are copied into the deck. No publication is performed.

The November 12 recommender update replaces the proposed nose feature and historical top-k snapshot on slides 4–5 with the paired perimeter-only/shared-nose experiment. Frozen aggregate numbers and private-report hashes are in `recommender-evidence.json`; individual records remain private. Classification uses a fixed 50% cutoff. The mixed-input gain and measured-only limitation are both explicit. The same 18 slides and 10-minute speaking budget are retained.
