terraform {
  required_version = "~> 1.13.2"

  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.83.2"
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
