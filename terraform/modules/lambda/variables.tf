variable "secrets_part_1" {
  description = "Secrets for secrets manager, part 1"
  type        = map(string)
}

variable "environment" {
}

variable "app_name" {
}

variable "region" {
}

variable "iam_role_policy" {
}

variable "edge" {
  default = false
}
