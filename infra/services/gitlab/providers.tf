provider "gitlab" {
  base_url = var.gitlab_api
  token    = var.gitlab_token
}

provider "dotenv" {}
