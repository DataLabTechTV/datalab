resource "proxmox_virtual_environment_download_file" "ubuntu_24_04_qcow2" {
  content_type = "iso"
  datastore_id = "local"
  node_name    = var.pm_node

  url       = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
  file_name = "ubuntu-24.04-noble-server-cloudimg-amd64.img"
}
