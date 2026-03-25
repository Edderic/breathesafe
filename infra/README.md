# Terraform for Mask Recommender Infrastructure Controls

This directory manages:
- S3 lifecycle rules for mask recommender artifacts and models
- CloudWatch log retention for mask recommender Lambda log groups

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
- This configuration targets existing buckets. It does not create buckets.
- The CloudWatch retention policy is set to 30 days.
- Adjust prefixes, log groups, or retention values as needed.
