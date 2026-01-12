#===============================================================================
# TERRAFORM OUTPUTS
#===============================================================================

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.main.repository_url
}

output "gitlab_ci_role_arn" {
  description = "ARN of the IAM role for GitLab CI"
  value       = aws_iam_role.gitlab_ci.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.main.name
}

output "nat_instance_public_ip" {
  description = "Public IP of the NAT instance"
  value       = aws_eip.nat.public_ip
}

output "webhook_url" {
  description = "Webhook URL for Telegram bot (HTTPS via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.main.domain_name}/webhook"
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name (HTTPS endpoint)"
  value       = aws_cloudfront_distribution.main.domain_name
}
