#===============================================================================
# TERRAFORM BOOTSTRAP - REMOTE STATE BACKEND
# Creates S3 bucket and DynamoDB table for Terraform state management
#===============================================================================
# RUN THIS FIRST: 
#   cd terraform/bootstrap
#   terraform init
#   terraform apply
#
# Then copy the output values to ../backend.tf
#===============================================================================

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project   = "telegram-bot"
      ManagedBy = "terraform-bootstrap"
      Purpose   = "state-management"
    }
  }
}

#-------------------------------------------------------------------------------
# Random Suffix for Unique Bucket Name
#-------------------------------------------------------------------------------

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

#-------------------------------------------------------------------------------
# S3 Bucket for Terraform State Storage
#-------------------------------------------------------------------------------

resource "aws_s3_bucket" "terraform_state" {
  bucket = "bot-tf-state-${random_id.bucket_suffix.hex}"

  # Prevent accidental deletion of this S3 bucket
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name = "Terraform State Bucket"
  }
}

# Enable versioning for state recovery
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# Block all public access to the bucket
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#-------------------------------------------------------------------------------
# DynamoDB Table for State Locking
#-------------------------------------------------------------------------------

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "bot-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "Terraform State Lock Table"
  }
}

#===============================================================================
# OUTPUTS - Copy these values to ../backend.tf
#===============================================================================

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state (copy to backend.tf)"
  value       = aws_s3_bucket.terraform_state.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking (copy to backend.tf)"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.terraform_locks.arn
}

output "backend_config" {
  description = "Backend configuration to copy to backend.tf"
  value       = <<-EOT
    
    ============================================================
    Copy this configuration to terraform/backend.tf:
    ============================================================
    
    terraform {
      backend "s3" {
        bucket         = "${aws_s3_bucket.terraform_state.id}"
        key            = "prod/bot/terraform.tfstate"
        region         = "us-east-1"
        encrypt        = true
        dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
      }
    }
    
    ============================================================
  EOT
}
