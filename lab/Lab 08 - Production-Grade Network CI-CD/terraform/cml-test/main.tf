locals {
  lab_name = "netdevops-test-${var.pipeline_id}"
  bootstrap = <<-IOS
    hostname TEST-C8000V-${var.pipeline_id}
    no ip domain lookup
    ip domain name lab.example
    username ${var.router_username} privilege 15 secret 0 ${var.router_password}
    interface GigabitEthernet1
     description CI TEST MANAGEMENT
     ip address ${var.router_ip} ${cidrnetmask("0.0.0.0/${var.router_prefix_length}")}
     no shutdown
    ip route 0.0.0.0 0.0.0.0 ${var.router_gateway}
    crypto key generate rsa modulus 2048
    ip ssh version 2
    line vty 0 4
     login local
     transport input ssh
    end
  IOS
}

resource "cml2_lab" "test" {
  title       = local.lab_name
  description = "Ephemeral CI test lab for GitLab pipeline ${var.pipeline_id}"
  notes       = "Managed by Terraform. Do not edit manually."
}

resource "cml2_node" "external" {
  lab_id         = cml2_lab.test.id
  label          = "Test management"
  nodedefinition = "external_connector"
  configuration  = var.external_connector
  tags           = ["infrastructure"]
  x              = -200
  y              = 0
}

resource "cml2_node" "switch" {
  lab_id         = cml2_lab.test.id
  label          = "Management switch"
  nodedefinition = "unmanaged_switch"
  tags           = ["infrastructure"]
  x              = 0
  y              = 0
}

resource "cml2_node" "router" {
  lab_id         = cml2_lab.test.id
  label          = "TEST-C8000V-${var.pipeline_id}"
  nodedefinition  = var.node_definition
  imagedefinition = var.image_definition
  configuration  = local.bootstrap
  ram            = var.router_ram_mb
  tags           = ["router"]
  x              = 200
  y              = 0
}

resource "cml2_link" "external_to_switch" {
  lab_id = cml2_lab.test.id
  node_a = cml2_node.external.id
  node_b = cml2_node.switch.id
}

resource "cml2_link" "switch_to_router" {
  lab_id = cml2_lab.test.id
  node_a = cml2_node.switch.id
  node_b = cml2_node.router.id
  slot_b = 0
}

resource "cml2_lifecycle" "test" {
  lab_id = cml2_lab.test.id
  state  = "STARTED"
  wait   = true
  update_triggers = {
    external = "${cml2_node.external.id}:${cml2_node.external.generation}"
    switch   = "${cml2_node.switch.id}:${cml2_node.switch.generation}"
    router   = "${cml2_node.router.id}:${cml2_node.router.generation}"
  }
  depends_on = [
    cml2_link.external_to_switch,
    cml2_link.switch_to_router,
  ]
  timeouts = {
    create = "15m"
    update = "15m"
    delete = "10m"
  }
}
