variable "address" {
  description = "HTTPS URL of the CML controller."
  type        = string

  validation {
    condition     = startswith(var.address, "https://")
    error_message = "The CML controller address must start with https://."
  }
}

variable "token" {
  description = "CML API JWT copied from the CML user menu."
  type        = string
  sensitive   = true
}

variable "skip_verify" {
  description = "Disable CML TLS certificate verification only in the isolated lab."
  type        = bool
  default     = false
}

variable "c8000v_image_definition" {
  description = "CML image definition installed for the cat8000v node definition."
  type        = string
}

variable "external_connector" {
  description = "CML external connector label."
  type        = string
  default     = "System Bridge"
}

variable "dev_router_ip" {
  description = "Static IPv4 address and prefix for C8000V GigabitEthernet1, in CIDR notation."
  type        = string

  validation {
    condition     = can(cidrhost(var.dev_router_ip, 0)) && !strcontains(var.dev_router_ip, ":")
    error_message = "TF_VAR_dev_router_ip must be an IPv4 address with a prefix, for example 192.0.2.50/24."
  }
}

variable "dev_default_gateway" {
  description = "IPv4 default gateway reachable through C8000V GigabitEthernet1."
  type        = string

  validation {
    condition     = can(cidrhost("${var.dev_default_gateway}/32", 0)) && !strcontains(var.dev_default_gateway, ":")
    error_message = "TF_VAR_dev_default_gateway must be an IPv4 address without a prefix."
  }
}

variable "dev_username" {
  type      = string
  sensitive = true
}

variable "dev_password" {
  type      = string
  sensitive = true
}
