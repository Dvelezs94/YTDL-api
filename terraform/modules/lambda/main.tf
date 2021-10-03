locals {
  lambda_identifiers = ["lambda.amazonaws.com", var.edge ? "edgelambda.amazonaws.com" : ""]
}

data "aws_caller_identity" "current_account" {
}

data "template_file" "kms_key_policy" {
  template = file("${path.module}/files/kms_key_policy.json")

  vars = {
    environment   = var.environment
    account_id    = data.aws_caller_identity.current_account.account_id
    app_name      = var.app_name
    task_role_arn = aws_iam_role.this.arn
  }
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = compact(local.lambda_identifiers)
    }
  }
}

resource "aws_iam_role" "this" {
  name = "${var.environment}_${var.app_name}_role"

  assume_role_policy = data.aws_iam_policy_document.lambda_policy.json

  tags = {
    Application = var.app_name
    Environment = var.environment
    Terraform   = true
  }
}

resource "aws_iam_policy" "this" {
  name        = "${var.environment}_${var.app_name}_role"
  description = "Role for ${var.environment} ${var.app_name}, managed by Terraform"

  policy = var.iam_role_policy
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}

resource "aws_kms_key" "this" {
  description             = "KMS key for ${var.environment} ${var.app_name}"
  deletion_window_in_days = 10

  tags = {
    Application = var.app_name
    Environment = var.environment
  }

  policy = data.template_file.kms_key_policy.rendered
}

resource "aws_kms_alias" "this" {
  name          = "alias/${var.environment}_${var.app_name}"
  target_key_id = aws_kms_key.this.key_id
}

resource "aws_secretsmanager_secret" "this_1" {
  name       = "${var.environment}/${var.app_name}/all-1"
  kms_key_id = aws_kms_key.this.id
}

resource "aws_secretsmanager_secret_version" "this" {
  secret_id     = aws_secretsmanager_secret.this_1.id
  secret_string = jsonencode(var.secrets_part_1)
}