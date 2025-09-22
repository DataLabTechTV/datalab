output "docker_vm_password" {
  value     = random_password.docker_vm[*].result
  sensitive = true
}

output "gitlab_vm_password" {
  value     = random_password.gitlab_vm.result
  sensitive = true
}
