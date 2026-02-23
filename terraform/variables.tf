variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "grovecj"
}

variable "domain" {
  description = "Base domain name"
  type        = string
  default     = "cartergrove.me"
}

variable "droplet_ip" {
  description = "IP address of the cartergrove-me droplet"
  type        = string
}

variable "database_cluster_name" {
  description = "Name of the shared PostgreSQL cluster"
  type        = string
  default     = "mlb-stats-db"
}

variable "jwt_secret" {
  description = "Secret key for JWT token signing"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
  default     = ""
}
