# Anonymous mask proposals

MasqFit sends only reviewed mask text to `GET /anonymous_contributions/mask_suggestions`. The public endpoint reuses `MaskMatching::Scorer` with tokenized names, returns up to five canonical masks, and never automatically assigns one. It does not invoke the prediction infrastructure. Users confirm a suggestion, search the catalog, or propose a new mask.

A fit test can include `propose_mask: true` instead of `mask_id`. Only consented contribution ingestion creates proposals. Normalized names share a proposal; each contribution/test position keeps its own link. The original payload digest remains immutable when review enriches the fit-test JSON, preserving idempotent retries.

Admins review at **Admin → Mask Proposals** (`/#/admin/masks/proposals`), match a canonical mask or create one under their own account, and update all linked anonymous tests transactionally. Future contributions carrying a resolved proposal use the reviewed match. The existing account-based import matching and duplicate tools remain available.

## Release and operations

- Deploy migration `20260917010000` with the backend and Vue frontend before shipping the iOS update.
- Keep the previously deployed anonymous-contribution endpoint/migration in the release branch.
- Sidekiq sends notifications to confirmed admin users, using the existing SMTP configuration. Emails contain only the proposed mask name and review link.
- Run `bundle exec rake mask_proposals:notify_pending` to recover notifications after queue failures or adding admin recipients. Jobs lock and check `notified_at`; ordinary retries do not resend. SMTP cannot guarantee exactly-once delivery across a crash immediately after sending.
- `bundle exec rspec spec/requests/anonymous_contributions_spec.rb spec/requests/mask_proposals_spec.rb` covers backward compatibility, suggestions, proposal deduplication, rollback, permissions, matching/creation, linked-test updates, immutable retry digests, and notifications.
- `npx vite build` checks the review UI build. Local tests use test mail delivery, not production SMTP.
