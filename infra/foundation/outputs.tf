output "minio_container_root_password" {
  value     = random_password.minio_container.result
  sensitive = true
}
