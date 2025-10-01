variable "gitlab_api" {
  type        = string
  description = "GitLab API endpoint base URL"
  default     = "http://gitlab/api/v4/"
}

variable "gitlab_user" {
  type        = string
  description = "GitLab user or group name"
}

variable "gitlab_project" {
  type        = string
  description = "GitLab project name to push datalab to for CI/CD"
  default     = "datalab"
}

variable "gitlab_token" {
  type        = string
  description = "GitLab project API token"
}

variable "dotenv_path" {
  type        = string
  description = "Relative path to the .env file to load into GitLab variables"
  default     = "../../../.env"
}
