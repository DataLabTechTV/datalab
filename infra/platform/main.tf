locals {
  docker = [
    {
      name  = "docker-gitlab"
      vm_id = 202
      cores = 1
      memory = {
        dedicated = 2048
        floating  = 4096
      }
      disk = {
        root = 20
        data = 30
      }
    },
    {
      name  = "docker-shared"
      vm_id = 203
      cores = 8
      memory = {
        dedicated = 12288
        floating  = 8192
      }
      disk = {
        root = 20
        data = 180
      }
    },
    {
      name  = "docker-apps"
      vm_id = 204
      cores = 2
      memory = {
        dedicated = 4096
        floating  = 8192
      }
      disk = {
        root = 20
        data = 80
      }
    }
  ]
}

resource "random_password" "gitlab_vm" {
  length  = 20
  special = false
}

resource "random_password" "docker_vm" {
  count   = length(local.docker)
  length  = 20
  special = false
}

resource "proxmox_virtual_environment_download_file" "ubuntu_24_04_qcow2" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = var.pm_endpoint

  url       = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
  file_name = "ubuntu-24.04-noble-server-cloudimg-amd64.img"
}

resource "proxmox_virtual_environment_file" "docker" {
  count = length(local.docker)

  content_type = "snippets"
  datastore_id = "local"
  node_name    = var.pm_node

  source_raw {
    data = <<-EOF
    #cloud-config
    hostname: "${local.docker[count.index].name}"
    password: "${random_password.docker_vm[count.index].result}"
    ssh_pwauth: true
    package_update: true
    package_upgrade: true
    packages:
      - qemu-guest-agent
    runcmd:
      - systemctl enable --now qemu-guest-agent
    EOF

    file_name = "${local.docker[count.index].name}.cloud-config.yaml"
  }
}

resource "proxmox_virtual_environment_vm" "docker" {
  count = length(local.docker)

  node_name = var.pm_node
  vm_id     = local.docker[count.index].vm_id

  agent {
    enabled = true
  }

  cpu {
    cores = try(local.docker[count.index].cores, 1)
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = try(local.docker[count.index].memory.dedicated, 1024)
    floating  = try(local.docker[count.index].memory.floating, 1024)
  }

  network_device {
    bridge = "vmbr0"
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "virtio0"
    size         = try(local.docker[count.index].disk.root, 20)
    file_id      = proxmox_virtual_environment_download_file.ubuntu_24_04_qcow2.id
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "virtio1"
    size         = try(local.docker[count.index].disk.data, 20)
  }

  operating_system {
    type = "l26"
  }

  name = local.docker[count.index].name

  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }

    user_data_file_id = proxmox_virtual_environment_file.docker[count.index].id
  }

  lifecycle {
    ignore_changes = [
      disk[1],
    ]
  }
}
