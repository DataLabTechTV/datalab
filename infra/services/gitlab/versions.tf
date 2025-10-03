terraform {
  required_version = "~> 1.13.2"

  required_providers {
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "18.4.1"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.7.2"
    }

    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.4"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.5.3"
    }
  }
}
