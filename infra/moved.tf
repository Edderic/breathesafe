moved {
  from = aws_s3_bucket_lifecycle_configuration.mask_recommender_use1["breathesafe-development"]
  to   = aws_s3_bucket_lifecycle_configuration.mask_recommender_use2["breathesafe-development"]
}

moved {
  from = aws_s3_bucket_lifecycle_configuration.mask_recommender_use1["breathesafe-staging"]
  to   = aws_s3_bucket_lifecycle_configuration.mask_recommender_use2["breathesafe-staging"]
}

moved {
  from = aws_s3_bucket_lifecycle_configuration.mask_recommender_use1["breathesafe-production"]
  to   = aws_s3_bucket_lifecycle_configuration.mask_recommender_use2["breathesafe-production"]
}
