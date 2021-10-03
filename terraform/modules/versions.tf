terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.59.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.1.0"
    }
    sops = {
      source  = "carlpett/sops"
      version = "0.6.2"
    }
  }
}