variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "environment" {
  type    = string
  default = "uat"
}

variable "app_name" {
  type    = string
  default = "payments-portal"
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "github_repo" {
  description = "owner/repo allowed to deploy via OIDC"
  type        = string
  default     = "devalraju1996/uat-automation-lab"
}
