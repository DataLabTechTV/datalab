output "docker_gitlab_vm_password" {
  value     = random_password.docker_vm[0].result
  sensitive = true
}

output "docker_shared_vm_password" {
  value     = random_password.docker_vm[1].result
  sensitive = true
}

output "docker_apps_vm_password" {
  value     = random_password.docker_vm[2].result
  sensitive = true
}

output "gitlab_vm_password" {
  value     = random_password.gitlab_vm.result
  sensitive = true
}

output "gitlab_root_password" {
  value     = random_password.gitlab_root.result
  sensitive = true
}
