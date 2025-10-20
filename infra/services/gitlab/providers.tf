provider "gitlab" {
  base_url = var.gitlab_api
  token    = var.gitlab_token
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

provider "dotenv" {}
