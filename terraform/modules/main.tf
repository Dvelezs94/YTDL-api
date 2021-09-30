data "aws_caller_identity" "current_account" {
}

data "aws_iam_policy_document" "lambda_role_policy" {
  statement {
    sid    = "AllowLogging"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current_account.account_id}:log-group:/aws/lambda/*",
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current_account.account_id}:log-group:/aws/lambda/*"
    ]
  }

  statement {
    sid    = "AllowKMSAccess"
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      "arn:aws:kms:${var.region}:${data.aws_caller_identity.current_account.account_id}:key/${module.lambda_serverless.aws_kms_key_id}"
    ]
  }

  statement {
    sid    = "AllowSecretsAccess"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current_account.account_id}:secret:${var.environment}/${var.app_name}/all-*"
    ]
  }

  statement {
    sid    = "AllowVPCNetworking"
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = [
      "*"
    ]
  }
}

# load sops
data "local_file" "sops_file" {
  filename = "${path.cwd}/secrets.auto.tfvars.sops.json"
}

data "sops_external" "sops" {
  source     = data.local_file.sops_file.content
  input_type = "json"
}

module "lambda_serverless" {
  source = "git::git@github.com:contextmedia/terraform-infrastructure-live.git//modules/lambda_serverless"

  app_name        = "scim"
  environment     = var.environment
  region          = var.region
  iam_role_policy = data.aws_iam_policy_document.lambda_role_policy.json
  department      = "devops"
  secrets_part_1 = {
    DB_USERNAME  = data.sops_external.sops.data.db_username
    DB_HOST      = data.sops_external.sops.data.db_host
    DB_PASSWORD  = data.sops_external.sops.data.db_password
    DB_NAME      = data.sops_external.sops.data.db_name
  }
}