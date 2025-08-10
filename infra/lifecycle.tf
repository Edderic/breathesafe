locals {
  buckets = [
    "breathesafe-production",
    "breathesafe-staging",
    "breathesafe-development",
  ]

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
  for_each = toset(local.buckets)
  bucket   = each.value

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
  for_each = toset(local.buckets)
  bucket   = each.value

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
