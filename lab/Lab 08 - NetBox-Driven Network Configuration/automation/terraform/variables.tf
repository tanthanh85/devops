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
