output "minio_ct_password" {
  value     = random_password.minio_ct.result
  sensitive = true
}

output "minio_admin_password" {
  value     = random_password.minio_admin.result
  sensitive = true
}
