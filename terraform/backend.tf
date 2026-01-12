#===============================================================================
# TERRAFORM REMOTE BACKEND CONFIGURATION
# S3 + DynamoDB for state storage and locking
#===============================================================================
# 
# IMPORTANT: Before using this backend, you must:
#
# 1. Run the bootstrap to create the S3 bucket and DynamoDB table:
#    cd terraform/bootstrap
#    terraform init
#    terraform apply
#
# 2. Copy the output values and replace the placeholders below.
#
# 3. Initialize this project with the new backend:
#    cd terraform
#    terraform init -migrate-state
#
#===============================================================================

terraform {
  backend "s3" {
    # S3 bucket created by bootstrap
    bucket = "bot-tf-state-2fc4a5f3"

    # State file path within the bucket
    key = "prod/bot/terraform.tfstate"

    # AWS region
    region = "us-east-1"

    # Enable server-side encryption
    encrypt = true

    # TODO: Replace with the DynamoDB table name from bootstrap output
    dynamodb_table = "bot-tf-locks"
  }
}
