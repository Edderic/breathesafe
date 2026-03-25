locals {
  mask_recommender_log_groups = {
    "/aws/lambda/mask-recommender"                        = "us-east-1"
    "/aws/lambda/mask-recommender-production"             = "us-east-1"
    "/aws/lambda/mask-recommender-staging"                = "us-east-1"
    "/aws/lambda/mask-recommender-inference-production"   = "us-east-1"
    "/aws/lambda/mask-recommender-inference-staging"      = "us-east-1"
    "/aws/lambda/mask-recommender-training-production"    = "us-east-1"
    "/aws/lambda/mask-recommender-training-staging"       = "us-east-1"
  }
}

resource "aws_cloudwatch_log_group" "mask_recommender" {
  for_each = {
    for name, region in local.mask_recommender_log_groups : name => region if region == "us-east-1"
  }

  provider          = aws.use1
  name              = each.key
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "mask_recommender_use2" {
  for_each = {
    for name, region in local.mask_recommender_log_groups : name => region if region == "us-east-2"
  }

  provider          = aws
  name              = each.key
  retention_in_days = 30
}
