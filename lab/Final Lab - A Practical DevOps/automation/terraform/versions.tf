terraform {
  required_version = ">= 1.6.0"
  backend "http" {}
  required_providers {
    cml2 = {
      source  = "CiscoDevNet/cml2"
      version = ">= 0.8.5"
    }
  }
}

provider "cml2" {
  address     = var.address
  token       = var.token
  skip_verify = var.skip_verify
}
