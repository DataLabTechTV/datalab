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

# ===============
# S3 Object Store
# ===============

variable "s3_access_key" {
  type        = string
  description = "S3 object store access key"
}

variable "s3_secret_key" {
  type        = string
  description = "S3 object store secret key"
}

variable "s3_region" {
  type        = string
  description = "S3 region"
  default     = "eu-west-1"
}

variable "s3_endpoint" {
  type        = string
  description = "S3 object store endpoint URI"
  default     = "http://minio:9000"
}

variable "s3_path_style" {
  type        = bool
  description = "S3 object store path style enable"
  default     = true
}

# ======
# GitLab
# ======

variable "gitlab_s3_registry_bucket" {
  type        = string
  description = "S3 object store bucket name for the GitLab container registry"
  default     = "gitlab"
}
