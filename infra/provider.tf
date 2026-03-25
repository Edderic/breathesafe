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
  default     = "us-east-2"
}

# Additional provider for resources hosted in us-east-1 when needed.
provider "aws" {
  alias  = "use1"
  region = "us-east-1"
}
