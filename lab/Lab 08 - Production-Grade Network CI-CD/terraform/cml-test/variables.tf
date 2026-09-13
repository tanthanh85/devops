variable "pipeline_id" { type = string }
variable "cml_address" { type = string }
variable "cml_token" { type = string; sensitive = true }
variable "cml_skip_verify" { type = bool; default = false }
variable "external_connector" { type = string; default = "bridge0" }
variable "node_definition" { type = string; default = "cat8000v" }
variable "image_definition" { type = string; default = null }
variable "router_ip" { type = string }
variable "router_prefix_length" { type = number }
variable "router_gateway" { type = string }
variable "router_username" { type = string }
variable "router_password" {
  type      = string
  sensitive = true
  validation {
    condition     = can(regex("^[A-Za-z0-9._-]{16,64}$", var.router_password))
    error_message = "Use a 16-64 character temporary password containing only letters, numbers, dot, underscore, or hyphen."
  }
}

variable "router_ram_mb" {
  type    = number
  default = 4096
  validation {
    condition     = var.router_ram_mb >= 4096
    error_message = "The instructor must allocate at least 4096 MB to the C8000V."
  }
}
