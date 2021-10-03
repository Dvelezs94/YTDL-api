output "aws_kms_key_id" {
  value = aws_kms_key.this.id
}

output "aws_iam_role_name" {
  value = aws_iam_role.this.name
}

output "secrets_manager_arn" {
  value = aws_secretsmanager_secret.this_1.arn
}

output "secrets_manager_version_arn" {
  value = aws_secretsmanager_secret_version.this.arn
}