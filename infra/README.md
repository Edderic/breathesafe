# Terraform for S3 Lifecycle Rules

This directory manages S3 lifecycle rules for mask recommender artifacts and models across environments.

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

## Notes
- This configuration targets existing buckets. It does not create buckets.
- Adjust prefixes or add more rules as needed.
