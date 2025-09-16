output "docker_shared_vm_password" {
  value     = random_password.docker_shared_vm.result
  sensitive = true
}

output "docker_apps_vm_password" {
  value     = random_password.docker_apps_vm.result
  sensitive = true
}

output "docker_gitlab_vm_password" {
  value     = random_password.docker_gitlab_vm.result
  sensitive = true
}

output "gitlab_vm_password" {
  value     = random_password.gitlab_vm.result
  sensitive = true
}
