# ===================
# Proxmox: Hypervisor
# ===================

variable "pm_endpoint" {
  type        = string
  description = "Proxmox VE endpoint URL"
}

variable "pm_insecure" {
  type        = bool
  description = "Proxmox VE endpoint insecure TLS"
  default     = false
}


variable "pm_node" {
  type        = string
  description = "Proxmox VE node name"
  default     = "pve"
}

variable "pm_user" {
  type        = string
  description = "Proxmox VE PAM user without realm"
  default     = "terraform"
}

variable "pm_token_id" {
  type        = string
  description = "Proxmox VE API token ID"
}

variable "pm_token_secret" {
  type        = string
  description = "Proxmox VE API token secret"
  sensitive   = true
}

# ---------------------
# Proxmox: Host Machine
# ---------------------

variable "pm_host_private_key_path" {
  type        = string
  description = "Path to the SSH private key used to access Proxmox VE"
  default     = "~/.ssh/proxmox"
}
