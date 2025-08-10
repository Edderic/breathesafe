locals {
  # Map buckets to their regions; adjust as needed
  bucket_regions = {
    "breathesafe-production"  = "us-east-1"
    "breathesafe-staging"     = "us-east-2"
    "breathesafe-development" = "us-east-2"
  }

  models_prefixes = [
    "mask-recommender-training-production/models/",
    "mask-recommender-training-staging/models/",
    "mask-recommender-training-development/models/",
  ]

  artifacts_prefixes = [
    "mask-recommender-training-production/artifacts/",
    "mask-recommender-training-staging/artifacts/",
    "mask-recommender-training-development/artifacts/",
  ]
}

# Attach lifecycle rules to existing buckets
resource "aws_s3_bucket_lifecycle_configuration" "mask_recommender_models" {
  for_each = local.bucket_regions
  bucket   = each.key
  provider = each.value == "us-east-2" ? aws.use2 : aws

  rule {
    id     = "expire-models-360d"
    status = "Enabled"

    filter {
      and {
        prefix = "mask-recommender-training-"
      }
    }

    expiration {
      days = 360
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "mask_recommender_artifacts" {
  for_each = local.bucket_regions
  bucket   = each.key
  provider = each.value == "us-east-2" ? aws.use2 : aws

  rule {
    id     = "expire-artifacts-360d"
    status = "Enabled"

    filter {
      and {
        prefix = "mask-recommender-training-"
      }
    }

    expiration {
      days = 360
    }
  }
}
