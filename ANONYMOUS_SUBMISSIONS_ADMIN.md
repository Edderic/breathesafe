# Manage anonymous submissions

Signed-in website admins can open **Admin → Anonymous Submissions**, at
`/#/admin/anonymous-contributions`. Both desktop and mobile navigation include it.

The page lists the newest received submissions first, 25 at a time. Search by
complete receipt UUID or anonymous participant database ID. Expand a submission
to inspect its facial measurements, fit-test scores, mask labels, protocol,
testing mode, and measurement source. Recovery credentials and internal digests
are never returned. Anonymous participant IDs do not identify a named person.

## Delete feature-test submissions

1. Match submissions to known test receipts and results. Recency alone does not
   establish that a submission is a disposable test run.
2. Select the submissions to remove (up to 100). Selections persist across pages
   and searches; use **Clear selection** to start over.
3. Choose **Review deletion**. Review the exact receipts, measurements, and test
   counts in the confirmation section. Cancel leaves the data intact.
4. Remove pending/failed copies of these submissions from the phone's queue, if
   any. A later retry can recreate a deleted submission.
5. Type `DELETE` and choose **Permanently delete submissions**.

This permanently removes the selected contributions, their facial measurements,
all their fit tests, and their mask-proposal links. Participant codes continue to
work. Shared mask proposals and catalog entries remain available, including
proposals with no remaining links. Existing exports and backups are unaffected.

If other submissions reuse selected measurements, the page reports their receipt
IDs and blocks deletion. Inspect those records, and include them only if they are
also disposable. No dependent submission is silently added or deleted.

This page supports review and deletion. Catalog matching remains under **Mask
Proposals**; raw fit-test scores and facial measurements cannot be edited here.

## Implementation and release

- All three endpoints require an authenticated admin and return `Cache-Control:
  no-store`. Mutations use the existing Rails CSRF protection.
- `GET /admin/anonymous_contributions.json` supports `receipt`, `participant`,
  and `before_id` filters.
- `POST /admin/anonymous_contributions/deletion_preview.json` accepts an array
  of `contribution_ids` and returns the selected data and a signed preview token.
- `DELETE /admin/anonymous_contributions/destroy_selected.json` accepts that
  token. It expires after 15 minutes and belongs to the admin who requested it.
- Selection is locked and dependencies are rechecked in a transaction. A changed
  or missing submission invalidates the preview. Reused snapshots are deleted
  before their source; any deletion failure rolls back the batch. The existing
  database foreign key also prevents concurrent dangling measurement references.
- Successful deletion logs the admin ID and receipt IDs as
  `anonymous_contributions_deleted`, without measurements or credentials. This
  uses application log retention, not a permanent database audit trail.

No new migration is introduced. The existing measurement-reuse migration
`20260929010000` must be applied. Deploy the backend and Vue build together using
the normal BreatheSafe release process. This implementation does not itself deploy
or delete any production data.

Validation:

```sh
bundle exec rspec spec/requests/admin_anonymous_contributions_spec.rb spec/requests/anonymous_contributions_spec.rb spec/requests/mask_proposals_spec.rb
node --test scripts/tests/admin_anonymous_contributions.test.cjs
npx vite build
```
