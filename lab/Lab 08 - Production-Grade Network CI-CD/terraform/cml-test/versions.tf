terraform {
  required_version = ">= 1.6, < 2.0"
  backend "http" {}
  required_providers {
    cml2 = {
      source  = "CiscoDevNet/cml2"
      version = "~> 0.9.0"
    }
  }
}

provider "cml2" {
  address     = var.cml_address
  token       = var.cml_token
  skip_verify = var.cml_skip_verify
}
