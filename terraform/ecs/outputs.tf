output "uat_base_url" {
  description = "Set this as the UAT_BASE_URL GitHub variable"
  value       = "http://${aws_lb.this.dns_name}"
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "github_deploy_role_arn" {
  description = "Set this as the AWS_DEPLOY_ROLE_ARN GitHub secret"
  value       = aws_iam_role.github_deploy.arn
}
