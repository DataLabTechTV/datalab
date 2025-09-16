output "minio_container_password" {
  value     = random_password.minio_container.result
  sensitive = true
}

output "minio_admin_password" {
  value     = random_password.minio_admin.result
  sensitive = true
}
