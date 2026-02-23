output "app_url" {
  description = "URL of the Oh Hell app"
  value       = "https://ohhell.${var.domain}"
}

output "deploy_public_key" {
  description = "Add this to the deploy user's authorized_keys on the droplet"
  value       = tls_private_key.deploy.public_key_openssh
}

output "database_url" {
  description = "Production PostgreSQL connection string"
  value       = local.database_url
  sensitive   = true
}
