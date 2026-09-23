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
    username ${var.dev_username} privilege 15 secret 0 ${var.dev_password}
    aaa new-model
    aaa authentication login default local
    aaa authorization exec default local
    ip domain name lab.local
    ip ssh rsa keypair-name LAB8-SSH
    ip ssh version 2
    restconf
    netconf-yang
    interface GigabitEthernet1
     ip address ${split("/", var.dev_router_ip)[0]} ${cidrnetmask(var.dev_router_ip)}
     no shutdown
    ip route 0.0.0.0 0.0.0.0 ${var.dev_default_gateway}
    line vty 0 4
     login authentication default
     authorization exec default
     transport input ssh
    event manager applet LAB8-GENERATE-SSH-KEY authorization bypass
     event timer countdown time 30
     action 1.0 cli command "enable"
     action 2.0 cli command "show crypto key mypubkey rsa | include LAB8-SSH"
     action 3.0 regexp "LAB8-SSH" "$_cli_result"
     action 4.0 if $_regexp_result eq "0"
     action 4.1 cli command "configure terminal"
     action 4.2 cli command "crypto key generate rsa general-keys modulus 2048 label LAB8-SSH"
     action 4.3 cli command "end"
     action 4.4 syslog msg "LAB8 generated the 2048-bit RSA SSH key"
     action 4.5 end
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
