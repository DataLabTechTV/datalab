resource "random_password" "docker_shared_vm" {
  length  = 20
  special = false
}

resource "random_password" "docker_apps_vm" {
  length  = 20
  special = false
}

resource "random_password" "docker_gitlab_vm" {
  length  = 20
  special = false
}

resource "random_password" "gitlab_vm" {
  length  = 20
  special = false
}
