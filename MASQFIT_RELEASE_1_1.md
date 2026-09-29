# BreatheSafe companion for MasqFit 1.1.0

Release candidate tag: `masqfit-api-v1.1.0-rc.1`.
Companion app: `v1.1.0-rc.1`, version 1.1.0, initial build 2.

PRs: [BreatheSafe #23](https://github.com/Edderic/breathesafe/pull/23) and [MasqFit #3](https://github.com/Edderic/masqfit/pull/3).

This tag identifies the compatible backend source, not a deployment. It deliberately does not use the `prod-*` or `deploy-ml-*` tag patterns. Do not move the tag after publication; use a new candidate tag for changes.

Includes anonymous submissions and exports, measurement reuse with original-scan provenance, admin submission management, grouped mask matching with automatically loaded suggestions and linked-test counts. The app defaults the reviewed batch mode to N99; the API continues to accept N95, N99, Unknown, and legacy omitted modes. Do not infer instrument mode from scores on ingestion.

Before the app ships:

1. Merge after CI passes and confirm production deploys the merged backend. The current deploy workflow keys off successful main workflows; older DEPLOYMENT.md references to development are stale. Watch the actual staging/production workflow outcomes.
2. Confirm the release migration `20260929010000_add_measurement_source_to_anonymous_contributions.rb` is applied. Existing proposal tables and worker processing are also required.
3. Verify saved-code lookup, grouped proposals, automated suggestions, and an admin decision updating linked tests. Suggestions alone must never confirm a catalog match. Use synthetic data and remove it through the admin cleanup flow after testing.
4. Verify Sidekiq and the mask-classifier configuration/cache. See MASK_PROPOSALS.md for catalog cache warming.
5. Complete the companion app’s device/TestFlight checks before public release. No new migration is introduced by this release-preparation commit.

The app’s APP_STORE_RELEASE.md contains the manual archive/upload steps and Xcode Cloud setup path. Neither tag automatically uploads an iOS build, submits App Review, nor publishes the app.
