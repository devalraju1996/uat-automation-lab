terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  # Uncomment after creating the state bucket:
  # backend "s3" {
  #   bucket       = "uat-automation-tfstate-<your-account-id>"
  #   key          = "ecs/uat.tfstate"
  #   region       = "eu-west-2"
  #   use_lockfile = true
  # }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "uat-automation-lab", Environment = var.environment, ManagedBy = "terraform" }
  }
}
