#===============================================================================
# TERRAFORM VARIABLES
# AWS ECS Infrastructure for Telegram Bot
#===============================================================================

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "telegram-bot"
}

#-------------------------------------------------------------------------------
# Secrets (passed via TF_VAR_ or -var)
#-------------------------------------------------------------------------------

variable "rapidapi_key" {
  description = "RapidAPI Key for GPT and Job Search"
  type        = string
  sensitive   = true
}

variable "bot_token" {
  description = "Telegram Bot Token"
  type        = string
  sensitive   = true
}

#-------------------------------------------------------------------------------
# Security
#-------------------------------------------------------------------------------

variable "allowed_ssh_ip" {
  description = "IP address allowed to SSH into NAT instance (CIDR notation)"
  type        = string
}

variable "ssh_key_name" {
  description = "Name of SSH key pair for EC2 instances (optional)"
  type        = string
  default     = ""
}
