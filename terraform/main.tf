terraform {
  required_version = ">= 1.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

provider "github" {
  token = var.github_token
  owner = var.github_owner
}

# --- DNS Record ---

data "digitalocean_reserved_ip" "cartergrove" {
  ip_address = var.droplet_ip
}

resource "digitalocean_record" "ohhell" {
  domain = var.domain
  type   = "A"
  name   = "ohhell"
  value  = var.droplet_ip
  ttl    = 3600
}

# --- Database ---

data "digitalocean_database_cluster" "postgres" {
  name = var.database_cluster_name
}

resource "digitalocean_database_db" "ohhell" {
  cluster_id = data.digitalocean_database_cluster.postgres.id
  name       = "ohhell"
}

resource "digitalocean_database_user" "ohhell" {
  cluster_id = data.digitalocean_database_cluster.postgres.id
  name       = "ohhell"
}

locals {
  database_url = "postgresql+asyncpg://${digitalocean_database_user.ohhell.name}:${digitalocean_database_user.ohhell.password}@${data.digitalocean_database_cluster.postgres.private_host}:${data.digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.ohhell.name}?ssl=require"
}

# --- GitHub Repository ---

resource "github_repository" "oh_hell" {
  name         = "oh-hell"
  description  = "Oh Hell Online — multiplayer card game"
  homepage_url = "https://ohhell.${var.domain}"
  visibility   = "public"

  has_issues   = true
  has_projects = true
  has_wiki     = false

  delete_branch_on_merge = true
  vulnerability_alerts   = true
}

resource "github_repository_dependabot_security_updates" "oh_hell" {
  repository = github_repository.oh_hell.name
  enabled    = true
}

resource "github_branch_protection" "main" {
  repository_id = github_repository.oh_hell.name
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = [
      "Backend Lint & Test",
      "Frontend Build & Test",
    ]
  }

  required_pull_request_reviews {
    required_approving_review_count = 0
    dismiss_stale_reviews           = true
  }

  allows_force_pushes = false
  allows_deletions    = false
  require_conversation_resolution = true
}

# --- Deploy Key (reuse cartergrove-me pattern) ---

resource "tls_private_key" "deploy" {
  algorithm = "ED25519"
}

# --- GitHub Actions Secrets ---

resource "github_actions_secret" "droplet_ip" {
  repository      = github_repository.oh_hell.name
  secret_name     = "DROPLET_IP"
  plaintext_value = var.droplet_ip
}

resource "github_actions_secret" "deploy_ssh_key" {
  repository      = github_repository.oh_hell.name
  secret_name     = "DEPLOY_SSH_KEY"
  plaintext_value = tls_private_key.deploy.private_key_openssh
}

resource "github_actions_secret" "database_url" {
  repository      = github_repository.oh_hell.name
  secret_name     = "DATABASE_URL"
  plaintext_value = local.database_url
}

resource "github_actions_secret" "jwt_secret" {
  repository      = github_repository.oh_hell.name
  secret_name     = "JWT_SECRET"
  plaintext_value = var.jwt_secret
}

resource "github_actions_secret" "google_client_id" {
  repository      = github_repository.oh_hell.name
  secret_name     = "GOOGLE_CLIENT_ID"
  plaintext_value = var.google_client_id
}

resource "github_actions_secret" "google_client_secret" {
  repository      = github_repository.oh_hell.name
  secret_name     = "GOOGLE_CLIENT_SECRET"
  plaintext_value = var.google_client_secret
}
