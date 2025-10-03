resource "gitlab_project_variable" "datalab_config" {
  project   = "${var.gitlab_user}/${var.gitlab_project}"
  key       = "MY_VARIABLE"
  value     = "secret_value"
  protected = true
  masked    = true
}
