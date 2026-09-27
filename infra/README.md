# Terraform for Mask Recommender Infrastructure Controls

This directory manages:
- S3 lifecycle rules for mask recommender artifacts and models
- CloudWatch log retention for mask recommender Lambda log groups
- IAM user policies that allow the dashboard web apps to read latest mask recommender metrics artifacts

## Prerequisites
- Terraform >= 1.3
- AWS credentials configured (env vars or shared credentials file)

## What this does
- Adds lifecycle rules to these buckets:
  - `breathesafe-production`
  - `breathesafe-staging`
  - `breathesafe-development`
- Expires objects under prefixes used by training:
  - `mask-recommender-training-*/models/` (latest pointers and versions)
  - `mask-recommender-training-*/artifacts/`
- Expiration: 360 days
- Sets CloudWatch Logs retention to 30 days for recommender Lambda log groups:
  - `/aws/lambda/mask-recommender`
  - `/aws/lambda/mask-recommender-production`
  - `/aws/lambda/mask-recommender-staging`
  - `/aws/lambda/mask-recommender-inference-production`
  - `/aws/lambda/mask-recommender-inference-staging`
  - `/aws/lambda/mask-recommender-training-production`
  - `/aws/lambda/mask-recommender-training-staging`
- Attaches inline IAM user policies so the production and staging Rails apps can read:
  - `s3://breathesafe/mask_recommender/models/*`
  - `s3://breathesafe-staging/mask_recommender/models/*`

## Usage

Initialize and review plan:

```bash
cd infra
terraform init
terraform plan -var="aws_region=us-east-1"
```

Apply:

```bash
terraform apply -var="aws_region=us-east-1"
```

If the buckets already have lifecycle configurations managed elsewhere, import first:

```bash
terraform import aws_s3_bucket_lifecycle_configuration.mask_recommender_models["breathesafe-staging"] breathesafe-staging
terraform import aws_s3_bucket_lifecycle_configuration.mask_recommender_artifacts["breathesafe-staging"] breathesafe-staging
# Repeat for production and development buckets
```

If the CloudWatch log groups already exist, import them before apply:

```bash
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender"]' '/aws/lambda/mask-recommender'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-production"]' '/aws/lambda/mask-recommender-production'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-staging"]' '/aws/lambda/mask-recommender-staging'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-inference-production"]' '/aws/lambda/mask-recommender-inference-production'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-inference-staging"]' '/aws/lambda/mask-recommender-inference-staging'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-training-production"]' '/aws/lambda/mask-recommender-training-production'
terraform import 'aws_cloudwatch_log_group.mask_recommender["/aws/lambda/mask-recommender-training-staging"]' '/aws/lambda/mask-recommender-training-staging'
```

## Notes
### Weekly training

`training_schedule.tf` schedules the existing `mask-recommender-production`
Lambda in us-east-1 for Sundays at 02:00 UTC, matching the GitHub schedule.
The schedule is enabled by default. It uses the Lambda's existing credentials;
no application secrets are embedded in the schedule.

Before enabling:
- Verify the deployed container contains the current combined handler and
  supports `raise_on_error` for asynchronous training failures.
- Verify production API credentials, S3 write permissions, memory, temporary
  storage, and a timeout sufficient for the complete training run (maximum 900s).
- Run training and confirm completion comfortably within that limit, successful
  artifact uploads, and the updated `mask_recommender/models/custom_latest.json`.
  This test promotes a production model; it is not a dry run.
- Scheduler delivery retries and Lambda asynchronous execution retries are
  disabled. Training publishes artifacts, so failed runs should be investigated
  before manually repeating them. The Lambda retry setting applies to all
  asynchronous invocations of the shared production function.
- Remove the GitHub workflow's `schedule` trigger at cutover; retain manual and
  tag triggers. Avoid overlapping manual and scheduled training runs.
- Review a Terraform plan with `-var='training_schedule_enabled=true'`, then
  apply the reviewed plan. Keep this variable set on subsequent applies.

Check Lambda logs and Errors/Duration metrics after the first scheduled run.
Failure alerts are described below. Stale models are not monitored.
To pause training, apply with `-var='training_schedule_enabled=false'`.

Production verification on September 16, 2026 (UTC): a complete 200-epoch run
finished in 67.8 seconds with 1,150 MB peak memory (3,008 MB configured), and
updated `s3://breathesafe/mask_recommender/models/custom_latest.json`.
The existing Heroku `MASK_RECOMMENDER_INTERNAL_API_TOKEN` was synchronized to
Lambda to restore authenticated dataset access. Keep it synchronized on rotation.
The deployed `scheduled-training-20260915` image preserves the prior production
image and replaces only the training handler with the asynchronous error fix.

### Failure notifications

`training_notifications.tf` manages SNS topic `mask-recommender-training-alerts`
in us-east-1 and an email subscription for `info@breathesafe.xyz`. Click the AWS
subscription confirmation link before expecting email delivery.

Three CloudWatch alarms notify on entering ALARM (no recovery emails):
- `mask-recommender-training-Errors`: production Lambda execution errors and
  timeouts, including recommendation errors because the function is shared.
- `mask-recommender-training-AsyncEventsDropped`: discarded asynchronous events.
- `mask-recommender-training-delivery`: Scheduler target errors or dropped
  invocations, scoped to the training schedule group.

Each alarm uses five-minute sums, a threshold of one, and treats missing data
as non-breaching. Alerts contain alarm metadata, not invocation payloads.
AWS metric delivery is best effort; these alarms do not detect a disabled
schedule or an out-of-date model. HTTP error responses returned without raising
an exception do not increment Lambda Errors; scheduled training raises failures.

Check the SNS subscription status with:

```bash
aws sns list-subscriptions-by-topic --profile breathesafe --region us-east-1 \
  --topic-arn arn:aws:sns:us-east-1:585068368316:mask-recommender-training-alerts
```

After confirmation, verify delivery using a temporary CloudWatch alarm named
`mask-recommender-training-notification-test`, with this topic as its ALARM
action. Force that test alarm to ALARM with a clearly labeled test reason, check
its action history and email receipt, then delete it. Do not force production
alarms or intentionally fail production training to test notifications.

For execution failures, inspect `/aws/lambda/mask-recommender-production` logs;
for dropped events check concurrency and event age. For delivery failures check
the Scheduler target and its IAM role. If emails stop, check subscription
confirmation, alarm actions, SNS policy and email spam filtering.

### Existing infrastructure

- This configuration targets existing buckets. It does not create buckets.
- This configuration also targets existing IAM users (`breathesafe-production` and `breathesafe-staging`). It does not create them.
- The CloudWatch retention policy is set to 30 days.
- Adjust prefixes, log groups, or retention values as needed.
