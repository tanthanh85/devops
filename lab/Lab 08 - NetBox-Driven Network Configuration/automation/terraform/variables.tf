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
  description = "CML external connector device name, for example bridge0."
  type        = string
  default     = "bridge0"
}

variable "dev_username" {
  type      = string
  sensitive = true
}

variable "dev_password" {
  type      = string
  sensitive = true
}
