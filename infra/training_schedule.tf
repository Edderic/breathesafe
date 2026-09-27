variable "training_schedule_enabled" {
  description = "Enable weekly production training; set false to pause."
  type        = bool
  default     = true
}

data "aws_lambda_function" "scheduled_training" {
  provider      = aws.use1
  function_name = "mask-recommender-production"
}

# Training publishes a model; don't automatically repeat failed executions.
resource "aws_lambda_function_event_invoke_config" "training" {
  provider                     = aws.use1
  function_name                = data.aws_lambda_function.scheduled_training.function_name
  maximum_event_age_in_seconds = 3600
  maximum_retry_attempts       = 0
}

resource "aws_scheduler_schedule_group" "training" {
  provider = aws.use1
  name     = "mask-recommender-training"
}

resource "aws_iam_role" "training_scheduler" {
  name = "mask-recommender-training-scheduler"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "scheduler.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        ArnEquals = { "aws:SourceArn" = aws_scheduler_schedule_group.training.arn }
      }
    }]
  })
}

resource "aws_iam_role_policy" "training_scheduler" {
  role = aws_iam_role.training_scheduler.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = data.aws_lambda_function.scheduled_training.arn
    }]
  })
}

resource "aws_scheduler_schedule" "training" {
  provider                     = aws.use1
  name                         = "mask-recommender-weekly-production"
  group_name                   = aws_scheduler_schedule_group.training.name
  description                  = "Weekly custom_lr training using production fit data"
  schedule_expression          = "cron(0 2 ? * SUN *)"
  schedule_expression_timezone = "UTC"
  state                        = var.training_schedule_enabled ? "ENABLED" : "DISABLED"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = data.aws_lambda_function.scheduled_training.arn
    role_arn = aws_iam_role.training_scheduler.arn
    input = jsonencode({
      method            = "train"
      environment       = "production"
      base_url          = "https://www.breathesafe.xyz"
      model_type        = "custom_lr"
      epochs            = 200
      learning_rate     = 0.01
      retrain_with_full = true
      class_reweight    = false
      raise_on_error    = true
    })
    retry_policy {
      maximum_event_age_in_seconds = 3600
      maximum_retry_attempts       = 0
    }
  }

  depends_on = [aws_iam_role_policy.training_scheduler, aws_lambda_function_event_invoke_config.training]
}
