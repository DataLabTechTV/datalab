locals {
  nvidia_driver_version = "580.82.09"

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
      gpu  = true
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

locals {
  docker_nvidia_install_cmds = <<-EOT
  - ls /boot/vmlinuz-* | sort | tail -n1 | cut -d- -f2- > /run/nvidia-kernel-name
  - apt update && apt install -y build-essential dkms linux-headers-$(cat /run/nvidia-kernel-name)
  - wget https://us.download.nvidia.com/XFree86/Linux-x86_64/${local.nvidia_driver_version}/NVIDIA-Linux-x86_64-${local.nvidia_driver_version}.run
  - sh NVIDIA-Linux-x86_64-${local.nvidia_driver_version}.run --silent --dkms --kernel-name=$(cat /run/nvidia-kernel-name)
  - |
    cat <<EOF >>/etc/modules-load.d/modules.conf
    nvidia
    nvidia-modeset
    nvidia_uvm
    EOF
  - update-initramfs -u
  - |
    cat <<EOF >>/etc/udev/rules.d/70-nvidia.rules
    KERNEL=="nvidia", RUN+="/bin/bash -c '/usr/bin/nvidia-smi -L && /bin/chmod 666 /dev/nvidia*'"
    KERNEL=="nvidia_modeset", RUN+="/bin/bash -c '/usr/bin/nvidia-modprobe -c0 -m && /bin/chmod 666 /dev/nvidia-modeset*'"
    KERNEL=="nvidia_uvm", RUN+="/bin/bash -c '/usr/bin/nvidia-modprobe -c0 -u && /bin/chmod 666 /dev/nvidia-uvm*'"
    EOF
  EOT
}

resource "proxmox_virtual_environment_file" "docker_cfg" {
  count = length(local.docker)

  content_type = "snippets"
  datastore_id = "local"
  node_name    = var.pm_node

  source_raw {
    data = templatefile("templates/docker.cloud-config.tftpl", {
      hostname       = local.docker[count.index].name
      password       = random_password.docker_vm[count.index].result
      docker_gpg_key = data.http.docker_gpg.response_body,
      extra_cmds     = try(local.docker[count.index].gpu, false) ? local.docker_nvidia_install_cmds : ""
    })

    file_name = "${local.docker[count.index].name}.cloud-config.yaml"
  }
}

resource "proxmox_virtual_environment_hardware_mapping_pci" "gpu_vga" {
  name = "gpu_vga"
  map = [
    {
      node         = var.pm_node
      path         = "0000:01:00.0"
      id           = "10de:1f15"
      subsystem_id = "17aa:3a47"
      iommu_group  = 10
    }
  ]
}

resource "proxmox_virtual_environment_hardware_mapping_pci" "gpu_audio" {
  name = "gpu_audio"
  map = [
    {
      node         = var.pm_node,
      path         = "0000:01:00.1",
      id           = "10de:10f9",
      subsystem_id = "10de:10f9"
      iommu_group  = 10
    }
  ]
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

  machine = try(local.docker[count.index].gpu, false) ? "q35" : "pc"

  dynamic "hostpci" {
    for_each = try(local.docker[count.index].gpu, false) ? [
      proxmox_virtual_environment_hardware_mapping_pci.gpu_vga.name,
      proxmox_virtual_environment_hardware_mapping_pci.gpu_audio.name
    ] : []

    content {
      device  = "hostpci${hostpci.key}"
      mapping = hostpci.value
      pcie    = true
    }
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
    # prevent_destroy = true
  }
}
