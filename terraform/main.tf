terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable Necessary GCP APIs
resource "google_project_service" "gcp_services" {
  for_each = toset([
    "aiplatform.googleapis.com",       # Vertex AI API for gemini-2.5-flash
    "run.googleapis.com",              # Google Cloud Run API
    "artifactregistry.googleapis.com", # Google Artifact Registry API
    "iam.googleapis.com",              # Identity and Access Management API
    "storage.googleapis.com",          # Google Cloud Storage API
    "cloudbuild.googleapis.com"        # Cloud Build API
  ])

  project                    = var.project_id
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = false
}

# 2. Artifact Registry Repository
resource "google_artifact_registry_repository" "cybage_repo" {
  depends_on    = [google_project_service.gcp_services]
  provider      = google
  location      = var.region
  repository_id = var.gar_repository_name
  description   = "Docker Repository for Cybage DevOps Applications & Agent Images"
  format        = "DOCKER"
}

# 3. Google Cloud Storage Bucket for Deployment Artifacts
resource "google_storage_bucket" "artifacts_bucket" {
  depends_on    = [google_project_service.gcp_services]
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
  }
}

resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.artifacts_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# 4. Deploy Webhook Handler & Agent Services to Cloud Run

# Webhook Service
resource "google_cloud_run_v2_service" "webhook_service" {
  name     = "github-webhook-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.adk_agent_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.gar_repository_name}/github-webhook-service:latest"
      
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "GAR_REPOSITORY"
        value = var.gar_repository_name
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = var.gcs_bucket_name
      }
      env {
        name  = "SLACK_WEBHOOK_URL"
        value = var.slack_webhook_url
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi"
        }
      }
    }
  }
}

# Unauthenticated IAM Access for GitHub Webhook Service
resource "google_cloud_run_v2_service_iam_member" "webhook_public_access" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.webhook_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Agents Deployment: Orchestrator Agent Service
resource "google_cloud_run_v2_service" "deployment_manager_agent_service" {
  name     = "deployment-manager-agent"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.adk_agent_sa.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.gar_repository_name}/deployment-manager-agent:latest"

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
    }
  }
}
