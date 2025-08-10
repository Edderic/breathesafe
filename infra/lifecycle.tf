locals {
  # Map buckets to their regions; adjust as needed
  bucket_regions = {
    "breathesafe-production"  = "us-east-1"
    "breathesafe-staging"     = "us-east-1"
    "breathesafe-development" = "us-east-1"
  }
}

# Attach lifecycle rules to existing buckets
resource "aws_s3_bucket_lifecycle_configuration" "mask_recommender_use1" {
  for_each = {
    for name, region in local.bucket_regions : name => region if region == "us-east-1"
  }
  provider = aws
  bucket   = each.key

  rule {
    id     = "expire-artifacts-prod-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-production/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-artifacts-staging-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-staging/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-artifacts-dev-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-development/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-prod-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-production/models/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-staging-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-staging/models/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-dev-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-development/models/" }
    expiration { days = 360 }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "mask_recommender_use2" {
  for_each = {
    for name, region in local.bucket_regions : name => region if region == "us-east-2"
  }
  provider = aws.use2
  bucket   = each.key

  rule {
    id     = "expire-artifacts-prod-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-production/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-artifacts-staging-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-staging/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-artifacts-dev-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-development/artifacts/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-prod-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-production/models/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-staging-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-staging/models/" }
    expiration { days = 360 }
  }
  rule {
    id     = "expire-models-dev-360d"
    status = "Enabled"
    filter { prefix = "mask-recommender-training-development/models/" }
    expiration { days = 360 }
  }
}
