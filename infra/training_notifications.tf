data "aws_caller_identity" "training_alerts" {
  provider = aws.use1
}

resource "aws_sns_topic" "training_alerts" {
  provider = aws.use1
  name     = "mask-recommender-training-alerts"
}

resource "aws_sns_topic_policy" "training_alerts" {
  provider = aws.use1
  arn      = aws_sns_topic.training_alerts.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "CloudWatchAlarmsPublish"
      Effect    = "Allow"
      Principal = { Service = "cloudwatch.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.training_alerts.arn
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.training_alerts.account_id }
        ArnLike = {
          "aws:SourceArn" = "arn:aws:cloudwatch:us-east-1:${data.aws_caller_identity.training_alerts.account_id}:alarm:mask-recommender-training-*"
        }
      }
    }]
  })
}

resource "aws_sns_topic_subscription" "training_alerts_email" {
  provider  = aws.use1
  topic_arn = aws_sns_topic.training_alerts.arn
  protocol  = "email"
  endpoint  = "info@breathesafe.xyz"
}

resource "aws_cloudwatch_metric_alarm" "training_lambda" {
  provider = aws.use1
  for_each = {
    Errors             = "Execution errors or timeouts. Inspect /aws/lambda/mask-recommender-production logs, API credentials and S3 permissions. Includes recommendation failures because this Lambda is shared."
    AsyncEventsDropped = "Queued asynchronous events were discarded. Inspect Lambda throttling, event age, execution errors and concurrency settings."
  }

  alarm_name          = "mask-recommender-training-${each.key}"
  alarm_description   = "mask-recommender-production: ${each.value}"
  namespace           = "AWS/Lambda"
  metric_name         = each.key
  dimensions          = { FunctionName = data.aws_lambda_function.scheduled_training.function_name }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.training_alerts.arn]

  depends_on = [aws_sns_topic_policy.training_alerts]
}

resource "aws_cloudwatch_metric_alarm" "training_delivery" {
  provider            = aws.use1
  alarm_name          = "mask-recommender-training-delivery"
  alarm_description   = "Weekly training delivery failed in schedule group mask-recommender-training. Check Scheduler target, IAM invoke permission, Lambda availability and throttling."
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.training_alerts.arn]

  metric_query {
    id          = "failures"
    expression  = "SUM([target_errors, dropped])"
    label       = "Scheduler delivery failures"
    return_data = true
  }

  dynamic "metric_query" {
    for_each = { target_errors = "TargetErrorCount", dropped = "InvocationDroppedCount" }
    content {
      id          = metric_query.key
      return_data = false
      metric {
        namespace   = "AWS/Scheduler"
        metric_name = metric_query.value
        dimensions  = { ScheduleGroup = aws_scheduler_schedule_group.training.name }
        stat        = "Sum"
        period      = 300
      }
    }
  }

  depends_on = [aws_sns_topic_policy.training_alerts]
}
