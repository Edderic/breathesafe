terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region to use for resources"
  type        = string
  default     = "us-east-1"
}

# Additional provider for buckets hosted in us-east-2
provider "aws" {
  alias  = "use2"
  region = var.aws_region_use2
}

variable "aws_region_use2" {
  description = "AWS region for buckets hosted in us-east-2"
  type        = string
  default     = "us-east-2"
}
