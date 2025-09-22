resource "random_password" "minio_container" {
  length  = 20
  special = false
}

resource "random_password" "minio_admin" {
  length  = 20
  special = false
}

resource "tls_private_key" "minio_container" {
  algorithm = "ED25519"
}

resource "proxmox_virtual_environment_download_file" "ubuntu_24_04_vztmpl" {
  content_type = "vztmpl"
  datastore_id = "local"
  node_name    = var.pm_node

  url = "http://download.proxmox.com/images/system/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
}

resource "proxmox_virtual_environment_container" "minio" {
  node_name = var.pm_node
  vm_id     = 101
  tags      = ["l1-foundation"]

  start_on_boot = true
  unprivileged  = true

  features {
    nesting = true
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
  }

  network_interface {
    name = "veth0"
  }

  disk {
    datastore_id = "local-lvm"
    size         = 20
  }

  mount_point {
    volume = "local-lvm"
    path   = "/data"
    size   = "100G"
    backup = true
  }

  operating_system {
    template_file_id = proxmox_virtual_environment_download_file.ubuntu_24_04_vztmpl.id
    type             = "ubuntu"
  }

  initialization {
    hostname = "minio"

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }

    user_account {
      keys     = [trimspace(tls_private_key.minio_container.public_key_openssh)]
      password = random_password.minio_container.result
    }
  }

  connection {
    agent       = false
    type        = "ssh"
    user        = "root"
    private_key = trimspace(tls_private_key.minio_container.private_key_openssh)
    host        = self.initialization[0].hostname
  }

  provisioner "file" {
    content = <<-EOF
    export MINIO_ROOT_USER='${var.minio_user}'
    export MINIO_ROOT_PASSWORD='${random_password.minio_admin.result}'
    export MINIO_DATA_DIR='${self.mount_point[0].path}'
    export MINIO_DEFAULT_BUCKETS='${join(" ", var.minio_buckets)}'
    EOF

    destination = "/root/config.envrc"
  }

  provisioner "file" {
    source      = "scripts/install_minio.sh"
    destination = "/root/install_minio.sh"
  }

  provisioner "remote-exec" {
    inline = ["sh /root/install_minio.sh"]
  }
}
