provider "proxmox" {
  endpoint  = var.pm_endpoint
  insecure  = var.pm_insecure
  api_token = "${var.pm_user}@pam!${var.pm_token_id}=${var.pm_token_secret}"

  ssh {
    agent       = false
    username    = var.pm_user
    private_key = file(var.pm_host_private_key_path)
  }
}

provider "random" {}

provider "null" {}

provider "local" {}
