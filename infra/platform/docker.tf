locals {
  docker = [
    {
      name  = "docker-gitlab"
      vm_id = 202
      cores = 1
      memory = {
        dedicated = 6144
        floating  = 2048
      }
      size = 100
    },
    {
      name  = "docker-shared"
      vm_id = 203
      cores = 8
      memory = {
        dedicated = 20480
        floating  = 12288
      }
      size = 200
    },
    {
      name  = "docker-apps"
      vm_id = 204
      cores = 2
      memory = {
        dedicated = 12288
        floating  = 4096
      }
      size = 100
    }
  ]
}

resource "random_password" "docker_vm" {
  count   = length(local.docker)
  length  = 20
  special = false
}

data "http" "docker_gpg" {
  url = "https://download.docker.com/linux/ubuntu/gpg"
}

resource "proxmox_virtual_environment_file" "docker_cfg" {
  count = length(local.docker)

  content_type = "snippets"
  datastore_id = "local"
  node_name    = var.pm_node

  source_raw {
    data = <<-EOF
    #cloud-config
    hostname: "${local.docker[count.index].name}"
    password: "${random_password.docker_vm[count.index].result}"
    chpasswd:
      expire: false
    ssh_pwauth: true
    apt:
      sources:
        docker:
          source: "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/docker.gpg] https://download.docker.com/linux/ubuntu noble stable"
          key: |
            ${indent(8, chomp(data.http.docker_gpg.response_body))}
    package_update: true
    package_upgrade: true
    packages:
      - qemu-guest-agent
      - docker-ce
    write_files:
      - path: /etc/systemd/system/docker.service.d/override.conf
        owner: 'root:root'
        permissions: '0600'
        content: |
          [Service]
          ExecStart=
          ExecStart=/usr/bin/dockerd
      - path: /etc/docker/daemon.json
        owner: 'root:root'
        permissions: '0600'
        content: |
          {
            "hosts": ["fd://", "tcp://0.0.0.0:2375"],
            "containerd": "/run/containerd/containerd.sock"
          }
    runcmd:
      - systemctl enable --now qemu-guest-agent
      - netplan apply
      - usermod -aG docker ubuntu
      - reboot
    EOF

    file_name = "${local.docker[count.index].name}.cloud-config.yaml"
  }
}

resource "proxmox_virtual_environment_vm" "docker" {
  count = length(local.docker)

  node_name = var.pm_node
  vm_id     = local.docker[count.index].vm_id
  tags      = ["l2-platform"]

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
    size         = try(local.docker[count.index].size, 20)
    file_id      = proxmox_virtual_environment_download_file.ubuntu_24_04_qcow2.id
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

    user_data_file_id = proxmox_virtual_environment_file.docker_cfg[count.index].id
  }

  lifecycle {
    prevent_destroy = true
  }
}
