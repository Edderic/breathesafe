# Anonymous measurement reuse

## Reusing previous facial measurements

Returning participants load their latest saved original measurements by default after scanning or pasting their participant code. The screen shows **Use my previous measurements**, the five values, their original submission date, and **Scan again**. The final consent review distinguishes reused measurements from a new scan. New participants and codes without saved measurements require a scan. Looking up measurements never submits data or creates a participant.

`GET /anonymous_contributions/previous_measurements` uses the same bearer code as submissions, has `Cache-Control: no-store`, and returns `{"previous_measurements": null}` or an object with `contribution_id`, `measurement_version`, `measurements`, and `consent_accepted_at`. It returns no fit-test history. Anyone holding the participant code can retrieve these measurements, so the app tells participants to keep the code private. Responses stay in memory until cleared or consented into the protected queue; the lookup uses no cookies or response cache.

Lookup requires connectivity and a successfully delivered original contribution. Pending offline scans are not available through lookup. Failures offer retry or a new scan; they are not treated as an empty history. Switching participants or starting a scan invalidates pending lookup responses. Canceling a rescan preserves already loaded previous measurements.

Reused submissions include optional `measurement_source_contribution_id` with the original contribution UUID, plus a fixed snapshot of all five measurements. The backend requires the source to belong to the same participant, be an original scan, and match the submitted version and values. Queue retries retain that exact snapshot and source, even after a newer scan is submitted. Older payloads omit the new field and keep their existing retry digests. Admin exports include provenance so reuse need not be counted as a new scan.

The latest original is selected by original consent/submission time, then database ID; reused submissions and older offline scans delivered later do not advance the original scan date. This is a submission date, not a claim about the exact capture time. No maximum age is enforced; participants can scan again when measurements change.

Deploy migration `20260929010000_add_measurement_source_to_anonymous_contributions.rb` and the backend lookup/validation before releasing this app update. Device checks: recover a code on a later visit; confirm default reuse; scan again; cancel a rescan; switch participants during lookup; test no history, unavailable network, offline queue retries, and consent cancellation.
