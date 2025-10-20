locals {
  gitlab = {
    name  = "gitlab"
    vm_id = 201
    cores = 4
    memory = {
      dedicated = 8192
      floating  = 8192
    }
    size = 200
  }
}

resource "random_password" "gitlab_vm" {
  length  = 20
  special = false
}

resource "random_password" "gitlab_root" {
  length  = 20
  special = false
}

resource "proxmox_virtual_environment_file" "gitlab_cfg" {
  content_type = "snippets"
  datastore_id = "local"
  node_name    = var.pm_node

  source_raw {
    data = <<-EOF
    #cloud-config
    hostname: ${local.gitlab.name}
    password: "${random_password.gitlab_vm.result}"
    chpasswd:
      expire: false
    ssh_pwauth: true
    package_update: true
    package_upgrade: true
    packages:
      - qemu-guest-agent
      - curl
    write_files:
      - path: /etc/gitlab/gitlab.rb
        owner: 'root:root'
        permissions: '0600'
        content: |
          external_url 'http://${local.gitlab.name}'
          gitlab_rails['initial_root_password'] = '${random_password.gitlab_root.result}'

          gitlab_rails['registry_enabled'] = true
          registry_external_url 'http://${local.gitlab.name}:5050'

          registry['database'] = {
            'enabled' => true,
          }

          registry['storage'] = {
            's3_v2' => {
              'regionendpoint' => '${var.s3_endpoint}',
              'region' => '${var.s3_region}',
              'accesskey' => '${var.s3_access_key}',
              'secretkey' => '${var.s3_secret_key}',
              'pathstyle' => ${var.s3_path_style},
              'bucket' => '${var.gitlab_s3_registry_bucket}',
              'checksum_disabled' => true,
            }
          }
    runcmd:
      - systemctl enable --now qemu-guest-agent
      - netplan apply
      - curl "https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh" | sudo bash
      - apt install -y gitlab-ce
      - gitlab-ctl reconfigure
      - |
        gitlab-rails console -e production <<EOT
          s = ApplicationSetting.current
          s.update!(
            signup_enabled: false,
            version_check_enabled: false,
            usage_ping_enabled: false,
            usage_ping_generation_enabled: false,
            whats_new_variant: 'disabled'
          )
        EOT
      - curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
      - apt install -y gitlab-runner
      - |
        gitlab-runner register --non-interactive \
          --url "http://${local.gitlab.name}/" \
          --registration-token "$(gitlab-rails runner 'puts ApplicationSetting.current.runners_registration_token')" \
          --executor "docker" \
          --docker-image "ubuntu:latest" \
          --description "ubuntu-latest-runner" \
          --tag-list "docker,remote,ubuntu" \
          --run-untagged="true" \
          --docker-host "tcp://${local.docker[0].name}:2375"
      - sed -i 's/^concurrent = 1/concurrent = 4/' /etc/gitlab-runner/config.toml
      - reboot
    EOF

    file_name = "${local.gitlab.name}.cloud-config.yaml"
  }
}

resource "proxmox_virtual_environment_vm" "gitlab" {
  node_name = var.pm_node
  vm_id     = local.gitlab.vm_id
  tags      = ["l2-platform"]

  agent {
    enabled = true
  }

  cpu {
    cores = local.gitlab.cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = local.gitlab.memory.dedicated
    floating  = local.gitlab.memory.floating
  }

  network_device {
    bridge = "vmbr0"
  }

  disk {
    datastore_id = "local-lvm"
    interface    = "virtio0"
    size         = local.gitlab.size
    file_id      = proxmox_virtual_environment_download_file.ubuntu_24_04_qcow2.id
  }

  operating_system {
    type = "l26"
  }

  name = "gitlab"

  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }

    user_data_file_id = proxmox_virtual_environment_file.gitlab_cfg.id
  }

  lifecycle {
    prevent_destroy = true
  }
}
