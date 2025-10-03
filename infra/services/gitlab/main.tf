locals {
  secret_regex = "(?i)PASSWORD|ACCESS_KEY|SECRET"
}

data "dotenv" "config" {
  filename = var.dotenv_path
}

resource "gitlab_project_variable" "datalab_config" {
  for_each      = data.dotenv.config.env
  project       = "${var.gitlab_user}/${var.gitlab_project}"
  key           = each.key
  value         = each.value
  variable_type = "env_var"
  protected     = false
  raw           = true
  hidden        = false
  masked        = can(regex(local.secret_regex, each.key))
}
