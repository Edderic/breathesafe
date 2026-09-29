# Anonymous mask proposals

MasqFit sends only reviewed mask text to `GET /anonymous_contributions/mask_suggestions`. The public endpoint classifies the reviewed name, reuses `MaskMatching::Scorer` with separate brand/model and fit-related components, and returns up to five canonical masks. It never automatically assigns one. Name-based matching remains available when classification is unavailable. Users confirm a suggestion, search the catalog, or propose a new mask.

A fit test can include `propose_mask: true` instead of `mask_id`. Only consented contribution ingestion creates proposals. Normalized names share a proposal; each contribution/test position keeps its own link. The original payload digest remains immutable when review enriches the fit-test JSON, preserving idempotent retries.

Admins review at **Admin → Mask Proposals** (`/#/admin/masks/proposals`), match a canonical mask or create one under their own account, and update all linked anonymous tests transactionally. Future contributions carrying a resolved proposal use the reviewed match. The existing account-based import matching and duplicate tools remain available.

## Release and operations

- Deploy migration `20260917010000` with the backend and Vue frontend before shipping the iOS update.
- Keep the previously deployed anonymous-contribution endpoint/migration in the release branch.
- Sidekiq sends notifications to confirmed admin users, using the existing SMTP configuration. Emails contain only the proposed mask name and review link.
- Run `bundle exec rake mask_proposals:notify_pending` to recover notifications after queue failures or adding admin recipients. Jobs lock and check `notified_at`; ordinary retries do not resend. SMTP cannot guarantee exactly-once delivery across a crash immediately after sending.
- `bundle exec rspec spec/requests/anonymous_contributions_spec.rb spec/requests/mask_proposals_spec.rb` covers backward compatibility, suggestions, proposal deduplication, rollback, permissions, matching/creation, linked-test updates, immutable retry digests, and notifications.
- `npx vite build` checks the review UI build. Local tests use test mail delivery, not production SMTP.

## Classified anonymous suggestions

The suggestion endpoint now classifies the reviewed query through `MaskComponentPredictorService` and compares brand/model and the existing fit-related components with `MaskMatching::Scorer`. Color is excluded from classified scoring. Numeric model suffixes are retained. Existing current-state catalog annotations take precedence, followed by the latest breakdown event, then cached predictions. Queries always require user confirmation in MasqFit.

Successful predictions are cached for 24 hours; failures for 30 seconds. Inline cache versions derive from the trained model and tokenizer file hashes. Set `MASK_PREDICTOR_VERSION` to a new unique version when deploying changes to a remote Lambda/Flask predictor. Queries have a five-second predictor deadline; stalled inline subprocesses are killed and reaped. Missing/unusable predictions, timeouts, and cache errors fall back to the existing name-based matcher, where color may still affect the fallback score.

Missing catalog classifications are queued for `WarmMaskMatchingCatalogJob`, with scheduling throttled to once per five minutes per model version. The worker skips annotated masks and uses the same versioned prediction cache. Existing names are never reclassified across the whole catalog synchronously in a request. Queue errors log a warning and leave fallback results available; subsequent requests can retry after the scheduling gate expires.

Before shipping the updated app, deploy the backend and run `bundle exec rake mask_matching:warm_catalog` with Sidekiq running. This enqueues cache preparation only; it does not edit catalog annotations or send emails. No new migrations or API response fields are required. Verify the Zimi B95-XL-01 White query and watch predictor-unavailable / catalog-scheduling warnings and job retries. Missing mask classifications can temporarily produce less accurate fallback suggestions until prepared.

## Community-event batch review

MasqFit now sends all nonblank reviewed imported mask names through the existing `propose_mask: true` path. Organizers select participant tests and review each distinct mask/protocol label pair once, without catalog matching on the phone. Blank names remain unspecified. Older payloads and explicitly confirmed catalog IDs retain their existing behavior.

Admin mask matching automatically loads ranked suggestions for unresolved names, with two concurrent automatic requests. Delayed responses cannot replace a newer manual search or a refreshed queue. A failed suggestion leaves other rows usable and offers retry/search. Suggestions never apply a match without explicit admin confirmation.

The admin list and update responses include `test_count`, the number of linked tests affected by a decision. The existing normalized-name grouping, reviewed-match reuse, transactional updates, and one notification per distinct proposal remain unchanged. No new migration or backfill is needed for this change.

Validation commands:

- `bundle exec rspec spec/requests/mask_proposals_spec.rb spec/requests/anonymous_contributions_spec.rb`
- `node --test scripts/tests/admin_mask_proposals.test.cjs`
- `node_modules/.bin/vite build`

Deploy the admin API/frontend before the companion app release. Device checks should cover mixed-participant imports, whole-group selection, privacy edits, canceling review, blank names, and offline delivery. Existing measurement-reuse migration requirements still apply.
