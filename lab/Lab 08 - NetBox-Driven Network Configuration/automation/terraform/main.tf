resource "cml2_lab" "validation" {
  title       = "Lab 8 loopback validation"
  description = "Temporary C8000V created by the Lab 8 NetBox-triggered pipeline"
}

resource "cml2_node" "external" {
  lab_id         = cml2_lab.validation.id
  label          = "External connectivity"
  nodedefinition = "external_connector"
  configuration  = var.external_connector
  x              = -100
  y              = 0
}

resource "cml2_node" "router" {
  lab_id          = cml2_lab.validation.id
  label           = "LAB8-C8000V-DEV"
  nodedefinition  = "cat8000v"
  imagedefinition = var.c8000v_image_definition
  x               = 100
  y               = 0
  configuration   = <<-EOT
    hostname LAB8-C8000V-DEV
    username ${var.dev_username} privilege 15 secret ${var.dev_password}
    ip domain name lab.local
    crypto key generate rsa modulus 2048
    ip ssh version 2
    restconf
    netconf-yang
    interface GigabitEthernet1
     ip address ${split("/", var.dev_router_ip)[0]} ${cidrnetmask(var.dev_router_ip)}
     no shutdown
    ip route 0.0.0.0 0.0.0.0 ${var.dev_default_gateway}
    line vty 0 4
     login local
     transport input ssh
    end
  EOT
}

resource "cml2_link" "management" {
  lab_id = cml2_lab.validation.id
  node_a = cml2_node.external.id
  slot_a = 0
  node_b = cml2_node.router.id
  slot_b = 0
}

resource "cml2_lifecycle" "validation" {
  lab_id = cml2_lab.validation.id
  state  = "STARTED"
  wait   = true
  depends_on = [cml2_link.management]
  timeouts = {
    create = "15m"
    update = "15m"
    delete = "10m"
  }
}

output "dev_router_ip" {
  value = split("/", var.dev_router_ip)[0]
}

output "cml_lab_id" {
  value = cml2_lab.validation.id
}
