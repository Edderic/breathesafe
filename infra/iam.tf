locals {
  dashboard_recommender_artifact_readers = {
    "breathesafe-production" = "breathesafe"
    "breathesafe-staging"    = "breathesafe-staging"
  }
}

data "aws_iam_policy_document" "dashboard_recommender_artifact_read" {
  for_each = local.dashboard_recommender_artifact_readers

  statement {
    sid    = "ReadMaskRecommenderDashboardArtifacts"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::${each.value}/mask_recommender/models/*"
    ]
  }
}

resource "aws_iam_user_policy" "dashboard_recommender_artifact_read" {
  for_each = local.dashboard_recommender_artifact_readers

  name   = "MaskRecommenderDashboardRead"
  user   = each.key
  policy = data.aws_iam_policy_document.dashboard_recommender_artifact_read[each.key].json
}
