terraform {
  required_version = "~> 1.13.2"

  required_providers {
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "18.4.1"
    }

    dotenv = {
      source  = "jrhouston/dotenv"
      version = "1.0.1"
    }
  }
}
