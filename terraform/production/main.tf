provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket  = "cloud-terraform-states"
    key     = "ytdl/production/terraform.tfstate"
    encrypt = true
    region  = "us-east-1"
  }
}


module "ytdl" {
  source      = "../modules/"
  environment = "production"
  region      = "us-east-1"
}