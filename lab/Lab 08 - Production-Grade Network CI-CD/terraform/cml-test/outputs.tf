output "lab_id" { value = cml2_lab.test.id }
output "lab_name" { value = cml2_lab.test.title }
output "learner_id" { value = var.learner_id }
output "router_node_id" { value = cml2_node.router.id }
output "router_name" { value = cml2_node.router.label }
output "router_management_ip" { value = var.router_ip }
output "lifecycle_booted" { value = cml2_lifecycle.test.booted }
