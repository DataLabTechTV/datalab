locals {
  secret_regex = "(?i)PASSWORD|SECRET"
}

data "dotenv" "config" {
  filename = var.dotenv_path
}

resource "gitlab_project_variable" "datalab_config" {
  for_each = {
    for k, v in data.dotenv.config.env :
    k => v if !can(regex(local.secret_regex, k))
  }

  project       = "${var.gitlab_user}/${var.gitlab_project}"
  key           = each.key
  value         = each.value
  variable_type = "env_var"
  protected     = false
  raw           = true
  hidden        = false
  masked        = false
}

resource "gitlab_project_variable" "datalab_secrets" {
  for_each = {
    for k, v in data.dotenv.config.env :
    k => v if can(regex(local.secret_regex, k))
  }

  project       = "${var.gitlab_user}/${var.gitlab_project}"
  key           = each.key
  value         = sensitive(each.value)
  variable_type = "env_var"
  protected     = false
  raw           = true
  hidden        = false
  masked        = true
}
